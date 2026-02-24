import json
import tempfile
import unittest
from pathlib import Path

from enricher import clean_text, contains_term, enrich_dictionary


class EnricherTests(unittest.TestCase):
    def test_clean_text_removes_markers_and_normalizes_spaces(self):
        raw = "1  Text + with * extra   spaces"
        self.assertEqual(clean_text(raw), "Text with extra spaces")

    def test_contains_term_avoids_partial_matches(self):
        self.assertFalse(contains_term("concatenate words", "cat"))
        self.assertTrue(contains_term("A cat sat here.", "cat"))

    def test_enrich_dictionary_matches_whole_term_and_writes_output(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            dict_path = tmp / "dictionary.json"
            st_path = tmp / "st.html"
            en_path = tmp / "en.html"
            out_path = tmp / "out.json"

            dictionary = [
                {
                    "entry_id": "entry_1",
                    "headword_english": "Cat",
                    "senses": [{"sense_id": "cat_01", "sesotho_term": ["cat"]}],
                }
            ]
            st_html = """
            <div>
              <span class="verse" id="v1">concatenate this value</span>
              <span class="verse" id="v2">A cat sat on the mat.</span>
            </div>
            """
            en_html = """
            <div>
              <span class="verse" id="v1">Ignore this verse.</span>
              <span class="verse" id="v2">A cat sat on the mat.</span>
            </div>
            """

            dict_path.write_text(json.dumps(dictionary), encoding="utf-8")
            st_path.write_text(st_html, encoding="utf-8")
            en_path.write_text(en_html, encoding="utf-8")

            count = enrich_dictionary(
                dict_path=str(dict_path),
                st_file=str(st_path),
                en_file=str(en_path),
                source_label="Test Source",
                output_path=str(out_path),
            )
            self.assertEqual(count, 1)

            out_data = json.loads(out_path.read_text(encoding="utf-8"))
            usage = out_data[0]["senses"][0]["usage_example"]
            self.assertEqual(usage["sesotho"], "A cat sat on the mat.")
            self.assertEqual(usage["english"], "A cat sat on the mat.")
            self.assertEqual(usage["source"], "Test Source (Verse v2)")

    def test_enrich_dictionary_prefers_best_ranked_candidate(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            dict_path = tmp / "dictionary.json"
            st_path = tmp / "st.html"
            en_path = tmp / "en.html"
            out_path = tmp / "out.json"

            dictionary = [
                {
                    "entry_id": "entry_1",
                    "headword_english": "Example",
                    "senses": [
                        {
                            "sense_id": "example_01",
                            "sesotho_term": ["leseli", "mohloli oa leseli"],
                        }
                    ],
                }
            ]
            st_html = """
            <div>
              <span class="verse" id="v1">Leseli le teng.</span>
              <span class="verse" id="v2">Mohloli oa leseli o moholo; leseli le teng.</span>
            </div>
            """
            en_html = """
            <div>
              <span class="verse" id="v1">There is light.</span>
              <span class="verse" id="v2">The light source is great; there is light.</span>
            </div>
            """

            dict_path.write_text(json.dumps(dictionary), encoding="utf-8")
            st_path.write_text(st_html, encoding="utf-8")
            en_path.write_text(en_html, encoding="utf-8")

            count = enrich_dictionary(
                dict_path=str(dict_path),
                st_file=str(st_path),
                en_file=str(en_path),
                output_path=str(out_path),
            )
            self.assertEqual(count, 1)

            out_data = json.loads(out_path.read_text(encoding="utf-8"))
            usage = out_data[0]["senses"][0]["usage_example"]
            self.assertIn("Mohloli oa leseli", usage["sesotho"])
            self.assertIn("(Verse v2)", usage["source"])

    def test_stop_terms_can_block_generic_match_terms(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            dict_path = tmp / "dictionary.json"
            st_path = tmp / "st.html"
            en_path = tmp / "en.html"

            dictionary = [
                {
                    "entry_id": "entry_1",
                    "headword_english": "Generic",
                    "senses": [{"sense_id": "generic_01", "sesotho_term": ["le"]}],
                }
            ]
            st_html = '<span class="verse" id="v1">Le motho o teng.</span>'
            en_html = '<span class="verse" id="v1">And a person exists.</span>'

            before = json.dumps(dictionary)
            dict_path.write_text(before, encoding="utf-8")
            st_path.write_text(st_html, encoding="utf-8")
            en_path.write_text(en_html, encoding="utf-8")

            count = enrich_dictionary(
                dict_path=str(dict_path),
                st_file=str(st_path),
                en_file=str(en_path),
                dry_run=True,
                stop_terms=["le"],
            )
            self.assertEqual(count, 0)
            self.assertEqual(dict_path.read_text(encoding="utf-8"), before)

    def test_weighted_scoring_can_prefer_shorter_verse(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            dict_path = tmp / "dictionary.json"
            st_path = tmp / "st.html"
            en_path = tmp / "en.html"
            out_path = tmp / "out.json"

            dictionary = [
                {
                    "entry_id": "entry_1",
                    "headword_english": "Light",
                    "senses": [{"sense_id": "light_01", "sesotho_term": ["leseli"]}],
                }
            ]
            st_html = """
            <div>
              <span class="verse" id="v1">Leseli le teng.</span>
              <span class="verse" id="v2">Leseli le teng lefatsheng lena lohle le leholo haholo.</span>
            </div>
            """
            en_html = """
            <div>
              <span class="verse" id="v1">There is light.</span>
              <span class="verse" id="v2">There is light in this entire very large world.</span>
            </div>
            """

            dict_path.write_text(json.dumps(dictionary), encoding="utf-8")
            st_path.write_text(st_html, encoding="utf-8")
            en_path.write_text(en_html, encoding="utf-8")

            count = enrich_dictionary(
                dict_path=str(dict_path),
                st_file=str(st_path),
                en_file=str(en_path),
                output_path=str(out_path),
                weight_term_count=1.0,
                weight_term_length=0.0,
                weight_verse_length_penalty=1.0,
            )
            self.assertEqual(count, 1)
            out_data = json.loads(out_path.read_text(encoding="utf-8"))
            usage = out_data[0]["senses"][0]["usage_example"]
            self.assertIn("(Verse v1)", usage["source"])

    def test_dry_run_does_not_modify_dictionary_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            dict_path = tmp / "dictionary.json"
            st_path = tmp / "st.html"
            en_path = tmp / "en.html"

            dictionary = [
                {
                    "entry_id": "entry_1",
                    "headword_english": "Light",
                    "senses": [{"sense_id": "light_01", "sesotho_term": ["leseli"]}],
                }
            ]
            st_html = '<span class="verse" id="v1">Leseli le teng.</span>'
            en_html = '<span class="verse" id="v1">There is light.</span>'

            before = json.dumps(dictionary)
            dict_path.write_text(before, encoding="utf-8")
            st_path.write_text(st_html, encoding="utf-8")
            en_path.write_text(en_html, encoding="utf-8")

            count = enrich_dictionary(
                dict_path=str(dict_path),
                st_file=str(st_path),
                en_file=str(en_path),
                dry_run=True,
            )
            self.assertEqual(count, 1)
            self.assertEqual(dict_path.read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
