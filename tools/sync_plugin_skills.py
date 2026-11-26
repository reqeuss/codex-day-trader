"""Copy the repository skills into the self-contained Codex plugin."""

from pathlib import Path
from shutil import copytree, ignore_patterns


ROOT = Path(__file__).resolve().parents[1]


if __name__ == "__main__":
    copytree(
        ROOT / ".agents" / "skills",
        ROOT / "plugins" / "day-trader-fr" / "skills",
        dirs_exist_ok=True,
        ignore=ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
    )
