class Bond:
    def __init__(self, data_zakupu, seria_obligacji	, typ_obligacji, wartosc_nominalna, cena_zakupu, data_emisji,
                 data_wykupu, oprocentowanie, aktualna_wartosc, kod_ISIN, numer_transakcji ):

        self.data_zakupu = data_zakupu
        self.seria_obligacji = seria_obligacji
        self.typ_obligacji = typ_obligacji
        self.wartosc_nominalna = wartosc_nominalna
        self.cena_zakupu = cena_zakupu
        self.data_emisji = data_emisji
        self.data_wykupu = data_wykupu
        self.oprocentowanie = oprocentowanie
        self.aktualna_wartosc = aktualna_wartosc
        self.kod_ISIN = kod_ISIN
        self.numer_transakcji = numer_transakcji

    def __repr__(self):
        return f"<Obligacja {self.Seria_Obligacji}>"
