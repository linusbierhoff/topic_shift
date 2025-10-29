from typing import List
from fastapi import FastAPI, UploadFile
from logic.topic_extraction import TopicsExtractor
from models.topic import Topic
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load environment variables from .env file on server startup."""
    load_dotenv()

    app.state.extractor = TopicsExtractor()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/extract-topics")
async def extract_topics(description: str, file: UploadFile) -> List[Topic]:
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
