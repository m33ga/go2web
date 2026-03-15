import typer

app = typer.Typer(
    name="go2web",
    help="Make HTTP requests and search the web from your terminal.",
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
    epilog="Made with [orange1]:heart:[/orange1] at FAF",
)


@app.command(no_args_is_help=True)
def fetch(url: str):
    """Make an HTTP request to the URL."""


@app.command(no_args_is_help=True)
def search(query: list[str]):
    """Search the web."""
