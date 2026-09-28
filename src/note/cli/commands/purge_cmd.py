import sys

import typer

from note.presentation.console import console, print_error


def execute(
    ctx: typer.Context,
):
    """Delete every closed note."""
    service = ctx.obj.note_service

    try:
        count = service.purge_closed_notes()
        console.print(f"removed {count} closed note(s)")
    except Exception as e:
        print_error(f"Failed to purge notes: {e}")
        sys.exit(1)
