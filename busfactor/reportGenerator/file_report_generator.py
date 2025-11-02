import json
import csv
import sys
from typing import List
from rich.console import Console
from rich.table import Table

from busfactor.models import RiskAnalysisResult


class ReportGenerator:
    def __init__(self):
        self.console = Console()

    def generate_report(self, results: List[RiskAnalysisResult], format: str):
        if format == "table":
            self._generate_table_report(results)
        else:
            raise ValueError(f"Formato não suportado: {format}")

    def _generate_table_report(self, results: List[RiskAnalysisResult]):
        table = Table(title="Bus Factor Analysis")

        table.add_column("Repositório")
        table.add_column("Arquivo")
        table.add_column("Autor Dominante")
        table.add_column("Commits")
        table.add_column("Linhas")
        table.add_column("Total Commits")
        table.add_column("Total Linhas")
        table.add_column("Autores")

        for result in results:
            table.add_row(
                result.repository,
                result.file_path,
                result.dominant_author_commits,
                result.commits_dominance_percentage,
                result.lines_dominance_percentage,
                str(result.total_commits),
                str(result.total_lines_changed),
                result.authors_preview
            )

            self.console.print(table)
