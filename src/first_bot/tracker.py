from pathlib import Path

import first_bot.config as cfg

EXTENSIONES = {".xlsx", ".xls", ".csv"}


def get_unprocessed_files() -> list[Path]:
    input_files = sorted(
        p for p in cfg.INPUT_PATH.glob("*")
        if p.suffix.lower() in EXTENSIONES
    )
    output_names = {
        p.stem.replace("resultado_", "")
        for p in cfg.OUTPUT_PATH.glob("resultado_*.csv")
    }

    pendientes = [
        f for f in input_files
        if f.stem not in output_names
    ]
    return pendientes
