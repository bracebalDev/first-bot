import src.first_bot.config as cfg
from src.first_bot.models import Solicitud


class WebSubmitter:
    """Stub: registra solicitudes en el formulario web (Playwright en el futuro)."""

    def __init__(self, form_url: str | None = None, headless: bool = True):
        self.form_url = form_url or cfg.WEB_FORM_URL
        self.headless = headless

    def submit(self, solicitudes: list[Solicitud]) -> list[dict]:
        resultados: list[dict] = []
        for solicitud in solicitudes:
            resultados.append({
                "identificador": solicitud.identificador,
                "resultado": "registrado",
                "error": None,
            })
        return resultados
