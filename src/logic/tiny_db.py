from logging import Logger

from tinydb import TinyDB, where

from src.models.cluster import Cluster, ClusterModel
from src.models.relation import Relation, RelationModel, RelationshipModel
from src.models.task import FullTaskModel, TaskModel


# Singletone
class DBConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBConnection, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path: str = "db.json"):
        self.logger = Logger("DBConnection")
        self.logger.info(f"Initializing TinyDB at {db_path}")
        self.db = TinyDB(db_path)

        self.tasks = self.db.table("tasks")
        self.clusters = self.db.table("clusters")
        self.relations = self.db.table("relations")

    # Task operations
    def insert_task(self, task_data: TaskModel) -> int:
        self.logger.info(f"Inserting task data: {task_data}")
        return self.tasks.insert(task_data.model_dump())

    def upgrade_task(self, task_id: int, update_data: dict):
        self.logger.info(f"Updating task {task_id} with data: {update_data}")
        self.tasks.update(update_data, doc_ids=[task_id])

    def get_task(self, task_id: int) -> TaskModel | None:
        self.logger.info(f"Retrieving task with ID: {task_id}")
        task_data = self.tasks.get(doc_id=task_id)
        if task_data:
            return TaskModel.model_validate(task_data)
        else:
            self.logger.warning(f"Task with ID {task_id} not found")
            return None

    def delete_task(self, task_id: int):
        self.logger.info(f"Deleting task with ID: {task_id}")
        self.tasks.remove(doc_ids=[task_id])
        self.clusters.remove(where("task_id") == task_id)
        self.relations.remove(where("task_id") == task_id)

    def get_all_tasks(self) -> list[FullTaskModel]:
        self.logger.info("Retrieving all tasks")
        all_tasks = self.tasks.all()
        return [
            FullTaskModel(task_id=task.doc_id, status=task["status"])
            for task in all_tasks
        ]

    # Cluster operations
    def insert_clusters(self, cluster_data: list[Cluster], task_id: int) -> list[int]:
        self.logger.info(f"Inserting cluster data for task ID {task_id}")
        cluster_models = [
            ClusterModel(
                task_id=task_id, title=cluster.title, documents=cluster.documents
            ).model_dump()
            for cluster in cluster_data
        ]
        return self.clusters.insert_multiple(cluster_models)

    def get_clusters_by_task_id(self, task_id: int) -> list[ClusterModel]:
        self.logger.info(f"Retrieving clusters for task ID: {task_id}")
        cluster_data = self.clusters.search(where("task_id") == task_id)
        return [ClusterModel.model_validate(cluster) for cluster in cluster_data]

    # Relation operations
    def insert_relations(self, relations: list[Relation], task_id: int) -> list[int]:
        self.logger.info(f"Inserting relation data for task ID {task_id}")
        relation_models = [
            RelationModel(
                task_id=task_id,
                document_A=relation.document_A,
                document_B=relation.document_B,
                relationship=RelationshipModel(relation.relationship),
            ).model_dump()
            for relation in relations
            if relation.relationship != "none"
        ]

        return self.relations.insert_multiple(relation_models)

    def get_relations_by_task_id(self, task_id: int) -> list[RelationModel]:
        self.logger.info(f"Retrieving relations for task ID: {task_id}")
        relation_data = self.relations.search(where("task_id") == task_id)
        return [RelationModel.model_validate(relation) for relation in relation_data]
