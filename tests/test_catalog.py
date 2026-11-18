"""Offline tests for the catalog generator."""

import io
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

from scripts import catalog


class ToolExtractionTests(unittest.TestCase):
    def test_extracts_sync_and_async_tools_and_write_annotations(self):
        with tempfile.TemporaryDirectory() as directory:
            src = Path(directory)
            (src / "tools.py").write_text(
                '''
@tool("Search")
def search():
    """Find products across
    shops. More details.

    An additional paragraph.
    """

@tool("Send", read_only=False)
async def send():
    """Send a message."""

def helper():
    """Not a tool."""
''',
                encoding="utf-8",
            )
            self.assertEqual(
                catalog.tools(src),
                [
                    {"name": "search", "title": "Search", "summary": "Find products across shops.", "read_only": True},
                    {"name": "send", "title": "Send", "summary": "Send a message.", "read_only": False},
                ],
            )

    def test_empty_directory_has_no_tools(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(catalog.tools(Path(directory)), [])


class ReleasedTests(unittest.TestCase):
    @staticmethod
    def not_found():
        return urllib.error.HTTPError("https://pypi.org/", 404, "not found", {}, None)

    @patch("scripts.catalog.urllib.request.urlopen")
    def test_existing_version_is_used(self, open_url):
        self.assertEqual(catalog.released("example", "1.0"), "1.0")
        open_url.assert_called_once_with("https://pypi.org/pypi/example/1.0/json", timeout=30)
        open_url.return_value.close.assert_called_once()

    @patch("scripts.catalog.urllib.request.urlopen")
    def test_owned_package_falls_back_to_latest(self, open_url):
        response = io.BytesIO(json.dumps({"info": {"version": "0.9"}}).encode())
        open_url.side_effect = [self.not_found(), response]
        self.assertEqual(catalog.released("example", "1.0"), "0.9")

    @patch("scripts.catalog.urllib.request.urlopen")
    def test_external_package_never_falls_back(self, open_url):
        open_url.side_effect = self.not_found()
        with self.assertRaisesRegex(SystemExit, "not on PyPI"):
            catalog.released("example", "1.0", ours=False)
        self.assertEqual(open_url.call_count, 1)

    @patch("scripts.catalog.urllib.request.urlopen")
    def test_other_http_errors_are_not_hidden(self, open_url):
        open_url.side_effect = urllib.error.HTTPError("https://pypi.org/", 503, "unavailable", {}, None)
        with self.assertRaises(urllib.error.HTTPError):
            catalog.released("example", "1.0")


if __name__ == "__main__":
    unittest.main()
