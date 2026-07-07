import subprocess
import sys
from pathlib import Path


def test_module_runs_as_main(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "joplin_to_obsidian", "--help"],
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )
    assert result.returncode == 0
    assert "Migrate Joplin notebook" in result.stdout
