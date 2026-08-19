from datetime import date
from pathlib import Path

from first_bot.models import ProcessableInputFile
from first_bot.utils import output_filename
import first_bot.config as cfg


def test_output_filename_con_processable_file(tmp_path):
    inp = ProcessableInputFile(
        year=2028,
        month=1,
        day=15,
        date=date(2028, 1, 15),
        path_dir="2028/01/15/solicitudes.csv",
        full_path=tmp_path / "data/input/2028/01/15/solicitudes.csv",
    )
    out = output_filename(inp, base_output=tmp_path / "data/output")
    expected = (tmp_path / "data/output/2028/01/15/solicitudes.csv").resolve()
    assert out.resolve() == expected


def test_output_filename_con_path_dentro_de_input(tmp_path):
    input_base = (tmp_path / "input").resolve()
    output_base = (tmp_path / "output").resolve()
    old_in, old_out = cfg.INPUT_PATH, cfg.OUTPUT_PATH
    cfg.INPUT_PATH = input_base
    cfg.OUTPUT_PATH = output_base

    try:
        file_path = input_base / "2028" / "01" / "15" / "archivo.csv"
        out = output_filename(file_path)
        expected = output_base / "2028" / "01" / "15" / "archivo.csv"
        assert out.resolve() == expected.resolve()
    finally:
        cfg.INPUT_PATH = old_in
        cfg.OUTPUT_PATH = old_out


def test_output_filename_con_path_fuera_de_input(tmp_path):
    file_path = tmp_path / "otro_directorio" / "archivo.csv"
    out = output_filename(file_path, base_output=tmp_path / "output")
    expected = (tmp_path / "output" / "archivo.csv").resolve()
    assert out.resolve() == expected
