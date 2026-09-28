import sqlite3
from datetime import datetime
from typing import Any

from note.domain.entities.note import Note
from note.domain.exceptions import NoteNotFoundError
from note.domain.repositories import NoteRepository


class SQLiteNoteRepository(NoteRepository):
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def _row_to_note(self, row: sqlite3.Row) -> Note:
        added_at = datetime.fromisoformat(row["added_at"])
        closed_at = datetime.fromisoformat(row["closed_at"]) if row["closed_at"] else None
        return Note(
            id=row["id"],
            body=row["body"],
            tag=row["tag"],
            done=bool(row["done"]),
            added_at=added_at,
            closed_at=closed_at,
        )

    def add(self, body: str, tag: str, added_at: str) -> Note:
        cursor = self._conn.cursor()
        cursor.execute(
            "INSERT INTO notes (body, tag, done, added_at) VALUES (?, ?, 0, ?)",
            (body, tag, added_at),
        )
        note_id = cursor.lastrowid
        if note_id is None:
            raise RuntimeError("Failed to retrieve inserted note ID")
        return self.get(note_id)

    def get(self, note_id: int) -> Note:
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT id, body, tag, done, added_at, closed_at FROM notes WHERE id = ?", (note_id,)
        )
        row = cursor.fetchone()
        if not row:
            raise NoteNotFoundError(note_id)
        return self._row_to_note(row)

    def list_notes(self, include_closed: bool = False, tag: str = "") -> list[Note]:
        query = "SELECT id, body, tag, done, added_at, closed_at FROM notes"
        where_clauses = []
        args: list[Any] = []

        if not include_closed:
            where_clauses.append("done = 0")

        if tag:
            where_clauses.append("tag = ?")
            args.append(tag)

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += " ORDER BY done, added_at, id"

        cursor = self._conn.cursor()
        cursor.execute(query, args)
        return [self._row_to_note(row) for row in cursor.fetchall()]

    def set_done(self, note_id: int, done: bool, closed_at: str | None) -> None:
        cursor = self._conn.cursor()
        cursor.execute(
            "UPDATE notes SET done = ?, closed_at = ? WHERE id = ?", (int(done), closed_at, note_id)
        )
        if cursor.rowcount == 0:
            raise NoteNotFoundError(note_id)

    def edit(self, note_id: int, body: str | None = None, tag: str | None = None) -> None:
        cursor = self._conn.cursor()
        if body is not None and tag is not None:
            cursor.execute("UPDATE notes SET body = ?, tag = ? WHERE id = ?", (body, tag, note_id))
        elif body is not None:
            cursor.execute("UPDATE notes SET body = ? WHERE id = ?", (body, note_id))
        elif tag is not None:
            cursor.execute("UPDATE notes SET tag = ? WHERE id = ?", (tag, note_id))
        else:
            # Nothing to update, verify note exists
            self.get(note_id)
            return

        if cursor.rowcount == 0:
            raise NoteNotFoundError(note_id)

    def remove(self, note_id: int) -> None:
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        if cursor.rowcount == 0:
            raise NoteNotFoundError(note_id)

    def purge(self) -> int:
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM notes WHERE done = 1")
        return cursor.rowcount

    def search(self, query: str, include_closed: bool = False, tag: str = "") -> list[Note]:
        # Escape wildcard characters for LIKE
        escaped_query = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        db_query = (
            "SELECT id, body, tag, done, added_at, closed_at FROM notes "
            "WHERE body LIKE ? ESCAPE '\\'"
        )
        args: list[Any] = [f"%{escaped_query}%"]

        if not include_closed:
            db_query += " AND done = 0"

        if tag:
            db_query += " AND tag = ?"
            args.append(tag)

        db_query += " ORDER BY done, added_at, id"

        cursor = self._conn.cursor()
        cursor.execute(db_query, args)
        return [self._row_to_note(row) for row in cursor.fetchall()]

    def get_tags(self) -> list[dict[str, Any]]:
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT
                tag,
                SUM(CASE WHEN done = 0 THEN 1 ELSE 0 END) AS open_count,
                SUM(CASE WHEN done = 1 THEN 1 ELSE 0 END) AS closed_count,
                COUNT(*) AS total_count
            FROM notes
            WHERE tag != ''
            GROUP BY tag
            ORDER BY tag ASC
            """
        )
        rows = cursor.fetchall()
        return [
            {
                "tag": row["tag"],
                "open": int(row["open_count"]),
                "closed": int(row["closed_count"]),
                "total": int(row["total_count"]),
            }
            for row in rows
        ]
