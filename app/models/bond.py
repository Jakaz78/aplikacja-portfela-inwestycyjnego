class Bond:
    # Mapowanie nazw kolumn z CSV/DB na pola obiektu
    COLUMN_MAPPING = {
        'data_zakupu': ['Data_Zakupu', 'purchase_date'],
        'seria_obligacji': ['Seria_Obligacji', 'series'],
        'typ_obligacji': ['Typ_Obligacji', 'bond_type'],
        'wartosc_nominalna': ['Wartosc_Nominalna', 'nominal_value', 'quantity'],
        'cena_zakupu': ['Cena_Zakupu', 'purchase_price'],
        'data_emisji': ['Data_Emisji', 'emission_date'],
        'data_wykupu': ['Data_Wykupu', 'maturity_date'],
        'aktualna_wartosc': ['Aktualna_Wartosc', 'current_value'],
        'kod_ISIN': ['Kod_ISIN', 'isin'],
        'numer_transakcji': ['Numer_Transakcji', 'transaction_reference']
    }

    def __init__(self, data_zakupu, seria_obligacji, typ_obligacji, wartosc_nominalna,
                 cena_zakupu, data_emisji, data_wykupu, oprocentowanie,
                 aktualna_wartosc, kod_ISIN, numer_transakcji, id=None):
        self.id = id
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

    @classmethod
    def from_dataframe_row(cls, row):
        """Fabryka: tworzy obiekt Bond na podstawie wiersza DataFrame"""
        return cls(
            id=row.get('holding_id') if 'holding_id' in row else None,
            data_zakupu=cls._get_val(row, 'data_zakupu'),
            seria_obligacji=cls._get_val(row, 'seria_obligacji'),
            typ_obligacji=cls._get_val(row, 'typ_obligacji'),
            wartosc_nominalna=cls._get_val(row, 'wartosc_nominalna'),
            cena_zakupu=cls._get_val(row, 'cena_zakupu'),
            data_emisji=cls._get_val(row, 'data_emisji'),
            data_wykupu=cls._get_val(row, 'data_wykupu'),
            oprocentowanie=cls._format_coupon(row),
            aktualna_wartosc=cls._get_val(row, 'aktualna_wartosc'),
            kod_ISIN=cls._get_val(row, 'kod_ISIN'),
            numer_transakcji=cls._get_val(row, 'numer_transakcji'),
        )

    @classmethod
    def _get_val(cls, row, field_name):
        candidates = cls.COLUMN_MAPPING.get(field_name, [])
        for candidate in candidates:
            val = row.get(candidate)
            if val is not None and str(val) != "None" and str(val) != "":
                return val
        return ""

    @staticmethod
    def _format_coupon(row):
        text_coupon = row.get("Oprocentowanie")
        if text_coupon and str(text_coupon) not in ("", "None"):
            return text_coupon

        coupon_rate = row.get("coupon_rate")
        if coupon_rate is not None and str(coupon_rate) not in ("", "None"):
            try:
                return f"{round(float(coupon_rate) * 100, 2)}%"
            except (ValueError, TypeError):
                pass
        return ""

    def __repr__(self):
        return f"<Obligacja {self.seria_obligacji}>"