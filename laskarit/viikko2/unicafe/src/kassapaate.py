class Kassapaate:
    def __init__(self):
        self.kassassa_rahaa = 1000
        self.edulliset = 0
        self.maukkaat = 0

    def syo_edullisesti_kateisella(self, maksu):
        if maksu >= 2.4:
            self.kassassa_rahaa = self.kassassa_rahaa + 2.4
            self.edulliset += 1
            return maksu - 2.4
        else:
            return maksu

    def syo_maukkaasti_kateisella(self, maksu):
        if maksu >= 4:
            self.kassassa_rahaa = self.kassassa_rahaa + 4
            self.maukkaat += 1
            return maksu - 4
        else:
            return maksu

    def syo_edullisesti_kortilla(self, kortti):
        if kortti.saldo >= 2.4:
            kortti.ota_rahaa(2.4)
            self.edulliset += 1
            return True
        else:
            return False

    def syo_maukkaasti_kortilla(self, kortti):
        if kortti.saldo >= 4:
            kortti.ota_rahaa(4)
            self.maukkaat += 1
            return True
        else:
            return False

    def lataa_rahaa_kortille(self, kortti, summa):
        if summa >= 0:
            kortti.lataa_rahaa(summa)
            self.kassassa_rahaa += summa
        else:
            return
