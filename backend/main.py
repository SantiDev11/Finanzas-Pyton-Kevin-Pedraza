from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="API de Finanzas Personales",
    description="Backend RESTful para gestión de finanzas personales y analítica predictiva.",
    version="1.0.0"
)

# Configuración básica de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", status_code=200)
def health_check():
    """
    Ruta básica de verificación de estado de la API.
    """
    return {
        "status": "ok",
        "message": "API de Finanzas Personales funcionando correctamente"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
