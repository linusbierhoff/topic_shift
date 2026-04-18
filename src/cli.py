import click

from src.logic.pdf_processing_pipe import build_pdf_processing_pipeline
from src.preperation import prepare


@click.command()
@click.option(
    "--output", default="output.png", help="Output file for the pipeline visualization"
)
def show_processing_pipe(output):
    prepare()
    pipe = build_pdf_processing_pipeline("placeholder", [], None)
    pipe.draw(path=output)


if __name__ == "__main__":
    show_processing_pipe()
