# 🛒 SmartShop — Sistema de Inventario Flask

## Estructura del proyecto

```
smartshop/
├── app.py                  ← Rutas Flask
├── mysql_crud.py           ← CRUD MySQL
├── setup_mysql.py          ← Inicialización MySQL (ejecutar 1 vez)
├── requirements.txt
├── smartshop.db            ← Base de datos SQLite (se crea automáticamente)
├── inventario/
│   ├── inventario.py       ← Clase Inventario (SQLite)
│   ├── bd.py               ← Modelos SQLAlchemy ORM
│   └── productos.py        ← Persistencia TXT / JSON / CSV
├── conexion/
│   └── conexion.py         ← Configuración conexión MySQL
├── reportes/
│   └── reporte_pdf.py      ← Generador PDF con ReportLab
├── static/
│   └── data/               ← Archivos TXT, JSON, CSV generados
└── templates/              ← Plantillas Jinja2
```

## Instalación y ejecución

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Ejecutar la app (SQLite funciona de inmediato)
```bash
python app.py
```
Abre http://127.0.0.1:5000

### 3. (Opcional) Configurar MySQL
Edita `conexion/conexion.py` con tus credenciales, luego:
```bash
python setup_mysql.py
```

## Credenciales demo
- **Usuario:** `admin`
- **Contraseña:** `admin123`
