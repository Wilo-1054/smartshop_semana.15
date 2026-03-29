"""
conexion/conexion.py — Gestión centralizada de la conexión MySQL.
Usa PyMySQL (sin problemas de auth_gssapi_client).
"""

import pymysql
import pymysql.cursors

# ── Credenciales ─────────────────────────────────────────────────────────────
DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': '',          # ← Cambia si tu MySQL tiene contraseña
    'database': 'smartshop_db',
    'port':     3306,
    'charset':  'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}
# ─────────────────────────────────────────────────────────────────────────────


def get_connection():
    """Abre y devuelve una conexión activa a MySQL via PyMySQL."""
    return pymysql.connect(**DB_CONFIG)


def close_connection(conn, cursor=None):
    """Cierra cursor y conexión de forma segura."""
    try:
        if cursor:
            cursor.close()
    except Exception:
        pass
    try:
        if conn:
            conn.close()
    except Exception:
        pass


def test_connection():
    """Comprueba si la conexión a MySQL es exitosa. Retorna (bool, mensaje)."""
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT VERSION()")
            version = cur.fetchone()
        return True, f"Conexión exitosa — MySQL {list(version.values())[0]}"
    except Exception as e:
        return False, str(e)
    finally:
        close_connection(conn)
