import unittest
from pipeline.enrichment.processor import EnricherProcessor


class TestEnricherE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.enricher = EnricherProcessor(db_path='data/pems_core.db')

    def test_loanword_protection_with_agreement(self):
        original = 'Digital strategy ea me'
        expected = 'Digital strategy sa me'
        self.assertEqual(self.enricher.process(original), expected)

    def test_orthography_plus_agreement(self):
        original = 'tjhuna ya me oa sebetsa'
        expected = 'chuna ea me ea sebetsa'
        self.assertEqual(self.enricher.process(original), expected)


if __name__ == '__main__':
    unittest.main()
