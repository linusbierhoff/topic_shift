from haystack import Document

from src.logic.components.cluster_component import EmbeddingClusteringComponent
from src.preperation import prepare


def test_cluster_component():
    prepare()

    documents: list[Document] = [
        Document(
            content="This is a test document about machine learning.",
            embedding=[0.1, 0.2, 0.3],
        ),
        Document(
            content="This document discusses deep learning techniques.",
            embedding=[0.1, 0.2, 0.25],
        ),
        Document(
            content="This is a completely different topic about cooking recipes.",
            embedding=[0.9, 0.8, 0.7],
        ),
    ]

    result = EmbeddingClusteringComponent("Machine Learning").run(documents)
    assert len(result["clusters"]) == 2
    assert len(result["clusters"][0].documents) == 2
    assert len(result["clusters"][1].documents) == 1
