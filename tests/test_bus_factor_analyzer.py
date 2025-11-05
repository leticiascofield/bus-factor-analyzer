from unittest.mock import MagicMock, patch

import pytest

from busfactor.models.data_models import AnalysisConfig, FileAnalysis
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


@patch("busfactor.service.bus_factor_analyzer.Repository")
def test_analyze_repository_with_empty_file_paths(mock_repo):
    # Mock commit with modification that has no path
    mock_commit = MagicMock()
    mock_modification = MagicMock()
    mock_modification.new_path = None
    mock_modification.old_path = None
    mock_commit.modified_files = [mock_modification]

    mock_repo_instance = MagicMock()
    mock_repo_instance.traverse_commits.return_value = [mock_commit]
    mock_repo.return_value = mock_repo_instance

    cfg = AnalysisConfig(include_patterns=["*.py"])
    analyzer = BusFactorAnalyzer(cfg)

    results = analyzer.analyze_repository("/some/path", "test_repo")
    assert len(results) == 0


@patch("busfactor.service.bus_factor_analyzer.Repository")
def test_analyze_repository_with_excluded_files(mock_repo):
    # Mock commit with modification that should be excluded
    mock_commit = MagicMock()
    mock_modification = MagicMock()
    mock_modification.new_path = "vendor/lib.py"
    mock_modification.old_path = None
    mock_modification.added_lines = 10
    mock_modification.deleted_lines = 5
    mock_commit.modified_files = [mock_modification]
    mock_commit.author.name = "Alice"

    mock_repo_instance = MagicMock()
    mock_repo_instance.traverse_commits.return_value = [mock_commit]
    mock_repo.return_value = mock_repo_instance

    cfg = AnalysisConfig(include_patterns=["*.py"], exclude_patterns=["vendor/*"])
    analyzer = BusFactorAnalyzer(cfg)

    results = analyzer.analyze_repository("/some/path", "test_repo")
    assert len(results) == 0


@patch("busfactor.service.bus_factor_analyzer.Repository")
def test_analyze_repository_with_single_file_multiple_authors(mock_repo):
    # Mock commits with multiple authors on same file
    mock_commits = []
    authors = ["Alice", "Bob", "Charlie"]
    for author in authors:
        mock_commit = MagicMock()
        mock_modification = MagicMock()
        mock_modification.new_path = "src/main.py"
        mock_modification.old_path = None
        mock_modification.added_lines = 10
        mock_modification.deleted_lines = 5
        mock_commit.modified_files = [mock_modification]
        mock_commit.author.name = author
        mock_commits.append(mock_commit)

    mock_repo_instance = MagicMock()
    mock_repo_instance.traverse_commits.return_value = mock_commits
    mock_repo.return_value = mock_repo_instance

    cfg = AnalysisConfig(
        include_patterns=["src/*.py"],
        dominance_threshold=0.8,  # Set high to ensure no risk with equal contributions
    )
    analyzer = BusFactorAnalyzer(cfg)

    results = analyzer.analyze_repository("/some/path", "test_repo")
    assert len(results) == 0  # Should not be risky as contributions are equal


def test_identify_risky_files_with_empty_commits():
    cfg = AnalysisConfig()
    analyzer = BusFactorAnalyzer(cfg)

    # Create a file analysis with no commits
    file_analysis = FileAnalysis(
        file_path="empty.py",
        repository="test_repo",
        total_commits=0,
        total_lines_changed=0,
        commits_by_author={},
        lines_by_author={},
    )

    results = analyzer._identify_risky_files([file_analysis])
    assert len(results) == 0
