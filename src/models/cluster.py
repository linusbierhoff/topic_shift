from dataclasses import dataclass

from haystack import Document
from pydantic import BaseModel


@dataclass
class Cluster:
    title: str
    documents: list[Document]

    def to_dict(self):
        return {
            "title": self.title,
            "documents": [doc.to_dict() for doc in self.documents],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Cluster":
        return cls(
            title=data["title"],
            documents=[Document.from_dict(doc) for doc in data["documents"]],
        )


class ClusterModel(BaseModel):
    task_id: int
    title: str
    documents: list[Document]
