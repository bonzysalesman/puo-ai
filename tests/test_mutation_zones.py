import unittest
import io
import sys
from pipeline.warden.agreement import AgreementEngine


class TestMutationZones(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = AgreementEngine(db_path='data/pems_core.db')

    def test_mutation_zone_flag_nasal_root(self):
        """Verify that nasal-context noun + nasal-sensitive root triggers mutation zone flag."""
        # Ntja (Class 9, nasal_context=1) + e + fubelu (nasal_sensitive=1)
        # Should flag a mutation zone and apply transformation (f -> kh)
        self.engine.mutation_zones = []  # reset
        original = 'Ntja o fubelu'
        expected = 'Ntja e nkhubelu'
        
        # Capture stdout to check for log
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        result = self.engine.apply_all_agreement(original)
        
        sys.stdout = sys.__stdout__
        
        # Check result is correct
        self.assertEqual(result, expected)
        # Check mutation zone was recorded
        self.assertTrue(len(self.engine.mutation_zones) > 0)
        self.assertEqual(self.engine.mutation_zones[0]['root'], 'fubelu')
        self.assertEqual(self.engine.mutation_zones[0]['class_id'], 9)

    def test_mutation_zone_nasal_sensitive_root_be(self):
        """Verify 'be' root triggers mutation zone for Class 9."""
        self.engine.mutation_zones = []
        original = 'Ntja o be'
        expected = 'Ntja e nmpe'
        
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        result = self.engine.apply_all_agreement(original)
        
        sys.stdout = sys.__stdout__
        
        self.assertEqual(result, expected)
        self.assertTrue(len(self.engine.mutation_zones) > 0)
        self.assertEqual(self.engine.mutation_zones[0]['root'], 'be')

    def test_no_mutation_zone_non_nasal_root(self):
        """Verify non-nasal-sensitive roots don't trigger mutation zones."""
        self.engine.mutation_zones = []
        original = 'Ntja o tle'
        expected = 'Ntja e ntle'
        
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        result = self.engine.apply_all_agreement(original)
        
        sys.stdout = sys.__stdout__
        
        self.assertEqual(result, expected)
        # tle is not nasal-sensitive, so no mutation zone
        self.assertEqual(len(self.engine.mutation_zones), 0)

    def test_mutation_zone_raro_root(self):
        """Verify 'raro' (nasal-sensitive) triggers mutation zone."""
        self.engine.mutation_zones = []
        original = 'Ntja o raro'
        expected = 'Ntja e ntharo'
        
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        result = self.engine.apply_all_agreement(original)
        
        sys.stdout = sys.__stdout__
        
        self.assertEqual(result, expected)
        self.assertTrue(len(self.engine.mutation_zones) > 0)
        self.assertEqual(self.engine.mutation_zones[0]['root'], 'raro')

    def test_red_dog_mutation_fubelu_to_khubelu(self):
        """Red Dog Test: Ntja o fubelu -> Ntja e khubelu (nasal mutation applied)."""
        self.engine.mutation_zones = []
        original = 'Ntja o fubelu'
        # Expected: nasal prefix 'n-' + mutated root 'khubelu' -> 'nkhubelu'
        # And the relative particle becomes 'e'
        expected = 'Ntja e nkhubelu'
        
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        result = self.engine.apply_all_agreement(original)
        
        sys.stdout = sys.__stdout__
        
        self.assertEqual(result, expected)
        # Verify mutation zone was recorded
        self.assertTrue(len(self.engine.mutation_zones) > 0)
        self.assertEqual(self.engine.mutation_zones[0]['root'], 'fubelu')

    def test_red_dog_mutation_be_to_mpe(self):
        """Red Dog Test: Ntja o be -> Ntja e nmpe (be mutates to mpe)."""
        self.engine.mutation_zones = []
        original = 'Ntja o be'
        expected = 'Ntja e nmpe'
        
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        result = self.engine.apply_all_agreement(original)
        
        sys.stdout = sys.__stdout__
        
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
