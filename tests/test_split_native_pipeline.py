import json
import tempfile
import unittest
from pathlib import Path

from enricher import enrich_split_datasets
from inject_historical_entries import inject_staged_entries_split


class SplitNativePipelineTests(unittest.TestCase):
    def test_enrich_split_datasets_adds_corpus_and_attestation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            lexicon_path = tmp / "lexicon.json"
            corpus_path = tmp / "corpus.json"
            attestations_path = tmp / "attestations.json"
            st_path = tmp / "st.html"
            en_path = tmp / "en.html"

            lexicon = [
                {
                    "entry_id": "e1",
                    "headword_english": "Light",
                    "pos": ["noun"],
                    "headword_sesotho": [{"orthographic": "leseli", "tone_marked": "", "ipa": "", "tone_pattern": ""}],
                    "syllables": ["le-se-li"],
                    "morphology": {"root": "", "derivation": "", "noun_class": ""},
                    "thesaurus": {"synonyms_en": [], "antonyms_en": [], "synonyms_st": [], "antonyms_st": []},
                    "senses": [{"sense_id": "s1", "definition_en": "light", "sesotho_term": ["leseli"]}],
                }
            ]
            lexicon_path.write_text(json.dumps(lexicon), encoding="utf-8")
            corpus_path.write_text("[]", encoding="utf-8")
            attestations_path.write_text("[]", encoding="utf-8")
            st_path.write_text('<span class="verse" id="v1">Leseli le teng.</span>', encoding="utf-8")
            en_path.write_text('<span class="verse" id="v1">There is light.</span>', encoding="utf-8")

            count = enrich_split_datasets(
                lexicon_path=str(lexicon_path),
                corpus_path=str(corpus_path),
                attestations_path=str(attestations_path),
                st_file=str(st_path),
                en_file=str(en_path),
                source_label="Test Source",
            )
            self.assertEqual(count, 1)

            corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
            attestations = json.loads(attestations_path.read_text(encoding="utf-8"))
            self.assertEqual(len(corpus), 1)
            self.assertEqual(len(attestations), 1)
            self.assertEqual(attestations[0]["sense_id"], "s1")
            self.assertEqual(attestations[0]["corpus_id"], corpus[0]["corpus_id"])

    def test_inject_staged_entries_split_writes_split_files(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            lexicon_path = tmp / "lexicon.json"
            corpus_path = tmp / "corpus.json"
            attestations_path = tmp / "attestations.json"
            staged_path = tmp / "staged.json"

            lexicon_path.write_text("[]", encoding="utf-8")
            corpus_path.write_text("[]", encoding="utf-8")
            attestations_path.write_text("[]", encoding="utf-8")

            staged = [
                {
                    "headword_english": ["Away"],
                    "pos": ["adverb"],
                    "headword_sesotho": {"orthographic": "hole"},
                    "senses": [
                        {
                            "definition": "hole",
                            "usage_examples": [
                                {
                                    "sesotho": "Ba ile hole.",
                                    "english": "They went away.",
                                    "source": "JW Bible - Gen1 (Verse v1)",
                                }
                            ],
                        }
                    ],
                }
            ]
            staged_path.write_text(json.dumps(staged), encoding="utf-8")

            inject_staged_entries_split(
                lexicon_file=str(lexicon_path),
                corpus_file=str(corpus_path),
                attestations_file=str(attestations_path),
                staged_files=[str(staged_path)],
            )

            lexicon = json.loads(lexicon_path.read_text(encoding="utf-8"))
            corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
            attestations = json.loads(attestations_path.read_text(encoding="utf-8"))

            self.assertEqual(len(lexicon), 1)
            self.assertEqual(lexicon[0]["headword_english"], "Away")
            self.assertEqual(len(corpus), 1)
            self.assertEqual(len(attestations), 1)


if __name__ == "__main__":
    unittest.main()
