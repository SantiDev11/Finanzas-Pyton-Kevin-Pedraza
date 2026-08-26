# 📊 Aplicación Web de Finanzas Personales con Dashboard Analítico

Aplicación web full-stack para el registro, control y análisis inteligente de finanzas personales, estructurada con arquitectura limpia por capas y preparada para despliegue continuo.

---

## 🎯 Objetivo General

Proveer una solución integral que permita a los usuarios registrar sus movimientos financieros (ingresos y gastos) clasificados por categorías, visualizando su balance en tiempo real, evaluando su comportamiento financiero y obteniendo proyecciones predictivas basadas en modelos de Machine Learning.

---

## 🛠️ Stack Tecnológico

* **Backend:** Python 3.10+ / FastAPI (Arquitectura RESTful por capas)
* **Frontend:** HTML5 Semántico, CSS3 Moderno, JavaScript Vanilla (Fetch API) y Chart.js
* **Base de Datos:** MySQL 8.0+ (Normalización 3FN)
* **Análisis de Datos:** Pandas, Scikit-learn (LinearRegression, Z-Score)
* **Testing:** Pytest, HTTPX (FastAPI TestClient)
* **Control de Versiones & Despliegue:** Git, GitHub, Render

---

## 📁 Estructura del Proyecto

```text
finanzas-personales/
├── backend/
│   ├── app/
│   │   ├── routes/          # Controladores y rutas HTTP
│   │   ├── services/        # Lógica de negocio y dominio
│   │   ├── repositories/    # Acceso a datos (SQL parametrizado)
│   │   ├── models/          # Entidades internas
│   │   ├── schemas/         # Validación de datos con Pydantic
│   │   └── analytics/       # Módulo analítico y Machine Learning
│   ├── tests/               # Pruebas unitarias y de integración
│   ├── requirements.txt     # Dependencias de Python
│   └── main.py              # Punto de entrada de FastAPI
├── frontend/
│   ├── index.html           # Estructura semántica HTML5
│   ├── css/
│   │   └── style.css        # Estilos base y responsive design
│   └── js/
│       └── app.js           # Lógica frontend
├── database/
│   ├── schema.sql           # Estructura: tablas, restricciones e índices
│   ├── seed.sql             # Datos de prueba
│   └── queries.sql          # Consultas de validación del modelo
├── docs/                    # Documentación técnica
├── .env.example             # Plantilla de variables de entorno
├── .gitignore               # Exclusiones de control de versiones
└── README.md                # Documentación principal
```

---

## 🗄️ Base de Datos

### Requisitos

* **MySQL 8.0 o superior.** El modelo usa restricciones `CHECK` (disponibles a partir de
  MySQL 8.0.16) y la intercalación `utf8mb4_0900_ai_ci`, ninguna de las dos existe en
  versiones anteriores.
* Motor de almacenamiento **InnoDB**, necesario para las claves foráneas.

### Creación de la base de datos

Los scripts crean la base de datos `finanzas_personales` por sí mismos, así que basta con
ejecutarlos en orden desde la raíz del proyecto:

```bash
mysql -u root -p < database/schema.sql
mysql -u root -p < database/seed.sql
```

En Windows (PowerShell), si el cliente `mysql` no está en el `PATH`, indica la ruta completa
al binario (por ejemplo el que incluye Laragon o XAMPP):

```powershell
Get-Content database\schema.sql -Raw -Encoding UTF8 | mysql -u root -p --default-character-set=utf8mb4
Get-Content database\seed.sql   -Raw -Encoding UTF8 | mysql -u root -p --default-character-set=utf8mb4
```

* `schema.sql` — crea la base de datos, las tres tablas, las restricciones y los índices.
  Es idempotente: elimina y recrea las tablas, por lo que **descarta los datos existentes**.
* `seed.sql` — carga datos de prueba. También es idempotente: vacía las tablas antes de
  insertar. Requiere `schema.sql` ejecutado previamente.
* `queries.sql` — consultas de validación (totales, balance, agrupaciones y filtros por
  fecha). No modifica datos; sirve para comprobar que el modelo responde correctamente.

### Estructura

Tres tablas relacionadas, normalizadas hasta la Tercera Forma Normal:

| Tabla             | Contenido                                        | Clave primaria  |
| ----------------- | ------------------------------------------------ | --------------- |
| `usuarios`        | Personas registradas en la aplicación            | `id_usuario`    |
| `categorias`      | Categorías de ingreso o gasto de cada usuario    | `id_categoria`  |
| `ingresos_gastos` | Movimientos financieros registrados              | `id_movimiento` |

```text
usuarios ──1:N──> categorias ──1:N──> ingresos_gastos
    └────────────────1:N───────────────────┘
```

Un usuario posee sus propias categorías y sus propios movimientos; cada movimiento se
clasifica mediante una categoría que pertenece a ese mismo usuario.

Detalles del diseño:

* Los importes se almacenan en `DECIMAL(12,2)`, nunca en `FLOAT`, para evitar el error de
  redondeo binario.
* El dominio de `tipo` (`ingreso` / `gasto`) se restringe con `ENUM`.
* Todas las claves foráneas usan `ON DELETE RESTRICT`: ningún borrado destruye historial
  financiero de forma implícita. La baja de una cuenta se ejecuta como una transacción
  ordenada, descrita en la sección 6 de `schema.sql`.
* El juego de caracteres es `utf8mb4` de extremo a extremo, de modo que tildes y eñes
  (á, é, í, ó, ú, ñ) se almacenan y se recuperan sin pérdida.

### Credenciales

Los scripts no contienen ninguna credencial. Copia `.env.example` a `.env` y ajusta ahí los
datos de conexión; `.env` está excluido del control de versiones. Los valores de
`contrasena_hash` incluidos en `seed.sql` son cadenas ficticias con formato de bcrypt y no
corresponden a ninguna contraseña real.

---

## 🚀 Guía de Inicio Rápido (Backend)

### 1. Requisitos Previos
* Python 3.10 o superior instalado.
* Git instalado.

### 2. Creación y Activación del Entorno Virtual

En la raíz del proyecto o dentro del directorio `backend/`:

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

Con el entorno virtual activado:
```bash
pip install -r backend/requirements.txt
```

### 4. Ejecución del Servidor Backend

Navega a la carpeta `backend` y ejecuta:
```bash
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

El servidor iniciará en: [http://127.0.0.1:8000](http://127.0.0.1:8000)

* Verificación de estado: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* Documentación interactiva Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Documentación alternativa Redoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🧪 Ejecución de Pruebas Automatizadas

Para correr la suite de pruebas con `pytest`:

```bash
cd backend
pytest -v
```
