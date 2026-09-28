from rich.console import Console

console = Console()
err_console = Console(stderr=True)


def print_success(message: str) -> None:
    console.print(f"[green]✓[/green] {message}")


def print_action(verb: str, note_id: int) -> None:
    """Print standard action message matching tickpost style: e.g. added #1, closed #1."""
    console.print(f"{verb} #{note_id}")


def print_error(message: str) -> None:
    err_console.print(f"note: [red]error:[/red] {message}")


def print_empty_state(message: str = "nothing open. enjoy it while it lasts.") -> None:
    console.print(message, style="italic dim")
