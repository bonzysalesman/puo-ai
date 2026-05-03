import unittest
from pipeline.warden.agreement import AgreementEngine


class TestAgreementEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = AgreementEngine(db_path='data/pems_core.db')

    def test_possessive_correction(self):
        self.assertEqual(self.engine.apply_possessive_agreement('Sefate oa'), 'Sefate sa')

    def test_preserve_correct(self):
        self.assertEqual(self.engine.apply_possessive_agreement('Sefate sa'), 'Sefate sa')

    def test_sentence_context(self):
        self.assertEqual(self.engine.apply_possessive_agreement('Sefate oa me'), 'Sefate sa me')

    def test_class7_adj_correction(self):
        original = 'Sefate o motle'
        expected = 'Sefate se setle'
        self.assertEqual(self.engine.apply_all_agreement(original), expected)

    def test_class1_adj_correction(self):
        original = 'Motho se setle'
        expected = 'Motho o motle'
        self.assertEqual(self.engine.apply_all_agreement(original), expected)

    def test_adj_insertion(self):
        original = 'Sefate tle'
        expected = 'Sefate se setle'
        self.assertEqual(self.engine.apply_all_agreement(original), expected)

    def test_nasal_flag_awareness(self):
        original = 'Ntja o motle'
        expected = 'Ntja e ntle'
        self.assertEqual(self.engine.apply_all_agreement(original), expected)

    def test_possessive_and_adj_chain(self):
        original = 'Sefate oa me o motle'
        expected = 'Sefate sa me se setle'
        self.assertEqual(self.engine.apply_all_agreement(original), expected)


if __name__ == '__main__':
    unittest.main()
