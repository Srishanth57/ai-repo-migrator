import typer
from agent import migrate

app = typer.Typer()

@app.command()
def run(file: str, instruction: str = "Upgrade this code to modern Python 3 syntax"):
    typer.echo(f"Migrating {file}...")
    try:
        migrate(file, instruction)
        typer.echo("✅ Migration succeeded, diff shown above.")
    except RuntimeError as e:
        typer.echo(f"❌ {e}")

if __name__ == "__main__":
    app()