from pathlib import Path
from loguru import logger

import first_bot.config as cfg
from first_bot.models import ProcessableInputFile, ProcessableOutputFile

EXTENSIONES = {".csv", ".xlsx"}


def get_unprocessed_files(
    input_path: Path | None = None,
    output_path: Path | None = None,
) -> list[ProcessableInputFile]:
    """Obtiene los archivos pendientes de procesar aplicando diferencia de conjuntos.
    
    Pasos:
    1. Recorrer recursivamente el directorio de entrada y crear objetos `ProcessableInputFile`.
    2. Recorrer recursivamente el directorio de salida y crear objetos `ProcessableOutputFile`.
    3. Obtener los pendientes como `inputs - outputs`.
    
    Solo se consideran las extensiones '.csv' y '.xlsx'.
    
    Returns:
        list[ProcessableInputFile]: Lista ordenada de archivos de entrada pendientes.
    """
    in_dir = (input_path or cfg.INPUT_PATH).resolve()
    out_dir = (output_path or cfg.OUTPUT_PATH).resolve()

    inputs: set[ProcessableInputFile] = set()
    outputs: set[ProcessableOutputFile] = set()

    if in_dir.exists() and in_dir.is_dir():
        for p in in_dir.rglob("*"):
            if p.is_file() and p.suffix.lower() in EXTENSIONES:
                try:
                    inputs.add(ProcessableInputFile.from_path(p, in_dir))
                except ValueError as e:
                    logger.warning(f"Omitiendo archivo de entrada con estructura inválida: {p} — {e}")

    if out_dir.exists() and out_dir.is_dir():
        for p in out_dir.rglob("*"):
            if p.is_file() and p.suffix.lower() in EXTENSIONES:
                try:
                    outputs.add(ProcessableOutputFile.from_path(p, out_dir))
                except ValueError as e:
                    logger.warning(f"Omitiendo archivo de salida con estructura inválida: {p} — {e}")

    # Diferencia de conjuntos: inputs - outputs
    pendientes_set = inputs - outputs

    # Retornar como lista ordenada cronológicamente y por ruta relativa
    return sorted(list(pendientes_set), key=lambda f: (f.date, f.path_dir))
