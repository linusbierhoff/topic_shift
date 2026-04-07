"""
This module contains the preparation logic for the topic shift project.
It includes functions to load environment variables, set up logging, and enable tracing for Haystack components.
"""

import logging
import os

from dotenv import load_dotenv
from haystack import tracing
from haystack.tracing.logging_tracer import LoggingTracer
from huggingface_hub import login


def prepare():
    load_dotenv()

    if os.getenv("HUGGINGFACE_TOKEN") is not None:
        login(token=os.getenv("HUGGINGFACE_TOKEN"))

    logging.basicConfig(
        format="%(levelname)s - %(name)s -  %(message)s",
        level=logging.WARNING,
    )
    logging.getLogger("haystack").setLevel(logging.DEBUG)

    tracing.tracer.is_content_tracing_enabled = True  # pyright: ignore[reportPrivateImportUsage]
    tracing.enable_tracing(  # pyright: ignore[reportPrivateImportUsage]
        LoggingTracer(
            tags_color_strings={
                "haystack.component.input": "\x1b[1;31m",
                "haystack.component.name": "\x1b[1;34m",
            },
        ),
    )
