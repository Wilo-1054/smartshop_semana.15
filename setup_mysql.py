"""
setup_mysql.py — Crea la base de datos y tablas en MySQL usando PyMySQL.
Ejecutar UNA SOLA VEZ: python setup_mysql.py
"""

import pymysql

ROOT_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': '',        # ← Cambia si tu root tiene contraseña
    'port':     3306,
    'charset':  'utf8mb4',
}

DB_NAME = 'smartshop_db'

SQLS = [
    (f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci", "Base de datos"),
    ("USE smartshop_db", None),
    ("""CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario  INT          AUTO_INCREMENT PRIMARY KEY,
        nombre      VARCHAR(100) NOT NULL,
        mail        VARCHAR(150) NOT NULL UNIQUE,
        password    VARCHAR(255) NOT NULL,
        creado_en   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB""", "Tabla usuarios"),
    ("""CREATE TABLE IF NOT EXISTS productos_mysql (
        id          INT            AUTO_INCREMENT PRIMARY KEY,
        nombre      VARCHAR(120)   NOT NULL,
        cantidad    INT            NOT NULL DEFAULT 0,
        precio      DECIMAL(10,2)  NOT NULL DEFAULT 0.00,
        creado_en   TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
        actualizado TIMESTAMP      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB""", "Tabla productos_mysql"),
    ("""CREATE TABLE IF NOT EXISTS categorias (
        id          INT         AUTO_INCREMENT PRIMARY KEY,
        nombre      VARCHAR(80) NOT NULL UNIQUE,
        descripcion TEXT
    ) ENGINE=InnoDB""", "Tabla categorias"),
    ("""CREATE TABLE IF NOT EXISTS pedidos (
        id           INT           AUTO_INCREMENT PRIMARY KEY,
        id_usuario   INT           NOT NULL,
        total        DECIMAL(10,2) NOT NULL DEFAULT 0.00,
        estado       ENUM('pendiente','completado','cancelado') DEFAULT 'pendiente',
        creado_en    TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
    ) ENGINE=InnoDB""", "Tabla pedidos"),
    ("""INSERT IGNORE INTO usuarios (nombre, mail, password) VALUES
        ('Admin SmartShop', 'admin@smartshop.com', 'admin123'),
        ('Juan Pérez',      'juan@correo.com',     'pass456'),
        ('María López',     'maria@correo.com',    'pass789')""", "Usuarios de ejemplo"),
    ("""INSERT IGNORE INTO categorias (nombre, descripcion) VALUES
        ('Electrónica',  'Dispositivos y accesorios electrónicos'),
        ('Herramientas', 'Herramientas manuales y eléctricas'),
        ('Oficina',      'Artículos de papelería y oficina')""", "Categorías de ejemplo"),
    ("""INSERT INTO productos_mysql (nombre, cantidad, precio) VALUES
        ('Teclado mecánico',        15,  45.99),
        ('Mouse inalámbrico',       30,  22.50),
        ('Monitor 24 pulgadas',      8, 199.00),
        ('Taladro eléctrico',        5,  89.99),
        ('Grapadora de escritorio', 20,  12.00)""", "Productos de ejemplo"),
]


def setup():
    conn = None
    try:
        print("Conectando a MySQL con PyMySQL...")
        conn = pymysql.connect(**ROOT_CONFIG)
        with conn.cursor() as cursor:
            for sql, label in SQLS:
                cursor.execute(sql)
                if label:
                    print(f"✔ {label}")
        conn.commit()
        print("\n✅ Configuración completada. Ya puedes correr: python app.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Verifica que MySQL esté corriendo y que las credenciales sean correctas.")
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    setup()
