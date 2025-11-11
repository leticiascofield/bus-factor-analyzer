from busfactor.models.data_models import AnalysisConfig, RiskAnalysisResult


def test_risk_analysis_result_properties():
    rar = RiskAnalysisResult(
        file_path="a.py",
        repository="repo",
        dominant_author_commits="Alice",
        dominant_author_lines="Alice",
        commits_dominance=0.756,
        lines_dominance=0.321,
        total_commits=10,
        total_lines_changed=200,
        all_authors=["Alice", "Bob", "Carol", "Dave"],
    )

    assert rar.commits_dominance_percentage == "75.6%"
    assert rar.lines_dominance_percentage == "32.1%"
    assert rar.authors_preview == "Alice, Bob, Carol... (+1)"


def test_analysis_config_should_have_correct_default_values():
    config = AnalysisConfig()
    assert config.days == 9000
    assert config.dominance_threshold == 0.6
    assert config.include_patterns == ["**/*"]
    assert config.exclude_patterns == ["docs/**", ".github/**"]
