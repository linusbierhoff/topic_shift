"""
This module provides functionality to extract text contents from PDF files using the DocumentConverter class from the docling library.
It defines a function `extract_pdf_contents` that takes the path to a PDF file as input and returns the extracted text content in markdown format.
"""

from typing import Optional

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    TableFormerMode,
    granite_picture_description,
)
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_haystack.converter import DoclingConverter
from haystack import Pipeline
from haystack.components.embedders import OpenAIDocumentEmbedder
from haystack.components.preprocessors import DocumentCleaner

from src.logic.components.cluster_component import EmbeddingClusteringComponent
from src.logic.components.relation_component import RelationshipClassificationComponent
from src.models.cluster import Cluster
from src.models.relation import Relation


def build_pdf_processing_pipeline(
    remove_substrings: list[str], clusters: Optional[int] = None
) -> Pipeline:
    """
    Build a Haystack pipeline for processing PDF documents.

    Returns:
        A Haystack Pipeline object configured for PDF processing
    """

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_picture_description = False
    pipeline_options.do_picture_classification = False
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.mode = TableFormerMode.FAST  # pyright: ignore[reportAttributeAccessIssue]
    pipeline_options.picture_description_options = granite_picture_description

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    pipe = Pipeline()

    pipe.add_component("converter", DoclingConverter(converter))
    pipe.add_component(
        "cleaner",
        DocumentCleaner(
            remove_substrings=remove_substrings,
            remove_extra_whitespaces=True,
            remove_empty_lines=True,
            strip_whitespaces=True,
        ),
    )
    pipe.add_component("embedder", OpenAIDocumentEmbedder())
    pipe.add_component("clusterer", EmbeddingClusteringComponent(n_clusters=clusters))
    pipe.add_component("relation_classifier", RelationshipClassificationComponent())

    pipe.connect("converter", "cleaner")
    pipe.connect("cleaner", "embedder")
    pipe.connect("embedder", "clusterer")
    pipe.connect("clusterer", "relation_classifier")

    return pipe


def extract_pdf_contents(
    pdf_path: str,
    remove_substrings: list[str] = [],
    clusters: Optional[int] = None,
) -> tuple[list[Cluster], list[Relation]]:
    """
    Extract text contents from a PDF file.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Extracted text content from the PDF file
    """
    pipe = build_pdf_processing_pipeline(
        remove_substrings=remove_substrings,
        clusters=clusters,
    )
    result = pipe.run(
        {"converter": {"paths": [pdf_path]}},
        include_outputs_from={"clusterer", "relation_classifier"},
    )
    return result["clusterer"]["clusters"], result["relation_classifier"]["relations"]
