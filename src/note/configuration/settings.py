import os
from pathlib import Path

from platformdirs import user_data_dir


def get_db_path() -> Path:
    """
    Get the path to the note SQLite database.
    Honours NOTE_DB, NOTES_DB, TICKPOST_DB, and JOTTER_DB,
    then defaults to platform-specific user data directory (e.g. ~/.local/share/note/note.db or AppData).
    """
    for env_var in ("NOTE_DB", "NOTES_DB", "TICKPOST_DB", "JOTTER_DB"):
        env_path = os.getenv(env_var)
        if env_path:
            return Path(env_path)

    xdg_data = os.getenv("XDG_DATA_HOME")
    if xdg_data:
        return Path(xdg_data) / "note" / "note.db"

    new_dir = Path(user_data_dir("note"))
    return new_dir / "note.db"
