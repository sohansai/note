from datetime import UTC, datetime
from typing import Any

from note.domain.entities.note import Note
from note.domain.exceptions import InvalidNoteError
from note.domain.repositories import NoteRepository


class NoteService:
    """Application service for coordinating note operations."""

    def __init__(self, repository: NoteRepository):
        self._repo = repository

    def _now(self) -> str:
        return datetime.now(UTC).isoformat()

    def add_note(self, body: str, tag: str = "") -> Note:
        body = body.strip()
        if not body:
            raise InvalidNoteError("Note body cannot be empty.")
        tag = tag.strip().lstrip("#").strip()
        return self._repo.add(body, tag, self._now())

    def get_note(self, note_id: int) -> Note:
        return self._repo.get(note_id)

    def list_notes(self, include_closed: bool = False, tag: str = "") -> list[Note]:
        return self._repo.list_notes(include_closed, tag.strip().lstrip("#").strip())

    def complete_note(self, note_id: int) -> None:
        self._repo.set_done(note_id, True, self._now())

    def complete_notes(self, note_ids: list[int]) -> list[int]:
        unique_ids = list(dict.fromkeys(note_ids))
        now = self._now()
        for nid in unique_ids:
            self._repo.set_done(nid, True, now)
        return unique_ids

    def reopen_note(self, note_id: int) -> None:
        self._repo.set_done(note_id, False, None)

    def reopen_notes(self, note_ids: list[int]) -> list[int]:
        unique_ids = list(dict.fromkeys(note_ids))
        for nid in unique_ids:
            self._repo.set_done(nid, False, None)
        return unique_ids

    def edit_note(self, note_id: int, body: str | None = None, tag: str | None = None) -> None:
        if body is not None:
            body = body.strip()
            if not body:
                raise InvalidNoteError("Note body cannot be empty.")
        if tag is not None:
            tag = tag.strip().lstrip("#").strip()
        self._repo.edit(note_id, body, tag)

    def remove_note(self, note_id: int) -> None:
        self._repo.remove(note_id)

    def remove_notes(self, note_ids: list[int]) -> list[int]:
        unique_ids = list(dict.fromkeys(note_ids))
        for nid in unique_ids:
            self._repo.remove(nid)
        return unique_ids

    def purge_closed_notes(self) -> int:
        return self._repo.purge()

    def search_notes(self, query: str, include_closed: bool = False, tag: str = "") -> list[Note]:
        clean_query = query.strip()
        clean_tag = tag.strip().lstrip("#").strip()
        if not clean_query and not clean_tag:
            return []
        return self._repo.search(clean_query, include_closed, clean_tag)

    def get_tags(self) -> list[dict[str, Any]]:
        return self._repo.get_tags()
