import asyncio
import json
import os
import random

from haystack import Document, component
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from pydantic import BaseModel, Field

from src.models.relation import Relation, Relationship


class Response(BaseModel):
    relationship: Relationship = Field(
        description="The identified relationship between the two documents. It can be 'example_of', 'subtopic_of'. 'alternative_to' or in most cases 'none' if no relationship could be identified.",
    )
    reasoning: str = Field(
        description="The reasoning behind the identified relationship between the two documents.",
    )


@component
class RelationshipClassificationComponent:
    def __init__(self, theme: str, window_size: int = 5) -> None:
        """Initialize the RelationshipClassificationComponent.
        Args:
            theme: The common theme shared by the documents in the s, which will be used to provide context for the relationship classification.
            window_size: The number of previous chunks to consider for the relationship classification. We only consider relationships between documents that are within this window size to reduce the number of comparisons and focus on more relevant relationships. Every requests considers the previous window_size chunks as context for the relationship classification. E.g.. if window_size is 5, when comparing chunk 10 and 8, the model will also receive chunks 5-9 as context for the relationship classification.
        """

        self.theme = theme
        self.window_size = window_size

    @component.output_types(relations=list[Relation])
    def run(self, documents: list[Document]):
        """
        Classify the relationships between the documents.

        Args:
            documents: A list of Document objects to classify relationships for
        Returns:
            A list of Relations objects representing the classified relationships between the documents
        """

        relation_model = OpenAIChatGenerator(
            model=os.environ.get("RELATION_MODEL", "gpt-5.4-mini"),
            api_base_url=os.environ.get("RELATION_MODEL_API_BASE_URL"),
            generation_kwargs={
                "response_format": Response,
                "temperature": os.environ.get("RELATION_MODEL_TEMPERATURE", 0.0),
            },
        )

        async def relation_request(
            source_doc: Document,
            target_doc: Document,
            context_docs: list[Document],
            relations: list[Relation],
        ) -> Relationship:
            few_shots: list[tuple[str, str]] = [
                # (
                #     """
                #     Theme: Machine Learning
                #     Chunks: Machine learning is a branch of artificial intelligence that focuses on the use of data and algorithms to imitate the way that humans learn, gradually improving its accuracy. It encompasses various techniques, including supervised learning, unsupervised learning, and reinforcement learning.<sep>Reinforcement learning involves training an agent to make a sequence of decisions by rewarding desired behaviors and punishing negative ones. It is highly effective in environments where an agent must interact to achieve a goal, such as in robotics or playing complex games like Go.""",
                #     "{relationship: 'specification', reasoning: 'The second document provides a specific aspect of machine learning, which is reinforcement learning. It falls under the broader topic of machine learning, making it a subtopic of the first document.'}",
                # ),
                # (
                #     """
                #     Theme: Invasive Species
                #     Chunks: Invasive species are non-native organisms that, when introduced to a new environment, cause harm to the local ecosystem. They often lack natural predators in their new habitats, allowing their populations to grow unchecked and outcompete native species for resources.<sep>In 1935, the cane toad was introduced to Australia to control the cane beetle population. However, without natural predators, the toxic toads rapidly multiplied, spreading across the continent and devastating local populations of snakes, lizards, and marsupials.""",
                #     "{relationship: 'example', reasoning: 'The second document provides a specific example of an invasive species, the cane toad in Australia, which illustrates the concepts discussed in the first document about invasive species and their impact on ecosystems.'}",
                # ),
                # (
                #     """
                #     Theme: Biotechnology
                #     Chunks: mRNA vaccines work by introducing a piece of messenger RNA that corresponds to a specific viral protein. This instructs the host's cells to produce the protein, triggering an immune response and the production of antibodies without ever exposing the body to the live virus.<sep>CRISPR-Cas9 is a revolutionary gene-editing technology derived from a natural defense mechanism found in bacteria. It acts like molecular scissors, using a guide RNA to allow scientists to precisely cut and alter specific sequences of DNA within a living organism's genome.""",
                #     "{type: 'none', reasoning: 'The two documents discuss entirely different topics within the field of biotechnology. The first document focuses on mRNA vaccines and their mechanism of action, while the second document describes CRISPR-Cas9 gene-editing technology. There is no significant relationship between the two documents in terms of content, topic, or perspective.'}",
                # ),
                # (
                #     """
                #     Theme: Web Technologies
                #     Chunks: Continuous Integration (CI) is a software development practice where developers regularly merge their code changes into a central repository. Automated builds and tests are then run against this new code to immediately identify integration errors and prevent broken software from reaching production.<sep>A Content Delivery Network (CDN) is a geographically distributed group of servers that work together to provide fast delivery of Internet content. By caching static assets like images and scripts closer to the end-user, CDNs significantly reduce page load latency and bandwidth costs.""",
                #     "{type: 'none', reasoning: 'The two documents discuss different aspects of technology. The first document focuses on software development practices, specifically Continuous Integration, while the second document describes Content Delivery Networks, which are related to web performance optimization. There is no significant relationship between the two documents in terms of content, topic, or perspective.'}",
                # ),
            ]

            ## shuffle few shots
            random.shuffle(few_shots)

            messages = []
            for example_input, example_output in few_shots:
                messages.append(ChatMessage.from_user(example_input))
                messages.append(ChatMessage.from_assistant(example_output))


            document_section = "\n".join([doc.content for doc in [*context_docs, source_doc]])

            relation = (
                (
                    await relation_model.run_async(
                        [
                            ChatMessage.from_system(
                                """
                                You are an assistant for analyzing the relationship between two document chunks. All the chunks share the same theme.
                                Your task is to identify if there is a specific relationship between the two documents and if so, classify it into one of the following categories: 'example', 'specification' or 'none'.

                                'example' indicates that one document serves as a specific example or case study illustrating the concepts or ideas presented in the other document.

                                'specification' indicates that one document covers a more specific aspect or subtopic that falls under the broader topic covered by the other document.

                                'none' indicates that there is no significant relationship between the two documents in terms of content, topic, or perspective.
                                """
                            ),
                            *messages,
                            ChatMessage.from_user(
                                f"""
                                Given the following part of a document:
                                
                                <document_section>{document_section}</document_section>
                                
                                The relation between: {source_doc.content} and  {target_doc.content} is:
                                """
                            ),
                        ]
                    )
                )["replies"][0].text
                or "{}"
            )  # Return an empty JSON object if the model does not provide a response
            relation = json.loads(relation).get("relationship", Relationship.NONE)
            if relation != Relationship.NONE:
                relations.append(
                    Relation(
                        document_A=target_doc.id,
                        document_B=source_doc.id,
                        relationship=relation,
                    )
                )

        relations = []

        relation_comparisons = []

        for i in range(
            1, len(documents)
        ):  # Start with 1 since we compare with previous documents
            source_doc = documents[i]
            last_index = max(0, i - self.window_size)

            context_docs = documents[last_index:i]

            for context_doc in context_docs:
                relation_comparisons.append(
                    relation_request(
                        source_doc=source_doc,
                        target_doc=context_doc,
                        context_docs=context_docs,
                        relations=relations,
                    )
                )

        async def run_comparisons():
            await asyncio.gather(*relation_comparisons)

        asyncio.run(run_comparisons())

        return {
            "relations": relations,
        }
