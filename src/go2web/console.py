"""Terminal output helpers using Rich.

All user-facing output goes through these helpers so formatting stays
consistent across the codebase. Informational and error messages are written
to **stderr**; parsed response content is written to **stdout**.
"""

from rich.console import Console
from rich.panel import Panel

console = Console()
err_console = Console(stderr=True)


def print_result(text: str, title: str = "") -> None:
    """Print *text* inside a cyan-bordered Rich panel on stdout.

    Args:
        text: The content to display (typically a parsed HTTP response body).
        title: Optional panel title shown in the top-left corner. Usually the
            requested URL.
    """
    console.print(Panel(text, border_style="cyan", title=title, title_align="left"))


def print_error(message: str) -> None:
    """Print *message* inside a red panel on stderr.

    Args:
        message: The error description to display.
    """
    err_console.print(Panel(f"[bold red]Error:[/bold red] {message}", border_style="red"))


def print_info(message: str) -> None:
    """Print a dim informational line on stderr.

    Args:
        message: The message to display (e.g. cache hit notice, redirect info).
    """
    err_console.print(f"[dim]{message}[/dim]")


def print_redirect(status: int, reason: str, from_url: str, to_url: str) -> None:
    """Print a redirect notification on stderr.

    Args:
        status: The HTTP redirect status code (e.g. ``301``).
        reason: The status phrase (e.g. ``"Moved Permanently"``).
        from_url: The URL that returned the redirect response.
        to_url: The ``Location`` URL being followed.
    """
    err_console.print(
        f"[yellow]Redirect {status} {reason}[/yellow]  [dim]{from_url}[/dim]\n           [cyan]-> {to_url}[/cyan]"
    )
