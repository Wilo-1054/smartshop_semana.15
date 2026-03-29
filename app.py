from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from io import BytesIO
from inventario.inventario import Inventario
from inventario.bd import db, ProductoORM
import os

app = Flask(__name__)
app.secret_key = 'smartshop_clave_secreta_2026'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'smartshop.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

inv = Inventario()
USUARIO = 'admin'
CONTRASENA = 'admin123'


@app.route('/')
def home():
    busqueda = request.args.get('q', '').strip()
    productos = inv.buscar_por_nombre(busqueda) if busqueda else inv.obtener_todos()
    total_prods, total_units, valor_total = inv.resumen()

    # Datos MySQL (opcionales — si no conecta se muestran en cero)
    mysql_ok = False
    mysql_productos = []
    mysql_total_prods = mysql_total_units = mysql_valor_total = 0
    try:
        from mysql_crud import obtener_productos_mysql, resumen_mysql
        mysql_productos  = obtener_productos_mysql()
        resumen          = resumen_mysql()
        mysql_total_prods  = resumen['total_productos']
        mysql_total_units  = resumen['total_unidades']
        mysql_valor_total  = resumen['valor_total']
        mysql_ok = True
    except Exception:
        pass

    return render_template('index.html',
        productos=productos, busqueda=busqueda,
        total_prods=total_prods, total_units=total_units, valor_total=valor_total,
        mysql_ok=mysql_ok, mysql_productos=mysql_productos,
        mysql_total_prods=mysql_total_prods,
        mysql_total_units=mysql_total_units,
        mysql_valor_total=mysql_valor_total,
        usuario=session.get('usuario'))


@app.route('/about')
def about():
    return render_template('about.html', usuario=session.get('usuario'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'usuario' in session:
        return redirect(url_for('home'))
    error = None
    if request.method == 'POST':
        if request.form['usuario'] == USUARIO and request.form['contrasena'] == CONTRASENA:
            session['usuario'] = request.form['usuario']
            flash('¡Bienvenido de nuevo!', 'success')
            return redirect(url_for('home'))
        error = 'Usuario o contraseña incorrectos.'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))


@app.route('/agregar', methods=['POST'])
def agregar():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    nombre   = request.form['nombre'].strip()
    cantidad = int(request.form['cantidad'])
    precio   = float(request.form['precio'])
    inv.agregar(nombre, cantidad, precio)
    flash(f'Producto "{nombre}" agregado correctamente.', 'success')
    return redirect(url_for('home'))


@app.route('/editar/<int:producto_id>', methods=['GET', 'POST'])
def editar(producto_id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    producto = inv.obtener_por_id(producto_id)
    if not producto:
        flash('Producto no encontrado.', 'danger')
        return redirect(url_for('home'))
    if request.method == 'POST':
        nombre   = request.form['nombre'].strip()
        cantidad = int(request.form['cantidad'])
        precio   = float(request.form['precio'])
        inv.actualizar(producto_id, nombre, cantidad, precio)
        flash(f'Producto "{nombre}" actualizado.', 'success')
        return redirect(url_for('home'))
    return render_template('editar.html', producto=producto, usuario=session.get('usuario'))


@app.route('/eliminar/<int:producto_id>', methods=['POST'])
def eliminar(producto_id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    producto = inv.obtener_por_id(producto_id)
    if producto and inv.eliminar(producto_id):
        flash(f'Producto "{producto.nombre}" eliminado.', 'success')
    else:
        flash('No se pudo eliminar el producto.', 'danger')
    return redirect(url_for('home'))


@app.route('/datos', methods=['GET', 'POST'])
def datos():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    from inventario.productos import guardar_txt, leer_txt, guardar_json, leer_json, guardar_csv, leer_csv
    if request.method == 'POST':
        nombre   = request.form['nombre'].strip()
        cantidad = int(request.form['cantidad'])
        precio   = float(request.form['precio'])
        formato  = request.form['formato']
        registro = {'nombre': nombre, 'cantidad': cantidad, 'precio': precio}
        if formato == 'txt':
            guardar_txt(registro);  flash(f'"{nombre}" guardado en TXT.', 'success')
        elif formato == 'json':
            guardar_json(registro); flash(f'"{nombre}" guardado en JSON.', 'success')
        elif formato == 'csv':
            guardar_csv(registro);  flash(f'"{nombre}" guardado en CSV.', 'success')
        return redirect(url_for('datos'))
    return render_template('datos.html',
        datos_txt=leer_txt(), datos_json=leer_json(), datos_csv=leer_csv(),
        usuario=session.get('usuario'))


@app.route('/productos_orm')
def productos_orm():
    productos = ProductoORM.query.all()
    return render_template('productos.html', productos=productos, usuario=session.get('usuario'))


@app.route('/productos_orm/agregar', methods=['POST'])
def agregar_orm():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    nombre   = request.form['nombre'].strip()
    cantidad = int(request.form['cantidad'])
    precio   = float(request.form['precio'])
    db.session.add(ProductoORM(nombre=nombre, cantidad=cantidad, precio=precio))
    db.session.commit()
    flash(f'Producto "{nombre}" agregado via ORM.', 'success')
    return redirect(url_for('productos_orm'))


@app.route('/productos_orm/eliminar/<int:pid>', methods=['POST'])
def eliminar_orm(pid):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    p = ProductoORM.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    flash(f'Producto "{p.nombre}" eliminado via ORM.', 'success')
    return redirect(url_for('productos_orm'))


@app.route('/productos_orm/editar/<int:pid>', methods=['GET', 'POST'])
def editar_orm(pid):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    p = ProductoORM.query.get_or_404(pid)
    if request.method == 'POST':
        p.nombre   = request.form['nombre'].strip()
        p.cantidad = int(request.form['cantidad'])
        p.precio   = float(request.form['precio'])
        db.session.commit()
        flash(f'Producto "{p.nombre}" actualizado via ORM.', 'success')
        return redirect(url_for('productos_orm'))
    return render_template('editar_orm.html', producto=p, usuario=session.get('usuario'))


# ─────────────────────────────────────────────
# MYSQL — PRODUCTOS
# ─────────────────────────────────────────────

@app.route('/mysql/productos')
def mysql_productos():
    try:
        from mysql_crud import obtener_productos_mysql, resumen_mysql
        productos = obtener_productos_mysql()
        resumen   = resumen_mysql()
        mysql_ok  = True; error_msg = None
    except Exception as e:
        productos = []; resumen = {'total_productos': 0, 'total_unidades': 0, 'valor_total': 0}
        mysql_ok  = False; error_msg = str(e)
    return render_template('mysql_productos.html', productos=productos, resumen=resumen,
        mysql_ok=mysql_ok, error_msg=error_msg, usuario=session.get('usuario'))


@app.route('/mysql/productos/agregar', methods=['POST'])
def mysql_agregar_producto():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    try:
        from mysql_crud import insertar_producto_mysql
        nombre   = request.form['nombre'].strip()
        cantidad = int(request.form['cantidad'])
        precio   = float(request.form['precio'])
        insertar_producto_mysql(nombre, cantidad, precio)
        flash(f'Producto "{nombre}" agregado en MySQL.', 'success')
    except Exception as e:
        flash(f'Error MySQL: {e}', 'danger')
    return redirect(url_for('mysql_productos'))


@app.route('/mysql/productos/editar/<int:pid>', methods=['GET', 'POST'])
def mysql_editar_producto(pid):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    try:
        from mysql_crud import obtener_producto_mysql_por_id, actualizar_producto_mysql
        producto = obtener_producto_mysql_por_id(pid)
        if not producto:
            flash('Producto no encontrado en MySQL.', 'danger')
            return redirect(url_for('mysql_productos'))
        if request.method == 'POST':
            nombre   = request.form['nombre'].strip()
            cantidad = int(request.form['cantidad'])
            precio   = float(request.form['precio'])
            actualizar_producto_mysql(pid, nombre, cantidad, precio)
            flash(f'Producto "{nombre}" actualizado en MySQL.', 'success')
            return redirect(url_for('mysql_productos'))
        return render_template('mysql_editar_producto.html', producto=producto,
                               usuario=session.get('usuario'))
    except Exception as e:
        flash(f'Error MySQL: {e}', 'danger')
        return redirect(url_for('mysql_productos'))


@app.route('/mysql/productos/eliminar/<int:pid>', methods=['POST'])
def mysql_eliminar_producto(pid):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    try:
        from mysql_crud import eliminar_producto_mysql, obtener_producto_mysql_por_id
        p = obtener_producto_mysql_por_id(pid)
        eliminar_producto_mysql(pid)
        flash(f'Producto "{p["nombre"]}" eliminado de MySQL.', 'success')
    except Exception as e:
        flash(f'Error MySQL: {e}', 'danger')
    return redirect(url_for('mysql_productos'))


# ─────────────────────────────────────────────
# MYSQL — USUARIOS
# ─────────────────────────────────────────────

@app.route('/mysql/usuarios')
def mysql_usuarios():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    try:
        from mysql_crud import obtener_usuarios
        usuarios = obtener_usuarios()
        mysql_ok = True; error_msg = None
    except Exception as e:
        usuarios = []; mysql_ok = False; error_msg = str(e)
    return render_template('mysql_usuarios.html', usuarios=usuarios,
        mysql_ok=mysql_ok, error_msg=error_msg, usuario=session.get('usuario'))


@app.route('/mysql/usuarios/agregar', methods=['POST'])
def mysql_agregar_usuario():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    try:
        from mysql_crud import insertar_usuario
        nombre   = request.form['nombre'].strip()
        mail     = request.form['mail'].strip()
        password = request.form['password']
        insertar_usuario(nombre, mail, password)
        flash(f'Usuario "{nombre}" creado en MySQL.', 'success')
    except Exception as e:
        flash(f'Error MySQL: {e}', 'danger')
    return redirect(url_for('mysql_usuarios'))


@app.route('/mysql/usuarios/editar/<int:uid>', methods=['GET', 'POST'])
def mysql_editar_usuario(uid):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    try:
        from mysql_crud import obtener_usuario_por_id, actualizar_usuario
        u = obtener_usuario_por_id(uid)
        if not u:
            flash('Usuario no encontrado.', 'danger')
            return redirect(url_for('mysql_usuarios'))
        if request.method == 'POST':
            nombre = request.form['nombre'].strip()
            mail   = request.form['mail'].strip()
            actualizar_usuario(uid, nombre, mail)
            flash(f'Usuario "{nombre}" actualizado.', 'success')
            return redirect(url_for('mysql_usuarios'))
        return render_template('mysql_editar_usuario.html', u=u, usuario=session.get('usuario'))
    except Exception as e:
        flash(f'Error MySQL: {e}', 'danger')
        return redirect(url_for('mysql_usuarios'))


@app.route('/mysql/usuarios/eliminar/<int:uid>', methods=['POST'])
def mysql_eliminar_usuario(uid):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    try:
        from mysql_crud import eliminar_usuario, obtener_usuario_por_id
        u = obtener_usuario_por_id(uid)
        eliminar_usuario(uid)
        flash(f'Usuario "{u["nombre"]}" eliminado de MySQL.', 'success')
    except Exception as e:
        flash(f'Error MySQL: {e}', 'danger')
    return redirect(url_for('mysql_usuarios'))


@app.route('/mysql/test')
def mysql_test():
    from conexion.conexion import test_connection
    ok, mensaje = test_connection()
    if ok:
        flash(f'✅ {mensaje}', 'success')
    else:
        flash(f'❌ Error de conexión: {mensaje}', 'danger')
    return redirect(url_for('mysql_productos'))


@app.route('/reporte/pdf')
def reporte_pdf():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    try:
        from mysql_crud import obtener_productos_mysql
        from reportes.reporte_pdf import generar_reporte_completo
        from datetime import datetime

        productos = obtener_productos_mysql()
        clientes  = []
        try:
            from conexion.conexion import get_connection, close_connection
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("SELECT * FROM clientes ORDER BY id_cliente")
            clientes = cur.fetchall()
            close_connection(conn, cur)
        except Exception:
            pass

        facturas = []
        try:
            from conexion.conexion import get_connection, close_connection
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""
                SELECT f.id_factura, c.nombre AS nombre_cliente,
                       f.total, f.estado, f.creado_en
                FROM facturas f
                LEFT JOIN clientes c ON f.id_cliente = c.id_cliente
                ORDER BY f.id_factura DESC
            """)
            facturas = cur.fetchall()
            close_connection(conn, cur)
        except Exception:
            pass

        pdf_bytes  = generar_reporte_completo(productos, clientes, facturas)
        nombre_arch = f"smartshop_reporte_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        return send_file(BytesIO(pdf_bytes), mimetype='application/pdf',
                         as_attachment=True, download_name=nombre_arch)
    except Exception as e:
        flash(f'Error al generar PDF: {e}', 'danger')
        return redirect(url_for('mysql_productos'))


if __name__ == '__main__':
    app.run(debug=True)
