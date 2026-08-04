from pathlib import Path
from typing import Union

import first_bot.config as cfg


def output_filename(input_path: Union[str, Path]) -> Path:
    path = Path(input_path)
    return cfg.OUTPUT_PATH / f"resultado_{path.stem}.csv"
