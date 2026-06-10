import typer

from . import user


app = typer.Typer(help="Game CLI")

app.add_typer(user.cli)