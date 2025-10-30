from enum import StrEnum
from typing import List
from pydantic import BaseModel, Field


class ImportanceEnum(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Topic(BaseModel):
    """Model representing a topic with its content"""

    id: str = Field(description="Identifier basierted auf dem Titel des Themas")
    title: str = Field(description="Titel des Themas")
    importance: ImportanceEnum = Field(description="Wichtigkeit des Themas")
    contents: List[str] = Field(description="Liste der Inhalte für das Thema")
    goal: str = Field(
        description="Das Ziel, das mit dem Thema verbunden ist. Z.B. 'Grundlagen von ... verstehen'"
    )
