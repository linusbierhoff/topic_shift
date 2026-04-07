import os
import shutil
from logging import Logger

from fastapi import BackgroundTasks, FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from src.logic.pdf_processing_pipe import extract_pdf_contents
from src.logic.tiny_db import DBConnection
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


@app.post("/api/task/start", tags=["tasks"])
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    remove_substrings: list[str] = [],
    clusters: int | None = None,
) -> FullTaskModel:
    # Save the uploaded file temporarily
    temp_file_path = f"/tmp/{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    task_id = DBConnection().insert_task(TaskModel(status=Status.IN_PROGRESS))

    def background_function(temp_file_path, remove_substrings, clusters):
        try:
            clusters, relations = extract_pdf_contents(
                temp_file_path, remove_substrings, clusters
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
        background_function, temp_file_path, remove_substrings, clusters
    )

    return FullTaskModel(task_id=task_id, status=Status.IN_PROGRESS)


@app.get("/api/task/{task_id}", tags=["tasks"])
def get_task(task_id: int) -> FullTaskModel | ResultModel | None:
    task = DBConnection().get_task(task_id)
    if not task:
        return None
    if task.status == Status.COMPLETED:
        clusters = DBConnection().get_clusters_by_task_id(task_id)
        relations = DBConnection().get_relations_by_task_id(task_id)
        return ResultModel(task_id=task_id, clusters=clusters, relations=relations)
    return FullTaskModel(task_id=task_id, status=task.status)


@app.delete("/api/task/{task_id}", tags=["tasks"])
def delete_task(task_id: int):
    DBConnection().delete_task(task_id)


@app.get("/api/tasks", tags=["tasks"])
def get_all_tasks() -> list[FullTaskModel]:
    return DBConnection().get_all_tasks()


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
