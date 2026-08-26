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
├── database/                # Scripts DDL y DML (Fase 2)
├── docs/                    # Documentación técnica
├── .env.example             # Plantilla de variables de entorno
├── .gitignore               # Exclusiones de control de versiones
└── README.md                # Documentación principal
```

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
