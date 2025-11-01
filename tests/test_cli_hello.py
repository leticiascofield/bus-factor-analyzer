import subprocess
import sys

def test_cli_hello_runs():
    proc = subprocess.run([sys.executable, "-m", "busfactor.cli", "hello"],
                          capture_output=True, text=True)
    assert proc.returncode == 0
    assert "funcionando" in proc.stdout.lower()
