import sys

# Force UTF-8 encoding on Windows to prevent charmap crashes for all entrypoints,
# including the installed console-script entrypoint rather than only `python -m note`.
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import typer

from note import __version__
from note.application.services.note_service import NoteService
from note.cli.commands import (
    add_cmd,
    done_cmd,
    edit_cmd,
    list_cmd,
    open_cmd,
    purge_cmd,
    remove_cmd,
    search_cmd,
    show_cmd,
    tags_cmd,
)
from note.cli.context import AppContext
from note.configuration.settings import get_db_path
from note.infrastructure.database.connection import get_connection
from note.infrastructure.database.migrations import run_migrations
from note.infrastructure.repositories.sqlite_note_repository import SQLiteNoteRepository
from note.presentation.console import print_error

app = typer.Typer(
    help=("note: fast notes and todos that live in your terminal, saved in a single SQLite file."),
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
)


def _setup_context(ctx: typer.Context) -> None:
    """Initialize dependencies and inject into Typer context."""
    if ctx.obj is None:
        ctx.obj = AppContext()

    try:
        db_path = get_db_path()
        conn = get_connection(db_path)
        run_migrations(conn)
        repo = SQLiteNoteRepository(conn)
        ctx.obj.note_service = NoteService(repo)
    except Exception as e:
        print_error(f"Failed to initialize database: {e}")
        sys.exit(1)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"note {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    version: bool | None = typer.Option(
        None,
        "--version",
        help="Print the version and exit",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """
    note: fast notes and todos that live in your terminal, saved in a single SQLite file.

    No background services, no servers, and no config files.
    One command and one local database file you can copy, move, back up, or delete anytime.
    """
    _setup_context(ctx)


@app.command(name="version", help="Print the version")
def cmd_version() -> None:
    typer.echo(f"note {__version__}")


# Register Commands
app.command(name="add", help="Add a note [-tag NAME]")(add_cmd.execute)
app.command(name="ls", help="List open notes (-a includes closed ones, -tag filters)")(
    list_cmd.execute
)
app.command(name="list", help="Alias for ls")(list_cmd.execute)
app.command(name="done", help="Close a note by ID")(done_cmd.execute)
app.command(name="open", help="Reopen a closed note by ID")(open_cmd.execute)
app.command(name="undone", hidden=True)(open_cmd.execute)
app.command(name="rm", help="Delete a note by ID")(remove_cmd.execute)
app.command(name="remove", help="Alias for rm")(remove_cmd.execute)
app.command(name="purge", help="Delete every closed note")(purge_cmd.execute)
app.command(name="tags", help="List all tags and note counts")(tags_cmd.execute)
app.command(name="tag", hidden=True)(tags_cmd.execute)
app.command(name="show", help="View details of a specific note")(show_cmd.execute)
app.command(name="edit", help="Edit an existing note")(edit_cmd.execute)
app.command(name="search", help="Search notes by content")(search_cmd.execute)
