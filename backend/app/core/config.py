import json
import os
import secrets
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

    # -------------------------------------------------------------------------
    # Autenticación JWT
    # -------------------------------------------------------------------------
    # SECRET_KEY firma los tokens: quien la conozca puede emitir tokens válidos
    # para cualquier usuario. Por eso NUNCA se escribe en el repositorio.
    #
    # En desarrollo, si la variable no está definida, se genera una clave
    # aleatoria distinta en cada arranque: la aplicación funciona sin
    # configuración previa y, de paso, los tokens caducan al reiniciar. En
    # producción esto sería un error grave (cada réplica firmaría con una clave
    # distinta), así que validar_produccion() lo impide explícitamente.
    SECRET_KEY: str = field(default_factory=lambda: os.getenv("SECRET_KEY") or secrets.token_urlsafe(64))
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    @property
    def SECRET_KEY_ES_EFIMERA(self) -> bool:
        """True cuando la clave se generó al vuelo por no estar configurada."""
        return not os.getenv("SECRET_KEY")

    def validar_produccion(self) -> List[str]:
        """
        Comprueba los requisitos que solo son exigibles fuera de desarrollo.

        Devuelve la lista de problemas encontrados (vacía si todo es correcto).
        Se invoca al arrancar la aplicación.
        """
        problemas: List[str] = []
        if self.APP_ENV.lower() != "production":
            return problemas

        if self.SECRET_KEY_ES_EFIMERA:
            problemas.append(
                "SECRET_KEY no está definida: en producción es obligatoria y debe ser estable "
                "entre reinicios y réplicas."
            )
        elif len(self.SECRET_KEY) < 32:
            problemas.append("SECRET_KEY es demasiado corta: se recomiendan 64 caracteres o más.")

        if not self.DB_PASSWORD:
            problemas.append("DB_PASSWORD está vacía en producción.")

        return problemas

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
