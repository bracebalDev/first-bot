"""Genera datos de prueba estructurados por fechas en INPUT_PATH como .xlsx y .csv."""

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


def generar_datos(n: int = 20, seed: int = 42) -> list[dict]:
    random.seed(seed)
    filas = []
    for i in range(n):
        nombre, apellido = random.choice(NOMBRES)
        filas.append({
            "First Name": nombre,
            "Last Name": apellido,
            "Company Name": random.choice(COMPANIAS),
            "Role in Company": random.choice(ROLES),
            "Address": f"Calle {random.randint(1, 200)}, Ciudad",
            "Email": f"{nombre.lower()}.{apellido.lower()}{i}@example.com",
            "Phone Number": f"+1-555-{random.randint(1000, 9999)}",
            "tipo_solicitud": random.choice(TIPOS),
            "fecha": date(2028, 1, 1 + i % 28).strftime("%Y-%m-%d"),
            "prioridad": random.choice(PRIORIDADES),
            "identificador": f"SOL-{2028000 + i}",
            "descripcion": f"Descripción de la solicitud {i + 1}",
            "estado": random.choice(ESTADOS),
        })
    return filas


def main():
    date_dir_1 = INPUT_PATH / "2028" / "01" / "15"
    date_dir_2 = INPUT_PATH / "2028" / "01" / "16"
    date_dir_1.mkdir(parents=True, exist_ok=True)
    date_dir_2.mkdir(parents=True, exist_ok=True)

    # Lote 1 (2028/01/15)
    datos_1 = generar_datos(10, seed=42)
    df_1 = pd.DataFrame(datos_1)
    csv_1 = date_dir_1 / "solicitudes_a.csv"
    xlsx_1 = date_dir_1 / "pedidos_b.xlsx"
    df_1.to_csv(csv_1, index=False)
    df_1.to_excel(xlsx_1, index=False, engine="openpyxl")

    # Lote 2 (2028/01/16)
    datos_2 = generar_datos(10, seed=99)
    df_2 = pd.DataFrame(datos_2)
    csv_2 = date_dir_2 / "reclamos_c.csv"
    df_2.to_csv(csv_2, index=False)

    print("Archivos de prueba generados en estructura jerárquica:")
    print(f"  - {csv_1}")
    print(f"  - {xlsx_1}")
    print(f"  - {csv_2}")


if __name__ == "__main__":
    main()
