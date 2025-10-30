from enum import StrEnum
from typing import List
from pydantic import BaseModel, Field


class ImportanceEnum(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Topic(BaseModel):
    """Model representing a topic with its content"""

    id: str = Field(description="textual identifier of the topic based on its title")
    title: str = Field(description="title of the topic")
    importance: ImportanceEnum = Field(description="importance level of the topic")
    contents: List[str] = Field(description="list of content items for the topic")
    goal: str = Field(
        description="The goal associated with the topic. E.g. 'Understand basics of ...'"
    )
