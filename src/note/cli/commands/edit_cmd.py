import sys

import typer

from note.domain.exceptions import NoteError
from note.presentation.console import print_action, print_error


def execute(
    ctx: typer.Context,
    note_id: int = typer.Argument(..., help="ID of the note to edit"),
    text: list[str] = typer.Argument(None, help="New body text for the note"),
    body: str | None = typer.Option(None, "--body", "-b", help="New body text for the note"),
    tag: str | None = typer.Option(None, "--tag", "-tag", "-t", help="New tag for the note"),
):
    """Edit an existing note."""
    if note_id <= 0:
        print_error(f"'{note_id}' is not a valid note id")
        sys.exit(1)

    service = ctx.obj.note_service

    new_body = body
    if new_body is None and text:
        new_body = " ".join(text).strip()

    if new_body is None and tag is None:
        print_error("nothing to update: provide new text or a tag")
        sys.exit(1)

    try:
        service.edit_note(note_id, new_body, tag)
        print_action("edited", note_id)
    except NoteError as e:
        print_error(str(e))
        sys.exit(1)
    except Exception as e:
        print_error(f"Failed to edit note: {e}")
        sys.exit(1)
