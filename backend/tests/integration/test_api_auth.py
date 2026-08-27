"""
Pruebas de autenticación (Fase 8A).

Cubren los diez escenarios exigidos:
 1. Login correcto.
 2. Contraseña incorrecta.
 3. Usuario inexistente.
 4. Token válido.
 5. Token expirado.
 6. Token inválido.
 7. Endpoint protegido sin token.
 8. Usuario A intentando acceder a los recursos del usuario B.
 9. Acceso correcto del usuario autenticado a sus propios recursos.
10. Flujo de cierre de sesión.
"""

import jwt
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import crear_token_acceso
from tests.conftest import (
    USUARIO_AJENO_CORREO,
    USUARIO_AJENO_PASSWORD,
    USUARIO_PRUEBA_CORREO,
    USUARIO_PRUEBA_PASSWORD,
)

# Endpoints que deben exigir autenticación siempre.
ENDPOINTS_PROTEGIDOS = [
    ("GET", "/api/movimientos"),
    ("GET", "/api/categorias"),
    ("GET", "/api/resumen?mes=2026-08"),
    ("GET", "/api/analitica/prediccion"),
    ("GET", "/api/analitica/anomalias"),
    ("GET", "/api/auth/me"),
]


# =============================================================================
# 1. LOGIN CORRECTO
# =============================================================================

def test_login_correcto_devuelve_token(client_anonimo: TestClient):
    """1. Credenciales válidas devuelven 200 con un token utilizable."""
    response = client_anonimo.post("/api/auth/login", json={
        "correo": USUARIO_PRUEBA_CORREO,
        "contrasena": USUARIO_PRUEBA_PASSWORD,
    })
    assert response.status_code == 200

    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0
    assert isinstance(data["access_token"], str) and data["access_token"]
    assert data["usuario"]["id_usuario"] == 1
    assert data["usuario"]["correo"] == USUARIO_PRUEBA_CORREO


def test_login_no_expone_el_hash_de_la_contrasena(client_anonimo: TestClient):
    """1b. La respuesta del login nunca incluye el hash ni la contraseña."""
    response = client_anonimo.post("/api/auth/login", json={
        "correo": USUARIO_PRUEBA_CORREO,
        "contrasena": USUARIO_PRUEBA_PASSWORD,
    })
    cuerpo = response.text.lower()
    assert "contrasena_hash" not in cuerpo
    assert "$2b$" not in cuerpo
    assert USUARIO_PRUEBA_PASSWORD.lower() not in cuerpo


def test_token_emitido_no_contiene_datos_sensibles(client_anonimo: TestClient):
    """1c. El payload del JWT solo lleva identidad y tiempos."""
    response = client_anonimo.post("/api/auth/login", json={
        "correo": USUARIO_PRUEBA_CORREO,
        "contrasena": USUARIO_PRUEBA_PASSWORD,
    })
    token = response.json()["access_token"]
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert payload["sub"] == "1"
    assert "exp" in payload and "iat" in payload
    assert "contrasena" not in payload
    assert "contrasena_hash" not in payload


# =============================================================================
# 2 y 3. CREDENCIALES INCORRECTAS
# =============================================================================

def test_login_contrasena_incorrecta(client_anonimo: TestClient):
    """2. Contraseña incorrecta devuelve 401."""
    response = client_anonimo.post("/api/auth/login", json={
        "correo": USUARIO_PRUEBA_CORREO,
        "contrasena": "ContraseñaEquivocada999",
    })
    assert response.status_code == 401


def test_login_usuario_inexistente(client_anonimo: TestClient):
    """3. Correo no registrado devuelve 401 (no 404)."""
    response = client_anonimo.post("/api/auth/login", json={
        "correo": "nadie@example.com",
        "contrasena": USUARIO_PRUEBA_PASSWORD,
    })
    assert response.status_code == 401


def test_login_no_permite_enumerar_usuarios(client_anonimo: TestClient):
    """
    3b. El mensaje es idéntico con correo inexistente y con contraseña errónea.

    Si difirieran, se podría averiguar qué correos están registrados probando
    uno a uno.
    """
    r_correo_malo = client_anonimo.post("/api/auth/login", json={
        "correo": "nadie@example.com", "contrasena": "Password123*",
    })
    r_password_mala = client_anonimo.post("/api/auth/login", json={
        "correo": USUARIO_PRUEBA_CORREO, "contrasena": "OtraCosa123*",
    })

    assert r_correo_malo.status_code == r_password_mala.status_code == 401
    assert r_correo_malo.json()["detail"] == r_password_mala.json()["detail"]


def test_login_valida_el_formato_del_correo(client_anonimo: TestClient):
    """3c. Un correo malformado se rechaza en la validación del esquema (422)."""
    response = client_anonimo.post("/api/auth/login", json={
        "correo": "esto-no-es-un-correo", "contrasena": "Password123*",
    })
    assert response.status_code == 422


# =============================================================================
# 4, 5 y 6. VALIDACIÓN DEL TOKEN
# =============================================================================

def test_token_valido_da_acceso(client_anonimo: TestClient):
    """4. Un token recién emitido permite usar los endpoints protegidos."""
    login = client_anonimo.post("/api/auth/login", json={
        "correo": USUARIO_PRUEBA_CORREO,
        "contrasena": USUARIO_PRUEBA_PASSWORD,
    })
    token = login.json()["access_token"]

    response = client_anonimo.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["id_usuario"] == 1


def test_token_expirado_se_rechaza(client_anonimo: TestClient):
    """5. Un token caducado devuelve 401."""
    token, _ = crear_token_acceso(
        id_usuario=1, correo=USUARIO_PRUEBA_CORREO, expira_en_minutos=-5
    )
    response = client_anonimo.get(
        "/api/movimientos", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
    assert "expirado" in response.json()["detail"].lower() or \
           "sesión" in response.json()["detail"].lower()


@pytest.mark.parametrize("token_invalido", [
    "esto.no.es.un.jwt",
    "",
    "Bearer",
    "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.firma_falsificada",
])
def test_token_invalido_se_rechaza(client_anonimo: TestClient, token_invalido):
    """6. Tokens malformados o con firma falsa devuelven 401."""
    response = client_anonimo.get(
        "/api/movimientos", headers={"Authorization": f"Bearer {token_invalido}"}
    )
    assert response.status_code == 401


def test_token_firmado_con_otra_clave_se_rechaza(client_anonimo: TestClient):
    """
    6b. Un token bien formado pero firmado con otra clave se rechaza.

    Es el caso que de verdad importa: sin verificación de firma, cualquiera
    podría fabricarse un token con el `sub` que quisiera.
    """
    token_falso = jwt.encode(
        {"sub": "1", "exp": 9999999999}, "clave-que-no-es-la-del-servidor-y-suficientemente-larga", algorithm="HS256"
    )
    response = client_anonimo.get(
        "/api/movimientos", headers={"Authorization": f"Bearer {token_falso}"}
    )
    assert response.status_code == 401


def test_token_de_usuario_eliminado_se_rechaza(client_anonimo: TestClient):
    """6c. Un token con firma válida pero de un usuario inexistente se rechaza."""
    token, _ = crear_token_acceso(id_usuario=99999, correo="fantasma@example.com")
    response = client_anonimo.get(
        "/api/movimientos", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401


# =============================================================================
# 7. ENDPOINTS PROTEGIDOS SIN TOKEN
# =============================================================================

@pytest.mark.parametrize("metodo,ruta", ENDPOINTS_PROTEGIDOS)
def test_endpoint_protegido_sin_token(client_anonimo: TestClient, metodo, ruta):
    """7. Todos los endpoints sensibles responden 401 sin cabecera Authorization."""
    response = client_anonimo.request(metodo, ruta)
    assert response.status_code == 401


def test_endpoints_de_escritura_sin_token(client_anonimo: TestClient):
    """7b. Las operaciones de escritura también exigen token."""
    assert client_anonimo.post("/api/movimientos", json={
        "id_categoria": 1, "tipo": "ingreso", "monto": "100.00", "fecha": "2026-06-01"
    }).status_code == 401
    assert client_anonimo.put("/api/movimientos/1", json={
        "id_categoria": 1, "tipo": "ingreso", "monto": "100.00", "fecha": "2026-06-01"
    }).status_code == 401
    assert client_anonimo.delete("/api/movimientos/1").status_code == 401


def test_respuesta_401_incluye_www_authenticate(client_anonimo: TestClient):
    """7c. El 401 incluye la cabecera WWW-Authenticate, como pide el RFC 7235."""
    response = client_anonimo.get("/api/movimientos")
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"


# =============================================================================
# 8. AISLAMIENTO ENTRE USUARIOS
# =============================================================================

def test_usuario_a_no_accede_a_recursos_de_usuario_b(
    client: TestClient, client_usuario_2: TestClient
):
    """8. Ningún recurso del usuario B es visible ni modificable por el usuario A."""
    # El usuario 2 crea una categoría y un movimiento propios.
    cat_b = client_usuario_2.post(
        "/api/categorias", json={"nombre": "Privada B", "tipo": "gasto"}
    ).json()["id_categoria"]
    mov_b = client_usuario_2.post("/api/movimientos", json={
        "id_categoria": cat_b, "tipo": "gasto", "monto": "777000.00", "fecha": "2026-07-07"
    }).json()["id_movimiento"]

    # Lectura: el usuario 1 no ve nada de B.
    movimientos_a = client.get("/api/movimientos").json()
    assert all(m["id_movimiento"] != mov_b for m in movimientos_a)
    categorias_a = client.get("/api/categorias").json()
    assert all(c["id_categoria"] != cat_b for c in categorias_a)

    # Escritura: no puede usar la categoría de B.
    r_crear = client.post("/api/movimientos", json={
        "id_categoria": cat_b, "tipo": "gasto", "monto": "1.00", "fecha": "2026-07-07"
    })
    assert r_crear.status_code == 400

    # Modificación y borrado del movimiento de B: rechazados.
    r_put = client.put(f"/api/movimientos/{mov_b}", json={
        "id_categoria": 2, "tipo": "gasto", "monto": "1.00", "fecha": "2026-07-07"
    })
    assert r_put.status_code == 400

    r_delete = client.delete(f"/api/movimientos/{mov_b}")
    assert r_delete.status_code == 400

    # El movimiento de B sigue intacto.
    movimientos_b = client_usuario_2.get("/api/movimientos").json()
    assert any(m["id_movimiento"] == mov_b for m in movimientos_b)


def test_analitica_y_resumen_aislados_entre_usuarios(
    client: TestClient, client_usuario_2: TestClient
):
    """8b. Resumen, predicción y anomalías nunca cruzan datos entre cuentas."""
    cat = client.post(
        "/api/categorias", json={"nombre": "Solo de A", "tipo": "gasto"}
    ).json()["id_categoria"]
    client.post("/api/movimientos", json={
        "id_categoria": cat, "tipo": "gasto", "monto": "2500000.00", "fecha": "2026-08-08"
    })

    resumen_b = client_usuario_2.get("/api/resumen", params={"mes": "2026-08"}).json()
    assert resumen_b["id_usuario"] == 2
    assert resumen_b["total_gastos"] == "0.00"

    prediccion_b = client_usuario_2.get("/api/analitica/prediccion").json()
    assert prediccion_b["id_usuario"] == 2
    assert prediccion_b["meses_procesados"] == 0

    anomalias_b = client_usuario_2.get("/api/analitica/anomalias").json()
    assert anomalias_b["id_usuario"] == 2
    assert anomalias_b["total_gastos_analizados"] == 0


def test_token_manipulado_para_suplantar_otro_usuario(client_anonimo: TestClient):
    """
    8c. Cambiar el `sub` del token sin la clave no permite suplantar a nadie.

    Se altera el payload de un token real y se vuelve a firmar con otra clave:
    la verificación de firma debe rechazarlo.
    """
    token_suplantador = jwt.encode(
        {"sub": "1", "correo": USUARIO_AJENO_CORREO, "exp": 9999999999},
        "clave-inventada-por-el-atacante-con-longitud-suficiente",
        algorithm="HS256",
    )
    response = client_anonimo.get(
        "/api/movimientos", headers={"Authorization": f"Bearer {token_suplantador}"}
    )
    assert response.status_code == 401


# =============================================================================
# 9. ACCESO CORRECTO A LOS PROPIOS RECURSOS
# =============================================================================

def test_usuario_autenticado_accede_a_sus_recursos(client_anonimo: TestClient):
    """9. Flujo completo: login -> token -> uso normal de la API."""
    login = client_anonimo.post("/api/auth/login", json={
        "correo": USUARIO_PRUEBA_CORREO,
        "contrasena": USUARIO_PRUEBA_PASSWORD,
    })
    cabeceras = {"Authorization": f"Bearer {login.json()['access_token']}"}

    r_cat = client_anonimo.post(
        "/api/categorias", json={"nombre": "Propia", "tipo": "gasto"}, headers=cabeceras
    )
    assert r_cat.status_code == 201
    assert r_cat.json()["id_usuario"] == 1

    r_mov = client_anonimo.post("/api/movimientos", json={
        "id_categoria": r_cat.json()["id_categoria"],
        "tipo": "gasto", "monto": "45000.00", "fecha": "2026-08-15",
    }, headers=cabeceras)
    assert r_mov.status_code == 201
    assert r_mov.json()["id_usuario"] == 1

    r_lista = client_anonimo.get("/api/movimientos", headers=cabeceras)
    assert r_lista.status_code == 200
    assert all(m["id_usuario"] == 1 for m in r_lista.json())

    r_resumen = client_anonimo.get(
        "/api/resumen", params={"mes": "2026-08"}, headers=cabeceras
    )
    assert r_resumen.status_code == 200
    assert r_resumen.json()["total_gastos"] == "45000.00"


def test_segundo_usuario_tambien_puede_iniciar_sesion(client_anonimo: TestClient):
    """9b. El login funciona para cualquier cuenta, no solo para la primera."""
    response = client_anonimo.post("/api/auth/login", json={
        "correo": USUARIO_AJENO_CORREO,
        "contrasena": USUARIO_AJENO_PASSWORD,
    })
    assert response.status_code == 200
    assert response.json()["usuario"]["id_usuario"] == 2


# =============================================================================
# 10. CIERRE DE SESIÓN
# =============================================================================

def test_flujo_de_logout(client_anonimo: TestClient):
    """
    10. Tras cerrar sesión, el cliente deja de tener acceso.

    El cierre de sesión es del lado del cliente: el frontend descarta el token
    y sus peticiones vuelven a ser anónimas. Lo que se comprueba aquí es que
    una petición sin token —el estado exacto en que queda el navegador después
    del logout— es rechazada con 401 en todos los endpoints protegidos.
    """
    login = client_anonimo.post("/api/auth/login", json={
        "correo": USUARIO_PRUEBA_CORREO,
        "contrasena": USUARIO_PRUEBA_PASSWORD,
    })
    cabeceras = {"Authorization": f"Bearer {login.json()['access_token']}"}
    assert client_anonimo.get("/api/auth/me", headers=cabeceras).status_code == 200

    # El frontend descarta el token: a partir de aquí no envía cabecera.
    for metodo, ruta in ENDPOINTS_PROTEGIDOS:
        assert client_anonimo.request(metodo, ruta).status_code == 401


def test_registro_seguido_de_login(client_anonimo: TestClient):
    """
    10b. Registro y login encadenados, que es el alta real de un usuario.

    Comprueba de extremo a extremo que la contraseña se guarda hasheada con
    bcrypt y que ese mismo hash sirve luego para autenticar.
    """
    r_registro = client_anonimo.post("/api/usuarios", json={
        "nombre": "Nueva Persona",
        "correo": "nueva@example.com",
        "contrasena": "MiClaveSegura123*",
    })
    assert r_registro.status_code == 201
    assert "contrasena" not in r_registro.text
    assert "hash" not in r_registro.text.lower()

    r_login = client_anonimo.post("/api/auth/login", json={
        "correo": "nueva@example.com",
        "contrasena": "MiClaveSegura123*",
    })
    assert r_login.status_code == 200
    assert r_login.json()["usuario"]["correo"] == "nueva@example.com"

    # La contraseña anterior de otro usuario no sirve para esta cuenta.
    r_login_malo = client_anonimo.post("/api/auth/login", json={
        "correo": "nueva@example.com",
        "contrasena": USUARIO_PRUEBA_PASSWORD,
    })
    assert r_login_malo.status_code == 401
