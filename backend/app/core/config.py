import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List
from dotenv import load_dotenv

# Cargar .env si existe en la raíz o backend
load_dotenv()


@dataclass(frozen=True)
class Settings:
    """
    Configuración centralizada e inmutable de la aplicación.
    Lee las variables de entorno de forma segura con valores por defecto para desarrollo.
    """
    APP_ENV: str = os.getenv("APP_ENV", "development")
    APP_HOST: str = os.getenv("APP_HOST", "127.0.0.1")
    # PORT tiene prioridad sobre APP_PORT: las plataformas de despliegue
    # (Render entre ellas) asignan el puerto por esa variable y la aplicación
    # debe escuchar en el que reciba, no en uno fijo de desarrollo.
    APP_PORT: int = int(os.getenv("PORT") or os.getenv("APP_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")

    # Configuración de Base de Datos MySQL
    DB_HOST: str = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "finanzas_personales")

    # Orígenes permitidos para CORS
    CORS_ORIGINS: List[str] = field(default_factory=lambda: Settings._parse_cors_origins(
        os.getenv("CORS_ORIGINS", '["http://localhost:3000", "http://127.0.0.1:5500", "http://localhost:5500", "http://127.0.0.1:8000"]')
    ))

    @staticmethod
    def _parse_cors_origins(raw: str) -> List[str]:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return parsed
            return [str(parsed)]
        except Exception:
            return [origin.strip() for origin in raw.split(",") if origin.strip()]

    def get_db_config(self) -> Dict[str, Any]:
        """
        Retorna el diccionario de configuración para la conexión con el driver de MySQL.
        """
        return {
            "host": self.DB_HOST,
            "port": self.DB_PORT,
            "user": self.DB_USER,
            "password": self.DB_PASSWORD,
            "database": self.DB_NAME,
            "charset": "utf8mb4",
            "autocommit": False,
        }


# Instancia única singleton para la aplicación
settings = Settings()
