import copy
import json
import unittest

from jsonschema import Draft202012Validator


class DictionarySchemaTests(unittest.TestCase):
    def setUp(self):
        with open("dictionary.schema.json", encoding="utf-8") as f:
            self.schema = json.load(f)
        with open("dictionary.json", encoding="utf-8") as f:
            self.dictionary = json.load(f)
        self.validator = Draft202012Validator(self.schema)

    def test_dictionary_json_conforms_to_schema(self):
        errors = sorted(self.validator.iter_errors(self.dictionary), key=lambda e: list(e.path))
        self.assertEqual(errors, [])

    def test_missing_required_field_fails_schema(self):
        bad = copy.deepcopy(self.dictionary)
        bad[0].pop("headword_english", None)
        errors = sorted(self.validator.iter_errors(bad), key=lambda e: list(e.path))
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
