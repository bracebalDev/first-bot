from dataclasses import FrozenInstanceError
from datetime import date
from pathlib import Path

import pytest
from pydantic import ValidationError

from first_bot.models import (
    Persona,
    ProcessableFile,
    ProcessableInputFile,
    ProcessableOutputFile,
    Solicitud,
    row_to_solicitud,
)


class TestProcessableFiles:
    def test_instanciacion_directa(self):
        full_path = Path("/tmp/data/input/2028/01/15/solicitudes.csv")
        inp = ProcessableInputFile(
            year=2028,
            month=1,
            day=15,
            date=date(2028, 1, 15),
            path_dir="2028/01/15/solicitudes.csv",
            full_path=full_path,
        )
        assert inp.year == 2028
        assert inp.month == 1
        assert inp.day == 15
        assert inp.date == date(2028, 1, 15)
        assert inp.path_dir == "2028/01/15/solicitudes.csv"
        assert inp.full_path == full_path

    def test_igualdad_entre_input_y_output(self):
        inp = ProcessableInputFile(
            year=2028,
            month=1,
            day=15,
            date=date(2028, 1, 15),
            path_dir="2028/01/15/solicitudes_a.csv",
            full_path=Path("/abs/data/input/2028/01/15/solicitudes_a.csv"),
        )
        out = ProcessableOutputFile(
            year=2028,
            month=1,
            day=15,
            date=date(2028, 1, 15),
            path_dir="2028/01/15/solicitudes_a.csv",
            full_path=Path("/abs/data/output/2028/01/15/solicitudes_a.csv"),
        )
        # Deben ser iguales por compartir path_dir
        assert inp == out
        assert out == inp
        assert hash(inp) == hash(out)

    def test_desigualdad_con_distinto_path_dir(self):
        inp = ProcessableInputFile(
            year=2028,
            month=1,
            day=15,
            date=date(2028, 1, 15),
            path_dir="2028/01/15/solicitudes_a.csv",
            full_path=Path("/abs/data/input/2028/01/15/solicitudes_a.csv"),
        )
        out = ProcessableOutputFile(
            year=2028,
            month=1,
            day=16,
            date=date(2028, 1, 16),
            path_dir="2028/01/16/solicitudes_a.csv",
            full_path=Path("/abs/data/output/2028/01/16/solicitudes_a.csv"),
        )
        assert inp != out
        assert inp != "otro_tipo"

    def test_operacion_diferencia_de_conjuntos(self):
        inp1 = ProcessableInputFile(
            year=2028,
            month=1,
            day=15,
            date=date(2028, 1, 15),
            path_dir="2028/01/15/solicitudes_a.csv",
            full_path=Path("/abs/data/input/2028/01/15/solicitudes_a.csv"),
        )
        inp2 = ProcessableInputFile(
            year=2028,
            month=1,
            day=16,
            date=date(2028, 1, 16),
            path_dir="2028/01/16/reclamos_c.csv",
            full_path=Path("/abs/data/input/2028/01/16/reclamos_c.csv"),
        )
        out1 = ProcessableOutputFile(
            year=2028,
            month=1,
            day=15,
            date=date(2028, 1, 15),
            path_dir="2028/01/15/solicitudes_a.csv",
            full_path=Path("/abs/data/output/2028/01/15/solicitudes_a.csv"),
        )

        inputs = {inp1, inp2}
        outputs = {out1}
        pendientes = inputs - outputs

        assert pendientes == {inp2}
        assert inp1 not in pendientes

    def test_inmutabilidad_frozen(self):
        inp = ProcessableInputFile(
            year=2028,
            month=1,
            day=15,
            date=date(2028, 1, 15),
            path_dir="2028/01/15/solicitudes_a.csv",
            full_path=Path("/abs/data/input/2028/01/15/solicitudes_a.csv"),
        )
        with pytest.raises(FrozenInstanceError):
            inp.year = 2029

    def test_from_path_valido(self, tmp_path):
        base_dir = tmp_path / "data" / "input"
        file_path = base_dir / "2028" / "01" / "15" / "pedidos_b.xlsx"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()

        inp = ProcessableInputFile.from_path(file_path, base_dir)
        assert inp.year == 2028
        assert inp.month == 1
        assert inp.day == 15
        assert inp.date == date(2028, 1, 15)
        assert inp.path_dir == "2028/01/15/pedidos_b.xlsx"
        assert inp.full_path == file_path.resolve()

    def test_from_path_invalido_lanza_error(self, tmp_path):
        base_dir = tmp_path / "data" / "input"
        file_path = base_dir / "invalido" / "archivo.csv"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()

        with pytest.raises(ValueError, match="no cumple con el esquema jerárquico"):
            ProcessableInputFile.from_path(file_path, base_dir)

    def test_from_path_fecha_invalida_lanza_error(self, tmp_path):
        base_dir = tmp_path / "data" / "input"
        file_path = base_dir / "2028" / "02" / "31" / "archivo.csv"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()

        with pytest.raises(ValueError):
            ProcessableInputFile.from_path(file_path, base_dir)


class TestPersona:
    def test_persona_valida(self, persona_data):
        p = Persona(**persona_data)
        assert p.first_name == "Juan"
        assert p.email == "juan@example.com"

    def test_persona_email_invalido(self, persona_data):
        persona_data["email"] = "no-es-un-email"
        with pytest.raises(ValidationError):
            Persona(**persona_data)

    def test_persona_first_name_vacio(self, persona_data):
        persona_data["first_name"] = ""
        with pytest.raises(ValidationError):
            Persona(**persona_data)

    def test_persona_last_name_vacio(self, persona_data):
        persona_data["last_name"] = "   "
        with pytest.raises(ValidationError):
            Persona(**persona_data)

    def test_persona_campos_con_espacios(self, persona_data):
        persona_data["first_name"] = "  Juan  "
        p = Persona(**persona_data)
        assert p.first_name == "Juan"


class TestSolicitud:
    def test_solicitud_valida(self, solicitud_data):
        s = Solicitud(**solicitud_data)
        assert s.persona.email == "juan@example.com"
        assert s.prioridad == "alta"
        assert s.fecha == date(2024, 6, 15)

    def test_solicitud_prioridad_invalida(self, solicitud_data):
        solicitud_data["prioridad"] = "urgente"
        with pytest.raises(ValidationError):
            Solicitud(**solicitud_data)

    def test_solicitud_estado_invalido(self, solicitud_data):
        solicitud_data["estado"] = "cancelado"
        with pytest.raises(ValidationError):
            Solicitud(**solicitud_data)

    def test_solicitud_fecha_dmy(self, solicitud_data):
        solicitud_data["fecha"] = "15/06/2024"
        s = Solicitud(**solicitud_data)
        assert s.fecha == date(2024, 6, 15)

    def test_solicitud_fecha_mdy(self, solicitud_data):
        solicitud_data["fecha"] = "06/15/2024"
        s = Solicitud(**solicitud_data)
        assert s.fecha == date(2024, 6, 15)

    def test_solicitud_fecha_ymd_con_barra(self, solicitud_data):
        solicitud_data["fecha"] = "2024/06/15"
        s = Solicitud(**solicitud_data)
        assert s.fecha == date(2024, 6, 15)

    def test_solicitud_fecha_invalida(self, solicitud_data):
        solicitud_data["fecha"] = "ayer"
        with pytest.raises(ValidationError):
            Solicitud(**solicitud_data)

    def test_solicitud_identificador_vacio(self, solicitud_data):
        solicitud_data["identificador"] = ""
        with pytest.raises(ValidationError):
            Solicitud(**solicitud_data)


class TestRowToSolicitud:
    def test_fila_valida(self):
        row = {
            "First Name": "Ana",
            "Last Name": "García",
            "Company Name": "Corp",
            "Role in Company": "Dev",
            "Address": "Calle 1",
            "Email": "ana@test.com",
            "Phone Number": "123",
            "tipo_solicitud": "soporte",
            "fecha": "2024-01-01",
            "prioridad": "alta",
            "identificador": "SOL-1",
            "descripcion": "desc",
            "estado": "pendiente",
        }
        s = row_to_solicitud(row)
        assert s.persona.first_name == "Ana"
        assert s.tipo_solicitud == "soporte"

    def test_fila_email_invalido(self):
        row = {
            "First Name": "X",
            "Last Name": "Y",
            "Company Name": "Z",
            "Role in Company": "R",
            "Address": "A",
            "Email": "malo",
            "Phone Number": "1",
            "tipo_solicitud": "s",
            "fecha": "2024-01-01",
            "prioridad": "alta",
            "identificador": "ID",
            "descripcion": "D",
            "estado": "pendiente",
        }
        with pytest.raises(ValidationError):
            row_to_solicitud(row)
