# 📊 Aplicación Web de Finanzas Personales con Dashboard Analítico

Aplicación web full-stack para el registro, control y análisis inteligente de finanzas personales, estructurada con arquitectura limpia por capas y preparada para despliegue continuo.

---

## 🎯 Objetivo General

Proveer una solución integral que permita a los usuarios registrar sus movimientos financieros (ingresos y gastos) clasificados por categorías, visualizando su balance en tiempo real, evaluando su comportamiento financiero y obteniendo proyecciones predictivas basadas en modelos de Machine Learning.

---

## 🛠️ Stack Tecnológico

* **Backend:** Python 3.10+ / FastAPI (Arquitectura RESTful por capas)
* **Frontend:** HTML5 Semántico, CSS3 Moderno (Grid, Flexbox, variables) y JavaScript Vanilla (Fetch API), sin frameworks ni dependencias externas
* **Base de Datos:** MySQL 8.0+ (Normalización 3FN con PyMySQL y SQL parametrizado)
* **Seguridad:** Hashing de contraseñas con `bcrypt` (rounds=12) y autenticación por **JWT** (`PyJWT`, HS256, con expiración)
* **Análisis de Datos:** Pandas, Scikit-learn (LinearRegression, Z-Score)
* **Testing:** Pytest, HTTPX (FastAPI TestClient)
* **Control de Versiones & Despliegue:** Git, GitHub, Render

---

## 📁 Estructura del Proyecto

```text
finanzas-personales/
├── backend/
│   ├── app/
│   │   ├── core/            # Configuración, seguridad (bcrypt + JWT), periodos, excepciones y dependencias
│   │   ├── database/        # Conexión, transacción context manager y pool MySQL
│   │   ├── routes/          # Controladores HTTP (Auth, Usuarios, Categorías, Movimientos, Resumen, Analítica)
│   │   ├── services/        # Lógica de negocio y validaciones de dominio
│   │   ├── repositories/    # Acceso a datos (SQL puro parametrizado)
│   │   ├── models/          # Entidades de dominio
│   │   ├── schemas/         # Validación y contratos de API con Pydantic
│   │   └── analytics/       # Módulo analítico: predicción (LinearRegression) y anomalías (Z-Score)
│   │       ├── prediction.py  # Preparación de datos, entrenamiento y predicción
│   │       └── anomalies.py   # Detección de gastos atípicos por Z-Score
│   ├── tests/               # Pruebas unitarias e integración (171 tests automatizados)
│   │   ├── unit/            # Tests de servicios, periodos, predicción, anomalías y seguridad
│   │   └── integration/     # Tests de endpoints HTTP, incluida la autenticación (test_api_auth.py)
│   ├── requirements.txt     # Dependencias de Python
│   └── main.py              # Punto de entrada de FastAPI
├── frontend/
│   ├── index.html           # Página de acceso: inicio de sesión y registro
│   ├── dashboard.html       # Panel: movimientos, categorías, resumen y análisis
│   ├── css/
│   │   ├── reset.css        # Normalización mínima del navegador
│   │   ├── variables.css    # Design tokens (color, espaciado, tipografía)
│   │   ├── layout.css       # Cabecera, navegación, rejillas y pie
│   │   ├── components.css   # Tarjetas, botones, formularios, tablas, diálogos
│   │   └── responsive.css   # Media queries (320 px → 1440 px+)
│   ├── js/
│   │   ├── config.js        # Configuración única (URL de la API, rutas)
│   │   ├── api.js           # Capa centralizada de fetch y errores
│   │   ├── ui.js            # Formateo (COP), estados de UI, diálogos y avisos
│   │   ├── sesion.js        # Sesión autenticada: token, usuario y cierre de sesión
│   │   ├── login.js         # Lógica de index.html (acceso y registro)
│   │   ├── app.js           # Lógica de dashboard.html (guardián y navegación)
│   │   ├── dashboard.js     # Vista principal (panel)
│   │   ├── movimientos.js   # CRUD y filtros de movimientos
│   │   ├── categorias.js    # Alta y consulta de categorías
│   │   ├── resumen.js       # Resumen mensual
│   │   └── analytics.js     # Predicción y anomalías
│   └── assets/
│       └── favicon.svg      # Icono de la aplicación
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

## 🔐 Seguridad

| Aspecto | Implementación |
|---|---|
| Contraseñas | `bcrypt` con coste 12 y salt aleatorio. Nunca en texto plano, nunca en las respuestas. |
| Autenticación | JWT firmado (`HS256` por defecto) con expiración. |
| Clave de firma | `SECRET_KEY` por variable de entorno; jamás en el repositorio. |
| Autorización | Dependencia `get_current_user()` en todos los endpoints sensibles. |
| Aislamiento | La identidad sale del token; `id_usuario` del cliente se ignora. |
| Enumeración de usuarios | Mensaje de error idéntico para correo inexistente y contraseña incorrecta. |
| SQL Injection | Consultas parametrizadas en toda la capa de repositorios. |
| Fugas de información | Los errores del motor MySQL solo van al log; el cliente recibe mensajes genéricos. |

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

# Autenticación JWT
SECRET_KEY=<genera la tuya, ver más abajo>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

`SECRET_KEY` firma los tokens de acceso. Genera una propia con:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

En **desarrollo** puede omitirse: la aplicación genera una clave efímera en
cada arranque y avisa por log (los tokens dejan de valer al reiniciar). En
**producción** es obligatoria y el arranque se aborta si falta.

> **Nota de Seguridad:** El archivo `.env` está expresamente excluido en `.gitignore`. Nunca subas credenciales reales ni la `SECRET_KEY` al repositorio.

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

> `--reload` es exclusivo del desarrollo local. El comando de producción no lo
> usa y escucha en el puerto que asigna el entorno: véase
> [Preparación para deployment](#-preparación-para-deployment).

---

## 🖥️ Guía de Inicio Rápido (Frontend)

El frontend es HTML5 semántico, CSS y JavaScript sin frameworks ni dependencias
externas: no necesita instalación, compilación ni gestor de paquetes. Solo debe
servirse por HTTP (no abrirlo con `file://`), porque el navegador exige un
origen válido para las peticiones a la API.

### 1. Levantar el backend

El frontend no funciona sin la API. Con el backend en marcha (ver la sección
anterior) en `http://127.0.0.1:8000`, abre **otra terminal**.

### 2. Servir el frontend

Cualquier servidor estático sirve. Con el propio Python:

```bash
cd frontend
python -m http.server 5500 --bind 127.0.0.1
```

Y abre [http://127.0.0.1:5500/index.html](http://127.0.0.1:5500/index.html),
que es la página de acceso.

> Con la extensión **Live Server** de VS Code (puerto 5500 por defecto) funciona
> igual: basta con abrir `frontend/index.html` con *Open with Live Server*.

### 3. Configuración de la API

La URL de la API se declara **en un único lugar** de todo el frontend, la
primera constante de `frontend/js/config.js`, que comparten las dos páginas:

```js
var URL_API_POR_DEFECTO = "http://127.0.0.1:8000";
```

El resto del código la consume a través de `js/api.js`. Para apuntar a otro
entorno (por ejemplo la URL pública de Render) basta con cambiar esa línea; no
hay ninguna otra URL de API repartida por los archivos. Opcionalmente, una
página puede sobrescribirla sin tocar el JavaScript añadiendo
`<meta name="api-base-url" content="...">` en su `<head>`.

El frontend **no contiene ningún secreto**: no maneja claves de API, tokens ni
credenciales de MySQL. Solo conoce la URL pública del backend.

### 4. Conexión con el backend (CORS)

El backend restringe los orígenes permitidos mediante `CORS_ORIGINS`. Los
puertos habituales de desarrollo ya vienen contemplados en `.env.example`:

```env
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:5500","http://localhost:5500","http://127.0.0.1:8000"]
```

Si sirves el frontend en otro puerto, añádelo a esa lista en tu `.env`.

### 5. Acceso, autenticación y sesión

El frontend son **dos páginas**:

| Página | Contenido |
|---|---|
| `index.html` | Acceso: formularios de inicio de sesión y de registro. Es el punto de entrada. |
| `dashboard.html` | Toda la lógica del proyecto: panel, movimientos, categorías, resumen y análisis. |

`dashboard.html` no muestra nada sin una sesión válida: al cargar valida el
token contra `GET /api/auth/me` y, si no es correcto, redirige a `index.html`.
A la inversa, `index.html` continúa automáticamente al panel cuando el token
guardado sigue siendo válido.

#### Flujo completo

```text
REGISTRO  ->  POST /api/usuarios      (contraseña hasheada con bcrypt)
LOGIN     ->  POST /api/auth/login    (verifica el hash y emite un JWT)
FRONTEND  ->  guarda el token en sessionStorage
API       ->  cada petición envía  Authorization: Bearer <token>
BACKEND   ->  valida firma y expiración, y deduce el usuario del token
LOGOUT    ->  el frontend descarta el token y vuelve al acceso
```

* **Crear cuenta** — `POST /api/usuarios`. La API cifra la contraseña con
  bcrypt (coste 12) y nunca la almacena en texto plano. Tras el alta, el
  frontend inicia sesión automáticamente con esas mismas credenciales.
* **Iniciar sesión** — correo y contraseña van en el **cuerpo** de
  `POST /api/auth/login`, nunca en la URL. El backend compara la contraseña
  con el hash almacenado y, si coincide, devuelve un JWT firmado.
* **Cerrar sesión** — el frontend descarta el token, oculta el panel y vuelve
  a `index.html`.

#### El token JWT

El token contiene **solo identidad y tiempos**: nunca la contraseña ni el hash.

| Campo | Contenido |
|---|---|
| `sub` | Identificador del usuario (en cadena, como exige el RFC 7519) |
| `correo` | Correo del usuario, para trazabilidad |
| `iat` | Momento de emisión |
| `exp` | Momento de expiración |

Se firma con `SECRET_KEY` usando `ALGORITHM` (por defecto `HS256`) y caduca a
los `ACCESS_TOKEN_EXPIRE_MINUTES` minutos (por defecto 60). Un token con la
firma alterada, caducado, o de un usuario que ya no existe, se rechaza con
`401`.

#### Dónde se guarda el token, y por qué

El token se guarda en **`sessionStorage`**. La alternativa a prueba de XSS
sería una cookie `httpOnly`, que el JavaScript no puede leer; se ha descartado
porque el frontend y la API son **dos servicios en orígenes distintos**, y una
cookie entre orígenes exigiría `SameSite=None; Secure` más protección CSRF
propia — un cambio de arquitectura que excede esta fase.

Las mitigaciones que sí se aplican:

* `sessionStorage` y no `localStorage`: el token muere al cerrar la pestaña,
  en lugar de quedarse en disco indefinidamente;
* el token **nunca** se escribe en consola ni se muestra en la interfaz;
* el token **nunca** viaja en la URL, solo en la cabecera `Authorization`;
* todo el renderizado usa `textContent`, nunca `innerHTML`: no hay ningún
  punto por el que inyectar el script que leería el token;
* los tokens caducan, así que uno robado tiene una ventana de uso limitada.

> **Riesgo residual conocido.** Un XSS en el frontend podría leer el token de
> `sessionStorage`. Se acepta de forma consciente y documentada; migrar a
> cookies `httpOnly` con CSRF es la evolución natural cuando el despliegue
> permita compartir dominio entre frontend y API.

#### Aislamiento por usuario

La identidad **siempre** procede del token. Los endpoints ya no aceptan
`id_usuario` como parámetro:

* enviarlo en la query string **se ignora**;
* enviarlo en el cuerpo JSON **se ignora**;
* no existe forma de leer, crear, modificar ni borrar datos de otra cuenta.

Las comprobaciones de pertenencia siguen además en la capa de servicio y en la
propia base de datos (la clave foránea compuesta `fk_movimientos_categoria`
garantiza a nivel de motor que la categoría de un movimiento es del mismo
usuario).

### 6. Moneda

Toda la interfaz muestra los importes en **pesos colombianos**, con
`Intl.NumberFormat("es-CO", { style: "currency", currency: "COP",
currencyDisplay: "code" })`, definido una sola vez en `js/ui.js`. El resultado
es `COP 1.500.000,00`: nunca se usa el símbolo `$`, ni `USD`, ni `US$`.

Es solo formato de presentación. Lo que se envía a la API sigue siendo un
número sin separadores ni símbolos, y la columna `monto` de MySQL continúa
siendo `DECIMAL(12,2)`. Por eso se conservan los dos decimales: redondear a
pesos enteros mostraría una cifra distinta de la almacenada.

---

## 📡 Endpoints Implementados

> **Todos los endpoints marcados con 🔒 exigen la cabecera
> `Authorization: Bearer <token>`.** Sin ella responden `401 Unauthorized` con
> `WWW-Authenticate: Bearer`. El usuario se deduce del token: **ningún endpoint
> acepta ya `id_usuario` como parámetro**.

### Salud y Estado
| Método | Endpoint | Propósito | Códigos |
|---|---|---|---|
| `GET` | `/` | Health check de la API | `200 OK` |

### Autenticación (Fase 8A)
| Método | Endpoint | Propósito | Request Body (JSON) | Códigos |
|---|---|---|---|---|
| `POST` | `/api/auth/login` | Verifica credenciales y emite un JWT | `{"correo": str, "contrasena": str}` | `200`, `401`, `422` |
| `GET` 🔒 | `/api/auth/me` | Usuario del token; valida la sesión | Ninguno | `200`, `401` |

Respuesta de `POST /api/auth/login`:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "usuario": { "id_usuario": 1, "nombre": "Ana Torres", "correo": "ana@example.com" }
}
```

Un `401` en el login usa **el mismo mensaje** tanto si el correo no existe como
si la contraseña es incorrecta, para no permitir enumerar las cuentas
registradas.

### Usuarios y Categorías
| Método | Endpoint | Propósito | Request Body (JSON) | Códigos |
|---|---|---|---|---|
| `POST` | `/api/usuarios` | Registro de nuevo usuario | `{"nombre": str, "correo": str, "contrasena": str}` | `201`, `400`, `409`, `422` |
| `POST` 🔒 | `/api/categorias` | Crea una categoría en la cuenta autenticada | `{"nombre": str, "tipo": "ingreso"\|"gasto"}` | `201`, `400`, `401`, `409`, `422` |
| `GET` 🔒 | `/api/categorias` | Categorías del usuario autenticado | Ninguno | `200`, `401` |

### Movimientos Financieros
| Método | Endpoint | Propósito | Request Body / Query Params | Códigos |
|---|---|---|---|---|
| `POST` 🔒 | `/api/movimientos` | Registrar ingreso o gasto | `{"id_categoria": int, "tipo": "ingreso"\|"gasto", "monto": Decimal, "fecha": date, "descripcion": str?}` | `201`, `400`, `401`, `404`, `422` |
| `GET` 🔒 | `/api/movimientos` | Listar los propios, con filtros | Query: `desde` (opt), `hasta` (opt), `categoria` (opt) | `200`, `400`, `401` |
| `PUT` 🔒 | `/api/movimientos/{id}` | Actualizar un movimiento propio | Path: `id`. Body: `MovimientoUpdate` | `200`, `400`, `401`, `404`, `422` |
| `DELETE` 🔒 | `/api/movimientos/{id}` | Eliminar un movimiento propio | Path: `id` | `200`, `400`, `401`, `404` |

### Reglas de Negocio en Movimientos:
1. **Precisión Monetaria:** El monto se valida y procesa como tipo `Decimal(12,2)` estrictamente positivo (`monto > 0`).
2. **Pertenencia de Categoría:** La categoría debe existir y pertenecer al mismo usuario (`id_usuario`).
3. **Coherencia de Tipo:** El `tipo` del movimiento (`ingreso`/`gasto`) debe coincidir exactamente con el `tipo` de la categoría asignada.
4. **Validación de Rangos:** En filtros de consulta, `desde` no puede ser posterior a `hasta`.
5. **Pertenencia del Movimiento:** `PUT` y `DELETE` rechazan (`400`) tocar un movimiento de otro usuario. El propietario se compara contra el usuario del token, que el cliente no puede falsificar.
5. **Aislamiento por Usuario:** Las consultas y modificaciones verifican la titularidad del recurso, impidiendo accesos o ediciones no autorizadas.
6. **Ordenamiento:** Los movimientos se listan ordenados de forma descendente (`fecha DESC, id_movimiento DESC`).

### Resumen Financiero
| Método | Endpoint | Propósito | Query Params | Códigos |
|---|---|---|---|---|
| `GET` 🔒 | `/api/resumen` | Resumen financiero de un mes | `mes` (req, `YYYY-MM`) | `200`, `400`, `401`, `422` |

**Parámetros:**

* `mes` — periodo en formato `YYYY-MM` (por ejemplo `2026-08`). Si el formato es incorrecto
  (`2026-8`, `agosto`) o el mes no existe (`2026-13`, `2026-00`) se devuelve `400`.

El usuario ya **no** se envía: sale del token.

**Ejemplo:**

```bash
curl -H "Authorization: Bearer $TOKEN" \
     "http://127.0.0.1:8000/api/resumen?mes=2026-08"
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

### 🔬 Módulo Analítico (Fase 6)

| Método | Endpoint | Propósito | Query Params | Códigos |
|---|---|---|---|---|
| `GET` 🔒 | `/api/analitica/prediccion` | Predicción de gastos del próximo mes | `id_usuario` (req) | `200 OK`, `404 Not Found` |
| `GET` 🔒 | `/api/analitica/anomalias` | Detección de gastos atípicos | `id_usuario` (req) | `200 OK`, `404 Not Found` |

#### Predicción de Gastos (LinearRegression)

Utiliza **Regresión Lineal** (`sklearn.linear_model.LinearRegression`) para predecir el gasto total del próximo mes a partir de la serie temporal mensual de gastos del usuario.

**Flujo de procesamiento (Pandas):**
1. Se obtienen los gastos históricos del repositorio (solo `tipo='gasto'`).
2. Se construye un `DataFrame` y se convierte la columna `fecha` a `datetime` con `pd.to_datetime()`.
3. Se agrupan los gastos por periodo mensual (`dt.to_period('M')` + `groupby().sum()`).
4. Se genera una variable numérica temporal (índice ordinal 0, 1, 2, …) como feature `X`.
5. Se entrena `LinearRegression()` con `X = índice temporal`, `y = gasto mensual`.
6. Se predice el valor del siguiente mes cronológico.

**Requisitos mínimos de datos:**
* **≥ 2 meses** de historial de gastos → regresión lineal, confianza `"media"` (2-5) o `"alta"` (≥6).
* **1 mes** → promedio simple, confianza `"baja"`.
* **0 meses** → `gasto_estimado = 0.0`, confianza `"baja"`.

Las predicciones negativas se truncan a `0.0` (no tiene sentido económico).

**Ejemplo de respuesta:**

```json
{
    "id_usuario": 1,
    "mes_predicho": "2026-08",
    "gasto_estimado": 2940000.0,
    "confianza": "alta",
    "razon": "Calculado con Regresión Lineal (7 meses procesados).",
    "meses_procesados": 7
}
```

#### Detección de Anomalías (Z-Score)

Detecta gastos atípicos utilizando **Z-Score agrupado por categoría**, conforme al repositorio del instructor.

**Fórmula:** `z = (monto - media_categoría) / desviación_estándar_categoría`

**Umbral:** `|Z| > 1.5` (definido por el ejercicio del instructor en `analitica.py` línea 54).

**Flujo de procesamiento (Pandas):**
1. Se construye un `DataFrame` con los gastos del usuario.
2. Se agrupan por `id_categoria` para calcular `mean` y `std` con `groupby().agg()`.
3. Se realiza `merge()` para asociar las estadísticas a cada gasto.
4. Se calcula el Z-Score con `np.where()` para evitar división por cero.
5. Se filtran los gastos cuyo `|z_score|` supera el umbral.

**Manejo de bordes:**
* `std = 0` (un solo gasto o todos iguales) → `z_score = 0` → no es anomalía.
* Sin gastos → lista vacía (no es un error).
* Sin anomalías → `total_anomalias = 0`, lista vacía con `200 OK`.

**Ejemplo de respuesta:**

```json
{
    "id_usuario": 1,
    "umbral_z_score": 1.5,
    "total_gastos_analizados": 7,
    "total_anomalias": 1,
    "anomalias": [
        {
            "id_movimiento": 7,
            "fecha": "2026-07-01",
            "monto": 5000000.0,
            "id_categoria": 1,
            "promedio_categoria": 831428.57,
            "z_score": 2.27,
            "descripcion": "Compra extraordinaria"
        }
    ]
}
```

---

## 🧪 Pruebas Automatizadas

La suite contiene **171 tests automatizados** cubriendo casos de éxito,
validaciones de borde, errores controlados, autenticación, aislamiento por
usuario y regresión:

```bash
.venv\Scripts\pytest backend/tests/ -v
```

Las pruebas usan repositorios en memoria (`backend/tests/conftest.py`), por lo
que **no necesitan MySQL en ejecución** y no tocan datos reales.

`backend/tests/integration/test_api_auth.py` cubre específicamente la
autenticación: login correcto, contraseña incorrecta, usuario inexistente,
token válido, expirado, malformado, firmado con otra clave o de un usuario
eliminado, endpoints protegidos sin token, intentos de acceso cruzado entre
usuarios y el flujo de cierre de sesión.

---

## 🚢 Preparación para deployment

> **Estado: preparado, NO desplegado.** Esta sección documenta la configuración
> necesaria para publicar el proyecto en Render. A día de hoy **no existe ningún
> despliegue**: la aplicación solo se ha ejecutado y verificado en local.

### Qué se ha preparado

| Punto | Estado |
|---|---|
| Puerto asignado por el entorno | `PORT` tiene prioridad sobre `APP_PORT` en `app/core/config.py` |
| Arranque sin `--reload` | La recarga solo se activa con `APP_ENV=development`; el comando de producción no la usa |
| Origen CORS configurable | `CORS_ORIGINS` se lee del entorno; nunca se usa `allow_origins=["*"]` |
| Cabecera `Authorization` en CORS | Incluida en `allow_headers`; sin ella el preflight fallaría y el token nunca llegaría |
| Credenciales fuera del código | Todas las variables sensibles salen de `.env` / variables de entorno |
| Clave de firma JWT | `SECRET_KEY` obligatoria en producción: el arranque se **aborta** si falta |
| URL de la API en el frontend | Declarada en un único punto (`frontend/js/config.js`) |

### Backend (Render — Web Service)

| Ajuste | Valor |
|---|---|
| Root Directory | `backend` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Runtime | Python 3.11+ |

El backend **debe** escuchar en `0.0.0.0` y en el puerto que entrega la
plataforma mediante la variable `PORT`; nunca en un puerto fijo de desarrollo.

### Variables de entorno en producción

```text
APP_ENV=production
DEBUG=false
DB_HOST=<host MySQL gestionado>
DB_PORT=3306
DB_USER=<usuario>
DB_PASSWORD=<contraseña>
DB_NAME=finanzas_personales
CORS_ORIGINS=["https://<dominio-del-frontend>"]

SECRET_KEY=<clave aleatoria de 64+ caracteres>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

`APP_HOST` y `APP_PORT` no se definen en producción: el host lo fija el comando
de arranque y el puerto lo aporta `PORT`.

**Sobre `SECRET_KEY`.** Es la clave que firma los tokens: quien la conozca
puede emitir tokens válidos para cualquier usuario. Genérala con

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

y guárdala **solo** en las variables de entorno del servicio, nunca en el
repositorio ni en este README. Debe ser **estable** entre reinicios y réplicas:
si cambia, todas las sesiones abiertas dejan de valer. Con `APP_ENV=production`
la aplicación se niega a arrancar si `SECRET_KEY` falta o es demasiado corta,
en lugar de generar una clave efímera silenciosamente.

> Render no ofrece MySQL gestionado. La base de datos debe alojarse en un
> servicio externo (Railway, Aiven, PlanetScale, Clever Cloud u otro) y el
> esquema crearse ejecutando `database/schema.sql` contra esa instancia.
> `database/seed.sql` es opcional y **no** debe cargarse en producción: sus
> hashes de contraseña son cadenas ficticias.

### Frontend

El frontend es estático (HTML, CSS y JavaScript sin build) y se publicará como
un **servicio independiente** (Render Static Site), no servido por FastAPI. Se
mantiene así la separación de responsabilidades de la arquitectura aprobada y
se evita añadir montajes de archivos estáticos al backend.

| Ajuste | Valor |
|---|---|
| Tipo | Static Site |
| Publish Directory | `frontend` |
| Build Command | (ninguno) |

Antes de publicar hay que apuntar el frontend al backend desplegado, cambiando
**una sola línea** en `frontend/js/config.js`:

```js
var URL_API_POR_DEFECTO = "https://<backend>.onrender.com";
```

Como alternativa sin tocar JavaScript, se puede añadir en el `<head>` de cada
página:

```html
<meta name="api-base-url" content="https://<backend>.onrender.com">
```

El dominio resultante del frontend debe añadirse a `CORS_ORIGINS` en el
backend, o el navegador bloqueará las peticiones.

### Antes de desplegar

* Verificar que `.env` **no** está versionado (`git check-ignore .env`).
* Ejecutar `database/schema.sql` en la instancia MySQL de producción.
* Confirmar que `CORS_ORIGINS` contiene el dominio real del frontend.
* Considerar desactivar `/docs` y `/redoc` si la API no debe documentarse
  públicamente (hoy están abiertos).
* Definir `SECRET_KEY` en el servicio y comprobar que el arranque no la rechaza.
* Servir el frontend por **HTTPS**: el token viaja en cada petición y sobre
  HTTP plano sería interceptable.
* Revisar `ACCESS_TOKEN_EXPIRE_MINUTES`: 60 minutos es razonable para uso
  interactivo; acortarlo reduce la ventana de un token robado.
