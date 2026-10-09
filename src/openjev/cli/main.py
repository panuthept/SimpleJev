import typer
from openjev.cli.serve_commands import serve_commands


entry_point = typer.Typer()
entry_point.add_typer(serve_commands)