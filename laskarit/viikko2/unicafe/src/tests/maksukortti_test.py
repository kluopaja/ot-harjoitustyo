import unittest
from maksukortti import Maksukortti

class TestMaksukortti(unittest.TestCase):
    def setUp(self):
        self.maksukortti = Maksukortti(10)

    def test_luotu_kortti_on_olemassa(self):
        self.assertNotEqual(self.maksukortti, None)

    def test_kortin_saldo_alussa(self):
        self.assertEqual(self.maksukortti.saldo, 10)

    def test_rahan_lataaminen_kasvattaa_saldoa(self):
        self.maksukortti.lataa_rahaa(2)
        self.assertEqual(self.maksukortti.saldo, 12)

    def test_rahan_ottaminen_muuttaa_saldoa(self):
        self.maksukortti.ota_rahaa(2)
        self.assertEqual(self.maksukortti.saldo, 8)

    def test_kortin_saldo_ei_muutu_kun_yritetaan_ottaa_liikaa(self):
        self.maksukortti.ota_rahaa(12)
        self.assertEqual(self.maksukortti.saldo, 10)

    def test_ota_rahaa_palauttaa_oikein_kun_rahaa_tarpeeksi(self):
        self.assertTrue(self.maksukortti.ota_rahaa(2))

    def test_ota_rahaa_palauttaa_oikein_kun_rahaa_ei_ole_tarpeeksi(self):
        self.assertFalse(self.maksukortti.ota_rahaa(12))

    def test_kortin_arvon_tulostaminen(self):
        self.assertEqual(str(self.maksukortti), "saldo: 10")
