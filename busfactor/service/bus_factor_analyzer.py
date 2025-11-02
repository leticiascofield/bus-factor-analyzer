import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from fnmatch import fnmatch
from pydriller import Repository

from busfactor.models.data_models import *


class BusFactorAnalyzer:
    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.since_date = datetime.now() - timedelta(days=config.days)

    def should_include_file(self, file_path: str) -> bool:
        # Primeiro verifica se está na lista de exclusão
        for pattern in self.config.exclude_patterns:
            if fnmatch(file_path, pattern):
                return False

        # Depois verifica se está na lista de inclusão
        for pattern in self.config.include_patterns:
            if fnmatch(file_path, pattern):
                return True

        return False

    def analyze_repository(self, repo_path: str, repo_identifier: str = "repo_identifier") -> List[RiskAnalysisResult]:
        file_stats: Dict[str, FileAnalysis] = {}
        try:
            for commit in Repository(repo_path, since=self.since_date).traverse_commits():
                for modification in commit.modified_files:
                    file_path = modification.new_path or modification.old_path

                    if not file_path:
                        continue

                    if not self.should_include_file(file_path):
                        continue

                    if file_path not in file_stats:
                        self.include_new_file_in_list(file_path, file_stats, repo_identifier)

                    file_stats[file_path].total_commits += 1
                    lines_changed = modification.added_lines + modification.deleted_lines
                    file_stats[file_path].total_lines_changed += lines_changed

                    author = commit.author.name

                    if author not in file_stats[file_path].commits_by_author:
                        self.add_new_author(author, file_path, file_stats)

                    file_stats[file_path].commits_by_author[author] += 1
                    file_stats[file_path].lines_by_author[author] += lines_changed

            return self._identify_risky_files(list(file_stats.values()))

        except Exception as e:
            raise Exception(f"Erro ao analisar repositório {repo_identifier}: {str(e)}")

    def add_new_author(self, author: str | None, file_path, file_stats: dict[str, FileAnalysis]):
        file_stats[file_path].commits_by_author[author] = 0
        file_stats[file_path].lines_by_author[author] = 0

    @staticmethod
    def include_new_file_in_list(file_path, file_stats: dict[str, FileAnalysis], repo_identifier: str):
        file_stats[file_path] = FileAnalysis(
            file_path=file_path,
            repository=repo_identifier,
            total_commits=0,
            total_lines_changed=0,
            commits_by_author={},
            lines_by_author={}
        )


    def _identify_risky_files(self, file_analyses: List[FileAnalysis]) -> List[RiskAnalysisResult]:

        risky_files = []

        for analysis in file_analyses:
            if not analysis.commits_by_author:
                continue

            # Encontra autor dominante por commits
            total_commits = analysis.total_commits
            dominant_author_commits = max(
                analysis.commits_by_author.items(),
                key=lambda x: x[1]
            )
            dominant_author_commits_name, dominant_author_commits_count = dominant_author_commits
            commits_dominance = dominant_author_commits_count / total_commits

            total_lines = analysis.total_lines_changed

            def get_commit_count(author_data):
                _, commit_count = author_data
                return commit_count

            dominant_author_lines = max(
                analysis.lines_by_author.items(),
                key=get_commit_count
            )
            dominant_author_lines_name, dominant_author_lines_count = dominant_author_lines
            lines_dominance = dominant_author_lines_count / total_lines if total_lines > 0 else 0

            if (commits_dominance >= self.config.dominance_threshold or
                    lines_dominance >= self.config.dominance_threshold):
                risky_files.append(RiskAnalysisResult(
                    file_path=analysis.file_path,
                    repository=analysis.repository,
                    dominant_author_commits=dominant_author_commits_name,
                    dominant_author_lines=dominant_author_lines_name,
                    commits_dominance=commits_dominance,
                    lines_dominance=lines_dominance,
                    total_commits=total_commits,
                    total_lines_changed=total_lines,
                    all_authors=list(analysis.commits_by_author.keys())
                ))

        return risky_files
