# Goal: Get list of topics with list of contents. Handle massive PDFs.
# Idea: Chunking PDF into smaller parts, extract topics from each chunk, then aggregate.

import operator
from typing import Annotated, List, Optional, Optional

from pydantic import BaseModel
from logic.pdf_content_loading import extract_pdf_contents
from models.topic import Topic
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.types import Command
from langgraph.graph import StateGraph, START
from loguru import logger


class State(BaseModel):
    """State to hold intermediate data during topic extraction"""

    description: Annotated[
        Optional[str],
        "Description of the context. E.g. the main topics covered in the PDF",
    ] = None

    page_contents: List[str]
    current_page: int = 0
    topics: List[Topic] = []


class Topics(BaseModel):
    """Model to hold extracted topics"""

    topics: List[Topic]


class TopicsExtractor:
    def __init__(self):
        self.model = ChatOpenAI(name="gpt-5-mini").with_structured_output(Topics, strict=True)
        graph = StateGraph(State)

        graph.add_node(
            "extract",
            self.extract,
        )
        graph.add_edge(START, "extract")
        self.graph = graph.compile()
        logger.info("Initialized TopicsExtractor")

    async def extract(self, state: State):
        """
        Extract topics from the contents of the PDF.

        Args:
            state: State object containing page contents

        Returns:
            Updated State object with extracted topics
        """
        description = state.description or "No description provided"
        current_topics = ", ".join([topic.title for topic in state.topics])
        contents_len = sum([len(content.contents) for content in state.topics])
        logger.info("Current topics: " + current_topics)
        if state.current_page >= len(state.page_contents):
            return Command(goto="end", update=state)

        current_content = state.page_contents[state.current_page]
        state.current_page += 1

        messages = [
            SystemMessage(
                f"""
                ### ROLE ###
                You are an expert AI assistant specializing in PDF content analysis and topic extraction. You will analyze page content and return a structured list of topics.

                ### GOAL ###
                Your primary goal is to extract **only significant, substantive topics** and their corresponding summary/content from the provided page text. You must differentiate between actual content and document artifacts and assign an importance level to each topic.
                You want to keep the number of topics low and try to summarize related content under existing topics whenever possible.
                Be aware that each call only covers one Page of the PDF at a time. The aggregation of all topics across all pages should be small enough to fit into a single call later on.
                    
                ### CONTEXT & INPUTS ###
                * **PDF Description:** {description}
                * **Current Topics (for reuse):** {current_topics}
                * **Page Content to Analyze:** [The raw text from the page will be provided after this prompt]

                ### OUTPUT FORMAT ###
                You MUST respond with a JSON-compatible list of dictionaries. Each dictionary must have three keys: 'id', 'topic', 'content', 'goal' and 'importance'. Do not provide any other text, preamble, or explanation.
                Be aware that each call only covers one Page of the PDF at a time. The aggregation of all topics across all pages should be small enough to fit into a single call later on.
                You already have {contents_len} contents extracted so far.
                
                **Example Format:**
                [
                    {{
                        "id": : "snake_case_title_1",
                        "topic": "Topic Title 1",
                        "contents": [
                            "Detail about Key Point A",
                            "Detail about Key Point B"
                        ],
                        "goal": "Understand basics of ...",
                        "importance": "high"
                    }},
                    {{
                        "id": : "snake_case_title_2",
                        "topic": "Topic Title 2",
                        "contents": [
                            "Detail about another point less central to the main themes",
                            "Additional context or information related to Topic Title 2"
                        ],
                        "goal": "Understand basics of ...",
                        "importance": "low"
                    }},
                    {{
                        "id": "snake_case_title_3",
                        "topic": "Topic Title 3",
                        "contents": [
                            "Detail about another point less but more central to the main themes",
                            "Additional context or information related to Topic Title 3"
                        ],
                        "goal": "Understand basics of ...",
                        "importance": "medium"
                    }}
                ]

                ### CORE INSTRUCTIONS ###
                1.  **Focus on Substance:** Identify the main themes, sections, or ideas on the page. A topic should represent a distinct, meaningful concept, argument, or data set.
                2.  **Filter Aggressively:** You **MUST** ignore and filter out all non-substantive elements. Do **NOT** create topics for:
                    * Page numbers (e.g., "Page 5", "- 5 -")
                    * Document headers and footers (e.g., running titles, confidentiality notices)
                    * Table of Contents entries (unless the *entire* page is the ToC itself)
                    * Reference lists / Bibliographies (unless the specific topic is "References")
                    * Formatting artifacts (e.g., random characters, excessive line breaks)
                    * Isolated tables or images without surrounding explanatory text.
                3.  **Topic Management:**
                    * **Reuse First:** Before creating a new topic, check if the content logically fits under one of the `Current Topics`: {current_topics}.
                    * **Create New:** If the content is new and significant, create a concise, descriptive new topic title. Try to generate 1 topic per page maximum.
                4.  **Content Summarization:** 
                    * For each topic, summarize the relevant content from the page into clear, concise bullet points or sentences. 
                    * Each content item should be a brief but informative snippet that captures the essence of the information related to the topic.
                    * Try to summarize concepts into one bullet point whenever possible.
                    * Try to keep the number of content items per topic low (avg 3).
                5.  **Handle Empty/Noisy Pages:** 
                    * If the page content, after filtering out all the elements from rule #2, contains no meaningful information, you **MUST** return an empty list `[]`.
                    * Do not include pages like "Lernziele", "Contents", "Index", "Agenda", "Referenzen", "References" or similar non-content pages.
                6.  **Assign Importance:** For each topic you extract, assign an `importance` rating based on this rubric:
                    * **"High":** For primary topics. This includes major section headings (e.g., "Chapter 2", "Introduction," "Methodology") or content that is central to the `PDF Description`.
                    * **"Medium":** For standard sub-topics or distinct, complete arguments that are part of a larger section.
                    * **"Low":** For minor points, sidebars, detailed examples, or tangential information.
                """
            ),
            HumanMessage(content=current_content),
        ]

        response = await self.model.ainvoke(messages)
        logger.info(f"Received response: {response}")
        topics = Topics.model_validate(response)

        for topic in topics.topics:
            # Check if topic already exists
            existing_topic = next(
                (t for t in state.topics if t.title == topic.title), None
            )

            if existing_topic:
                existing_topic.contents.extend(topic.contents)
            else:
                state.topics.append(topic)

        return Command(goto="extract", update=state)

    async def extract_topics(self, pdf_path: str, description: str) -> List[Topic]:
        page_contents = extract_pdf_contents(pdf_path)

        # Merge pages with very little content
        merged_pages = []
        buffer = ""
        for content in page_contents:
            if len(content.strip()) < 1000 and merged_pages:
                buffer += "\n" + content
            else:
                if buffer:
                    merged_pages[-1] += "\n" + buffer
                    buffer = ""
                merged_pages.append(content)

        logger.info(
            f"Extracted {len(page_contents)} pages from PDF. Merged to {len(merged_pages)} pages."
        )
        state = State(page_contents=merged_pages, description=description)
        state = await self.graph.ainvoke(
            state, {"recursion_limit": len(merged_pages) + 2}
        )

        formatted_state = State.model_validate(state)
        return formatted_state.topics
