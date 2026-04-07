from pydantic import BaseModel

from src.models.cluster import ClusterModel
from src.models.relation import RelationModel


class ResultModel(BaseModel):
    task_id: int
    relations: list[RelationModel]
    clusters: list[ClusterModel]
