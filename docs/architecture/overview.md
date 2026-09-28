# Note Architecture Overview

`note` follows a clean, layered architecture to maintain clear boundaries between the terminal user interface, business logic, and SQLite infrastructure details. 

## Dependency Flow

Dependencies flow strictly inward:

```
CLI / Presentation (Typer, Rich)
       ↓
  Application (NoteService)
       ↓
    Domain (Note, Exceptions, Repository Protocol)
       ↑
 Infrastructure (SQLiteNoteRepository, SQLite Connection)
```

## Layers

### Domain
The `domain` layer holds the core entities (`Note`), domain-specific exceptions (`NoteError`, `NoteNotFoundError`), and interface definitions (`NoteRepository` Protocol). It has zero external dependencies and no knowledge of how notes are stored or displayed.

### Application
The `application` layer coordinates the use-cases of `note`. `NoteService` validates inputs, generates ISO-8601 UTC timestamps, and orchestrates calls to the repository.

### Infrastructure
The `infrastructure` layer manages operating-system and persistence concerns. 
- `database/`: Manages SQLite connections with WAL mode, busy timeouts, foreign keys, schemas, and migrations via `user_version`.
- `repositories/`: Implements the `NoteRepository` protocol using SQLite queries.

### Presentation & CLI
- `presentation/`: Formatting logic. JSON output, Rich terminal tables, and age formatting live here.
- `cli/`: Uses Typer to parse arguments, setup dependency injection via `AppContext`, and route execution to services.

### Configuration
Centralizes database path resolution honoring `NOTE_DB`, `NOTES_DB`, `TICKPOST_DB`, `JOTTER_DB`, `XDG_DATA_HOME`, and platform-specific data directories.
