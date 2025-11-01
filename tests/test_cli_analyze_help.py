import subprocess
import sys

def test_cli_analyze_help_runs():
    proc = subprocess.run([sys.executable, "-m", "busfactor.cli", "analyze", "--help"],
                          capture_output=True, text=True)
    assert proc.returncode == 0
    assert "REPO..." in proc.stdout
