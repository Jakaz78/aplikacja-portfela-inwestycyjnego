import pandas as pd
from werkzeug.datastructures import FileStorage


class CsvService:
    @staticmethod
    def read_csv_with_encoding(file: FileStorage) -> pd.DataFrame:
        """
        Odczytuje plik CSV przyjmując kodowanie UTF-8.
        """
        file.seek(0)
        return pd.read_csv(file, header=0, encoding='utf-8')