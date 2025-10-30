from typing import List
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from logic.topic_extraction import TopicsExtractor
from models.topic import Topic
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import yaml
from fastapi import Form


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load environment variables from .env file on server startup."""
    load_dotenv()

    app.state.extractor = TopicsExtractor()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/extract-topics")
async def extract_topics(description: str = Form(...), file: UploadFile = File(...)) -> List[Topic]:
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
    json_content = await file.read()
    json_dict = yaml.safe_load(json_content)
    # Drop importance scores if present
    for item in json_dict:
        item.pop("importance", None)
    yaml_content = yaml.safe_dump(json_dict)
    temp_file = "temp_output.yaml"
    with open(temp_file, "w") as f:
        f.write(yaml_content)

    return FileResponse(temp_file, media_type="application/x-yaml")
