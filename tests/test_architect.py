import unittest
from pipeline.core.architect import MorphologicalArchitect


class TestMorphologicalArchitect(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.architect = MorphologicalArchitect(db_path='data/pems_core.db')

    def test_nasal_mutation_be_to_mpe(self):
        """Test nasal mutation: be -> mpe (Class 9)."""
        result = self.architect.mutate('be', context='nasal')
        self.assertEqual(result, 'mpe')

    def test_nasal_mutation_fubelu_to_khubelu(self):
        """Test nasal mutation: fubelu -> khubelu (Class 9)."""
        result = self.architect.mutate('fubelu', context='nasal')
        self.assertEqual(result, 'khubelu')

    def test_nasal_mutation_raro_to_tharo(self):
        """Test nasal mutation: raro -> tharo (Class 9)."""
        result = self.architect.mutate('raro', context='nasal')
        self.assertEqual(result, 'tharo')

    def test_nasal_mutation_haufi_to_khaufi(self):
        """Test nasal mutation: haufi -> khaufi (Class 9)."""
        result = self.architect.mutate('haufi', context='nasal')
        self.assertEqual(result, 'khaufi')

    def test_nasal_mutation_s_to_ts_setle(self):
        """Test nasal mutation: setle -> tšotle (sibilant mutation, Class 9)."""
        result = self.architect.mutate('setle', context='nasal')
        # s -> tš, so setle -> tšetle
        self.assertEqual(result, 'tšetle')

    def test_no_mutation_unknown_context(self):
        """Test that unknown context returns original root."""
        result = self.architect.mutate('be', context='unknown')
        self.assertEqual(result, 'be')

    def test_no_mutation_no_rule(self):
        """Test that roots without rules return unchanged."""
        result = self.architect.mutate('tle', context='nasal')
        # tle starts with 't', no nasal rule for 't'
        self.assertEqual(result, 'tle')

    def test_mutate_for_class_nasal_context(self):
        """Test class-based mutation for Class 9 (nasal_context=1)."""
        result = self.architect.mutate_for_class('be', class_id=9)
        self.assertEqual(result, 'mpe')

    def test_mutate_for_class_non_nasal_context(self):
        """Test class-based mutation for Class 1 (nasal_context=0)."""
        result = self.architect.mutate_for_class('be', class_id=1)
        # Class 1 has no nasal context, so no mutation
        self.assertEqual(result, 'be')

    def test_empty_root(self):
        """Test that empty root returns empty."""
        result = self.architect.mutate('', context='nasal')
        self.assertEqual(result, '')


if __name__ == '__main__':
    unittest.main()
