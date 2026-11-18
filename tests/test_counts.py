"""Tests for catalog count validation."""

import unittest

from scripts.check_counts import validate


class CountTests(unittest.TestCase):
    def setUp(self):
        self.catalog = [{"name": "example-mcp", "tool_count": 2, "tools": [{}, {}]}]
        self.docs = {
            "README.md": 'alt="iran-mcp: 1 MCP servers and 2 tools',
            "README.fa.md": 'alt="iran-mcp: ۱ سرور MCP و ۲ ابزار',
            "AGENTS.md": "1 MCP servers for Iranian websites, 2 tools",
            "llms.txt": "> 1 MCP servers (2 tools)",
        }

    def test_valid_counts(self):
        self.assertEqual(validate(self.catalog, self.docs), [])

    def test_server_tool_count_mismatch(self):
        self.catalog[0]["tool_count"] = 3
        self.assertTrue(any("example-mcp" in error for error in validate(self.catalog, self.docs)))

    def test_stale_or_missing_document_counts_fail(self):
        for name in self.docs:
            with self.subTest(name=name):
                docs = dict(self.docs)
                docs[name] = "outdated"
                self.assertTrue(any(name in error for error in validate(self.catalog, docs)))

    def test_duplicate_server_names_fail(self):
        self.catalog.append(dict(self.catalog[0]))
        self.assertTrue(any("duplicate" in error for error in validate(self.catalog, self.docs)))


if __name__ == "__main__":
    unittest.main()
