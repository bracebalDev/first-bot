import tempfile
from pathlib import Path

import pytest

from first_bot.models import ProcessableInputFile
from first_bot.tracker import get_unprocessed_files


@pytest.fixture
def tracker_env():
    with tempfile.TemporaryDirectory() as input_dir, tempfile.TemporaryDirectory() as output_dir:
        import first_bot.config as cfg
        old_input, old_output = cfg.INPUT_PATH, cfg.OUTPUT_PATH
        cfg.INPUT_PATH = Path(input_dir)
        cfg.OUTPUT_PATH = Path(output_dir)
        yield Path(input_dir), Path(output_dir)
        cfg.INPUT_PATH = old_input
        cfg.OUTPUT_PATH = old_output


def test_sin_archivos_input(tracker_env):
    input_dir, _ = tracker_env
    pendientes = get_unprocessed_files()
    assert pendientes == []


def test_archivos_pendientes_sin_output(tracker_env):
    input_dir, _ = tracker_env
    file_a = input_dir / "2028" / "01" / "15" / "a.csv"
    file_b = input_dir / "2028" / "01" / "16" / "b.xlsx"
    file_a.parent.mkdir(parents=True, exist_ok=True)
    file_b.parent.mkdir(parents=True, exist_ok=True)
    file_a.touch()
    file_b.touch()

    pendientes = get_unprocessed_files()
    assert len(pendientes) == 2
    assert isinstance(pendientes[0], ProcessableInputFile)
    assert [p.path_dir for p in pendientes] == ["2028/01/15/a.csv", "2028/01/16/b.xlsx"]


def test_archivo_ya_procesado_se_omite(tracker_env):
    input_dir, output_dir = tracker_env
    in_data = input_dir / "2028" / "01" / "15" / "data.csv"
    in_other = input_dir / "2028" / "01" / "15" / "other.xlsx"
    out_data = output_dir / "2028" / "01" / "15" / "data.csv"

    in_data.parent.mkdir(parents=True, exist_ok=True)
    in_other.parent.mkdir(parents=True, exist_ok=True)
    out_data.parent.mkdir(parents=True, exist_ok=True)

    in_data.touch()
    in_other.touch()
    out_data.touch()

    pendientes = get_unprocessed_files()
    assert len(pendientes) == 1
    assert pendientes[0].path_dir == "2028/01/15/other.xlsx"


def test_ignora_extensiones_no_soportadas(tracker_env):
    input_dir, _ = tracker_env
    base = input_dir / "2028" / "01" / "15"
    base.mkdir(parents=True, exist_ok=True)
    (base / "nota.txt").touch()
    (base / "imagen.png").touch()
    (base / "valido.csv").touch()

    pendientes = get_unprocessed_files()
    assert len(pendientes) == 1
    assert pendientes[0].path_dir == "2028/01/15/valido.csv"


def test_todos_procesados(tracker_env):
    input_dir, output_dir = tracker_env
    in_a = input_dir / "2028" / "01" / "15" / "a.csv"
    out_a = output_dir / "2028" / "01" / "15" / "a.csv"
    in_a.parent.mkdir(parents=True, exist_ok=True)
    out_a.parent.mkdir(parents=True, exist_ok=True)
    in_a.touch()
    out_a.touch()

    pendientes = get_unprocessed_files()
    assert pendientes == []


def test_ignora_archivos_sin_estructura_fecha(tracker_env):
    input_dir, _ = tracker_env
    (input_dir / "suelto.csv").touch()
    valid_file = input_dir / "2028" / "01" / "15" / "solicitudes.csv"
    valid_file.parent.mkdir(parents=True, exist_ok=True)
    valid_file.touch()

    pendientes = get_unprocessed_files()
    assert len(pendientes) == 1
    assert pendientes[0].path_dir == "2028/01/15/solicitudes.csv"


def test_ignora_archivos_output_con_estructura_invalida(tracker_env):
    input_dir, output_dir = tracker_env
    valid_file = input_dir / "2028" / "01" / "15" / "solicitudes.csv"
    valid_file.parent.mkdir(parents=True, exist_ok=True)
    valid_file.touch()

    # Output file suelto que no cumple estructura
    (output_dir / "suelto_out.csv").touch()

    pendientes = get_unprocessed_files()
    assert len(pendientes) == 1
    assert pendientes[0].path_dir == "2028/01/15/solicitudes.csv"
