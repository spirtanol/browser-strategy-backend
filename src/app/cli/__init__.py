import typer

from . import user
from . import market


app = typer.Typer(help="Game CLI")

app.add_typer(user.cli)
app.add_typer(market.cli)