import asyncio
import json
import os
import random

from haystack import component
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from pydantic import BaseModel, Field
from tqdm import trange

from src.models.cluster import Cluster
from src.models.relation import Relation, Relationship


class Response(BaseModel):
    relationship: Relationship = Field(
        description="The identified relationship between the two documents. It can be 'example_of', 'subtopic_of'. 'alternative_to' or in most cases 'none' if no relationship could be identified.",
    )
    reasoning: str = Field(
        description="The reasoning behind the identified relationship between the two documents.",
    )


@component
class ClusterRelationshipClassificationComponent:
    def __init__(self, theme: str) -> None:
        self.theme = theme

    @component.output_types(relations=list[Relation])
    def run(self, clusters: list[Cluster]):
        """
        Classify the relationships between the clustered documents.

        Args:
            clusters: A list of Cluster objects to classify relationships for
        Returns:
            A list of Relations objects representing the classified relationships between the clustered documents
        """

        relation_model = OpenAIChatGenerator(
            model=os.environ.get("RELATION_MODEL", "gpt-5.4-mini"),
            api_base_url=os.environ.get("RELATION_MODEL_API_BASE_URL"),
            generation_kwargs={
                "response_format": Response,
                "temperature": os.environ.get("RELATION_MODEL_TEMPERATURE", 0.0),
            },
        )

        async def relation_request(doc_A, doc_B) -> Relationship:
            few_shots: list[tuple[str, str]] = [
                (
                    """
                    Theme: Machine Learning
                    Chunks: Machine learning is a branch of artificial intelligence that focuses on the use of data and algorithms to imitate the way that humans learn, gradually improving its accuracy. It encompasses various techniques, including supervised learning, unsupervised learning, and reinforcement learning.<sep>Reinforcement learning involves training an agent to make a sequence of decisions by rewarding desired behaviors and punishing negative ones. It is highly effective in environments where an agent must interact to achieve a goal, such as in robotics or playing complex games like Go.""",
                    "{relationship: 'specification', reasoning: 'The second document provides a specific aspect of machine learning, which is reinforcement learning. It falls under the broader topic of machine learning, making it a subtopic of the first document.'}",
                ),
                (
                    """
                    Theme: Invasive Species
                    Chunks: Invasive species are non-native organisms that, when introduced to a new environment, cause harm to the local ecosystem. They often lack natural predators in their new habitats, allowing their populations to grow unchecked and outcompete native species for resources.<sep>In 1935, the cane toad was introduced to Australia to control the cane beetle population. However, without natural predators, the toxic toads rapidly multiplied, spreading across the continent and devastating local populations of snakes, lizards, and marsupials.""",
                    "{relationship: 'example', reasoning: 'The second document provides a specific example of an invasive species, the cane toad in Australia, which illustrates the concepts discussed in the first document about invasive species and their impact on ecosystems.'}",
                ),
                (
                    """
                    Theme: Biotechnology
                    Chunks: mRNA vaccines work by introducing a piece of messenger RNA that corresponds to a specific viral protein. This instructs the host's cells to produce the protein, triggering an immune response and the production of antibodies without ever exposing the body to the live virus.<sep>CRISPR-Cas9 is a revolutionary gene-editing technology derived from a natural defense mechanism found in bacteria. It acts like molecular scissors, using a guide RNA to allow scientists to precisely cut and alter specific sequences of DNA within a living organism's genome.""",
                    "{type: 'none', reasoning: 'The two documents discuss entirely different topics within the field of biotechnology. The first document focuses on mRNA vaccines and their mechanism of action, while the second document describes CRISPR-Cas9 gene-editing technology. There is no significant relationship between the two documents in terms of content, topic, or perspective.'}",
                ),
                (
                    """
                    Theme: Web Technologies
                    Chunks: Continuous Integration (CI) is a software development practice where developers regularly merge their code changes into a central repository. Automated builds and tests are then run against this new code to immediately identify integration errors and prevent broken software from reaching production.<sep>A Content Delivery Network (CDN) is a geographically distributed group of servers that work together to provide fast delivery of Internet content. By caching static assets like images and scripts closer to the end-user, CDNs significantly reduce page load latency and bandwidth costs.""",
                    "{type: 'none', reasoning: 'The two documents discuss different aspects of technology. The first document focuses on software development practices, specifically Continuous Integration, while the second document describes Content Delivery Networks, which are related to web performance optimization. There is no significant relationship between the two documents in terms of content, topic, or perspective.'}",
                ),
            ]

            ## shuffle few shots
            random.shuffle(few_shots)

            messages = []
            for example_input, example_output in few_shots:
                messages.append(ChatMessage.from_user(example_input))
                messages.append(ChatMessage.from_assistant(example_output))

            relation = (
                (
                    await relation_model.run_async(
                        [
                            ChatMessage.from_system(
                                """
                                You are an assistant for analyzing the relationship between two document chunks. All the chunks share the same theme.
                                Your task is to identify if there is a specific relationship between the two documents and if so, classify it into one of the following categories: 'example_of', 'subtopic_of', 'alternative_to' or 'none'.

                                'example' indicates that one document serves as a specific example or case study illustrating the concepts or ideas presented in the other document.

                                'specification' indicates that one document covers a more specific aspect or subtopic that falls under the broader topic covered by the other document.

                                'none' indicates that there is no significant relationship between the two documents in terms of content, topic, or perspective.
                                """
                            ),
                            *messages,
                            ChatMessage.from_user(
                                f"""
                                Theme: {self.theme}
                                Chunks: {doc_A.content}<sep>{doc_B.content}
                                """
                            ),
                        ]
                    )
                )["replies"][0].text
                or "{}"
            )  # Return an empty JSON object if the model does not provide a response

            return json.loads(relation).get("relationship", Relationship.NONE)

        async def single_relation_comparison(i, relations, cluster_docs):
            results = await asyncio.gather(
                *[
                    relation_request(cluster_docs[i], cluster_docs[j])
                    for j in range(i + 1, len(cluster_docs))
                ]
            )
            for j in range(i + 1, len(cluster_docs)):
                result = results[j - (i + 1)]
                if result != Relationship.NONE:
                    relations.append(
                        Relation(
                            document_A=cluster_docs[i].id,
                            document_B=cluster_docs[j].id,
                            relationship=result,
                        )
                    )

        relations = []

        for cluster in clusters:
            cluster_docs = cluster.documents

            relation_comparisons = []

            for i in trange(
                len(cluster_docs),
                desc="Classifying relationships between documents in cluster",
            ):
                relation_comparisons.append(
                    single_relation_comparison(i, relations, cluster_docs)
                )

            async def run_comparisons():
                await asyncio.gather(*relation_comparisons)

            asyncio.run(run_comparisons())

        return {
            "relations": relations,
        }
