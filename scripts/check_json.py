"""Validate tracked JSON files without changing generated artifacts."""

import json
import subprocess
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    output = subprocess.check_output(
        ["git", "ls-files", "-z", "--", "*.json"], cwd=root
    )
    paths = [path for path in output.decode("utf-8").split("\0") if path]
    for path in paths:
        try:
            json.loads((root / path).read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            raise SystemExit(f"{path}: {error}") from error
    print(f"Validated {len(paths)} tracked JSON files")


if __name__ == "__main__":
    main()
