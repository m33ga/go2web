import typer
from typing import List

app = typer.Typer(
    name="go2web",
    help="Make HTTP requests and search the web from your terminal.",
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
    epilog="Made with :heart: at F[orange1]A[/orange1]F"
)

@app.command(no_args_is_help=True)
def fetch(url: str):
    """Make an HTTP request to the URL."""
    pass


@app.command(no_args_is_help=True)
def search(query: List[str]):
    """Search the web."""
    pass
