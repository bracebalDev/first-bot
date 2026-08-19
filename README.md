# 🤖 First Bot — Sistema de Procesamiento y Tracking por Fechas (RPA)

> **Asignatura:** Sistemas de Información — Semestre 7  
> **Taller:** Robotic Process Automation (RPA) — Asignación 1  
> **Carácter:** Académico / Formativo  

---

## 📌 1. Resumen Ejecutivo y Contexto Académico

En el marco de la asignatura **Sistemas de Información**, este proyecto implementa un bot de **Robotic Process Automation (RPA)** modular, resiliente y escalable en Python. Su objetivo es automatizar el ciclo de vida completo de ingesta, validación, deduplicación, clasificación, carga web y trazabilidad de solicitudes de negocio provenientes de archivos tabulares (`.csv`, `.xlsx`).

### 🎯 La Problemática de la Asignación 1
En implementaciones iniciales de RPA, los archivos suelen depositarse en carpetas planas y el control de procesamiento se basa en prefijos rígidos (por ejemplo, anteponer `resultado_` al nombre del archivo). Aunque funcional para demostraciones básicas, este enfoque presenta serias limitaciones de escalabilidad:
- Dificultad para organizar grandes volúmenes diarios o históricos de información.
- Acoplamiento entre el nombre de salida y el mecanismo de rastreo.
- Ineficiencia al buscar y comparar archivos de forma lineal $O(N \times M)$.

### 💡 Solución Desarrollada
Se diseñó e implementó un **nuevo sistema de tracking jerárquico por fechas con conjuntos matemáticos**:
1. **Estructura Jerárquica por Fechas:** Ingesta y salida organizadas bajo la convención de carpetas `YYYY/MM/DD/archivo.ext`.
2. **Entidades Inmutables de Dominio:** Clases `@dataclass(frozen=True)` (`ProcessableInputFile` y `ProcessableOutputFile`) con igualdad basada exclusivamente en la ruta relativa (`path_dir`).
3. **Tracking por Diferencia de Conjuntos ($O(1)$ Hash Lookup):** Detección instantánea de archivos pendientes mediante la operación de conjuntos `inputs - outputs`.
4. **Idempotencia y Preservación de Formatos:** Los archivos procesados se guardan en `data/output/` replicando la ruta relativa exacta, el nombre y el formato original.

---

## 🏛️ 2. Arquitectura y Patrones de Diseño de Software

El bot sigue estrictamente los principios **SOLID**, la separación de responsabilidades (*Separation of Concerns*) y patrones de diseño reconocidos en la ingeniería de software y automatización:

```
                               ┌───────────────────────────┐
                               │       Orchestrator        │
                               └─────────────┬─────────────┘
                                             │
             ┌───────────────────────────────┼───────────────────────────────┐
             │                               │                               │
             ▼                               ▼                               ▼
  ┌─────────────────────┐         ┌─────────────────────┐         ┌─────────────────────┐
  │   Tracker Module    │         │   Reader Factory    │         │    Service Layer    │
  │ (Set Diff Strategy) │         │  (Factory Pattern)  │         │ (Business Logic)    │
  │   inputs - outputs  │         │ CSV / Excel Readers │         │ Validate, Dedup...  │
  └─────────────────────┘         └─────────────────────┘         └─────────────────────┘
             │                                                           │
             ▼                                                           ▼
  ┌─────────────────────┐                                         ┌─────────────────────┐
  │  Value Object Model │                                         │ Submitter & Reporter│
  │ ProcessableFile     │                                         │ Playwright Stub &   │
  │ (Frozen Dataclass)  │                                         │ Loguru / CSV Export │
  └─────────────────────┘                                         └─────────────────────┘
```

### 1. Value Object & Immutable Model Pattern (`models.py`)
- `ProcessableFile`, `ProcessableInputFile` y `ProcessableOutputFile` son estructuras inmutables (`frozen=True`, `eq=False` con `__eq__` y `__hash__` personalizados).
- Dos objetos son estructuralmente equivalentes si comparten el mismo `path_dir` (ruta relativa normalizada), sin importar si uno es instancia de entrada o de salida.
- Incorporan el método factoría de clase `from_path(file_path, base_dir)` para parsear y validar la jerarquía de fecha (`YYYY/MM/DD`).

### 2. Set Difference Strategy Pattern (`tracker.py`)
- En lugar de iterar y comparar cadenas manualmente, el rastreador escanea recursivamente el directorio de entrada y el de salida, construye los conjuntos hash `inputs: set[ProcessableInputFile]` y `outputs: set[ProcessableOutputFile]`, y calcula los pendientes como:
  $$\text{Pendientes} = \text{Inputs} \setminus \text{Outputs}$$
- Esto garantiza ejecución **idempotente**: si un archivo ya existe en la salida con la misma ruta relativa, es excluido automáticamente en tiempo constante.

### 3. Factory Method Pattern (`readers.py`)
- Permite desacoplar el origen del archivo de su estrategia de lectura mediante `reader_factory(extension)`. Instancia dinámicamente `CsvReader` o `XlsxReader` asegurando una interfaz común `BaseReader`.

### 4. Service Layer Pattern (`services.py`)
- Funciones puras e independientes de infraestructura:
  - `validate(df)`: Valida cada fila contra el modelo de datos Pydantic `Solicitud`.
  - `deduplicate(validos, key="email")`: Previene registros repetidos en el sistema destino.
  - `classify(unicos, by="tipo_solicitud")`: Agrupa las solicitudes por su tipología de negocio.

### 5. Orchestrator Pattern (`orchestrator.py`)
- Actúa como controlador central del flujo de trabajo: coordina la detección de pendientes, la lectura, validación, deduplicación, envío web y generación de bitácoras sin acoplar la lógica interna de cada módulo.

---

## 📂 3. Estructura de Carpetas

```text
first-bot/
├── data/
│   ├── input/                     # Directorio de entrada jerárquico
│   │   └── 2028/
│   │       └── 01/
│   │           ├── 15/
│   │           │   ├── solicitudes_a.csv
│   │           │   └── pedidos_b.xlsx
│   │           └── 16/
│   │               └── reclamos_c.csv
│   └── output/                    # Directorio de salida (mantiene rutas relativas)
│       ├── 2028/
│       │   └── 01/...
│       └── logs/                  # Bitácoras de ejecución con rotación
├── scripts/
│   └── generate_input.py          # Generador de lotes de prueba sintéticos
├── src/
│   └── first_bot/
│       ├── __init__.py
│       ├── config.py              # Parámetros y variables de entorno
│       ├── exceptions.py          # Jerarquía de excepciones personalizadas
│       ├── main.py                # Punto de entrada principal
│       ├── models.py              # Modelos Pydantic y Dataclasses ProcessableFile
│       ├── orchestrator.py        # Orquestador del flujo RPA
│       ├── readers.py             # Lectores polimórficos (Factory Pattern)
│       ├── reporter.py            # Generación de reportes CSV/Excel y logs
│       ├── services.py            # Lógica de validación, dedup y clasificación
│       ├── submitter.py           # Adaptador de envío web (Playwright / Stub)
│       ├── tracker.py             # Tracking por diferencia de conjuntos
│       └── utils.py               # Funciones de soporte y resolución de rutas
├── tests/                         # Batería de pruebas unitarias e integración (62 tests)
│   ├── __init__.py
│   ├── conftest.py                # Fixtures aisladas de pytest
│   ├── test_main.py
│   ├── test_models.py
│   ├── test_orchestrator.py
│   ├── test_readers.py
│   ├── test_reporter.py
│   ├── test_services.py
│   ├── test_submitter.py
│   ├── test_tracker.py
│   └── test_utils.py
├── .gitignore
├── pyproject.toml                 # Configuración de dependencias y empaquetado PDM
├── pdm.lock                       # Lockfile reproducible
├── run_bot.bat                    # Script de ejecución para Windows
└── run_bot.sh                     # Script de ejecución para Linux/macOS
```

---

## 📊 4. Esquema de Datos y Reglas de Negocio

Cada archivo procesado (`.csv` o `.xlsx`) debe estructurarse con **13 columnas obligatorias**:

| # | Columna | Tipo | Regla de Negocio / Validación |
|---|---|---|---|
| 1 | `First Name` | String | Obligatorio, no vacío tras strip |
| 2 | `Last Name` | String | Obligatorio, no vacío tras strip |
| 3 | `Company Name` | String | Obligatorio, no vacío tras strip |
| 4 | `Role in Company` | String | Obligatorio, no vacío tras strip |
| 5 | `Address` | String | Obligatorio, no vacío tras strip |
| 6 | `Email` | EmailStr | Formato RFC válido (e.g. `usuario@dominio.com`) |
| 7 | `Phone Number` | String | Obligatorio, no vacío tras strip |
| 8 | `tipo_solicitud` | String | Categoría de negocio (`soporte`, `consulta`, etc.) |
| 9 | `fecha` | Date | Formatos: `YYYY-MM-DD`, `DD/MM/YYYY`, `MM/DD/YYYY`, `YYYY/MM/DD` |
| 10 | `prioridad` | Enum | Literal: `alta`, `media`, `baja` |
| 11 | `identificador` | String | Clave única de la solicitud (e.g. `SOL-001`) |
| 12 | `descripcion` | String | Detalle de la solicitud |
| 13 | `estado` | Enum | Literal: `pendiente`, `en_proceso`, `completada` |

---

## 🚀 5. Guía de Instalación y Ejecución

### Prerrequisitos
- Python `>= 3.11`
- [PDM](https://pdm-project.org/) (administrador de paquetes moderno y estándar PEP 621)

### Paso 1: Clonar e instalar dependencias
```bash
# Clonar el repositorio
git clone https://github.com/bracebalDev/first-bot.git
cd first-bot

# Instalar dependencias base y de desarrollo
pdm install -d
```

### Paso 2: Generar datos de prueba
Para crear automáticamente la estructura de fechas con archivos `.csv` y `.xlsx`:
```bash
pdm run python scripts/generate_input.py
```

### Paso 3: Ejecutar el bot RPA
```bash
pdm run python -m first_bot.main
```
*(Alternativamente en Windows: ejecutar `run_bot.bat`, o en Linux/macOS: `./run_bot.sh`)*

### Paso 4: Ejecutar la batería de pruebas y cobertura
```bash
pdm run pytest -v --cov=first_bot --cov-report=term-missing
```

---

## 🧪 6. Resultados de Calidad y Pruebas Automatizadas

El proyecto cuenta con **62 pruebas automatizadas** que validan la funcionalidad de cada capa del sistema:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.x, pytest-9.1.1, pluggy-1.6.0
collected 62 items

tests/test_main.py .                                                     [  1%]
tests/test_models.py .......................                             [ 38%]
tests/test_orchestrator.py ......                                        [ 48%]
tests/test_readers.py ..........                                         [ 64%]
tests/test_reporter.py ..                                                [ 67%]
tests/test_services.py .......                                           [ 79%]
tests/test_submitter.py ...                                              [ 83%]
tests/test_tracker.py .......                                            [ 95%]
tests/test_utils.py ...                                                  [100%]

=============================== tests coverage ================================
Name                            Stmts   Miss  Cover   Missing
-------------------------------------------------------------
src/first_bot/config.py             9      0   100%
src/first_bot/exceptions.py         4      0   100%
src/first_bot/main.py               6      1    83%
src/first_bot/models.py           102     10    90%
src/first_bot/orchestrator.py      63      6    90%
src/first_bot/readers.py           33      0   100%
src/first_bot/reporter.py          46      0   100%
src/first_bot/services.py          31      2    94%
src/first_bot/submitter.py         11      0   100%
src/first_bot/tracker.py           26      0   100%
src/first_bot/utils.py             14      0   100%
-------------------------------------------------------------
TOTAL                             345     19    94%
============================= 62 passed in 0.68s ==============================
```

---

## 🎓 7. Aprendizajes y Reflexión Académica

El desarrollo de esta asignación en el curso de **Sistemas de Información** permitió consolidar conocimientos fundamentales para el desarrollo de soluciones empresariales:

1. **RPA como integrador de Sistemas de Información:**  
   RPA no consiste únicamente en mover el ratón o rellenar formularios, sino en actuar como un componente de integración no invasivo entre sistemas legados basados en archivos, servicios web y plataformas de trazabilidad.
2. **Importancia de los Patrones de Diseño:**  
   Separar el código en modelos de dominio, servicios de negocio, adaptadores y orquestadores evita el "código espagueti" típico de los scripts desechables, permitiendo que la solución sea mantenible, testeable y extensible.
3. **Estructuras de Datos y Complejidad Algorítmica:**  
   La transición de comparaciones cuadráticas de cadenas a operaciones de conjuntos con Hash Sets ($O(1)$) ilustra cómo la teoría computacional impacta directamente en el rendimiento de procesos batch industriales.
4. **Idempotencia y Tolerancia a Fallos:**  
   En producción, un bot puede fallar por problemas de red o datos corruptos. Diseñar sistemas donde reejecutar el bot no duplique transacciones ni corrompa el estado es un principio indispensable de la ingeniería de software.
