import typer
from typing import List

from rich.console import Console

from busfactor.models import AnalysisConfig
from busfactor.reportGenerator.file_report_generator import ReportGenerator
from busfactor.service.bus_factor_analyzer import BusFactorAnalyzer
from busfactor.service.repository_manager import RepositoryManager

app = typer.Typer(
    help="Detecta risco de monopólio de conhecimento (bus factor baixo) por arquivo.",
    no_args_is_help=True,
)

console = Console()

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

class BusFactorCLI:
    """Interface de linha de comando para o Bus Factor Analyzer"""

    def __init__(self):
        self.repository_manager = RepositoryManager()
        self.report_generator = ReportGenerator()

    def analyze_repositories(
            self,
            repos: List[str],
            days: int = 9000,
            dominance_threshold: float = 0.5,
            include: List[str] = None,
            exclude: List[str] = None,
            format: str = "table"
    ):
        config = AnalysisConfig(
            days=days,
            dominance_threshold=dominance_threshold,
            include_patterns=include or None,
            exclude_patterns=exclude or None
        )

        analyzer = BusFactorAnalyzer(config)
        all_results = []

        for repo in repos:
            console.print(f"🔍 Analisando repositório: [bold]{repo}[/bold]")

            try:
                repo_path = self.repository_manager.clone_repository(repo)

                risky_files = analyzer.analyze_repository(repo_path, repo)
                all_results.extend(risky_files)

                console.print(f"Análise concluída: {len(risky_files)} arquivos de risco encontrados")

            except Exception as e:
                console.print(f"Erro ao analisar {repo}: {e}")
                continue

        if not all_results:
            console.print("Nenhum arquivo com risco de monopólio encontrado! Repo saúdavel")
        else:
            console.print(f"Relatório Final: {len(all_results)} arquivos com risco encontrados")
            self.report_generator.generate_report(all_results, format)

cli = BusFactorCLI()
@app.command("analyze")
def analyze(
    repos: List[str] = typer.Argument(..., metavar="REPO...", help="Um ou mais repositórios (URL, owner/repo ou caminho local)"),
    days: int = typer.Option(9000, "--days", help="Janela temporal (dias)"),
    dominance_threshold: float = typer.Option(0.5, "--dominance-threshold", help="Limiar de dominância (0–1)"),
    include: List[str] = typer.Option(None, "--include", help="Globs para incluir (pode repetir)"),
    exclude: List[str] = typer.Option(None, "--exclude", help="Globs para excluir (pode repetir)"),
    format: str = typer.Option("table", "--format", help="table|json|csv"),
):

    cli.analyze_repositories(
        repos=repos,
        days=days,
        dominance_threshold=dominance_threshold,
        include=include,
        exclude=exclude,
        format=format
    )

def main():
    app(prog_name="bus-factor-analyzer")

if __name__ == "__main__":
    main()
