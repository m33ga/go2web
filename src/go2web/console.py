from rich.console import Console
from rich.panel import Panel

console = Console()
err_console = Console(stderr=True)


def print_result(text: str, title: str = "") -> None:
    console.print(Panel(text, border_style="cyan", title=title, title_align="left"))


def print_error(message: str) -> None:
    """Print message inside a red panel on stderr."""
    err_console.print(Panel(f"[bold red]Error:[/bold red] {message}", border_style="red"))


def print_info(message: str) -> None:
    """Print a dim info line on stderr."""
    err_console.print(f"[dim]{message}[/dim]")


def print_redirect(status: int, reason: str, from_url: str, to_url: str) -> None:
    """Print a redirect ack on stderr."""
    err_console.print(
        f"[yellow]Redirect {status} {reason}[/yellow]  [dim]{from_url}[/dim]\n           [cyan]-> {to_url}[/cyan]"
    )
