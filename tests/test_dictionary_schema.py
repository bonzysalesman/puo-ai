import copy
import json
import unittest

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - optional dependency path
    Draft202012Validator = None


class DictionarySchemaTests(unittest.TestCase):
    def setUp(self):
        with open("schemas/lexicon.schema.json", encoding="utf-8") as f:
            self.schema = json.load(f)
        with open("data/lexicon.json", encoding="utf-8") as f:
            self.dictionary = json.load(f)
        self.validator = (
            Draft202012Validator(self.schema) if Draft202012Validator is not None else None
        )

    def _validate_with_fallback(self, data):
        if self.validator is not None:
            errors = sorted(self.validator.iter_errors(data), key=lambda e: list(e.path))
            self.assertEqual(errors, [])
            return

        # Fallback structural validation when jsonschema package is unavailable.
        required = set(self.schema["items"]["required"])
        for i, entry in enumerate(data):
            self.assertIsInstance(entry, dict, msg=f"entry[{i}] must be object")
            self.assertTrue(required.issubset(entry.keys()), msg=f"entry[{i}] missing required fields")
            self.assertIsInstance(entry["entry_id"], str)
            self.assertIsInstance(entry["headword_english"], str)
            self.assertIsInstance(entry["pos"], list)
            self.assertIsInstance(entry["headword_sesotho"], list)
            self.assertIsInstance(entry["syllables"], list)
            self.assertIsInstance(entry["morphology"], dict)
            self.assertIsInstance(entry["senses"], list)
            self.assertIsInstance(entry["thesaurus"], dict)

            for sense in entry["senses"]:
                self.assertIsInstance(sense, dict)
                self.assertIn("sense_id", sense)
                self.assertIn("definition_en", sense)
                self.assertIn("sesotho_term", sense)
                self.assertIsInstance(sense["sesotho_term"], list)
                if "usage_example" in sense:
                    usage = sense["usage_example"]
                    self.assertIsInstance(usage, dict)
                    for key in ["sesotho", "english", "source"]:
                        self.assertIn(key, usage)

    def test_dictionary_json_conforms_to_schema(self):
        self._validate_with_fallback(self.dictionary)

    def test_missing_required_field_fails_schema(self):
        bad = copy.deepcopy(self.dictionary)
        bad[0].pop("headword_english", None)
        if self.validator is not None:
            errors = sorted(self.validator.iter_errors(bad), key=lambda e: list(e.path))
            self.assertTrue(errors)
            return

        with self.assertRaises(AssertionError):
            self._validate_with_fallback(bad)


if __name__ == "__main__":
    unittest.main()
