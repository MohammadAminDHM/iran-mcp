"""Validate safety annotations in hosted server cards."""

import unittest

from scripts import catalog


class CardAnnotationTests(unittest.TestCase):
    def test_rejects_non_boolean_authentication_required(self):
        for value in (0, "false", None):
            with self.subTest(value=value):
                card = {"authentication": {"required": value}, "tools": []}
                with self.assertRaisesRegex(ValueError, "authentication.required must be a boolean"):
                    catalog.card_tools(card)

    def test_rejects_non_boolean_read_only_hint(self):
        for value in ("false", 1, None):
            with self.subTest(value=value):
                card = {
                    "tools": [{
                        "name": "action",
                        "description": "Take action.",
                        "annotations": {"readOnlyHint": value},
                    }],
                }
                with self.assertRaisesRegex(ValueError, "readOnlyHint must be a boolean"):
                    catalog.card_tools(card)


if __name__ == "__main__":
    unittest.main()
