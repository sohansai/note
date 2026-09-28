import sys

import typer

from note.domain.exceptions import NoteError
from note.presentation.console import print_action, print_error


def execute(
    ctx: typer.Context,
    note_ids: list[int] = typer.Argument(..., help="One or more note IDs to close"),
):
    """Close one or more notes."""
    service = ctx.obj.note_service

    for nid in note_ids:
        if nid <= 0:
            print_error(f"'{nid}' is not a valid note id")
            sys.exit(1)

    unique_ids = list(dict.fromkeys(note_ids))

    try:
        for nid in unique_ids:
            service.complete_note(nid)
            print_action("closed", nid)
    except NoteError as e:
        print_error(str(e))
        sys.exit(1)
    except Exception as e:
        print_error(f"Failed to close note: {e}")
        sys.exit(1)
