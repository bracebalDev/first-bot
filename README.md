# First Bot — Procesador Automatizado de Solicitudes (RPA)

Bot que automatiza el proceso de negocio de registro de solicitudes: lee archivos Excel/CSV, valida, deduplica, clasifica y registra cada solicitud en un formulario web vía Playwright.

---

## Concepto de RPA

**RPA (Robotic Process Automation)** es la automatización de tareas repetitivas basadas en reglas que tradicionalmente realiza un humano interactuando con interfaces de usuario de sistemas de información. Un bot RPA emula las acciones del usuario: leer archivos, navegar páginas web, llenar formularios, extraer datos, aplicar reglas de negocio y generar trazabilidad.

---

## Diferencias: tarea manual, script, bot y sistema automatizado

| Concepto | Definición | Ejemplo |
|----------|-----------|---------|
| **Tarea manual** | Persona ejecuta cada paso sin automatización. Lento, propenso a error, no auditado. | Operador abre `solicitudes.xlsx`, transcribe cada fila al formulario web una por una. |
| **Script** | Código que automatiza _una parte_ del flujo. Generalmente rígido, sin manejo robusto de errores, sin bitácora. | `for row in df: requests.post(url, row)` — se rompe si el archivo no existe; no valida ni registra. |
| **Bot** | Software que ejecuta un proceso de negocio _completo_ de principio a fin. Maneja excepciones, registra resultados, es supervisable y deja trazabilidad. | Este proyecto: lee archivos → valida → deduplica → clasifica → registra en web → genera bitácora → presenta resumen. |
| **Sistema automatizado** | Ecosistema orquestado de bots + APIs + reglas de negocio + monitoreo. Escala empresarial con múltiples procesos interconectados. | 10 bots ejecutándose en paralelo, orquestador central, dashboard de KPIs, alertas. |

---

## Relación entre RPA, procesos de negocio y sistemas de información

```
PROCESO DE NEGOCIO
"Registrar solicitudes de clientes en el sistema CRM"

    ├── ENTRADA: archivos Excel/CSV con 13 columnas
    │
    ├── REGLAS DE NEGOCIO:
    │   • Email debe ser válido (formato RFC)
    │   • Prioridad: alta, media o baja
    │   • Estado: pendiente, en_proceso, completada
    │   • No registrar solicitudes con email duplicado
    │   • Clasificar por tipo_solicitud
    │
    ├── SISTEMAS DE INFORMACIÓN:
    │   • Sistema de archivos local (input/output)
    │   • Formulario web (https://rpachallenge.com)
    │   • Directorio de bitácoras (logs)
    │
    └── SALIDA:
        • CSV con resultados por cada archivo procesado
        • Bitácora de ejecución con loguru (.log)
        • Resumen de ejecución en consola
```

El bot RPA es el **puente** entre archivos (entrada) y el sistema web (destino), aplicando reglas de negocio y dejando trazabilidad.

---

## Criterios para seleccionar un proceso automatizable

| Criterio | Cumplimiento en este proyecto |
|----------|-------------------------------|
| **Alto volumen y repetitivo** | Sí: múltiples archivos, múltiples filas, misma operación por fila. |
| **Basado en reglas (no requiere juicio humano)** | Sí: validación de email, prioridad, estado, dedup por email. |
| **Entrada estructurada** | Sí: Excel/CSV con columnas predefinidas. |
| **Salida predecible** | Sí: cada fila se registra o se rechaza con motivo explícito. |
| **Bajo cambio frecuente** | Sí: columnas estables, reglas fijas. |
| **Auditable** | Sí: bitácora por ejecución, CSV de resultados, resumen. |
| **Integración con sistemas existentes** | Sí: filesystem + web. |

---

## Entradas, salidas, reglas y excepciones

### Entradas

- 1 a N archivos `.xlsx` o `.csv` en el directorio definido por `INPUT_PATH` en `.env`.
- Cada archivo debe contener **13 columnas** con los siguientes nombres exactos:

| # | Columna | Tipo | Validación |
|---|---------|------|------------|
| 1 | `First Name` | texto | obligatorio, no vacío |
| 2 | `Last Name` | texto | obligatorio, no vacío |
| 3 | `Company Name` | texto | obligatorio, no vacío |
| 4 | `Role in Company` | texto | obligatorio, no vacío |
| 5 | `Address` | texto | obligatorio, no vacío |
| 6 | `Email` | email | formato RFC válido |
| 7 | `Phone Number` | texto | obligatorio, no vacío |
| 8 | `tipo_solicitud` | texto | obligatorio, no vacío |
| 9 | `fecha` | fecha | formatos: `YYYY-MM-DD`, `DD/MM/YYYY`, `MM/DD/YYYY`, `YYYY/MM/DD` |
| 10 | `prioridad` | enum | `alta`, `media`, `baja` |
| 11 | `identificador` | texto | obligatorio, no vacío |
| 12 | `descripcion` | texto | obligatorio, no vacío |
| 13 | `estado` | enum | `pendiente`, `en_proceso`, `completada` |

### Salidas

- **1 archivo CSV** por cada input procesado en `OUTPUT_PATH` con prefijo `resultado_`.
- **1 archivo `.log`** por ejecución en `OUTPUT_PATH/logs/` con rotación de 10 MB y retención de 7 días.
- **Resumen en consola**: archivos procesados, total de registros, válidos, duplicados, errores.

### Reglas de negocio

1. Solo se procesan archivos no procesados previamente (tracker compara input vs output).
2. Cada fila se valida contra el modelo `Solicitud(BaseModel)` de Pydantic.
3. Una fila inválida no detiene el proceso; se registra el error y se continúa.
4. Email debe tener formato válido (RFC).
5. Prioridad debe ser `alta`, `media` o `baja`.
6. Estado debe ser `pendiente`, `en_proceso` o `completada`.
7. Fecha debe ser parseable desde los formatos soportados.
8. Campos obligatorios no pueden estar vacíos ni ser solo espacios.
9. Deduplicación por Email: primera ocurrencia se procesa; las subsecuentes se marcan como duplicadas.
10. Clasificación por `tipo_solicitud`: agrupa solicitudes válidas por tipo.
11. Cada solicitud válida se envía al formulario web.

### Excepciones personalizadas

| Excepción | Cuándo se lanza |
|-----------|----------------|
| `FileReadError` | Archivo no existe, corrupto, extensión no soportada. |
| `ValidationFailedError` | Errores de validación acumulados por fila (no detiene el pipeline). |
| `SubmissionError` | Fallo al enviar una solicitud individual al formulario web. |

---

## Lectura de archivos con Python

Se usa **pandas** como motor de lectura con el patrón **Strategy**:

```
BaseReader (ABC)
├── CsvReader  → pd.read_csv()
└── XlsxReader → pd.read_excel(engine="openpyxl")
```

La función **factory** `reader_factory(extensión: str) -> BaseReader` selecciona el lector según la extensión del archivo (`.csv`, `.xlsx`, `.xls`). Si se agrega soporte para JSON, Parquet u otros formatos, solo se añade una clase concreta y se registra en la factory, sin modificar el resto del sistema.

---

## Validación de datos

Se usa **Pydantic v2** con `BaseModel`:

```python
class Persona(BaseModel):
    first_name: str
    email: EmailStr  # validación RFC automática
    ...

class Solicitud(BaseModel):
    persona: Persona        # composición
    prioridad: Literal["alta", "media", "baja"]
    fecha: date             # field_validator con múltiples formatos
    ...
```

Cada fila del DataFrame se convierte en `dict` y se pasa al modelo. Errores de validación se capturan por fila, se registran vía loguru y no detienen el pipeline.

---

## Identificación de duplicados

Clave de deduplicación: **Email**. Se recorre la lista de solicitudes válidas manteniendo un `set` de emails vistos. La primera ocurrencia se considera válida; las subsecuentes se marcan como duplicadas. Se registra cada duplicado en la bitácora y en el CSV de salida.

**¿Por qué Email?** Es el campo que identifica de forma única a un solicitante en el formulario web de destino (`rpachallenge.com`), por lo que enviar dos solicitudes con el mismo email generaría un conflicto.

---

## Generación de archivos de resultados

Cada archivo de entrada produce un CSV de salida:

```
resultado_{nombre_base}.csv
```

**Columnas del output:**

| Columna | Contenido |
|---------|-----------|
| `first_name` | Nombre del solicitante |
| `last_name` | Apellido |
| `email` | Correo electrónico |
| `tipo_solicitud` | Tipo de solicitud |
| `fecha` | Fecha de la solicitud |
| `prioridad` | Prioridad (alta/media/baja) |
| `identificador` | ID de la solicitud |
| `estado` | Estado (pendiente/en_proceso/completada) |
| `resultado` | `registrado`, `duplicado`, `error_validacion` |
| `error` | Motivo del error (o `None`) |

---

## Manejo de errores con loguru

**loguru** es el sistema de logging central. Tres niveles de salida:

| Destino | Nivel | Propósito |
|---------|-------|-----------|
| Consola (`sys.stderr`) | INFO+ | Feedback inmediato al operador |
| Archivo `.log` | DEBUG+ | Trazabilidad completa de cada ejecución |
| Rotación | 10 MB | Evita archivos de log excesivamente grandes |
| Retención | 7 días | Limpieza automática de logs antiguos |

**Jerarquía de captura:**

1. `@logger.catch` en entrypoints para excepciones no anticipadas.
2. `try/except` con `logger.exception()` para tracebacks completos.
3. `logger.warning()` para datos inválidos y duplicados (no bloqueantes).
4. `logger.info()` para hitos del pipeline.
5. `logger.error()` para fallos de submit individuales.

---

## Arquitectura del proyecto

```
first-bot/
├── .env                          # INPUT_PATH, OUTPUT_PATH, WEB_FORM_URL, HEADLESS
├── .gitignore
├── pyproject.toml                # Dependencias y metadatos
├── README.md
├── run_bot.bat                   # Launcher Windows (loop + pausa)
├── run_bot.sh                    # Launcher Linux/macOS (loop + pausa)
├── scripts/
│   └── generate_input.py         # Genera 20 filas de prueba
├── src/
│   └── first_bot/
│       ├── __init__.py
│       ├── main.py               # CLI entrypoint
│       ├── config.py             # Settings desde .env
│       ├── exceptions.py         # Excepciones personalizadas
│       ├── models.py             # Persona + Solicitud (BaseModel)
│       ├── readers.py            # Strategy + Factory para lectura
│       ├── services.py           # validate, deduplicate, classify
│       ├── submitter.py          # WebSubmitter (stub → Playwright)
│       ├── orchestrator.py       # Pipeline central
│       ├── tracker.py            # Archivos procesados vs pendientes
│       ├── reporter.py           # CSV output + log + resumen
│       └── utils.py              # Helpers de ruta
└── tests/
    ├── __init__.py
    ├── conftest.py               # Fixtures compartidos
    ├── test_readers.py           # 10 tests
    ├── test_models.py            # 15 tests
    ├── test_services.py          # 7 tests
    ├── test_submitter.py         # 3 tests
    ├── test_tracker.py           # 5 tests
    └── test_orchestrator.py      # 3 tests
```

---

## Flujo completo del Orchestrator

```
main.py
  │
  └── Orchestrator.run()
        │
        ├── 1. setup_logging()              → archivo .log con timestamp
        │
        ├── 2. tracker.get_unprocessed()    → lista de archivos pendientes
        │
        ├── 3. For each archivo:
        │       │
        │       ├── 3a. reader_factory(ext).read(archivo) → DataFrame
        │       │       └── FileReadError → skip archivo
        │       │
        │       ├── 3b. services.validate(df) → (válidos, errores)
        │       │       └── por fila inválida → logger.warning()
        │       │
        │       ├── 3c. services.deduplicate(válidos, "email") → (únicos, dups)
        │       │       └── por duplicado → logger.warning()
        │       │
        │       ├── 3d. services.classify(únicos, "tipo_solicitud") → dict
        │       │
        │       ├── 3e. submitter.submit(únicos) → resultados
        │       │       └── por error → logger.error() (no detiene)
        │       │
        │       ├── 3f. reporter.guardar_resultados() → CSV en OUTPUT_PATH
        │       │
        │       └── 3g. reporter.resumen_archivo() → consola
        │
        └── 4. reporter.resumen_global()    → resumen final en consola
```

---

## Patrones de diseño aplicados

### Strategy — `readers.py`

```
BaseReader (ABC)
  ├── CsvReader  → pd.read_csv()
  └── XlsxReader → pd.read_excel() con openpyxl
```

**Motivo:** Permite intercambiar el backend de lectura sin modificar el orquestador. Cumple el principio Open/Closed (abierto a extensión, cerrado a modificación). Si se necesita soporte para JSON o Parquet, se agrega una clase sin tocar el resto.

### Factory — `reader_factory(ext) -> BaseReader`

**Motivo:** Encapsula la decisión de qué reader instanciar basado en la extensión del archivo. El orquestador no conoce las clases concretas. Centraliza la lógica de creación en un solo punto.

### Composite — `Solicitud` compone `Persona`

**Motivo:** `Persona` agrupa los 7 campos del formulario web (datos personales); `Solicitud` agrega los 6 campos de negocio. Esta separación refleja la estructura del dominio y facilita el mapeo al formulario web. Si el formulario cambia sus campos, solo se modifica `Persona`.

### Orchestrator — `orchestrator.py`

**Motivo:** Centraliza la coordinación del flujo completo. Separa el _qué_ (secuencia de pasos) del _cómo_ (implementación de cada paso). `main.py` solo instancia y llama `.run()`. Facilita testing: se puede probar el flujo completo con dependencias mockeadas.

### Template Method — `WebSubmitter.submit()`

**Motivo:** La secuencia de pasos está definida (abrir navegador → navegar → llenar campos → enviar → cerrar) pero la implementación concreta con Playwright se desarrolla después. El stub actual permite probar el pipeline completo sin depender de Playwright ni de una URL real.

### Dependency Injection

**Motivo:** El orchestrator recibe sus dependencias (reader via factory, submitter vía constructor). Esto permite inyectar mocks en tests sin necesidad de monkey-patching de imports. Cada componente es testeable de forma aislada.

---

## Cómo ejecutar

### 1. Requisitos previos

- Python 3.11+
- Navegador Chromium (para Playwright cuando se implemente)

### 2. Instalar dependencias

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# o .venv\Scripts\activate  # Windows

pip install pandas openpyxl "pydantic[email]" loguru python-dotenv playwright pytest pytest-cov
playwright install chromium  # solo cuando se implemente Playwright
```

### 3. Configurar

Editar `.env`:

```env
INPUT_PATH=./data/input
OUTPUT_PATH=./data/output
WEB_FORM_URL=https://rpachallenge.com/
HEADLESS=true
```

### 4. Generar datos de prueba

```bash
python scripts/generate_input.py
```

Esto crea `data/input/solicitudes_prueba.xlsx` y `data/input/solicitudes_prueba.csv` con 20 registros cada uno.

### 5. Ejecutar una vez

```bash
python -m src.first_bot.main
```

### 6. Ejecutar en bucle continuo

**Linux/macOS:**
```bash
./run_bot.sh
```

**Windows:**
```
run_bot.bat
```

El bot se ejecuta en bucle: procesa archivos pendientes, espera 60 segundos y repite. Si haces click en la consola se pausa; presiona Enter para reanudar. Ctrl+C para detener.

### 7. Ejecutar tests

```bash
pytest tests/ -v
```

---

## Tecnologías utilizadas

| Tecnología | Propósito |
|-----------|-----------|
| **Pandas** | Lectura y escritura de archivos tabulares (CSV, Excel) |
| **OpenPyXL** | Backend de Excel para pandas |
| **Pydantic v2** | Validación de datos con BaseModel, EmailStr, Literal |
| **Loguru** | Logging estructurado con rotación y retención |
| **python-dotenv** | Carga de configuración desde `.env` |
| **Playwright** | Automatización de navegador para el formulario web (stub actual) |
| **Pytest** | Framework de testing unitario y de integración |
