import click
from importlib import import_module
from pathlib import Path


@click.group()
def cli():
    """CLI tool for math rally and add/sub operations."""
    pass


# Check if the 'cli' directory exists
if not Path("cli").exists():
    click.echo("Error: 'cli' directory not found. Please ensure it exists.")
    exit(1)

# Dynamically load commands from the cli package
for file in Path("cli").glob("*.py"):
    if file.stem != "__init__":
        try:
            module = import_module(f"cli.{file.stem}")
            command = getattr(module, file.stem, None)
            if command:
                cli.add_command(command)
            else:
                raise AttributeError(f"No command found in {file.stem}.py")
        except Exception as e:
            click.echo(f"Error loading command from {file.stem}.py: {e}")

if __name__ == "__main__":
    cli()
