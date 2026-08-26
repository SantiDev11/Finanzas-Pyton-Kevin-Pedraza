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
│   │   ├── core/            # Configuración, seguridad (bcrypt), excepciones y dependencias
│   │   ├── database/        # Conexión, transacción context manager y pool MySQL
│   │   ├── routes/          # Controladores y rutas HTTP (Usuarios, Categorías)
│   │   ├── services/        # Lógica de negocio y validaciones de dominio
│   │   ├── repositories/    # Acceso a datos (SQL puro parametrizado)
│   │   ├── models/          # Entidades de dominio
│   │   ├── schemas/         # Validación y contratos de API con Pydantic
│   │   └── analytics/       # Módulo analítico y Machine Learning (Fases posteriores)
│   ├── tests/               # Pruebas unitarias e integración (23 tests automatizados)
│   │   ├── unit/            # Tests de servicios y seguridad
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

## 📡 Endpoints Implementados (Fase 3)

| Método | Endpoint | Propósito | Request Body (JSON) | Códigos de Respuesta |
|---|---|---|---|---|
| `GET` | `/` | Health check de la API | Ninguno | `200 OK` |
| `POST` | `/api/usuarios` | Registro de nuevo usuario | `{"nombre": str, "correo": str, "contrasena": str}` | `201 Created`, `400`, `409 Conflict`, `422` |
| `POST` | `/api/categorias` | Creación de categoría | `{"nombre": str, "tipo": "ingreso"\|"gasto", "id_usuario": int}` | `201 Created`, `400`, `404 Not Found`, `409 Conflict`, `422` |
| `GET` | `/api/categorias?id_usuario=` | Listado de categorías de un usuario | Ninguno (Query Param: `id_usuario`) | `200 OK`, `400`, `404 Not Found` |

---

## 🧪 Pruebas Automatizadas

La suite de pruebas incluye tests unitarios de seguridad y servicios, así como tests de integración sobre los endpoints HTTP usando `pytest` y `TestClient`:

```bash
.venv\Scripts\pytest backend/tests/ -v
```
