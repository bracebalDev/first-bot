"""Genera 20 filas de prueba en INPUT_PATH como .xlsx y .csv."""

import os
import random
import sys
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from first_bot.config import INPUT_PATH
from first_bot.models import COLUMNAS_ARCHIVO

NOMBRES = [
    ("Carlos", "García"), ("María", "López"), ("Juan", "Martínez"),
    ("Ana", "Rodríguez"), ("Pedro", "Hernández"), ("Laura", "González"),
    ("Luis", "Pérez"), ("Sofía", "Sánchez"), ("Diego", "Ramírez"),
    ("Elena", "Torres"), ("Miguel", "Flores"), ("Carmen", "Rivera"),
    ("Javier", "Cruz"), ("Isabel", "Ortiz"), ("Andrés", "Morales"),
    ("Patricia", "Vargas"), ("Fernando", "Reyes"), ("Gabriela", "Jiménez"),
    ("Ricardo", "Ruiz"), ("Valentina", "Mendoza"),
]

COMPANIAS = [
    "TechCorp", "InnovaSoft", "DataSys", "CloudNet", "SecuWare",
    "GreenTech", "MediCare", "EduPro", "FinServ", "LogiTrans",
]

ROLES = ["Manager", "Developer", "Analyst", "Designer", "Director"]

TIPOS = ["soporte", "consulta", "reclamo", "sugerencia"]
PRIORIDADES = ["alta", "media", "baja"]
ESTADOS = ["pendiente", "en_proceso", "completada"]


def generar_datos(n: int = 20) -> list[dict]:
    random.seed(42)
    filas = []
    for i in range(n):
        nombre, apellido = random.choice(NOMBRES)
        filas.append({
            "First Name": nombre,
            "Last Name": apellido,
            "Company Name": random.choice(COMPANIAS),
            "Role in Company": random.choice(ROLES),
            "Address": f"Calle {random.randint(1,200)}, Ciudad",
            "Email": f"{nombre.lower()}.{apellido.lower()}{i}@example.com",
            "Phone Number": f"+1-555-{random.randint(1000,9999)}",
            "tipo_solicitud": random.choice(TIPOS),
            "fecha": date(2024, 1, 1 + i % 360).strftime("%Y-%m-%d"),
            "prioridad": random.choice(PRIORIDADES),
            "identificador": f"SOL-{2024000 + i}",
            "descripcion": f"Descripción de la solicitud {i + 1}",
            "estado": random.choice(ESTADOS),
        })
    return filas


def main():
    INPUT_PATH.mkdir(parents=True, exist_ok=True)

    datos = generar_datos(20)
    df = pd.DataFrame(datos)

    xlsx_path = INPUT_PATH / "solicitudes_prueba.xlsx"
    csv_path = INPUT_PATH / "solicitudes_prueba.csv"

    df.to_excel(xlsx_path, index=False, engine="openpyxl")
    df.to_csv(csv_path, index=False)

    print(f"Generados 20 registros en:")
    print(f"  {xlsx_path}")
    print(f"  {csv_path}")


if __name__ == "__main__":
    main()
