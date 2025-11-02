from dataclasses import dataclass
from typing import List, Dict

@dataclass
class FileAnalysis:
    file_path: str
    repository: str
    total_commits: int
    total_lines_changed: int
    commits_by_author: Dict[str, int]
    lines_by_author: Dict[str, int]


@dataclass
class RiskAnalysisResult:
    file_path: str
    repository: str
    dominant_author_commits: str
    dominant_author_lines: str
    commits_dominance: float
    lines_dominance: float
    total_commits: int
    total_lines_changed: int
    all_authors: List[str]

    @property
    def commits_dominance_percentage(self) -> str:
        return f"{self.commits_dominance:.1%}"

    @property
    def lines_dominance_percentage(self) -> str:
        return f"{self.lines_dominance:.1%}"

    @property
    def authors_preview(self) -> str:
        preview = ", ".join(self.all_authors[:3])
        if len(self.all_authors) > 3:
            preview += f"... (+{len(self.all_authors) - 3})"
        return preview


@dataclass
class AnalysisConfig:
    days: int = 90
    dominance_threshold: float = 0.6 # default
    include_patterns: List[str] = None
    exclude_patterns: List[str] = None

    def __post_init__(self):
        if self.include_patterns is None:
            self.include_patterns = ["**/*"]
        if self.exclude_patterns is None:
            self.exclude_patterns = ["docs/**", ".github/**"]
            #todo should we exclude tests ?? "tests/**",