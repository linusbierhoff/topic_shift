from enum import StrEnum

from pydantic import BaseModel


class Status(StrEnum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskModel(BaseModel):
    status: Status


class FullTaskModel(BaseModel):
    task_id: int
    status: Status
