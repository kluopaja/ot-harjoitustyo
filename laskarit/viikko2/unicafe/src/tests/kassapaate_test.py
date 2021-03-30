import unittest
from kassapaate import Kassapaate
from maksukortti import Maksukortti
class TestKassapaate(unittest.TestCase):
    def setUp(self):
        self.kassapaate = Kassapaate()


    def test_kassapaate_luodaan_oikein(self):
        self.assertEqual(self.kassapaate.kassassa_rahaa, 1000)
        self.assertEqual(self.kassapaate.edulliset, 0)
        self.assertEqual(self.kassapaate.maukkaat, 0)

    def test_syo_edullisesti_kateisella_palauttaa_oikean_maaran_rahaa(self):
        self.assertAlmostEqual(self.kassapaate.syo_edullisesti_kateisella(3), 0.6)

    def test_syo_edullisesti_kateisella_paivittaa_kassaa_oikein(self):
        self.kassapaate.syo_edullisesti_kateisella(3)
        self.assertAlmostEqual(self.kassapaate.kassassa_rahaa, 1002.4)
        self.assertEqual(self.kassapaate.edulliset, 1)
        self.assertEqual(self.kassapaate.maukkaat, 0)

    def test_syo_edullisesti_kateisella_liian_vahan_rahaa_ei_muuta_kassaa(self):
        self.kassapaate.syo_edullisesti_kateisella(1)
        self.assertEqual(self.kassapaate.kassassa_rahaa, 1000)
        self.assertEqual(self.kassapaate.edulliset, 0)
        self.assertEqual(self.kassapaate.maukkaat, 0)

    def test_syo_edullisesti_liian_vahan_rahaa_palauttaa_kaiken_rahan(self):
        self.assertEqual(self.kassapaate.syo_edullisesti_kateisella(1), 1)

    def test_syo_maukkaasti_palauttaa_oikean_maaran_rahaa(self):
        self.assertEqual(self.kassapaate.syo_maukkaasti_kateisella(5), 1)

    def test_syo_maukkaasti_paivittaa_kassaa_oikein(self):
        self.kassapaate.syo_maukkaasti_kateisella(5)
        self.assertEqual(self.kassapaate.kassassa_rahaa, 1004)
        self.assertEqual(self.kassapaate.edulliset, 0)
        self.assertEqual(self.kassapaate.maukkaat, 1)

    def test_syo_maukkaasti_kateisella_liian_vahan_rahaa_ei_muuta_kassaa(self):
        self.kassapaate.syo_maukkaasti_kateisella(3.3)
        self.assertEqual(self.kassapaate.kassassa_rahaa, 1000)
        self.assertEqual(self.kassapaate.edulliset, 0)
        self.assertEqual(self.kassapaate.maukkaat, 0)

    def test_syo_maukkaasti_kateisella_liian_vahan_rahaa_palauttaa_kaiken_rahan(self):
        self.assertAlmostEqual(self.kassapaate.syo_maukkaasti_kateisella(1.2), 1.2)


    def test_syo_edullisesti_kortilla_palauttaa_oikein_onnistuessa(self):
        self.assertEqual(self.kassapaate.syo_edullisesti_kortilla(Maksukortti(10)), True)

    def test_syo_edullisesti_kortilla_muuttaa_kortin_arvoa_onnistuessa(self):
        maksukortti = Maksukortti(10)
        self.kassapaate.syo_edullisesti_kortilla(maksukortti)
        self.assertAlmostEqual(maksukortti.saldo, 7.6)

    def test_syo_edullisesti_kortilla_ei_muuta_kassan_rahaa_onnistuessa(self):
        maksukortti = Maksukortti(10)
        self.kassapaate.syo_edullisesti_kortilla(maksukortti)
        self.assertEqual(self.kassapaate.kassassa_rahaa, 1000)

    def test_syo_edullisesti_kortilla_paivittaa_myytyja_annoksia_oikein_onnistuessa(self):
        maksukortti = Maksukortti(10)
        self.kassapaate.syo_edullisesti_kortilla(maksukortti)
        self.assertEqual(self.kassapaate.edulliset, 1)
        self.assertEqual(self.kassapaate.maukkaat, 0)


    def test_syo_edullisesti_kortilla_palauttaa_oikein_epaonnistuessa(self):
        self.assertEqual(self.kassapaate.syo_edullisesti_kortilla(Maksukortti(1)), False)

    def test_syo_edullisesti_kortilla_ei_muuta_kortin_saldoa_epaonnistuessa(self):
        maksukortti = Maksukortti(1)
        self.kassapaate.syo_edullisesti_kortilla(maksukortti)
        self.assertEqual(maksukortti.saldo, 1)

    def test_syo_edullisesti_kortilla_ei_muuta_kassaa_epaonnistuessa(self):
        maksukortti = Maksukortti(1)
        self.kassapaate.syo_edullisesti_kortilla(maksukortti)
        self.assertEqual(self.kassapaate.kassassa_rahaa, 1000)
        self.assertEqual(self.kassapaate.edulliset, 0)
        self.assertEqual(self.kassapaate.maukkaat, 0)


    def test_syo_maukkaasti_kortilla_palauttaa_oikein_onnistuessa(self):
        self.assertEqual(self.kassapaate.syo_maukkaasti_kortilla(Maksukortti(10)), True)

    def test_syo_maukkaasti_kortilla_muuttaa_kortin_arvoa_onnistuessa(self):
        maksukortti = Maksukortti(10)
        self.kassapaate.syo_maukkaasti_kortilla(maksukortti)
        self.assertEqual(maksukortti.saldo, 6)

    def test_syo_maukkaasti_kortilla_ei_muuta_kassan_rahaa_onnistuessa(self):
        maksukortti = Maksukortti(10)
        self.kassapaate.syo_maukkaasti_kortilla(maksukortti)
        self.assertEqual(self.kassapaate.kassassa_rahaa, 1000)

    def test_syo_edullisesti_kortilla_paivittaa_myytyja_annoksia_oikein_onnistuessa(self):
        maksukortti = Maksukortti(10)
        self.kassapaate.syo_maukkaasti_kortilla(maksukortti)
        self.assertEqual(self.kassapaate.edulliset, 0)
        self.assertEqual(self.kassapaate.maukkaat, 1)

    def test_syo_maukkaasti_kortilla_palauttaa_oikein_epaonnistuessa(self):
        self.assertEqual(self.kassapaate.syo_maukkaasti_kortilla(Maksukortti(2)), False)

    def test_syo_maukkaasti_kortilla_ei_muuta_kortin_saldoa_epaonnistuessa(self):
        maksukortti = Maksukortti(1)
        self.kassapaate.syo_maukkaasti_kortilla(maksukortti)
        self.assertEqual(maksukortti.saldo, 1)

    def test_syo_maukkaasti_kortilla_ei_muuta_kassaa_epaonnistuessa(self):
        maksukortti = Maksukortti(1)
        self.kassapaate.syo_maukkaasti_kortilla(maksukortti)
        self.assertEqual(self.kassapaate.kassassa_rahaa, 1000)
        self.assertEqual(self.kassapaate.edulliset, 0)
        self.assertEqual(self.kassapaate.maukkaat, 0)

    def test_lataa_rahaa_kortilla_kasvattaa_kortin_saldoa_oikein(self):
        maksukortti = Maksukortti(10)
        self.kassapaate.lataa_rahaa_kortille(maksukortti, 2)
        self.assertEqual(maksukortti.saldo, 12)

    def test_lataa_rahaa_kortilla_lisaa_kassan_rahaa_oikein(self):
        maksukortti = Maksukortti(10)
        self.kassapaate.lataa_rahaa_kortille(maksukortti, 2)
        self.assertEqual(self.kassapaate.kassassa_rahaa, 1002)

    def test_lataa_rahaa_kortille_negatiivinen_lataussumma_ei_muuta_kassaa(self):
        maksukortti = Maksukortti(10)
        self.kassapaate.lataa_rahaa_kortille(maksukortti, -2)
        self.assertEqual(self.kassapaate.kassassa_rahaa, 1000)

    def test_lataa_rahaa_kortille_negatiivinen_lataussumma_ei_muuta_kortin_saldoa(self):
        maksukortti = Maksukortti(10)
        self.kassapaate.lataa_rahaa_kortille(maksukortti, -2)
        self.assertEqual(maksukortti.saldo, 10)
