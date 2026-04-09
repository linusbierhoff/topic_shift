import os
from typing import Optional

import numpy as np
from haystack import component
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage, Document
from sklearn.cluster import AgglomerativeClustering

from src.models.cluster import Cluster


@component
class EmbeddingClusteringComponent:
    """
    A Haystack component that clusters document chunks based on their content similarity.
    """

    def __init__(
        self,
        theme: str,
        n_clusters: Optional[int] = None,
        distance_threshold: Optional[float] = 1.2,
    ):
        self.theme = theme
        self.n_clusters = n_clusters
        self.distance_threshold = distance_threshold if n_clusters is None else None

    @component.output_types(clusters=list[Cluster])
    def run(self, documents: list[Document]):
        """
        Cluster the input documents and return the clustered documents.

        Args:
            documents: A list of Document objects to be clustered
        Returns:
            A list of clustered Document objects
        """

        embeddings = np.array([doc.embedding for doc in documents])

        clustering_model = AgglomerativeClustering(
            n_clusters=self.n_clusters,  # pyright: ignore[reportArgumentType]
            distance_threshold=self.distance_threshold,
        )
        detected_clusters = clustering_model.fit_predict(embeddings)

        topic_model = OpenAIChatGenerator(
            model=os.environ.get("TOPIC_MODEL", "gpt-5.4-mini"),
            api_base_url=os.environ.get("TOPIC_MODEL_API_BASE_URL"),
            generation_kwargs={
                "temperature": os.environ.get("TOPIC_MODEL_TEMPERATURE", 0.0)
            },
        )
        full_clusters: list[Cluster] = []
        for k in set(detected_clusters):
            cluster_docs = [
                doc for j, doc in enumerate(documents) if detected_clusters[j] == k
            ]
            topic = (
                topic_model.run(
                    [
                        ChatMessage.from_system(
                            f"""
                            You are a helpful assistant for identifying the main topic of a cluster of document chunks.
                            The theme of the overall document is: {self.theme}.
                            The following document chunks belong to the same cluster and likely share the same topic.
                            Please identify the main topic of these document chunks in one or two words.
                            """
                        ),
                        ChatMessage.from_user(
                            "<sep>".join([doc.content or "" for doc in cluster_docs])
                        ),
                    ]
                )["replies"][0].text
                or "No topic identified"
            )
            full_clusters.append(Cluster(title=topic, documents=cluster_docs))

        return {
            "clusters": full_clusters,
        }
