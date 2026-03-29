"""
mysql_crud.py — Operaciones CRUD sobre MySQL para SmartShop.
Usa PyMySQL con DictCursor (configurado en conexion/conexion.py).
"""

from conexion.conexion import get_connection, close_connection


# ══════════════════════════════════════════════════════
#  USUARIOS
# ══════════════════════════════════════════════════════

def obtener_usuarios():
    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_usuario, nombre, mail, creado_en FROM usuarios ORDER BY id_usuario")
        return cursor.fetchall()
    finally:
        close_connection(conn, cursor)


def insertar_usuario(nombre: str, mail: str, password: str) -> int:
    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nombre, mail, password) VALUES (%s, %s, %s)",
            (nombre.strip(), mail.strip(), password)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        close_connection(conn, cursor)


def actualizar_usuario(id_usuario: int, nombre: str, mail: str) -> bool:
    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuarios SET nombre=%s, mail=%s WHERE id_usuario=%s",
            (nombre.strip(), mail.strip(), id_usuario)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        close_connection(conn, cursor)


def eliminar_usuario(id_usuario: int) -> bool:
    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id_usuario=%s", (id_usuario,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        close_connection(conn, cursor)


def obtener_usuario_por_id(id_usuario: int):
    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_usuario, nombre, mail, creado_en FROM usuarios WHERE id_usuario=%s",
            (id_usuario,)
        )
        return cursor.fetchone()
    finally:
        close_connection(conn, cursor)


# ══════════════════════════════════════════════════════
#  PRODUCTOS MYSQL
# ══════════════════════════════════════════════════════

def obtener_productos_mysql():
    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos_mysql ORDER BY id")
        return cursor.fetchall()
    finally:
        close_connection(conn, cursor)


def obtener_producto_mysql_por_id(pid: int):
    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos_mysql WHERE id=%s", (pid,))
        return cursor.fetchone()
    finally:
        close_connection(conn, cursor)


def insertar_producto_mysql(nombre: str, cantidad: int, precio: float) -> int:
    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO productos_mysql (nombre, cantidad, precio) VALUES (%s, %s, %s)",
            (nombre.strip(), cantidad, precio)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        close_connection(conn, cursor)


def actualizar_producto_mysql(pid: int, nombre: str, cantidad: int, precio: float) -> bool:
    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE productos_mysql SET nombre=%s, cantidad=%s, precio=%s WHERE id=%s",
            (nombre.strip(), cantidad, precio, pid)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        close_connection(conn, cursor)


def eliminar_producto_mysql(pid: int) -> bool:
    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM productos_mysql WHERE id=%s", (pid,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        close_connection(conn, cursor)


def buscar_productos_mysql(texto: str) -> list:
    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM productos_mysql WHERE nombre LIKE %s ORDER BY id",
            (f"%{texto}%",)
        )
        return cursor.fetchall()
    finally:
        close_connection(conn, cursor)


def resumen_mysql() -> dict:
    conn = cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                COUNT(*)                            AS total_productos,
                COALESCE(SUM(cantidad), 0)          AS total_unidades,
                COALESCE(SUM(cantidad * precio), 0) AS valor_total
            FROM productos_mysql
        """)
        return cursor.fetchone()
    finally:
        close_connection(conn, cursor)
