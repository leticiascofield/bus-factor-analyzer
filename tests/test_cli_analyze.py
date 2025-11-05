import os
import subprocess
import sys
import tempfile

import git
import pytest


@pytest.fixture
def test_repo():
    """Creates a temporary Git repository for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Configuração Git
        subprocess.run(["git", "init", tmp_dir], check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "--global", "user.email", "test@example.com"],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "--global", "user.name", "Test User"],
            check=True,
            capture_output=True,
        )

        # Cria alguns arquivos
        files = {
            "main.py": "print('hello')\n",
            "lib.py": "def func(): pass\n",
            "test.py": "def test_func(): pass\n",
        }

        for fname, content in files.items():
            fpath = os.path.join(tmp_dir, fname)
            with open(fpath, "w") as f:
                f.write(content)

        # Primeiro commit como author1
        subprocess.run(
            ["git", "-C", tmp_dir, "add", "."], check=True, capture_output=True
        )
        subprocess.run(
            [
                "git",
                "-C",
                tmp_dir,
                "commit",
                "-m",
                "initial commit",
                "--author",
                "Author1 <author1@test.com>",
            ],
            check=True,
            capture_output=True,
        )

        # Modifica main.py como author2
        with open(os.path.join(tmp_dir, "main.py"), "a") as f:
            f.write("print('world')\n")

        # Segundo commit como author2
        subprocess.run(
            ["git", "-C", tmp_dir, "add", "main.py"], check=True, capture_output=True
        )
        subprocess.run(
            [
                "git",
                "-C",
                tmp_dir,
                "commit",
                "-m",
                "update main",
                "--author",
                "Author2 <author2@test.com>",
            ],
            check=True,
            capture_output=True,
        )

        yield tmp_dir


def test_cli_analyze_should_accept_days_parameter(test_repo):
    proc = subprocess.run(
        [sys.executable, "-m", "busfactor.cli", "analyze", test_repo, "--days", "1"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0


def test_cli_analyze_should_accept_dominance_threshold(test_repo):
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "busfactor.cli",
            "analyze",
            test_repo,
            "--dominance-threshold",
            "0.9",
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0


def test_cli_analyze_should_respect_include_and_exclude_patterns(test_repo):
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "busfactor.cli",
            "analyze",
            test_repo,
            "--include",
            "*.py",
            "--exclude",
            "test.py",
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "test.py" not in proc.stdout  # Should be excluded by pattern
