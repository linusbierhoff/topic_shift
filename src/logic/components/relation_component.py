import asyncio
import json
from typing import Optional

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
class RelationshipClassificationComponent:
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
            generation_kwargs={"response_format": Response}, model="gpt-4.1-mini"
        )

        async def relation_request(doc_A, doc_B) -> Optional[Relationship]:
            relation = (
                (
                    await relation_model.run_async(
                        [
                            ChatMessage.from_system(
                                """
                                You are an assistant for analyzing the relationship between two documents. Your task is to identify if there is a specific relationship between the two documents and if so, classify it into one of the following categories: 'example_of', 'subtopic_of', 'alternative_to' or 'none'.

                                'example_of' indicates that one document serves as a specific example or case study illustrating the concepts or ideas presented in the other document.

                                'subtopic_of' indicates that one document covers a more specific aspect or subtopic that falls under the broader topic covered by the other document.

                                'alternative_to' indicates that the two documents present different approaches, methods, or perspectives on the same topic, suggesting that they can be considered as alternatives to each other.

                                'none' indicates that there is no significant relationship between the two documents in terms of content, topic, or perspective.
                                """
                            ),
                            ChatMessage.from_user(
                                f"""
                                {doc_A.content}
                                <sep>
                                {doc_B.content}
                                """
                            ),
                        ]
                    )
                )["replies"][0].text
                or "{}"
            )  # Return an empty JSON object if the model does not provide a response

            return json.loads(relation).get("relationship", None)

        async def single_relation_comparison(i, relations, cluster_docs):
            results = await asyncio.gather(
                *[
                    relation_request(cluster_docs[i], cluster_docs[j])
                    for j in range(i + 1, len(cluster_docs))
                ]
            )
            for j in range(i + 1, len(cluster_docs)):
                result = results[j - (i + 1)]
                if result is not None:
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
