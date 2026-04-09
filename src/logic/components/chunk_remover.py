import asyncio
import json
import os
import random
from enum import StrEnum
from typing import Optional

from haystack import Document, Pipeline, component, super_component
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage
from haystack.dataclasses.chat_message import (
    _CONTENT_PART_CLASSES_TO_SERIALIZATION_KEYS,
)
from pydantic import BaseModel, Field


@super_component
class ChunkRemover:
    """
    Component which removes document chunks that are not relevant
    """

    def __init__(self, theme: str) -> None:
        self.pipeline = Pipeline()
        self.pipeline.add_component(
            "length_based_chunk_remover", LengthBasedChunkRemover(min_length=20)
        )
        self.pipeline.add_component(
            "type_based_chunk_remover", TypeBasedChunkRemover(theme)
        )

        self.pipeline.connect("length_based_chunk_remover", "type_based_chunk_remover")


@component
class LengthBasedChunkRemover:
    """
    A simple implementation of the ChunkRemover which removes chunks based on their length.
    """

    def __init__(self, min_length: int = 50) -> None:
        self.min_length = min_length

    @component.output_types(documents=list[Document])
    def run(self, documents: list[Document]):
        filtered_docs: list[Document] = [
            doc for doc in documents if len(doc.content or "") >= self.min_length
        ]
        return {"documents": filtered_docs}


class ChunkType(StrEnum):
    RELEVANT_CONTENT = "relevant_content"
    IRRELEVANT_CONTENT = "irrelevant_content"
    SUMMARY = "summary"
    CONCLUSION = "conclusion"
    CONTENT_OVERVIEW = "content_overview"
    FOOTER = "footer"
    HEADER = "header"
    OTHER = "other"


class Response(BaseModel):
    type: ChunkType = Field(
        description="The identified type of the document chunk. It can be 'relevant_content', 'irrelevant_content', 'summary', 'conclusion', 'content_overview', 'footer', 'header' or 'other'."
    )
    reasoning: str = Field(
        description="The reasoning behind the identified type of the document chunk."
    )


@component
class TypeBasedChunkRemover:
    """
    A simple implementation of the ChunkRemover which removes chunks based on their type as identified by a language model.
    """

    def __init__(self, theme: str) -> None:
        self.theme = theme

    @component.output_types(documents=list[Document])
    def run(self, documents: list[Document]):

        topic_model = OpenAIChatGenerator(
            model=os.environ.get("CHUNK_REMOVER_MODEL", "gpt-5.4-mini"),
            api_base_url=os.environ.get("CHUNK_REMOVER_MODEL_API_BASE_URL"),
            generation_kwargs={
                "response_format": Response,
                "temperature": os.environ.get("CHUNK_REMOVER_MODEL_TEMPERATURE", 0.0),
            },
        )

        async def type_request(doc) -> Optional[ChunkType]:
            few_shots: list[tuple[str, str]] = [
                (
                    """
                    Theme: Artificial Intelligence in Healthcare
                    Content: Global Market Analysis Report 2024 | Prepared by: Dr. Jane Smith | Date: October 12, 2024 | CONFIDENTIAL
                    """,
                    "{type: 'header', reasoning: 'The text contains the document title, author name, date and a confidentiality notice, which are typical elements found in the header section of a document.'}",
                ),
                (
                    """
                    Theme: Artificial Intelligence in Healthcare
                    Content: Check out our sponsor's website for the best deals on flights to Hawaii! Click here to subscribe to our weekly newsletter and never miss an update about our CEO's weekend golf tournaments"
                    """,
                    "{type: 'irrelevant_content', reasoning: 'The text promotes a sponsor's website, a newsletter subscription, and CEO's golf tournaments, which are not relevant to the main topic or purpose of the document.'}",
                ),
                (
                    """
                    Theme: Artificial Intelligence in Healthcare
                    Content: © 2024 TechSolutions Inc. All rights reserved. | Page 34 of 120 | For support, visit
                    """,
                    "{type: 'footer', reasoning: 'The text contains a copyright notice, page number, and support information, which are typical elements found in the footer section of a document.'}",
                ),
                (
                    """
                    Theme: Human Computer Interaction
                    Content: Let's define cognitive dissonance. It refers to the mental discomfort experienced by someone who holds two or more contradictory beliefs, ideas, or values. This often happens when a person performs an action that contradicts their personal beliefs.
                    """,
                    "{type: 'relevant_content', reasoning: 'The text provides a definition and explanation of the concept of cognitive dissonance, which is relevant to the main topic or purpose of the document.'}",
                ),
                (
                    """
                    Theme: Mathematics Quadratic Equations
                    Content: For example, if we apply the quadratic formula here, we substitute a=1, b=-5, and c=6. This gives us x equals 5 plus or minus the square root of 25 minus 24, all over 2. Ultimately, we find our two solutions are x=3 and x=2.
                    """,
                    "{type: 'relevant_content', reasoning: 'The text provides a step-by-step explanation of how to apply the quadratic formula to solve a mathematical problem, which is relevant to the main topic or purpose of the document.'}",
                ),
                (
                    """
                    Theme: Environmental Science Climate Change
                    Content: The document is structured as follows: Introduction, Methodology, Results, Discussion, Conclusion, and References. Each section provides a comprehensive overview of the research process and findings related to climate change, ensuring a clear and logical flow of information for the reader.
                    """,
                    "{type: 'content_overview', reasoning: 'The text provides an overview of the structure of the document, outlining the main sections and their purpose, which is relevant to the main topic or purpose of the document.'}",
                ),
                (
                    """
                    Theme: Business Strategy Market Analysis
                    Content: In conclusion, our market analysis indicates that there is a significant opportunity for growth in the renewable energy sector. By investing in sustainable technologies and focusing on eco-friendly products, we can position ourselves as a leader in the industry and capitalize on the increasing demand for green solutions.
                    """,
                    "{type: 'conclusion', reasoning: 'The text provides a concluding statement that summarizes the findings of a market analysis and offers strategic recommendations, which is relevant to the main topic or purpose of the document.'}",
                ),
            ]

            ## shuffle few shots
            random.shuffle(few_shots)

            messages = []
            for example_input, example_output in few_shots:
                messages.append(ChatMessage.from_user(example_input))
                messages.append(ChatMessage.from_assistant(example_output))

            chunk_type = (
                await topic_model.run_async(
                    [
                        ChatMessage.from_system(
                            """
                                You are an assistant for analyzing the type of a document chunk with respect to a specific theme of the whole document.
                                Your task is to identify the type of the document chunk and classify it into one of the following categories: 'relevant_content', 'irrelevant_content', 'design_element', 'footer', 'header' or 'other'.

                                'relevant_content' indicates that the document chunk contains information that is relevant to the main topic or purpose of the document. These are the main body of the documents and the only type of chunks that should be kept for the further processing.

                                'irrelevant_content' indicates that the document chunk contains information that is not relevant to the main topic or purpose of the document.

                                'summary' indicates that the document chunk provides a brief summary of the main points or findings of the document.

                                'conclusion' indicates that the document chunk provides a concluding statement or final thoughts on the topic of the document.

                                'content_overview' indicates that the document chunk provides an overview of the structure or organization of the document, such as an outline of the sections or a description of the main topics covered.

                                'footer' indicates that the document chunk is part of the footer section of the document, which typically contains information such as page numbers, copyright notices, or contact information.

                                'header' indicates that the document chunk is part of the header section of the document, which typically contains information such as the document title, author name, or date.

                                'other' indicates that the document chunk does not fit into any of the above categories and may require further analysis to determine its relevance or type.
                                """
                        ),
                        *messages,
                        # Actual query
                        ChatMessage.from_user(
                            f"""
                            Theme: {self.theme}
                            Content: {doc.content}
                            """
                        ),
                    ]
                )
            )["replies"][0].text or "{}"
            return json.loads(chunk_type).get("type", ChunkType.OTHER)

        requests = [type_request(doc) for doc in documents]
        relevant_docs: list[Document] = []

        async def process_requests(relevant_docs: list[Document]):
            types = await asyncio.gather(*requests)
            relevant_docs.extend(
                [
                    doc
                    for doc, chunk_type in zip(documents, types)
                    if chunk_type == ChunkType.RELEVANT_CONTENT
                ]
            )

        asyncio.run(process_requests(relevant_docs))

        return {
            "documents": relevant_docs,
        }
