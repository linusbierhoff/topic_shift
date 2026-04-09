from dataclasses import dataclass
from enum import StrEnum

from pydantic import BaseModel


class Relationship(StrEnum):
    EXAMPLE = "example"
    SPECIFICATION = "specification"
    NONE = "none"


class RelationshipModel(StrEnum):
    EXAMPLE = "example"
    SPECIFICATION = "specification"
    ALTERNATIVE_TO = "alternative_to"


@dataclass
class Relation:
    document_A: str
    document_B: str
    relationship: Relationship

    def to_dict(self):
        return {
            "document_A": self.document_A,
            "document_B": self.document_B,
            "relationship": self.relationship.value,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Relation":
        return cls(
            document_A=data["document_A"],
            document_B=data["document_B"],
            relationship=Relationship(data["relationship"]),
        )


class RelationModel(BaseModel):
    task_id: int
    document_A: str
    document_B: str
    relationship: RelationshipModel
