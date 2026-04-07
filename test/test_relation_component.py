from haystack import Document

from src.logic.components.relation_component import RelationshipClassificationComponent
from src.models.cluster import Cluster
from src.preperation import prepare


def test_relation_component():
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

    clusters = [
        Cluster(title="Machine Learning", documents=[documents[0], documents[1]]),
        Cluster(title="Cooking", documents=[documents[2]]),
    ]

    result = RelationshipClassificationComponent().run(clusters)
    assert len(result["relations"]) == 1
    assert result["relations"][0].document_A in [documents[0].id, documents[1].id]
    assert result["relations"][0].document_B in [documents[0].id, documents[1].id]
    assert result["relations"][0].document_A != result["relations"][0].document_B
    assert result["relations"][0].relationship is not None
