from unittest.mock import MagicMock, patch

from busfactor.models.data_models import AnalysisConfig, FileAnalysis
from busfactor.service.bus_factor_analyzer import BusFactorAnalyzer


class TestBusFactorAnalyzerEdgeCases:
    def test_should_include_file_exclude_takes_precedence(self):
        cfg = AnalysisConfig(
            include_patterns=["**/*"],
            exclude_patterns=["vendor/**"],
        )
        analyzer = BusFactorAnalyzer(cfg)

        # Exclude takes precedence over include
        assert analyzer.should_include_file("vendor/lib.py") is False
        assert analyzer.should_include_file("src/main.py") is True

    def test_identify_risky_files_single_author(self):
        cfg = AnalysisConfig(dominance_threshold=0.5)
        analyzer = BusFactorAnalyzer(cfg)

        file_analysis = FileAnalysis(
            file_path="single.py",
            repository="test_repo",
            total_commits=10,
            total_lines_changed=500,
            commits_by_author={"Alice": 10},
            lines_by_author={"Alice": 500},
        )

        results = analyzer._identify_risky_files([file_analysis])
        assert len(results) == 1
        assert results[0].commits_dominance == 1.0
        assert results[0].lines_dominance == 1.0

    @patch("busfactor.service.bus_factor_analyzer.Repository")
    def test_analyze_repository_with_renamed_files(self, mock_repo):
        mock_commit = MagicMock()
        mock_modification = MagicMock()
        mock_modification.new_path = "src/new_name.py"
        mock_modification.old_path = "src/old_name.py"
        mock_modification.added_lines = 5
        mock_modification.deleted_lines = 3
        mock_commit.modified_files = [mock_modification]
        mock_commit.author.name = "Alice"

        mock_repo_instance = MagicMock()
        mock_repo_instance.traverse_commits.return_value = [mock_commit]
        mock_repo.return_value = mock_repo_instance

        cfg = AnalysisConfig(include_patterns=["src/*.py"])
        analyzer = BusFactorAnalyzer(cfg)

        results = analyzer.analyze_repository("/some/path", "test_repo")
        # Should use new_path when available
        assert len(results) == 1
        assert results[0].file_path == "src/new_name.py"
