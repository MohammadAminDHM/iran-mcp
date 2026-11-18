"""Reject duplicate tool names within a single server."""

import tempfile
import unittest
from pathlib import Path

from scripts import catalog


class ToolDuplicateTests(unittest.TestCase):
    def test_duplicate_names_in_hosted_card_fail(self):
        tool = {"name": "search", "description": "Search."}
        with self.assertRaisesRegex(ValueError, "duplicate tool name.*search"):
            catalog.card_tools({"tools": [tool, tool]})

    def test_duplicate_names_across_files_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            src = Path(directory)
            for filename in ("a.py", "b.py"):
                (src / filename).write_text('@tool("Search")\ndef search():\n    pass\n', encoding="utf-8")
            with self.assertRaisesRegex(SystemExit, "duplicate tool name.*search"):
                catalog.tools(src)


if __name__ == "__main__":
    unittest.main()
