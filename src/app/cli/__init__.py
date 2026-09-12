import typer

from . import player
from . import market


app = typer.Typer(help="Game CLI")

app.add_typer(player.cli)
app.add_typer(market.cli)