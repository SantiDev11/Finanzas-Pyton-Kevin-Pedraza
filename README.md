# 📊 Aplicación Web de Finanzas Personales con Dashboard Analítico

Aplicación web full-stack para el registro, control y análisis inteligente de finanzas personales, estructurada con arquitectura limpia por capas y preparada para despliegue continuo.

---

## 🎯 Objetivo General

Proveer una solución integral que permita a los usuarios registrar sus movimientos financieros (ingresos y gastos) clasificados por categorías, visualizando su balance en tiempo real, evaluando su comportamiento financiero y obteniendo proyecciones predictivas basadas en modelos de Machine Learning.

---

## 🛠️ Stack Tecnológico

* **Backend:** Python 3.10+ / FastAPI (Arquitectura RESTful por capas)
* **Frontend:** HTML5 Semántico, CSS3 Moderno, JavaScript Vanilla (Fetch API) y Chart.js
* **Base de Datos:** MySQL 8.0+ (Normalización 3FN con PyMySQL y SQL parametrizado)
* **Seguridad:** Hashing seguro de contraseñas con `bcrypt` (rounds=12)
* **Análisis de Datos:** Pandas, Scikit-learn (LinearRegression, Z-Score) *(Próximas fases)*
* **Testing:** Pytest, HTTPX (FastAPI TestClient)
* **Control de Versiones & Despliegue:** Git, GitHub, Render

---

## 📁 Estructura del Proyecto

```text
finanzas-personales/
├── backend/
│   ├── app/
│   │   ├── core/            # Configuración, seguridad (bcrypt), periodos, excepciones y dependencias
│   │   ├── database/        # Conexión, transacción context manager y pool MySQL
│   │   ├── routes/          # Controladores HTTP (Usuarios, Categorías, Movimientos, Resumen)
│   │   ├── services/        # Lógica de negocio y validaciones de dominio
│   │   ├── repositories/    # Acceso a datos (SQL puro parametrizado)
│   │   ├── models/          # Entidades de dominio
│   │   ├── schemas/         # Validación y contratos de API con Pydantic
│   │   └── analytics/       # Módulo analítico y Machine Learning (Fases posteriores)
│   ├── tests/               # Pruebas unitarias e integración (110 tests automatizados)
│   │   ├── unit/            # Tests de servicios, periodos, movimientos y seguridad
│   │   └── integration/     # Tests de endpoints HTTP
│   ├── requirements.txt     # Dependencias de Python
│   └── main.py              # Punto de entrada de FastAPI
├── frontend/
│   ├── index.html           # Estructura semántica HTML5
│   ├── css/
│   │   └── style.css        # Estilos base y responsive design
│   └── js/
│       └── app.js           # Lógica frontend
├── database/
│   ├── schema.sql           # Estructura: tablas, restricciones e índices (3FN)
│   ├── seed.sql             # Datos de prueba (6+ meses de histórico)
│   └── queries.sql          # Consultas de validación del modelo
├── docs/                    # Documentación técnica
├── .env.example             # Plantilla de variables de entorno
├── .gitignore               # Exclusiones de control de versiones
└── README.md                # Documentación principal
```

---

## 🗄️ Base de Datos y Variables de Entorno

### Configuración del Entorno (`.env`)

Copia la plantilla `.env.example` a un archivo `.env` en la raíz del proyecto y configura tus credenciales de MySQL:

```env
APP_ENV=development
APP_HOST=127.0.0.1
APP_PORT=8000
DEBUG=True

DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=finanzas_personales
```

> **Nota de Seguridad:** El archivo `.env` está expresamente excluido en `.gitignore`. Nunca subas credenciales reales al repositorio.

### Creación del Esquema en MySQL 8.0+

```bash
mysql -u root -p < database/schema.sql
mysql -u root -p < database/seed.sql
```

En Windows PowerShell:
```powershell
Get-Content database\schema.sql -Raw -Encoding UTF8 | mysql -u root -p --default-character-set=utf8mb4
Get-Content database\seed.sql   -Raw -Encoding UTF8 | mysql -u root -p --default-character-set=utf8mb4
```

---

## 🚀 Guía de Inicio Rápido (Backend)

### 1. Requisitos Previos
* Python 3.10 o superior instalado.
* MySQL 8.0 o superior en ejecución.

### 2. Creación y Activación del Entorno Virtual

**En Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**En Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalación de Dependencias

```bash
pip install -r backend/requirements.txt
```

### 4. Ejecución del Servidor Backend

Navega a la carpeta `backend` e inicia el servidor ASGI:
```bash
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

* **API Root:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* **Documentación Interactiva Swagger:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Documentación Alternativa ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📡 Endpoints Implementados (Fases 1 a 5)

### Salud y Estado
| Método | Endpoint | Propósito | Códigos |
|---|---|---|---|
| `GET` | `/` | Health check de la API | `200 OK` |

### Usuarios y Categorías (Fase 3)
| Método | Endpoint | Propósito | Request Body (JSON) | Códigos |
|---|---|---|---|---|
| `POST` | `/api/usuarios` | Registro de nuevo usuario | `{"nombre": str, "correo": str, "contrasena": str}` | `201`, `400`, `409`, `422` |
| `POST` | `/api/categorias` | Creación de categoría | `{"nombre": str, "tipo": "ingreso"\|"gasto", "id_usuario": int}` | `201`, `400`, `404`, `409`, `422` |
| `GET` | `/api/categorias?id_usuario=` | Listado de categorías de un usuario | Ninguno (Query Param) | `200`, `400`, `404` |

### Movimientos Financieros (Fase 4)
| Método | Endpoint | Propósito | Request Body / Query Params | Códigos |
|---|---|---|---|---|
| `POST` | `/api/movimientos` | Registrar ingreso o gasto | `{"id_usuario": int, "id_categoria": int, "tipo": "ingreso"\|"gasto", "monto": Decimal, "fecha": date, "descripcion": str?}` | `201 Created`, `400 Bad Request`, `404 Not Found`, `422 Unprocessable` |
| `GET` | `/api/movimientos` | Listar con filtros | Query: `id_usuario` (req), `desde` (opt), `hasta` (opt), `categoria` (opt) | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `PUT` | `/api/movimientos/{id}` | Actualizar movimiento existente | Path: `id`. Body: `MovimientoUpdate` | `200 OK`, `400 Bad Request`, `404 Not Found`, `422` |
| `DELETE` | `/api/movimientos/{id}` | Eliminar movimiento por ID | Path: `id` | `200 OK`, `404 Not Found` |

### Reglas de Negocio en Movimientos:
1. **Precisión Monetaria:** El monto se valida y procesa como tipo `Decimal(12,2)` estrictamente positivo (`monto > 0`).
2. **Pertenencia de Categoría:** La categoría debe existir y pertenecer al mismo usuario (`id_usuario`).
3. **Coherencia de Tipo:** El `tipo` del movimiento (`ingreso`/`gasto`) debe coincidir exactamente con el `tipo` de la categoría asignada.
4. **Validación de Rangos:** En filtros de consulta, `desde` no puede ser posterior a `hasta`.
5. **Aislamiento por Usuario:** Las consultas y modificaciones verifican la titularidad del recurso, impidiendo accesos o ediciones no autorizadas.
6. **Ordenamiento:** Los movimientos se listan ordenados de forma descendente (`fecha DESC, id_movimiento DESC`).

### Resumen Financiero (Fase 5)
| Método | Endpoint | Propósito | Query Params | Códigos |
|---|---|---|---|---|
| `GET` | `/api/resumen` | Resumen financiero de un mes | `id_usuario` (req), `mes` (req, `YYYY-MM`) | `200 OK`, `400 Bad Request`, `404 Not Found`, `422 Unprocessable` |

**Parámetros:**

* `id_usuario` — entero positivo. Si el usuario no existe se devuelve `404`.
* `mes` — periodo en formato `YYYY-MM` (por ejemplo `2026-08`). Si el formato es incorrecto
  (`2026-8`, `agosto`) o el mes no existe (`2026-13`, `2026-00`) se devuelve `400`.

**Ejemplo:**

```bash
curl "http://127.0.0.1:8000/api/resumen?id_usuario=1&mes=2026-08"
```

```json
{
    "id_usuario": 1,
    "mes": "2026-08",
    "total_ingresos": "3749.87",
    "total_gastos": "1558.69",
    "balance": "2191.18"
}
```

**Qué calcula cada campo:**

* **`total_ingresos`** — suma de los montos de los movimientos de tipo `ingreso` del usuario
  cuya fecha contable cae dentro del mes solicitado.
* **`total_gastos`** — suma de los montos de los movimientos de tipo `gasto` del mismo usuario
  y mes.
* **`balance`** — ahorro del periodo: `total_ingresos - total_gastos`. Lo calcula siempre el
  backend, que es la única fuente de verdad; el cliente nunca envía importes. Un balance
  **negativo es un resultado válido** y se devuelve con `200` cuando los gastos superan a los
  ingresos.

Los tres importes se manejan como `Decimal` con dos decimales, nunca como `float`, para evitar
el error de redondeo binario. Un mes **sin movimientos no es un error**: la respuesta es `200`
con los tres importes en `0.00`.

---

## 🧪 Pruebas Automatizadas

La suite de pruebas contiene **110 tests automatizados** cubriendo casos de éxito, validaciones de borde, errores controlados y regresión:

```bash
.venv\Scripts\pytest backend/tests/ -v
```
