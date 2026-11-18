"""Validate safety annotations in hosted server cards."""

import unittest

from scripts import catalog


class CardAnnotationTests(unittest.TestCase):
    def test_authentication_must_be_an_object_when_present(self):
        for value in (None, [], "", False):
            with self.subTest(value=value):
                card = {"authentication": value, "tools": []}
                with self.assertRaisesRegex(ValueError, "authentication must be an object"):
                    catalog.card_tools(card)

    def test_missing_authentication_is_allowed(self):
        self.assertEqual(catalog.card_tools({"tools": []}), ([], "none", True))

    def test_oauth_schemes_must_be_a_list_of_strings(self):
        for schemes in ("oauth2", None, [123], {"oauth2": True}):
            with self.subTest(schemes=schemes):
                card = {"authentication": {"required": True, "schemes": schemes}, "tools": []}
                with self.assertRaisesRegex(ValueError, "authentication.schemes must be a list of strings"):
                    catalog.card_tools(card)

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
