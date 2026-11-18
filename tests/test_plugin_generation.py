"""Regression tests for plugin generation failure safety."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import catalog


class PluginGenerationTests(unittest.TestCase):
    def test_manifest_failure_restores_existing_plugins(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old = root / "plugins" / "sentinel.txt"
            old.parent.mkdir()
            old.write_text("keep", encoding="utf-8")
            with (
                patch.object(catalog, "ROOT", root),
                patch.object(catalog, "_build_plugins", return_value=({}, {"name": "test"})),
                patch.object(Path, "replace", side_effect=OSError("cannot replace manifest")),
                self.assertRaisesRegex(OSError, "cannot replace manifest"),
            ):
                catalog.plugins([], {})
            self.assertEqual(old.read_text(encoding="utf-8"), "keep")

    def test_success_replaces_tree_and_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old = root / "plugins" / "sentinel.txt"
            old.parent.mkdir()
            old.write_text("old", encoding="utf-8")

            def build(servers, mcp, output):
                (output / "new.txt").write_text("new", encoding="utf-8")
                return {"test": {}}, {"name": "test"}

            with patch.object(catalog, "ROOT", root), patch.object(catalog, "_build_plugins", side_effect=build):
                self.assertEqual(catalog.plugins([], {}), {"test": {}})
            self.assertFalse(old.exists())
            self.assertEqual((root / "plugins" / "new.txt").read_text(encoding="utf-8"), "new")
            self.assertTrue((root / ".claude-plugin" / "marketplace.json").exists())

    def test_skill_generation_failure_preserves_existing_plugins(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old = root / "plugins" / "existing" / "sentinel.txt"
            old.parent.mkdir(parents=True)
            old.write_text("keep", encoding="utf-8")
            server = {
                "name": "hosted-mcp", "title": "Hosted", "description": "Test",
                "version": "1.0", "url": "https://example.org/mcp",
                "repository": "https://example.org/repo", "category": "test",
                "site": "https://example.org", "env": [], "auth": "none",
            }
            with (
                patch.object(catalog, "ROOT", root),
                patch.object(catalog, "skill", side_effect=ValueError("bad skill")),
                self.assertRaisesRegex(ValueError, "bad skill"),
            ):
                catalog.plugins([server], {"hosted": {"url": server["url"]}})
            self.assertEqual(old.read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
