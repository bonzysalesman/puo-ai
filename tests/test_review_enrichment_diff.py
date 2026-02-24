import unittest

from review_enrichment_diff import render_report, summarize_changes


class ReviewEnrichmentDiffTests(unittest.TestCase):
    def test_summarize_changes_detects_usage_example_updates(self):
        base = [
            {
                "entry_id": "entry_1",
                "headword_english": "Light",
                "senses": [
                    {
                        "sense_id": "light_01",
                        "definition_en": "illumination",
                        "usage_example": {
                            "sesotho": "old",
                            "english": "old",
                            "source": "Old Source",
                        },
                    }
                ],
            }
        ]
        candidate = [
            {
                "entry_id": "entry_1",
                "headword_english": "Light",
                "senses": [
                    {
                        "sense_id": "light_01",
                        "definition_en": "illumination",
                        "usage_example": {
                            "sesotho": "new",
                            "english": "new",
                            "source": "New Source",
                        },
                    }
                ],
            }
        ]

        summary = summarize_changes(base, candidate)
        self.assertEqual(len(summary["changed"]), 1)
        self.assertEqual(len(summary["added"]), 0)
        self.assertEqual(len(summary["removed"]), 0)

    def test_render_report_is_deterministic_and_contains_counts(self):
        summary = {
            "changed": [
                (
                    ("entry_2", "sense_b"),
                    {"usage_example": {"source": "S1"}},
                    {"headword_english": "B", "usage_example": {"source": "S2"}},
                ),
                (
                    ("entry_1", "sense_a"),
                    {"usage_example": {"source": "S3"}},
                    {"headword_english": "A", "usage_example": {"source": "S4"}},
                ),
            ],
            "added": [],
            "removed": [],
        }
        report = render_report(summary, "dictionary.json", "dictionary.enriched.json")
        self.assertIn("Changed usage examples: 2", report)
        self.assertIn("`entry_2` / `sense_b`", report)
        self.assertIn("`entry_1` / `sense_a`", report)


if __name__ == "__main__":
    unittest.main()
