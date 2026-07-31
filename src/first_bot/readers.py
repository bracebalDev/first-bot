from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

from src.first_bot.exceptions import FileReadError
from src.first_bot.models import COLUMNAS_ARCHIVO


class BaseReader(ABC):
    @abstractmethod
    def read(self, filepath: Path) -> pd.DataFrame:
        ...


class CsvReader(BaseReader):
    def read(self, filepath: Path) -> pd.DataFrame:
        try:
            df = pd.read_csv(filepath)
        except Exception as e:
            raise FileReadError(f"No se pudo leer el CSV: {filepath} — {e}") from e
        return self._normalizar(df)

    def _normalizar(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.rename(columns={
            col: col.strip()
            for col in df.columns
        })
        return df


class XlsxReader(BaseReader):
    def read(self, filepath: Path) -> pd.DataFrame:
        try:
            df = pd.read_excel(filepath, engine="openpyxl")
        except Exception as e:
            raise FileReadError(f"No se pudo leer el XLSX: {filepath} — {e}") from e
        return self._normalizar(df)

    def _normalizar(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.rename(columns={
            col: col.strip()
            for col in df.columns
        })
        return df


def reader_factory(extension: str) -> BaseReader:
    ext = extension.lower().lstrip(".")
    if ext == "csv":
        return CsvReader()
    if ext in ("xlsx", "xls"):
        return XlsxReader()
    raise FileReadError(f"Extensión no soportada: {extension}")
