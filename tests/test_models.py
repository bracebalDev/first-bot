from datetime import date

import pytest
from pydantic import ValidationError

from first_bot.models import Persona, Solicitud, row_to_solicitud


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
