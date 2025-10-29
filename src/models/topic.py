from enum import StrEnum
from typing import List
from pydantic import BaseModel


class ImportanceEnum(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Topic(BaseModel):
    """Model representing a topic with its content"""

    title: str
    importance: ImportanceEnum
    contents: List[str]
