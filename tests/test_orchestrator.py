import tempfile
from pathlib import Path

import pytest

from src.first_bot.orchestrator import Orchestrator


@pytest.fixture
def orch_env():
    with tempfile.TemporaryDirectory() as input_dir, tempfile.TemporaryDirectory() as output_dir:
        import src.first_bot.config as cfg
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
    import shutil
    input_dir, output_dir = orch_env
    dest = input_dir / csv_valido.name
    shutil.copy(csv_valido, dest)

    orch = Orchestrator()
    orch.run()

    output_files = list(output_dir.glob("resultado_*.csv"))
    assert len(output_files) == 1


def test_orchestrator_no_reprocesa(orch_env, csv_valido):
    import shutil
    input_dir, output_dir = orch_env
    dest = input_dir / csv_valido.name
    shutil.copy(csv_valido, dest)

    orch = Orchestrator()
    orch.run()

    output_count_before = len(list(output_dir.glob("resultado_*.csv")))

    orch.run()

    output_count_after = len(list(output_dir.glob("resultado_*.csv")))
    assert output_count_after == output_count_before
