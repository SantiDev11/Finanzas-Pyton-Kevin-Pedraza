# Finanzas Personales

Aplicación web full-stack para el registro, control, visualización y análisis inteligente de finanzas personales, estructurada con arquitectura limpia por capas y preparada técnicamente para despliegue continuo.

---

## Descripción

**Finanzas Personales** es una solución integral diseñada para que los usuarios gestionen sus finanzas de manera ordenada, segura y predecible. Permite registrar movimientos de ingresos y gastos categorizados, consultar balances y totales en tiempo real expresados exclusivamente en pesos colombianos (COP), proyectar el gasto del próximo mes utilizando modelos de Machine Learning (Regresión Lineal) e identificar automáticamente gastos atípicos o anomalías mediante técnicas estadísticas (Z-Score por categoría).

La plataforma incorpora autenticación completa con contraseñas protegidas mediante `bcrypt` y sesiones stateless basadas en tokens `JWT` con expiración, garantizando aislamiento estricto entre usuarios en todas las capas del sistema.

---

## Tecnologías

* **Backend:** Python 3.10+ / FastAPI (Framework ASGI de alto rendimiento)
* **Frontend:** HTML5 Semántico, CSS3 Moderno (Custom Properties, CSS Grid, Flexbox) y JavaScript Vanilla (Fetch API y Chart.js vía CDN), sin frameworks pesados ni empaquetadores
* **Base de Datos:** MySQL 8.0+ (Motor InnoDB, normalización en 3FN, claves foráneas compuestas e integridad referencial)
* **Seguridad:** Hashing de contraseñas con `bcrypt` (coste 12), tokens de acceso firmados con `PyJWT` (algoritmo `HS256`, expiración configurable y clave `SECRET_KEY`)
* **Análisis de Datos & ML:** `Pandas` (manipulación y series temporales), `Scikit-learn` (`LinearRegression` para predicción de gasto) y `NumPy` / `SciPy` (análisis estadístico Z-Score)
* **Testing Automatizado:** `pytest` (171 pruebas automatizadas unitarias y de integración) y `HTTPX` (`TestClient` de FastAPI)
* **Control de Versiones & Deployment:** Git, GitHub, Render (Static Site + Web Service)

---

## Arquitectura

El sistema implementa una **Arquitectura Limpia por Capas** con separación estricta de responsabilidades y flujo unidireccional de dependencias:

```text
       [ Navegador Web / Frontend ]
                    │
            HTTP / REST (JSON)
                    │
                    ▼
         [ 1. Capa de Rutas (Routes) ]
                    │
                    ▼
       [ 2. Capa de Servicios (Services) ]
          │                          │
          ▼                          ▼
[ 3. Repositorios (SQL) ]    [ Módulo Analítico ]
          │                  (Pandas / Scikit-learn)
          ▼
    [ MySQL 8.0+ ]
```

### Reglas Arquitectónicas Cumplidas:
1. **Sin SQL en Rutas ni en Analítica:** Las consultas SQL residen exclusivamente en los repositorios (`app/repositories/`).
2. **Sin Lógica de Negocio en Repositorios:** Los repositorios solo ejecutan consultas parametrizadas y mapean tuplas; las validaciones y cálculos residen en los servicios (`app/services/`).
3. **Flujo de Analítica:** `Routes` → `AnalyticsService` → `MovimientoRepository` (consulta gastos) → `prediction.py` / `anomalies.py` (Pandas & Scikit-learn).
4. **Independencia del Frontend:** El frontend consume la API REST de forma agnóstica vía `fetch()`, manejando el token JWT en cabeceras HTTP.

---

## Estructura del proyecto

```text
finanzas-personales/
├── backend/
│   ├── app/
│   │   ├── analytics/           # Módulo predictivo y estadístico
│   │   │   ├── anomalies.py     # Detección de anomalías por Z-Score
│   │   │   └── prediction.py    # Predicción de gastos con LinearRegression
│   │   ├── core/                # Configuración, seguridad (bcrypt + JWT), excepciones y dependencias
│   │   │   ├── config.py        # Carga de variables de entorno y validaciones
│   │   │   ├── dependencies.py  # Inyección de dependencias (get_current_user)
│   │   │   ├── exceptions.py    # Manejadores globales de errores HTTP
│   │   │   ├── periodo.py       # Utilidades y validación de periodos mensuales
│   │   │   └── security.py      # Hashing bcrypt y generación/validación de JWT
│   │   ├── database/            # Conexión, pooling y transacciones MySQL
│   │   │   ├── connection.py    # Pool de conexiones PyMySQL
│   │   │   └── session.py       # Context manager de sesión/transacción
│   │   ├── models/              # Clases de entidad de dominio
│   │   ├── repositories/        # Consultas SQL parametrizadas a base de datos
│   │   ├── routes/              # Controladores y endpoints REST de FastAPI
│   │   ├── schemas/             # Contratos y validaciones de datos con Pydantic
│   │   └── services/            # Lógica de negocio y reglas de dominio
│   ├── tests/                   # Suite de pruebas automatizadas (171 tests)
│   │   ├── conftest.py          # Fixtures y repositorios en memoria (fakes)
│   │   ├── integration/         # Pruebas de endpoints HTTP y flujos completos
│   │   └── unit/                # Pruebas unitarias de servicios, periodos, seguridad y ML
│   ├── main.py                  # Inicialización y configuración de la app FastAPI
│   └── requirements.txt         # Dependencias de Python fijadas
├── frontend/
│   ├── assets/                  # Favicon y recursos visuales vectoriales
│   ├── css/                     # Hojas de estilo modularizadas en Vanilla CSS
│   │   ├── reset.css            # Normalización del navegador
│   │   ├── variables.css        # Paleta de color, tipografía y tokens de diseño
│   │   ├── layout.css           # Estructura visual, navegación lateral y cabeceras
│   │   ├── components.css       # Tarjetas, botones, inputs, tablas y modales
│   │   └── responsive.css       # Adaptaciones responsive (320px a 1920px)
│   ├── js/                      # Lógica de cliente en Vanilla JavaScript
│   │   ├── config.js            # Configuración central de la API y constantes
│   │   ├── api.js               # Cliente HTTP centralizado con manejo de token y errores
│   │   ├── ui.js                # Formateo monetario en COP, avisos y componentes UI
│   │   ├── sesion.js            # Gestión de autenticación, token y logout
│   │   ├── login.js             # Controlador de index.html (login y registro)
│   │   ├── app.js               # Controlador de dashboard.html y enrutamiento
│   │   ├── dashboard.js         # Vista general del panel y gráficos
│   │   ├── movimientos.js       # CRUD de movimientos con filtros
│   │   ├── categorias.js        # Gestión de categorías de ingresos y gastos
│   │   ├── resumen.js           # Resumen financiero mensual y balance
│   │   └── analytics.js         # Visualización de predicción y tabla de anomalías
│   ├── index.html               # Vista de autenticación (Login / Registro)
│   └── dashboard.html           # Vista principal del sistema
├── database/
│   ├── schema.sql               # Esquema de tablas, índices, constraints y claves foráneas
│   ├── seed.sql                 # Semilla de datos de prueba para desarrollo
│   └── queries.sql              # Consultas de verificación del modelo
├── docs/                        # Documentación complementaria del proyecto
├── .env.example                 # Plantilla de variables de entorno requeridas
├── .gitignore                   # Exclusiones de control de versiones
└── README.md                    # Manual integral del proyecto
```

---

## Requisitos

Para ejecutar el proyecto localmente se requiere:

* **Python:** Versión 3.10 o superior (recomendado 3.11+).
* **MySQL Server:** Versión 8.0 o superior en ejecución.
* **Git:** Para clonar el repositorio.
* **Navegador Web Moderno:** Chrome, Firefox, Edge o Safari con soporte para ES6+.

---

## Instalación

Sigue estos 9 pasos exactos para configurar y levantar el proyecto desde cero:

### 1. Crear entorno virtual
```bash
python -m venv .venv
```
*En Windows (PowerShell):* `.venv\Scripts\Activate.ps1`  
*En Linux / macOS:* `source .venv/bin/activate`

### 2. Instalar dependencias
```bash
pip install -r backend/requirements.txt
```

### 3. Configurar .env
Copia el archivo de plantilla a la raíz del proyecto:
```bash
cp .env.example .env
```
*(En Windows PowerShell: `Copy-Item .env.example .env`)*  
Abre `.env` y define tu contraseña de MySQL y la clave `SECRET_KEY`.

### 4. Crear base de datos
Asegúrate de que el servidor MySQL esté encendido. Si la base de datos no existe:
```sql
CREATE DATABASE finanzas_personales CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
```

### 5. Ejecutar schema.sql
Aplica la estructura relacional de tablas, restricciones e índices:
```bash
mysql -u root -p finanzas_personales < database/schema.sql
```
*En Windows PowerShell:*
```powershell
Get-Content database\schema.sql -Raw -Encoding UTF8 | mysql -u root -p --default-character-set=utf8mb4 finanzas_personales
```

### 6. Ejecutar seed.sql
Carga los datos iniciales de prueba:
```bash
mysql -u root -p finanzas_personales < database/seed.sql
```
*En Windows PowerShell:*
```powershell
Get-Content database\seed.sql -Raw -Encoding UTF8 | mysql -u root -p --default-character-set=utf8mb4 finanzas_personales
```

### 7. Iniciar backend
Navega al directorio backend e inicia el servidor ASGI:
```bash
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 8. Abrir frontend
En otra terminal, sirve los archivos estáticos:
```bash
cd frontend
python -m http.server 5500 --bind 127.0.0.1
```
Abre en tu navegador: [http://127.0.0.1:5500/index.html](http://127.0.0.1:5500/index.html).

### 9. Ejecutar tests
Ejecuta la suite completa de pruebas automatizadas:
```bash
pytest backend/tests -v
```

---

## Variables de entorno

El archivo `.env` en la raíz contiene las siguientes variables:

| Variable | Descripción | Valor por Defecto / Ejemplo |
|---|---|---|
| `APP_ENV` | Entorno de ejecución (`development` o `production`) | `development` |
| `APP_HOST` | Host local de FastAPI | `127.0.0.1` |
| `APP_PORT` | Puerto local de FastAPI | `8000` |
| `DEBUG` | Modo depuración | `True` |
| `DB_HOST` | Host de la base de datos MySQL | `127.0.0.1` |
| `DB_PORT` | Puerto de MySQL | `3306` |
| `DB_USER` | Usuario de MySQL | `root` |
| `DB_PASSWORD` | Contraseña de MySQL | *(definir según entorno)* |
| `DB_NAME` | Nombre de la base de datos | `finanzas_personales` |
| `CORS_ORIGINS` | Lista JSON de orígenes web permitidos | `["http://127.0.0.1:5500", "http://localhost:5500"]` |
| `SECRET_KEY` | Clave secreta para firmar tokens JWT | *(Generar con `secrets.token_urlsafe(64)`)* |
| `ALGORITHM` | Algoritmo de firma criptográfica | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Tiempo de vida del token de acceso | `60` |

> **Seguridad:** El archivo `.env` está estrictamente ignorado por Git en `.gitignore`. Nunca se versionan credenciales reales en el repositorio.

---

## MySQL

El modelo de datos está normalizado en Tercera Forma Normal (3FN) con motor InnoDB y juego de caracteres `utf8mb4`:

1. **`usuarios`**: Almacena usuarios registrados con `contrasena_hash` (bcrypt), `correo` único y constraints de validación.
2. **`categorias`**: Categorías de ingresos o gastos asignadas a cada usuario con restricción única `(id_usuario, tipo, nombre)`.
3. **`ingresos_gastos`**: Libro contable de movimientos con montos en tipo `DECIMAL(12, 2)` (precisión exacta sin error de coma flotante) y clave foránea compuesta `(id_usuario, id_categoria, tipo)` referenciando a `categorias`.

### Integridad Referencial
* **`ON DELETE RESTRICT`** uniforme: Previene la eliminación accidental de categorías o usuarios que conservan movimientos financieros.
* Índices optimizados `idx_mov_usuario_fecha` y `idx_mov_categoria` para búsquedas y agrupaciones de alto rendimiento.

---

## Ejecución local

* **Backend FastAPI:** Iniciar en `http://127.0.0.1:8000`
  * Documentación interactiva Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
  * Documentación ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
* **Frontend:** Servido en `http://127.0.0.1:5500/index.html` (o mediante la extensión Live Server de VS Code).

---

## Autenticación

El sistema implementa un esquema de autenticación robusto basado en el estándar JSON Web Token (JWT):

1. **Registro:** `POST /api/usuarios` recibe nombre, correo y contraseña en texto plano, la cual es cifrada inmediatamente con `bcrypt` (12 rondas de hashing y salt aleatorio).
2. **Login:** `POST /api/auth/login` valida las credenciales y genera un token JWT firmado (`HS256`) con caducidad establecida en `ACCESS_TOKEN_EXPIRE_MINUTES`.
3. **Protección:** Todos los endpoints financieros requieren la cabecera `Authorization: Bearer <token>`.
4. **Aislamiento:** La identidad del usuario se extrae del claim `sub` del token en la dependencia `get_current_user()`. Cualquier parámetro `id_usuario` enviado en el cuerpo o query string es ignorado por completo.
5. **Mitigación de Enumeración:** Los errores de autenticación devuelven un mensaje genérico `401 Unauthorized` idéntico para correos inexistentes o contraseñas incorrectas.

---

## Endpoints

Todos los endpoints marcados con 🔒 requieren autenticación mediante JWT.

### Salud
* `GET /` — Health check de la API (`200 OK`)

### Autenticación
* `POST /api/auth/login` — Iniciar sesión y obtener token JWT (`200 OK`, `401 Unauthorized`)
* `GET /api/auth/me` 🔒 — Obtener datos del usuario autenticado (`200 OK`, `401 Unauthorized`)

### Usuarios
* `POST /api/usuarios` — Registro de cuenta de usuario (`201 Created`, `400 Bad Request`, `409 Conflict`)

### Categorías
* `POST /api/categorias` 🔒 — Crear una categoría (`201 Created`, `409 Conflict`)
* `GET /api/categorias` 🔒 — Listar categorías del usuario autenticado (`200 OK`)

### Movimientos Financieros
* `POST /api/movimientos` 🔒 — Registrar un nuevo movimiento (`201 Created`, `400 Bad Request`)
* `GET /api/movimientos` 🔒 — Listar movimientos con filtros (`desde`, `hasta`, `categoria`) (`200 OK`)
* `PUT /api/movimientos/{id}` 🔒 — Actualizar un movimiento propio (`200 OK`, `404 Not Found`)
* `DELETE /api/movimientos/{id}` 🔒 — Eliminar un movimiento propio (`200 OK`, `404 Not Found`)

### Resumen Financiero
* `GET /api/resumen` 🔒 — Resumen del mes (`mes=YYYY-MM`) con total de ingresos, gastos y balance (`200 OK`)

### Módulo Analítico
* `GET /api/analitica/prediccion` 🔒 — Predicción de gastos del próximo mes con `LinearRegression` (`200 OK`)
* `GET /api/analitica/anomalias` 🔒 — Detección de gastos atípicos con `Z-Score > 1.5` (`200 OK`)

---

## Dashboard

El Dashboard (`dashboard.html`) proporciona una interfaz interactiva con las siguientes vistas y componentes:

* **Panel General:** KPIs con total de ingresos, total de gastos y balance neto del mes actual, junto con gráficos interactivos (distribución de gastos por categoría y tendencia histórica mensual).
* **Movimientos:** Tabla interactiva de ingresos y gastos con paginación visual, filtros por fecha y categoría, modal para registro y edición, y confirmación de eliminación.
* **Categorías:** Vista para crear y visualizar categorías propias clasificadas por tipo (ingreso / gasto).
* **Análisis Predictivo:** Tarjeta con predicción de gastos futuros y badge de nivel de confianza, complementada con la tabla de anomalías detectadas.
* **Guardián de Sesión:** Si no existe un token válido o ha expirado, redirige de forma transparente al usuario a `index.html`.

---

## Analytics

El módulo analítico (`backend/app/analytics/`) procesa exclusivamente datos de gastos (`tipo='gasto'`) del usuario autenticado:

### 1. Predicción de Gastos (`prediction.py`)
* Agrupa los gastos históricos por periodo mensual (`YYYY-MM`) usando Pandas.
* Aplica `sklearn.linear_model.LinearRegression` utilizando el índice cronológico como variable explicativa $X$ y el gasto acumulado como variable $y$.
* Genera la proyección para el siguiente mes cronológico, asignando un nivel de confianza (`alta` para $\ge 6$ meses, `media` para 2 a 5 meses, `baja` para 1 mes o menos).
* Garantiza que el valor estimado nunca sea negativo.

### 2. Detección de Anomalías (`anomalies.py`)
* Calcula la media ($\mu$) y desviación estándar ($\sigma$) del gasto agrupado por cada categoría.
* Computa el puntaje Z: $Z = \frac{x - \mu}{\sigma}$.
* Identifica como anomalías aquellos movimientos donde $|Z| > 1.5$ (umbral establecido).
* Controla divisiones por cero cuando la desviación estándar es 0 (gastos idénticos o muestra única).

---

## Tests

El proyecto cuenta con una cobertura integral de pruebas automatizadas:

## Tests

Ejecuta la suite completa de pruebas automatizadas:
```bash
pytest backend/tests -v
```

* **Total de Pruebas:** 194 tests (100% aprobadas).
* **Resultados:** 194 passed, 0 failed, 1 warning (deprecation menor de Starlette TestClient).
* **Arquitectura de Tests:** Utiliza dobles de prueba y repositorios en memoria (`InMemoryUsuarioRepository`, `InMemoryCategoriaRepository`, `InMemoryMovimientoRepository`), permitiendo ejecutar toda la suite de forma ultra rápida sin requerir una conexión activa a MySQL.

---

## Responsive

El diseño web es 100% adaptable mediante CSS Grid, Flexbox y media queries fluidas en los siguientes puntos de quiebre evaluados:

* **320px / 375px (Móviles pequeños y estándar):** Tablas apilables en formato tarjeta (`data-etiqueta`), menú lateral con cajón colapsable (`drawer`), botones accesibles y sin scroll horizontal accidental.
* **768px (Tablets):** Rejilla de 2 columnas para KPIs y distribución balanceada de formularios.
* **1024px (Laptops y Escritorio):** Barra lateral estática fijada a la izquierda, área de trabajo con margen dinámico y rejilla de gráficos en 2 columnas.
* **1440px / 1920px (Pantallas ultra anchas):** Contenedores centrados con padding balanceado y alturas proporcionales para gráficos.

---

## Moneda

* Todos los valores monetarios en la interfaz se visualizan estrictamente en **Pesos Colombianos (COP)** siguiendo el estándar internacional: `COP 1.500.000,00`.
* En la capa de almacenamiento y cálculo, los valores se manejan con tipo `DECIMAL(12, 2)` (en MySQL y Python `Decimal`), evitando cualquier inconsistencia o redondeo impreciso.
* No se utilizan abreviaturas foráneas ni símbolos ambiguos como `USD`, `US$` o `$`.

---

## Deployment en Render

> **Estado:** **Preparado para deployment en Render.**

El repositorio está completamente configurado y estructurado para su despliegue en la nube mediante los siguientes servicios:

### 1. Backend → Web Service (Python / FastAPI)
* **Root Directory:** `backend`
* **Environment:** `Python 3`
* **Build Command:** `pip install -r requirements.txt`
* **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
* **Health Check Path:** `GET /`

#### Variables de Entorno del Backend en Render:
* `APP_ENV=production`
* `DEBUG=false`
* `SECRET_KEY=<clave_aleatoria_estable_minimo_64_caracteres>`
* `CORS_ORIGINS=["https://<tu-frontend>.onrender.com"]`
* `ACCESS_TOKEN_EXPIRE_MINUTES=60`
* `DB_HOST=<host_mysql_remoto>`
* `DB_PORT=<puerto_mysql_remoto>`
* `DB_USER=<usuario_mysql>`
* `DB_PASSWORD=<contrasena_mysql>`
* `DB_NAME=<nombre_base_datos_mysql>`

### 2. Frontend → Static Site
* **Publish Directory:** `frontend`
* **Build Command:** *(dejar vacío, HTML/CSS/JS nativo)*

### 3. Conexión Backend ↔ Frontend
* **URL del backend:** Se obtiene al crear el Web Service (ej: `https://finanzas-api.onrender.com`).
* **URL del frontend:** Se obtiene al crear el Static Site (ej: `https://finanzas-app.onrender.com`).
* **Configuración en el cliente:** Se configura en `frontend/js/config.js` (`URL_API_POR_DEFECTO`) o mediante `<meta name="api-base-url" content="https://finanzas-api.onrender.com">` en `index.html` y `dashboard.html`.
* **Configuración CORS:** La URL pública del frontend se añade a la variable `CORS_ORIGINS` del backend en Render.

### 4. Base de Datos MySQL
* Alojada en un servicio compatible con MySQL 8.0 (ej: Aiven, Railway, TiDB o Clever Cloud).
* Inicialización ejecutando:
  ```bash
  mysql -h <DB_HOST> -P <DB_PORT> -u <DB_USER> -p < database/schema.sql
  mysql -h <DB_HOST> -P <DB_PORT> -u <DB_USER> -p < database/seed.sql
  ```

