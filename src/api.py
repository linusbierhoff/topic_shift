from typing import List
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from logic.topic_extraction import TopicsExtractor
from logic.json_to_amsl import json_to_amsl
from models.topic import Topic
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import Form


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load environment variables from .env file on server startup."""
    load_dotenv()

    app.state.extractor = TopicsExtractor()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/extract-topics")
async def extract_topics(
    description: str = Form(...), file: UploadFile = File(...)
) -> List[Topic]:
    """
    Upload a PDF file and extract topics and contents.

    Args:
        file: PDF file to upload

    Returns:
        TopicExtractionResponse containing extracted topics and contents
    """
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())

    extractor: TopicsExtractor = app.state.extractor

    topics = await extractor.extract_topics(file_location, description=description)

    # Clean up the temporary file
    os.remove(file_location)

    return topics


@app.post("/json-to-amsl")
async def json_to_yaml(file: UploadFile) -> FileResponse:
    """
    Convert JSON data to YAML format.

    Args:
        json_data: JSON data to convert

    Returns:
        YAML formatted string
    """
    json_data = await file.read()
    amsl_data = json_to_amsl(json_data.decode("utf-8"))

    return FileResponse(amsl_data, media_type="application/x-yaml")
