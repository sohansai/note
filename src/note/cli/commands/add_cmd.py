import sys

import typer

from note.domain.exceptions import NoteError
from note.presentation.console import print_action, print_error


def execute(
    ctx: typer.Context,
    text: list[str] = typer.Argument(None, help="The body of the note"),
    tag: str = typer.Option("", "--tag", "-tag", "-t", help="Tag to organize notes"),
):
    """Add a new note."""
    service = ctx.obj.note_service
    body = " ".join(text).strip() if text else ""

    # Allow reading body from stdin if piped and no arguments were given
    if not body and not sys.stdin.isatty():
        body = sys.stdin.read().strip()

    if not body:
        print_error('nothing to add, try: note add "drain the queue before deploy"')
        sys.exit(1)

    try:
        note = service.add_note(body, tag)
        print_action("added", note.id)
    except NoteError as e:
        print_error(str(e))
        sys.exit(1)
    except Exception as e:
        print_error(f"Failed to add note: {e}")
        sys.exit(1)
