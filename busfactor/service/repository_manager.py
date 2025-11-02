import subprocess
import tempfile
import shutil


class RepositoryManager:
    def __init__(self):
        self.temp_dirs = []

    def clone_repository(self, repo_url: str) -> str:
        temp_dir = tempfile.mkdtemp(prefix="bus_factor_")
        self.temp_dirs.append(temp_dir)

        try:
            if not self._is_github_url(repo_url):
                raise ValueError(
                    "URL do repositório inválida, apenas urls do github sendo repositórios públicos são validos")

            subprocess.run(
                ['git', 'clone', '--depth', '1', repo_url, temp_dir],
                check=True,
                capture_output=True,
                text=True
            )

            return temp_dir

        except subprocess.CalledProcessError as e:
            self._cleanup_temp_dir(temp_dir)
            raise Exception(f"Erro ao clonar repositório {repo_url}: {e.stderr}")

    def _is_github_url(self, repo_identifier: str) -> bool:
        return repo_identifier.index('https://github.com/') != -1

    def _cleanup_temp_dir(self, temp_dir: str):
        if temp_dir in self.temp_dirs:
            self.temp_dirs.remove(temp_dir)

    def __del__(self):
        self.temp_dirs.clear()
