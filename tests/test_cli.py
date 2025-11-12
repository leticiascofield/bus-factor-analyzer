from unittest.mock import MagicMock, patch

import pytest

from busfactor.cli import BusFactorCLI
from busfactor.models.data_models import RiskAnalysisResult


@pytest.fixture
def sample_risky_results():
    """Sample results for testing"""
    return [
        RiskAnalysisResult(
            file_path="src/main.py",
            repository="test_repo",
            dominant_author_commits="Alice",
            dominant_author_lines="Alice",
            commits_dominance=0.85,
            lines_dominance=0.90,
            total_commits=20,
            total_lines_changed=500,
            all_authors=["Alice", "Bob"],
        )
    ]


class TestBusFactorCLI:
    def test_cli_initialization(self):
        cli = BusFactorCLI()
        assert cli.repository_manager is not None
        assert cli.report_generator is not None

    @patch("busfactor.cli.BusFactorAnalyzer")
    @patch("busfactor.cli.RepositoryManager")
    @patch("busfactor.cli.ReportGenerator")
    def test_analyze_repositories_aggregates_results(
        self, mock_report_gen_class, mock_rm_class, mock_analyzer_class
    ):
        mock_analyzer = MagicMock()
        mock_analyzer_class.return_value = mock_analyzer

        result1 = RiskAnalysisResult(
            file_path="src/main.py",
            repository="repo1",
            dominant_author_commits="Alice",
            dominant_author_lines="Alice",
            commits_dominance=0.8,
            lines_dominance=0.8,
            total_commits=10,
            total_lines_changed=500,
            all_authors=["Alice"],
        )

        result2 = RiskAnalysisResult(
            file_path="src/utils.py",
            repository="repo2",
            dominant_author_commits="Bob",
            dominant_author_lines="Bob",
            commits_dominance=0.75,
            lines_dominance=0.75,
            total_commits=8,
            total_lines_changed=300,
            all_authors=["Bob"],
        )

        mock_analyzer.analyze_repository.side_effect = [[result1], [result2]]

        mock_rm = MagicMock()
        mock_rm_class.return_value = mock_rm
        mock_rm.clone_repository.side_effect = ["/tmp/repo1", "/tmp/repo2"]

        mock_report_gen = MagicMock()
        mock_report_gen_class.return_value = mock_report_gen

        cli = BusFactorCLI()
        cli.analyze_repositories(
            repos=[
                "https://github.com/user/repo1",
                "https://github.com/user/repo2",
            ],
            format="html",
        )

        # Verify aggregated results were passed to report generator
        called_results = mock_report_gen.generate_report.call_args[0][0]
        assert len(called_results) == 2
        assert called_results[0].file_path == "src/main.py"
        assert called_results[1].file_path == "src/utils.py"
