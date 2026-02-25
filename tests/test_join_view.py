import unittest

from join_view import join_view


class JoinViewTests(unittest.TestCase):
    def test_join_adds_usage_example_for_linked_sense(self):
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
        corpus = [
            {
                "corpus_id": "c1",
                "source": "JW Bible - Genesis 1",
                "ref": "v1001003",
                "sesotho_text": "Leseli le be teng.",
                "english_text": "Let there be light.",
            }
        ]
        attestations = [
            {"attestation_id": "a1", "sense_id": "s1", "corpus_id": "c1", "source_raw": "", "score": 0.9, "method": "x", "match_terms": ["leseli"]}
        ]

        joined = join_view(lexicon, corpus, attestations)
        usage = joined[0]["senses"][0]["usage_example"]
        self.assertEqual(usage["sesotho"], "Leseli le be teng.")
        self.assertEqual(usage["english"], "Let there be light.")
        self.assertEqual(usage["source"], "JW Bible - Genesis 1 (Verse v1001003)")

    def test_join_ignores_attestations_with_missing_corpus_reference(self):
        lexicon = [
            {
                "entry_id": "e1",
                "headword_english": "Light",
                "pos": [],
                "headword_sesotho": [],
                "syllables": [],
                "morphology": {"root": "", "derivation": "", "noun_class": ""},
                "thesaurus": {"synonyms_en": [], "antonyms_en": [], "synonyms_st": [], "antonyms_st": []},
                "senses": [{"sense_id": "s1", "definition_en": "", "sesotho_term": []}],
            }
        ]
        joined = join_view(
            lexicon,
            corpus=[],
            attestations=[{"attestation_id": "a1", "sense_id": "s1", "corpus_id": "missing", "source_raw": "", "score": None, "method": "x", "match_terms": []}],
        )
        self.assertNotIn("usage_example", joined[0]["senses"][0])

    def test_join_prefers_highest_score_when_multiple_attestations_exist(self):
        lexicon = [
            {
                "entry_id": "e1",
                "headword_english": "Light",
                "pos": [],
                "headword_sesotho": [],
                "syllables": [],
                "morphology": {"root": "", "derivation": "", "noun_class": ""},
                "thesaurus": {"synonyms_en": [], "antonyms_en": [], "synonyms_st": [], "antonyms_st": []},
                "senses": [{"sense_id": "s1", "definition_en": "", "sesotho_term": []}],
            }
        ]
        corpus = [
            {"corpus_id": "c1", "source": "A", "ref": "1", "sesotho_text": "x", "english_text": "low"},
            {"corpus_id": "c2", "source": "A", "ref": "2", "sesotho_text": "x", "english_text": "high"},
        ]
        attestations = [
            {"attestation_id": "a1", "sense_id": "s1", "corpus_id": "c1", "source_raw": "", "score": 0.2, "method": "x", "match_terms": []},
            {"attestation_id": "a2", "sense_id": "s1", "corpus_id": "c2", "source_raw": "", "score": 0.8, "method": "x", "match_terms": []},
        ]
        joined = join_view(lexicon, corpus, attestations)
        self.assertEqual(joined[0]["senses"][0]["usage_example"]["english"], "high")


if __name__ == "__main__":
    unittest.main()
