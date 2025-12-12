import pandas as pd
from werkzeug.datastructures import FileStorage


class CsvService:
    @staticmethod
    def read_csv_with_encoding(file: FileStorage) -> pd.DataFrame:
        """
        Próbuje odczytać plik CSV używając różnych standardów kodowania
        (utf-8, cp1250 dla polskich Windowsów, iso-8859-2).
        """
        encodings = ['utf-8', 'cp1250', 'iso-8859-2']

        # Kopia strumienia, żeby móc go przewijać
        file_content = file.read()

        for encoding in encodings:
            try:
                from io import BytesIO
                file.seek(0)
                # Używamy BytesIO, żeby pandas mógł czytać z pamięci
                return pd.read_csv(BytesIO(file_content), header=0, encoding=encoding)
            except (UnicodeDecodeError, UnicodeError):
                continue
            except Exception:
                break

        # Ostatnia deska ratunku - domyślne ustawienia
        file.seek(0)
        return pd.read_csv(file, header=0)