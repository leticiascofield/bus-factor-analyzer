from unittest.mock import patch

import pytest

from busfactor.models.data_models import RiskAnalysisResult
from busfactor.reportGenerator.file_report_generator import ReportGenerator
from busfactor.reportGenerator.html_report_generator import HTMLReportGenerator


@pytest.fixture
def sample_results():
    """Creates sample RiskAnalysisResult for testing"""
    return [
        RiskAnalysisResult(
            file_path="src/main.py",
            repository="repo1",
            dominant_author_commits="Alice",
            dominant_author_lines="Alice",
            commits_dominance=0.85,
            lines_dominance=0.90,
            total_commits=20,
            total_lines_changed=500,
            all_authors=["Alice", "Bob", "Charlie", "David"],
        ),
        RiskAnalysisResult(
            file_path="src/utils.py",
            repository="repo1",
            dominant_author_commits="Bob",
            dominant_author_lines="Bob",
            commits_dominance=0.72,
            lines_dominance=0.65,
            total_commits=15,
            total_lines_changed=300,
            all_authors=["Bob", "Alice"],
        ),
    ]


class TestReportGenerator:
    def test_generate_report_calls_html_generator(self, sample_results):
        generator = ReportGenerator()

        with patch.object(HTMLReportGenerator, "generate_html") as mock_html_gen:
            generator.generate_report(sample_results, format="html")
            mock_html_gen.assert_called_once_with(sample_results)


class TestHTMLReportGenerator:
    def test_generate_html_creates_file(self, sample_results, tmp_path):
        generator = HTMLReportGenerator()
        output_file = tmp_path / "report.html"

        generator.generate_html(sample_results, output_path=str(output_file))

        assert output_file.exists()
        content = output_file.read_text()
        assert "Relatório de Análise de Bus Factor" in content
        assert "src/main.py" in content
        assert "Alice" in content
