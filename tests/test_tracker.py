import tempfile
from pathlib import Path

import pytest

from src.first_bot.tracker import get_unprocessed_files


@pytest.fixture
def tracker_env():
    with tempfile.TemporaryDirectory() as input_dir, tempfile.TemporaryDirectory() as output_dir:
        import src.first_bot.config as cfg
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
    (input_dir / "a.csv").touch()
    (input_dir / "b.xlsx").touch()
    pendientes = get_unprocessed_files()
    assert len(pendientes) == 2


def test_archivo_ya_procesado_se_omite(tracker_env):
    input_dir, output_dir = tracker_env
    (input_dir / "data.csv").touch()
    (input_dir / "other.xlsx").touch()
    (output_dir / "resultado_data.csv").touch()

    pendientes = get_unprocessed_files()
    assert len(pendientes) == 1
    assert pendientes[0].name == "other.xlsx"


def test_ignora_extensiones_no_soportadas(tracker_env):
    input_dir, _ = tracker_env
    (input_dir / "nota.txt").touch()
    (input_dir / "imagen.png").touch()
    (input_dir / "valido.csv").touch()

    pendientes = get_unprocessed_files()
    assert len(pendientes) == 1
    assert pendientes[0].name == "valido.csv"


def test_todos_procesados(tracker_env):
    input_dir, output_dir = tracker_env
    (input_dir / "a.csv").touch()
    (output_dir / "resultado_a.csv").touch()

    pendientes = get_unprocessed_files()
    assert pendientes == []
