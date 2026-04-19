import json

import click

from src.logic.pdf_processing_pipe import (
    build_pdf_processing_pipeline,
    extract_pdf_contents,
)
from src.logic.tiny_db import DBConnection
from src.models.task import Status, TaskModel
from src.preperation import prepare


@click.group()
def cli():
    """Topic Shift CLI for processing PDF documents and extracting topics and relationships."""
    prepare()


@cli.group(name="task")
def task_group():
    """Commands related to task management."""
    pass


@cli.group(name="debug")
def debug_group():
    """Debug and visualization tools."""
    pass


@task_group.command(name="create")
@click.option(
    "--file",
    type=click.Path(exists=True),
    required=True,
    help="Path to the PDF file",
)
@click.option("--theme", required=True, help="Theme for extraction")
@click.option(
    "--window-size", default=5, help="Window size for relation classification"
)
@click.option("--remove-substrings", help="Comma-separated list of substrings to remove")
@click.option("--clusters", type=int, help="Number of clusters (optional)")
def create_task(file, theme, window_size, remove_substrings, clusters):
    """Start processing a PDF file."""
    substrings = remove_substrings.split(",") if remove_substrings else []

    task_id = DBConnection().insert_task(
        TaskModel(status=Status.IN_PROGRESS, theme=theme)
    )
    click.echo(f"Task started with ID: {task_id}")

    try:
        clusters_res, relations = extract_pdf_contents(
            file, theme, window_size, substrings, clusters
        )
        DBConnection().upgrade_task(task_id, {"status": Status.COMPLETED})
        DBConnection().insert_clusters(clusters_res, task_id)
        DBConnection().insert_relations(relations, task_id)
        click.echo(f"Task {task_id} completed successfully.")
    except Exception as e:
        click.echo(f"Error processing task {task_id}: {e}", err=True)
        DBConnection().upgrade_task(task_id, {"status": Status.FAILED})


@task_group.command(name="list")
def list_tasks():
    """List all tasks."""
    tasks = DBConnection().get_all_tasks()
    if not tasks:
        click.echo("No tasks found.")
        return
    for task in tasks:
        click.echo(
            f"ID: {task.task_id} | Status: {task.status.value} | Theme: {task.theme}"
        )


@task_group.command(name="describe")
@click.argument("task_id", type=int)
def describe_task(task_id):
    """Get details of a specific task."""
    task = DBConnection().get_task(task_id)
    if task:
        click.echo(f"ID: {task_id} | Status: {task.status.value} | Theme: {task.theme}")
    else:
        click.echo(f"Task {task_id} not found.")


@task_group.command(name="delete")
@click.argument("task_id", type=int)
def delete_task(task_id):
    """Delete a task."""
    DBConnection().delete_task(task_id)
    click.echo(f"Task {task_id} deleted.")


@task_group.command(name="result")
@click.argument("task_id", type=int)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output format",
)
def get_result(task_id, output_format):
    """Get the result of a completed task."""
    clusters = DBConnection().get_clusters_by_task_id(task_id)
    relations = DBConnection().get_relations_by_task_id(task_id)

    if not clusters and not relations:
        click.echo(f"No results found for task {task_id}.")
        return

    if output_format == "json":
        result = {
            "task_id": task_id,
            "clusters": [c.model_dump() for c in clusters],
            "relations": [r.model_dump() for r in relations],
        }
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(f"--- Results for Task {task_id} ---")
        click.echo("\nClusters:")
        for c in clusters:
            click.echo(f"- {c.title}: {len(c.documents)} documents")
        click.echo("\nRelations:")
        for r in relations:
            click.echo(
                f"- {r.document_A} <-> {r.document_B}: {r.relationship.value}"
            )


@task_group.command(name="export")
@click.argument("task_id", type=int)
@click.option("--json-schema", help="JSON schema for export")
def export_task(task_id, json_schema):
    """Export results (Not Implemented)."""
    click.echo("Export functionality is not implemented yet.", err=True)


@task_group.command(name="chat")
@click.argument("task_id", type=int)
@click.argument("message")
def chat_task(task_id, message):
    """Chat with the document (Not Implemented)."""
    click.echo("Chat functionality is not implemented yet.", err=True)


@debug_group.command(name="pipe")
@click.option(
    "--output",
    default="output.png",
    help="Output file for the pipeline visualization",
)
def show_pipe(output):
    """Visualize the processing pipeline."""
    pipe = build_pdf_processing_pipeline("placeholder", 0, [], None)
    pipe.draw(path=output)
    click.echo(f"Pipeline visualization saved to {output}")


@cli.command(name="health")
def health():
    """Check health status."""
    click.echo("Status: ok")


if __name__ == "__main__":
    cli()
