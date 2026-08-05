from pathlib import Path
from datetime import date
import tempfile

import pandas as pd
import pytest

from first_bot.config import INPUT_PATH


@pytest.fixture
def new_solicitud() -> Path:
    return Path(INPUT_PATH) / "new_solicitud.csv"


@pytest.fixture
def temp_input_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        old = Path(INPUT_PATH)
        import first_bot.config as cfg

        cfg.INPUT_PATH = Path(tmpdir)
        yield Path(tmpdir)
        cfg.INPUT_PATH = old


@pytest.fixture
def csv_valido(temp_input_dir):
    path = temp_input_dir / "valido.csv"
    df = pd.DataFrame(
        [
            {
                "First Name": "Juan",
                "Last Name": "Pérez",
                "Company Name": "TechCorp",
                "Role in Company": "Developer",
                "Address": "Calle 123",
                "Email": "juan@example.com",
                "Phone Number": "+1-555-1234",
                "tipo_solicitud": "soporte",
                "fecha": "2024-06-15",
                "prioridad": "alta",
                "identificador": "SOL-001",
                "descripcion": "Problema con el sistema",
                "estado": "pendiente",
            }
        ]
    )
    df.to_csv(path, index=False)
    return path


@pytest.fixture
def xlsx_valido(temp_input_dir):
    path = temp_input_dir / "valido.xlsx"
    df = pd.DataFrame(
        [
            {
                "First Name": "María",
                "Last Name": "López",
                "Company Name": "InnovaSoft",
                "Role in Company": "Analyst",
                "Address": "Av. 456",
                "Email": "maria@example.com",
                "Phone Number": "+1-555-5678",
                "tipo_solicitud": "consulta",
                "fecha": "2024-03-20",
                "prioridad": "media",
                "identificador": "SOL-002",
                "descripcion": "Consulta sobre factura",
                "estado": "en_proceso",
            }
        ]
    )
    df.to_excel(path, index=False, engine="openpyxl")
    return path


@pytest.fixture
def csv_con_errores(temp_input_dir):
    path = temp_input_dir / "errores.csv"
    df = pd.DataFrame(
        [
            {
                "First Name": "",
                "Last Name": "",
                "Company Name": "X",
                "Role in Company": "X",
                "Address": "X",
                "Email": "no-email",
                "Phone Number": "X",
                "tipo_solicitud": "soporte",
                "fecha": "no-fecha",
                "prioridad": "invalida",
                "identificador": "ERR-001",
                "descripcion": "X",
                "estado": "invalido",
            },
            {
                "First Name": "Ana",
                "Last Name": "García",
                "Company Name": "DataCorp",
                "Role in Company": "Manager",
                "Address": "Calle 5",
                "Email": "ana@example.com",
                "Phone Number": "+1-555-9999",
                "tipo_solicitud": "reclamo",
                "fecha": "2024-01-10",
                "prioridad": "alta",
                "identificador": "SOL-003",
                "descripcion": "Reclamo válido",
                "estado": "pendiente",
            },
        ]
    )
    df.to_csv(path, index=False)
    return path


@pytest.fixture
def persona_data():
    return {
        "first_name": "Juan",
        "last_name": "Pérez",
        "company_name": "TechCorp",
        "role_in_company": "Developer",
        "address": "Calle 123",
        "email": "juan@example.com",
        "phone_number": "+1-555-1234",
    }


@pytest.fixture
def solicitud_data(persona_data):
    from first_bot.models import Persona

    return {
        "persona": Persona(**persona_data),
        "tipo_solicitud": "soporte",
        "fecha": date(2024, 6, 15),
        "prioridad": "alta",
        "identificador": "SOL-001",
        "descripcion": "Problema con el sistema",
        "estado": "pendiente",
    }
