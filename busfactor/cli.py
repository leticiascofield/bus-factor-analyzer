import typer
from typing import List

app = typer.Typer(
    help="Detecta risco de monopólio de conhecimento (bus factor baixo) por arquivo.",
    no_args_is_help=True,
)

# Comando 1: hello (sanity check)
@app.command("hello")
def hello():
    """Comando de teste: apenas exibe uma mensagem."""
    typer.echo("bus-factor-analyzer: funcionando ✅")

# Comando 2: version
@app.command("version")
def version():
    """Mostra a versão da ferramenta."""
    typer.echo("bus-factor-analyzer 0.1.0")

# Comando 3: analyze (stub para testes)
@app.command("analyze")
def analyze(
    repos: List[str] = typer.Argument(..., metavar="REPO...", help="Um ou mais repositórios (URL, owner/repo ou caminho local)"),
    days: int = typer.Option(90, "--days", help="Janela temporal (dias)"),
    dominance_threshold: float = typer.Option(0.5, "--dominance-threshold", help="Limiar de dominância (0–1)"),
    include: List[str] = typer.Option(["**/*"], "--include", help="Globs para incluir (pode repetir)"),
    exclude: List[str] = typer.Option(["tests/**", "docs/**", ".github/**"], "--exclude", help="Globs para excluir (pode repetir)"),
    format: str = typer.Option("table", "--format", help="table|json|csv"),
):
    """
    (MVP) Por enquanto, só imprime os parâmetros recebidos.
    Próximo passo: conectar com analyzer/report.
    """
    typer.echo("=== parâmetros recebidos ===")
    typer.echo(f"repos: {repos}")
    typer.echo(f"days: {days}")
    typer.echo(f"dominance_threshold: {dominance_threshold}")
    typer.echo(f"include: {include}")
    typer.echo(f"exclude: {exclude}")
    typer.echo(f"format: {format}")

def main():
    app(prog_name="bus-factor-analyzer")

if __name__ == "__main__":
    main()
