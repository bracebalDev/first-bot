import tempfile
from pathlib import Path
import shutil
from unittest.mock import patch

import pytest
import pandas as pd

from first_bot.orchestrator import Orchestrator
from first_bot.exceptions import FileReadError


@pytest.fixture
def orch_env():
    with tempfile.TemporaryDirectory() as input_dir, tempfile.TemporaryDirectory() as output_dir:
        import first_bot.config as cfg
        old_input, old_output = cfg.INPUT_PATH, cfg.OUTPUT_PATH
        cfg.INPUT_PATH = Path(input_dir)
        cfg.OUTPUT_PATH = Path(output_dir)
        yield Path(input_dir), Path(output_dir)
        cfg.INPUT_PATH = old_input
        cfg.OUTPUT_PATH = old_output


def test_orchestrator_sin_archivos(orch_env):
    orch = Orchestrator()
    orch.run()


def test_orchestrator_procesa_csv_valido(orch_env, csv_valido):
    input_dir, output_dir = orch_env
    dest_dir = input_dir / "2028" / "01" / "15"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / csv_valido.name
    shutil.copy(csv_valido, dest)

    orch = Orchestrator()
    orch.run()

    expected_output = output_dir / "2028" / "01" / "15" / csv_valido.name
    assert expected_output.exists()


def test_orchestrator_procesa_xlsx_valido(orch_env, xlsx_valido):
    input_dir, output_dir = orch_env
    dest_dir = input_dir / "2028" / "01" / "15"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / xlsx_valido.name
    shutil.copy(xlsx_valido, dest)

    orch = Orchestrator()
    orch.run()

    expected_output = output_dir / "2028" / "01" / "15" / xlsx_valido.name
    assert expected_output.exists()


def test_orchestrator_no_reprocesa(orch_env, csv_valido):
    input_dir, output_dir = orch_env
    dest_dir = input_dir / "2028" / "01" / "15"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / csv_valido.name
    shutil.copy(csv_valido, dest)

    orch = Orchestrator()
    orch.run()

    expected_output = output_dir / "2028" / "01" / "15" / csv_valido.name
    assert expected_output.exists()
    mtime_before = expected_output.stat().st_mtime

    # Segunda ejecución: no debe reescribir ni reprocesar
    orch.run()
    mtime_after = expected_output.stat().st_mtime
    assert mtime_after == mtime_before


def test_orchestrator_maneja_error_en_archivo(orch_env, csv_valido):
    input_dir, output_dir = orch_env
    dest_dir = input_dir / "2028" / "01" / "15"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / csv_valido.name
    shutil.copy(csv_valido, dest)

    orch = Orchestrator()
    with patch("first_bot.orchestrator.reader_factory", side_effect=FileReadError("Corrupto")):
        orch.run()
    # No debería explotar ni abortar el proceso


def test_orchestrator_procesa_con_duplicados_y_errores(orch_env, csv_con_errores):
    input_dir, output_dir = orch_env
    dest_dir = input_dir / "2028" / "01" / "15"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / csv_con_errores.name
    shutil.copy(csv_con_errores, dest)

    orch = Orchestrator()
    orch.run()

    expected_output = output_dir / "2028" / "01" / "15" / csv_con_errores.name
    assert expected_output.exists()
