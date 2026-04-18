import os
import shutil
from logging import Logger

from fastapi import BackgroundTasks, FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from src.logic.pdf_processing_pipe import extract_pdf_contents
from src.logic.tiny_db import DBConnection
from src.models.cluster import ClusterModel
from src.models.relation import RelationModel
from src.models.result import ResultModel
from src.models.task import FullTaskModel, Status, TaskModel
from src.preperation import prepare

prepare()

logger = Logger("API")  # Initialize logger for the API module
app = FastAPI()


app.title = "Topic Shift API"
app.description = (
    "API for processing PDF documents and extracting topics and relationships."
)
app.version = "1.0.0"


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#### Task Endpoints ####


@app.post("/api/task/start", tags=["tasks"])
async def upload_pdf(
    background_tasks: BackgroundTasks,
    theme: str,
    file: UploadFile,
    remove_substrings: list[str] = [],
    clusters: int | None = None,
    window_size: int | None = None,
) -> FullTaskModel:
    # Save the uploaded file temporarily
    temp_file_path = f"/tmp/{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    task_id = DBConnection().insert_task(
        TaskModel(status=Status.IN_PROGRESS, theme=theme)
    )

    def background_function(
        temp_file_path, theme, remove_substrings, clusters, window_size
    ):
        try:
            clusters, relations = extract_pdf_contents(
                temp_file_path, theme, remove_substrings, clusters, window_size
            )
            DBConnection().upgrade_task(task_id, {"status": Status.COMPLETED})
            DBConnection().insert_clusters(clusters, task_id)
            DBConnection().insert_relations(relations, task_id)

        except Exception as e:
            logger.error(f"Error processing task {task_id}: {e}")
            DBConnection().upgrade_task(task_id, {"status": Status.FAILED})
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    background_tasks.add_task(
        background_function,
        temp_file_path,
        theme,
        remove_substrings,
        clusters,
        window_size,
    )

    return FullTaskModel(task_id=task_id, status=Status.IN_PROGRESS, theme=theme)


@app.get("/api/tasks", tags=["tasks"])
def get_all_tasks() -> list[FullTaskModel]:
    return DBConnection().get_all_tasks()


@app.get("/api/task/{task_id}", tags=["tasks"])
def get_task(task_id: int) -> FullTaskModel | None:
    task_model = DBConnection().get_task(task_id)
    if task_model is not None:
        return FullTaskModel(
            task_id=task_id, status=task_model.status, theme=task_model.theme
        )
    return None


@app.delete("/api/task/{task_id}", tags=["tasks"])
def delete_task(task_id: int):
    DBConnection().delete_task(task_id)


#### Result Endpoints ####


@app.get("/api/task/{task_id}/result", tags=["result"])
def get_result(task_id: int) -> ResultModel | None:
    clusters = DBConnection().get_clusters_by_task_id(task_id)
    relations = DBConnection().get_relations_by_task_id(task_id)
    if clusters is not None and relations is not None:
        return ResultModel(task_id=task_id, clusters=clusters, relations=relations)

    return None


@app.get("/api/task/{task_id}/clusters", tags=["result"])
def get_clusters(task_id: int) -> list[ClusterModel] | None:
    return DBConnection().get_clusters_by_task_id(task_id)


@app.get("/api/task/{task_id}/relations", tags=["result"])
def get_relations(task_id: int) -> list[RelationModel] | None:
    return DBConnection().get_relations_by_task_id(task_id)


#### Export Endpoints ####


@app.get("/api/task/{task_id}/export", tags=["export"])
def get_exported_topics(task_id: int, json_schema: dict) -> dict | None:
    raise NotImplementedError("Export functionality is not implemented yet.")


#### Chat Endpoints ####


@app.post("/api/task/{task_id}/chat", tags=["chat"])
def chat_with_documentk(task_id: int, message: str) -> str:
    raise NotImplementedError("Chat functionality is not implemented yet.")


#### Utils Endpoint ####


@app.get("/api/health", tags=["utils"])
def health_check():
    return {"status": "ok"}
