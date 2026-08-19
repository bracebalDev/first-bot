from pathlib import Path
from typing import Union

import first_bot.config as cfg
from first_bot.models import ProcessableInputFile


def output_filename(
    input_file: Union[ProcessableInputFile, str, Path],
    base_output: Path | None = None,
) -> Path:
    """Genera la ruta de salida correspondiente manteniendo la misma ruta relativa y nombre que la entrada."""
    out_base = (base_output or cfg.OUTPUT_PATH).resolve()

    if isinstance(input_file, ProcessableInputFile):
        return out_base / Path(input_file.path_dir)

    path = Path(input_file)
    try:
        rel = path.resolve().relative_to(cfg.INPUT_PATH.resolve())
        return out_base / rel
    except (ValueError, Exception):
        return out_base / path.name
