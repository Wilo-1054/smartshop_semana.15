import sqlite3
import os

DB_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'smartshop.db')


class Producto:
    def __init__(self, id, nombre, cantidad, precio):
        self.id       = id
        self.nombre   = nombre
        self.cantidad = cantidad
        self.precio   = precio

    def subtotal(self):
        return self.cantidad * self.precio

    def __repr__(self):
        return f'<Producto {self.nombre}>'


class Inventario:
    def _connect(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre   TEXT    NOT NULL,
                cantidad INTEGER NOT NULL DEFAULT 0,
                precio   REAL    NOT NULL DEFAULT 0.0
            )
        """)
        conn.commit()
        return conn

    def _row_to_producto(self, row):
        if row is None:
            return None
        return Producto(row['id'], row['nombre'], row['cantidad'], row['precio'])

    def obtener_todos(self):
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM productos ORDER BY id").fetchall()
        return [self._row_to_producto(r) for r in rows]

    def buscar_por_nombre(self, texto):
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM productos WHERE nombre LIKE ? ORDER BY id",
                (f'%{texto}%',)
            ).fetchall()
        return [self._row_to_producto(r) for r in rows]

    def obtener_por_id(self, producto_id):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM productos WHERE id=?", (producto_id,)
            ).fetchone()
        return self._row_to_producto(row)

    def agregar(self, nombre, cantidad, precio):
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO productos (nombre, cantidad, precio) VALUES (?, ?, ?)",
                (nombre, cantidad, precio)
            )
            conn.commit()
            return cursor.lastrowid

    def actualizar(self, producto_id, nombre, cantidad, precio):
        with self._connect() as conn:
            conn.execute(
                "UPDATE productos SET nombre=?, cantidad=?, precio=? WHERE id=?",
                (nombre, cantidad, precio, producto_id)
            )
            conn.commit()
            return True

    def eliminar(self, producto_id):
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM productos WHERE id=?", (producto_id,))
            conn.commit()
            return cursor.rowcount > 0

    def resumen(self):
        productos = self.obtener_todos()
        total_prods  = len(productos)
        total_units  = sum(p.cantidad for p in productos)
        valor_total  = sum(p.subtotal() for p in productos)
        return total_prods, total_units, valor_total
