import subprocess
from unittest.mock import MagicMock, patch

import pytest

from busfactor.service.repository_manager import RepositoryManager


class TestRepositoryManager:
    def test_is_github_url_with_valid_url(self):
        manager = RepositoryManager()
        url = "https://github.com/user/repo"
        assert manager._is_github_url(url) is True

    @patch("busfactor.service.repository_manager.subprocess.run")
    @patch("busfactor.service.repository_manager.tempfile.mkdtemp")
    def test_clone_repository_success(self, mock_mkdtemp, mock_run):
        mock_mkdtemp.return_value = "/tmp/test_repo"
        mock_run.return_value = MagicMock(returncode=0)

        manager = RepositoryManager()
        result = manager.clone_repository("https://github.com/user/repo")

        assert result == "/tmp/test_repo"
        mock_run.assert_called_once()
        assert "/tmp/test_repo" in manager.temp_dirs

    @patch("busfactor.service.repository_manager.subprocess.run")
    @patch("busfactor.service.repository_manager.tempfile.mkdtemp")
    def test_clone_repository_git_failure(self, mock_mkdtemp, mock_run):
        mock_mkdtemp.return_value = "/tmp/test_repo"
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "git clone", stderr="Repository not found"
        )

        manager = RepositoryManager()

        with pytest.raises(Exception) as exc_info:
            manager.clone_repository("https://github.com/user/nonexistent")

        assert "Erro ao clonar repositório" in str(exc_info.value)
        assert "/tmp/test_repo" not in manager.temp_dirs
