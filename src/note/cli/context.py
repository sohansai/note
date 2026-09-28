from note.application.services.note_service import NoteService


class AppContext:
    """Dependency injection context for CLI commands."""

    def __init__(self) -> None:
        self.note_service: NoteService | None = None
