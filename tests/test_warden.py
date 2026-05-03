import unittest
from pipeline.warden.normalize_orthography import Warden

class TestWardenFirewall(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.warden = Warden(db_path='data/pems_core.db')

    def test_priority_1_collisions(self):
        self.assertEqual(self.warden.normalize('tjhuna'), 'chuna')

    def test_nasal_anchors(self):
        self.assertEqual(self.warden.normalize('nyenyane'), 'nyenyane')
        self.assertEqual(self.warden.normalize('ngaka'), 'ngaka')

    def test_glide_transformation(self):
        self.assertEqual(self.warden.normalize('moya'), 'moea')
        self.assertEqual(self.warden.normalize('wena'), 'oena')

    def test_aspirated_sibilants(self):
        self.assertEqual(self.warden.normalize('tshaba'), 'tšaba')
        self.assertEqual(self.warden.normalize('shapa'), 'šapa')

    def test_sa_g_shift(self):
        self.assertEqual(self.warden.normalize('gare'), 'hare')

if __name__ == '__main__':
    unittest.main()
