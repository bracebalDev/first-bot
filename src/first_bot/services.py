from pydantic import ValidationError

from src.first_bot.models import Solicitud, row_to_solicitud


def validate(df):
    validos: list[Solicitud] = []
    errores: list[dict] = []

    for idx, row in df.iterrows():
        try:
            solicitud = row_to_solicitud(row.to_dict())
            validos.append(solicitud)
        except ValidationError as e:
            errores.append({
                "fila": int(idx),
                "errores": [err["msg"] for err in e.errors()],
            })
        except Exception as e:
            errores.append({
                "fila": int(idx),
                "errores": [str(e)],
            })

    return validos, errores


def deduplicate(validos: list[Solicitud], key: str = "email"):
    unicos: list[Solicitud] = []
    duplicados: list[dict] = []
    vistos: set[str] = set()

    for solicitud in validos:
        valor = getattr(solicitud.persona, key)
        if valor in vistos:
            duplicados.append({
                "identificador": solicitud.identificador,
                key: valor,
            })
        else:
            vistos.add(valor)
            unicos.append(solicitud)

    return unicos, duplicados


def classify(unicos: list[Solicitud], by: str = "tipo_solicitud"):
    grupos: dict[str, list[Solicitud]] = {}
    for solicitud in unicos:
        valor = getattr(solicitud, by)
        grupos.setdefault(valor, []).append(solicitud)
    return grupos
