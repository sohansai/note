class NoteError(Exception):
    """Base exception for all note errors."""


# Backward compatibility alias
JotterError = NoteError


class NoteNotFoundError(NoteError):
    """Raised when a note ID does not exist."""

    def __init__(self, note_id: int):
        self.note_id = note_id
        super().__init__(f"note not found: {note_id}")


class InvalidNoteError(NoteError):
    """Raised when note data is invalid."""
