import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.exceptions import AppException
from app.routes.usuarios_routes import router as usuarios_router
from app.routes.categorias_routes import router as categorias_router
from app.routes.movimientos_routes import router as movimientos_router
from app.routes.resumen_routes import router as resumen_router
from app.routes.analitica_routes import router as analitica_router

# Configuración de logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("finanzas_api")

app = FastAPI(
    title="API de Finanzas Personales",
    description="Backend RESTful con arquitectura por capas para gestión de finanzas personales.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuración de CORS
#
# Nunca se usa allow_origins=["*"]: la lista sale de CORS_ORIGINS y, si la
# variable llegara vacía, se cae a los orígenes locales de desarrollo en lugar
# de abrir la API a cualquier origen. Un comodín junto a allow_credentials=True
# es además una combinación que los navegadores rechazan.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Accept", "Content-Type"],
)


# =============================================================================
# MANEJADORES GLOBALES DE EXCEPCIONES
# =============================================================================

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Maneja excepciones de dominio de la aplicación."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Maneja errores de validación de esquemas Pydantic con formato consistente."""
    errors = []
    for err in exc.errors():
        field_name = " -> ".join(str(loc) for loc in err.get("loc", []))
        errors.append(f"{field_name}: {err.get('msg', 'Inválido')}")
    return JSONResponse(
        status_code=422,
        content={"detail": "Error de validación de datos de entrada", "errors": errors}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Maneja errores no controlados sin exponer información sensible."""
    logger.exception("Error no controlado durante la petición: %s", str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Ocurrió un error interno en el servidor."}
    )


# =============================================================================
# REGISTRO DE RUTAS
# =============================================================================

app.include_router(usuarios_router)
app.include_router(categorias_router)
app.include_router(movimientos_router)
app.include_router(resumen_router)
app.include_router(analitica_router)


@app.get("/", status_code=status.HTTP_200_OK, tags=["Salud"])
def health_check():
    """
    Ruta básica de verificación de estado de la API.
    """
    return {
        "status": "ok",
        "message": "API de Finanzas Personales funcionando correctamente"
    }


if __name__ == "__main__":
    # Arranque de conveniencia para desarrollo local.
    #
    # En producción NO se usa este bloque ni la recarga automática: el proceso
    # lo lanza el servidor con
    #   uvicorn main:app --host 0.0.0.0 --port $PORT
    # (véase la sección "Preparación para deployment" del README).
    import uvicorn

    es_desarrollo = settings.APP_ENV.lower() == "development"
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=es_desarrollo and settings.DEBUG
    )
