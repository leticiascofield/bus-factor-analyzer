from unittest.mock import MagicMock, patch

import pytest

from busfactor.models.data_models import AnalysisConfig
from busfactor.service.bus_factor_analyzer import BusFactorAnalyzer


def test_should_include_file():
    cfg = AnalysisConfig(
        include_patterns=["src/**"],
        exclude_patterns=["src/vendor/**"],
    )
    analyzer = BusFactorAnalyzer(cfg)

    assert analyzer.should_include_file("src/main.py") is True
    assert analyzer.should_include_file("src/vendor/lib.py") is False
    assert analyzer.should_include_file("tests/test_main.py") is False


def test_include_new_file_and_add_author_and_identify_risky():
    cfg = AnalysisConfig(dominance_threshold=0.5)
    analyzer = BusFactorAnalyzer(cfg)

    file_stats = {}
    analyzer.include_new_file_in_list("a.py", file_stats, "repo1")
    assert "a.py" in file_stats

    analyzer.add_new_author("Alice", "a.py", file_stats)
    assert "Alice" in file_stats["a.py"].commits_by_author

    # populate stats to represent dominance by Alice
    file_stats["a.py"].total_commits = 4
    file_stats["a.py"].total_lines_changed = 100
    file_stats["a.py"].commits_by_author["Alice"] = 3
    file_stats["a.py"].commits_by_author["Bob"] = 1
    file_stats["a.py"].lines_by_author["Alice"] = 80
    file_stats["a.py"].lines_by_author["Bob"] = 20

    results = analyzer._identify_risky_files(list(file_stats.values()))
    assert len(results) == 1
    res = results[0]
    assert res.file_path == "a.py"
    assert res.dominant_author_commits == "Alice"
    assert res.commits_dominance >= 0.75


def test_analyze_repository_with_invalid_path():
    cfg = AnalysisConfig()
    analyzer = BusFactorAnalyzer(cfg)

    with pytest.raises(Exception) as exc_info:
        analyzer.analyze_repository("/invalid/path", "test_repo")
    assert "Erro ao analisar repositório test_repo" in str(exc_info.value)


@patch("busfactor.service.bus_factor_analyzer.Repository")
def test_analyze_repository_with_no_commits(mock_repo):
    # Mock repository with no commits
    mock_repo_instance = MagicMock()
    mock_repo_instance.traverse_commits.return_value = []
    mock_repo.return_value = mock_repo_instance

    cfg = AnalysisConfig(include_patterns=["*.py"])
    analyzer = BusFactorAnalyzer(cfg)

    results = analyzer.analyze_repository("/some/path", "test_repo")
    assert len(results) == 0
