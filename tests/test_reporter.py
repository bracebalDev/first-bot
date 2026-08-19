from datetime import date
from pathlib import Path
import pandas as pd

from first_bot.models import Persona, ProcessableInputFile, Solicitud
from first_bot.reporter import guardar_resultados, resumen_archivo, resumen_global, setup_logging


def test_guardar_resultados_csv_y_xlsx(tmp_path):
    p = Persona(
        first_name="Juan",
        last_name="Perez",
        company_name="Corp",
        role_in_company="Dev",
        address="Calle 1",
        email="juan@test.com",
        phone_number="123",
    )
    s = Solicitud(
        persona=p,
        tipo_solicitud="soporte",
        fecha=date(2028, 1, 15),
        prioridad="alta",
        identificador="SOL-001",
        descripcion="Desc",
        estado="pendiente",
    )

    inp_csv = ProcessableInputFile(
        year=2028,
        month=1,
        day=15,
        date=date(2028, 1, 15),
        path_dir="2028/01/15/test.csv",
        full_path=tmp_path / "input/2028/01/15/test.csv",
    )
    inp_xlsx = ProcessableInputFile(
        year=2028,
        month=1,
        day=15,
        date=date(2028, 1, 15),
        path_dir="2028/01/15/test.xlsx",
        full_path=tmp_path / "input/2028/01/15/test.xlsx",
    )

    duplicados = [{"identificador": "DUP-1", "email": "dup@test.com"}]
    errores = [{"fila": 2, "errores": ["email inválido"]}]
    resultados_submit = [{"identificador": "SOL-001", "resultado": "registrado", "error": None}]

    import first_bot.config as cfg
    old_out = cfg.OUTPUT_PATH
    cfg.OUTPUT_PATH = tmp_path / "output"
    try:
        guardar_resultados(inp_csv, [s], duplicados, errores, resultados_submit)
        out_csv_path = tmp_path / "output/2028/01/15/test.csv"
        assert out_csv_path.exists()
        df_csv = pd.read_csv(out_csv_path)
        assert len(df_csv) == 3

        guardar_resultados(inp_xlsx, [s], duplicados, errores, resultados_submit)
        out_xlsx_path = tmp_path / "output/2028/01/15/test.xlsx"
        assert out_xlsx_path.exists()
        df_xlsx = pd.read_excel(out_xlsx_path)
        assert len(df_xlsx) == 3
    finally:
        cfg.OUTPUT_PATH = old_out


def test_setup_logging_and_resumen(tmp_path):
    import first_bot.config as cfg
    old_log = cfg.LOG_DIR
    cfg.LOG_DIR = tmp_path / "logs"
    try:
        setup_logging()
        assert cfg.LOG_DIR.exists()
        resumen_archivo("test.csv", 10, 8, 1, 1, 8, 0)
        resumen_global(1, 1, 0)
    finally:
        cfg.LOG_DIR = old_log
