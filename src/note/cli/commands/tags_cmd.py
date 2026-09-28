import sys

import typer

from note.presentation.console import console, print_empty_state, print_error
from note.presentation.formatters.json import format_tags_json
from note.presentation.formatters.table import build_tags_table


def execute(
    ctx: typer.Context,
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List all tags and note counts."""
    service = ctx.obj.note_service

    try:
        tags = service.get_tags()
        if as_json:
            print(format_tags_json(tags))
        else:
            if not tags:
                print_empty_state("no tags found.")
            else:
                console.print(build_tags_table(tags))
    except Exception as e:
        print_error(f"Failed to list tags: {e}")
        sys.exit(1)
