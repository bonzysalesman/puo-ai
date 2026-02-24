import unittest

from extract_wordlist import extract_words, render_markdown


class ExtractWordlistTests(unittest.TestCase):
    def test_extract_words_deduplicates_and_prefers_headword_display(self):
        dictionary = [
            {
                "headword_english": "Away",
                "headword_sesotho": [{"orthographic": "hōle"}],
                "senses": [{"sesotho_term": ["hōle"]}],
                "thesaurus": {
                    "synonyms_en": ["away", "Distant"],
                    "antonyms_en": ["near"],
                    "synonyms_st": ["HŌLE", "kgakala"],
                    "antonyms_st": ["haufi"],
                },
            }
        ]

        english_words, sesotho_words = extract_words(dictionary)

        self.assertEqual(english_words, ["Away", "Distant", "near"])
        self.assertEqual(sesotho_words, ["haufi", "hōle", "kgakala"])

    def test_extract_words_keeps_diacritic_and_non_diacritic_variants(self):
        dictionary = [
            {
                "headword_english": "Example",
                "headword_sesotho": [{"orthographic": "hōle"}],
                "senses": [{"sesotho_term": ["hole"]}],
                "thesaurus": {},
            }
        ]

        _, sesotho_words = extract_words(dictionary)
        self.assertIn("hōle", sesotho_words)
        self.assertIn("hole", sesotho_words)
        self.assertEqual(len(sesotho_words), 2)

    def test_render_markdown_includes_counts_and_list_items(self):
        content = render_markdown(["Away", "Distant"], ["hōle"])
        self.assertIn("## English Words (2 unique)", content)
        self.assertIn("## Sesotho Words (1 unique)", content)
        self.assertIn("- Away", content)
        self.assertIn("- hōle", content)


if __name__ == "__main__":
    unittest.main()
