import json
import unittest

from split_datasets import split_datasets

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - optional dependency path
    Draft202012Validator = None


class SplitDatasetsTests(unittest.TestCase):
    def _validate_schema(self, path, payload):
        with open(path, encoding="utf-8") as f:
            schema = json.load(f)
        if Draft202012Validator is None:
            # Basic fallback: if jsonschema is unavailable we still assert shape minimally.
            self.assertIsInstance(payload, list)
            return
        errors = sorted(
            Draft202012Validator(schema).iter_errors(payload),
            key=lambda e: list(e.path),
        )
        self.assertEqual(errors, [])

    def test_split_normalizes_and_links_usage_examples(self):
        dictionary = [
            {
                "entry_id": "e1",
                "headword_english": ["Light"],
                "pos": ["noun"],
                "headword_sesotho": [{"orthographic": "leseli"}],
                "syllables": ["le-se-li"],
                "morphology": {"root": "", "derivation": "", "noun_class": ""},
                "thesaurus": {"synonyms_en": [], "antonyms_en": [], "synonyms_st": [], "antonyms_st": []},
                "senses": [
                    {
                        "id": "legacy_1",
                        "definition": "light",
                        "usage_examples": [
                            {
                                "sesotho": "Leseli le be teng.",
                                "english": "Let there be light.",
                                "source": "JW Bible - Genesis 1 (Verse v1001003)",
                            }
                        ],
                    }
                ],
            }
        ]

        lexicon, corpus, attestations = split_datasets(dictionary)

        self.assertEqual(len(lexicon), 1)
        self.assertEqual(lexicon[0]["headword_english"], "Light")
        self.assertEqual(lexicon[0]["senses"][0]["sense_id"], "legacy_1")
        self.assertEqual(lexicon[0]["senses"][0]["definition_en"], "light")

        self.assertEqual(len(corpus), 1)
        self.assertEqual(corpus[0]["source"], "JW Bible - Genesis 1")
        self.assertEqual(corpus[0]["ref"], "v1001003")

        self.assertEqual(len(attestations), 1)
        self.assertEqual(attestations[0]["sense_id"], "legacy_1")
        self.assertEqual(attestations[0]["corpus_id"], corpus[0]["corpus_id"])

    def test_split_current_dictionary_satisfies_new_schemas_and_links(self):
        with open("data/legacy/dictionary.json", encoding="utf-8") as f:
            dictionary = json.load(f)
        lexicon, corpus, attestations = split_datasets(dictionary)

        self._validate_schema("schemas/lexicon.schema.json", lexicon)
        self._validate_schema("schemas/corpus.schema.json", corpus)
        self._validate_schema("schemas/attestations.schema.json", attestations)

        lexicon_sense_ids = {
            sense["sense_id"]
            for entry in lexicon
            for sense in entry.get("senses", [])
        }
        corpus_ids = {row["corpus_id"] for row in corpus}
        for row in attestations:
            self.assertIn(row["sense_id"], lexicon_sense_ids)
            self.assertIn(row["corpus_id"], corpus_ids)


if __name__ == "__main__":
    unittest.main()
