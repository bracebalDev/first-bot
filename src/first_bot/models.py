import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Literal, Self

from pydantic import BaseModel, EmailStr, field_validator


@dataclass(frozen=True, eq=False)
class ProcessableFile:
    """Clase base inmutable para archivos procesables en el bot RPA.
    
    Permite la comparación e igualdad basada exclusivamente en `path_dir`
    (ruta relativa dentro del directorio base), lo que habilita operaciones
    de conjuntos (e.g. inputs - outputs) entre diferentes tipos de archivos.
    """
    year: int
    month: int
    day: int
    date: date
    path_dir: str
    full_path: Path

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ProcessableFile):
            return self.path_dir == other.path_dir
        return False

    def __hash__(self) -> int:
        return hash(self.path_dir)

    @classmethod
    def from_path(cls, file_path: Path, base_dir: Path) -> Self:
        """Crea una instancia a partir de la ruta del archivo y el directorio base.
        
        Extrae año, mes, día y construye el objeto `date` correspondiente.
        La estructura esperada es `.../YYYY/MM/DD/archivo.ext`.
        """
        resolved_file = file_path.resolve()
        resolved_base = base_dir.resolve()
        rel = resolved_file.relative_to(resolved_base)
        path_dir = rel.as_posix()

        parts = rel.parts
        if len(parts) >= 4:
            try:
                year = int(parts[0])
                month = int(parts[1])
                day = int(parts[2])
                file_date = date(year, month, day)
            except ValueError as e:
                raise ValueError(
                    f"Componentes de fecha no válidos en la ruta '{path_dir}': {e}"
                ) from e
        else:
            match = re.search(r"(\d{4})[\\/](\d{1,2})[\\/](\d{1,2})", path_dir)
            if match:
                try:
                    year = int(match.group(1))
                    month = int(match.group(2))
                    day = int(match.group(3))
                    file_date = date(year, month, day)
                except ValueError as e:
                    raise ValueError(
                        f"Valores de fecha fuera de rango en la ruta '{path_dir}': {e}"
                    ) from e
            else:
                raise ValueError(
                    f"La ruta '{path_dir}' no cumple con el esquema jerárquico YYYY/MM/DD/archivo"
                )

        return cls(
            year=year,
            month=month,
            day=day,
            date=file_date,
            path_dir=path_dir,
            full_path=resolved_file,
        )


@dataclass(frozen=True, eq=False)
class ProcessableInputFile(ProcessableFile):
    """Representa un archivo de entrada a procesar por el bot."""
    pass


@dataclass(frozen=True, eq=False)
class ProcessableOutputFile(ProcessableFile):
    """Representa un archivo de salida ya generado/procesado por el bot."""
    pass


class Persona(BaseModel):
    """Datos personales mapeables al formulario web."""
    first_name: str
    last_name: str
    company_name: str
    role_in_company: str
    address: str
    email: EmailStr
    phone_number: str

    @field_validator("first_name", "last_name", "company_name", "role_in_company", "address", "phone_number")
    @classmethod
    def not_empty(cls, v: str) -> str:
        stripped = v.strip() if isinstance(v, str) else v
        if not stripped:
            raise ValueError("campo obligatorio vacío")
        return stripped


class Solicitud(BaseModel):
    """Solicitud completa: persona + datos de negocio."""
    persona: Persona
    tipo_solicitud: str
    fecha: date
    prioridad: Literal["alta", "media", "baja"]
    identificador: str
    descripcion: str
    estado: Literal["pendiente", "en_proceso", "completada"]

    @field_validator("tipo_solicitud", "identificador", "descripcion")
    @classmethod
    def not_empty_str(cls, v: str) -> str:
        stripped = v.strip() if isinstance(v, str) else v
        if not stripped:
            raise ValueError("campo obligatorio vacío")
        return stripped

    @field_validator("fecha", mode="before")
    @classmethod
    def parse_fecha(cls, v: object) -> date:
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"):
                try:
                    from datetime import datetime
                    return datetime.strptime(v.strip(), fmt).date()
                except ValueError:
                    continue
            raise ValueError(f"formato de fecha no reconocido: {v}")
        if hasattr(v, "date"):
            return v.date()
        raise ValueError(f"tipo de fecha no soportado: {type(v)}")


COLUMNAS_ARCHIVO = [
    "First Name", "Last Name", "Company Name", "Role in Company",
    "Address", "Email", "Phone Number",
    "tipo_solicitud", "fecha", "prioridad",
    "identificador", "descripcion", "estado",
]


def row_to_solicitud(row: dict) -> Solicitud:
    persona = Persona(
        first_name=str(row.get("First Name", "")),
        last_name=str(row.get("Last Name", "")),
        company_name=str(row.get("Company Name", "")),
        role_in_company=str(row.get("Role in Company", "")),
        address=str(row.get("Address", "")),
        email=str(row.get("Email", "")),
        phone_number=str(row.get("Phone Number", "")),
    )
    return Solicitud(
        persona=persona,
        tipo_solicitud=str(row.get("tipo_solicitud", "")),
        fecha=row.get("fecha", ""),
        prioridad=str(row.get("prioridad", "")),
        identificador=str(row.get("identificador", "")),
        descripcion=str(row.get("descripcion", "")),
        estado=str(row.get("estado", "")),
    )
