from datetime import datetime
from tkinter import messagebox
from datetime import date
from doctest import script_from_examples
from django import forms

from django.core.exceptions import ValidationError
#from cgi import print_form
from flaskext.mysql import MySQL
from flask import Flask, redirect, url_for, render_template, request, flash
from pymysql import Date
import pyodbc
import datetime

app = Flask(__name__)
app.secret_key = "Redvital"

mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
#app.config['MYSQL_DATABASE_PASSWORD'] = 'R3dv1t4l/*'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'inventario_redvital'
mysql.init_app(app)

#server = 'tcp:10.5.10.5,2638'
#database = 'T_003002_2'
#username = 'dba'
#password = 'sql'
#cnxn = pyodbc.connect('DRIVER={"SQL Anywhere 17"};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
cnxn = pyodbc.connect('DSN=T_003002_2;UID=dba;PWD=sql')
cursor = cnxn.cursor()

@app.route('/')
def home():
    sql = "SELECT * FROM `ubicaciones`"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)

    ubicacion = cursor.fetchall()

    conn.commit()
    return render_template('inventario/index.html', ubicacion=ubicacion)


@app.route('/create')
def create():
    return render_template("inventario/create.html")


@app.route('/columnas')
def columnas():
    return render_template("inventario/columna.html")


@app.route('/paletas')
def paletas():
    sql = "SELECT * FROM `divisiones`"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)

    divisiones = cursor.fetchall()
    conn.commit()
    return render_template("inventario/paletas.html", divisiones=divisiones)


@app.route('/estantes')
def estantes():
    sql = "SELECT * FROM `estantes_productos`"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)

    estantes = cursor.fetchall()
    conn.commit()
    return render_template("inventario/estantes.html", estantes=estantes)


@app.route('/listar_estantes')
def listar_estantes():
    sql = "SELECT cod_estante,descrip_estante, ubicaciones.descrip_ubica FROM estantes_productos JOIN ubicaciones ON estantes_productos.cod_ubica = ubicaciones.cod_ubica"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)

    estantes = cursor.fetchall()
    conn.commit()
    return render_template("inventario/listar_estantes.html", estantes=estantes)


@app.route('/listar_columnas')
def listar_columnas():
    sql = "SELECT * FROM columnas"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)

    columnas = cursor.fetchall()
    conn.commit()
    return render_template("inventario/listar_columnas.html", columnas=columnas)


@app.route('/productos')
def productos():
    cursor = cnxn.cursor()
    sql = "SELECT TOP 500 tv_producto.cod_interno,tv_barra.cod_barra2,tv_producto.txt_descripcion_larga,tv_producto.txt_referencia,td_departamento.txt_descrip_dep,td_producto_adicional.titulo,CONVERT(NUMERIC(10,0),tv_existencia.saldo_producto),ta_marca.txt_marca,ta_precio_producto.mto_precio, ta_precio_producto.mto_moneda FROM tv_producto JOIN tv_existencia ON tv_producto.cod_interno = tv_existencia.cod_interno JOIN td_producto_adicional on tv_producto.cod_interno = td_producto_adicional.cod_interno JOIN ta_marca ON tv_producto.cod_marca = ta_marca.cod_marca JOIN ta_precio_producto ON tv_producto.cod_interno = ta_precio_producto.cod_interno JOIN tv_barra ON tv_producto.cod_interno = tv_barra.cod_interno JOIN td_departamento ON tv_producto.cod_departamento = td_departamento.cod_departamento where DBA.ta_precio_producto.cod_precio = 0 AND tv_existencia.saldo_producto > 0 ORDER BY tv_producto.cod_interno"
    cursor.execute(sql)
    productos = cursor.fetchall()
    cnxn.commit()
    return render_template("inventario/productos.html", productos=productos)


@app.route('/buscar_producto', methods=['POST'])
def buscar_producto():
    _codigo = request.form['txtCodigoProducto']
    if _codigo == '':
        flash('Recuerde llenar todos los campos')
        return redirect(url_for('productos'))

    cursor = cnxn.cursor()
    sql = "SELECT tv_producto.cod_interno,tv_barra.cod_barra2,tv_producto.txt_descripcion_larga,tv_producto.txt_referencia,td_departamento.txt_descrip_dep,td_producto_adicional.titulo,CONVERT(NUMERIC(10,0),tv_existencia.saldo_producto),ta_marca.txt_marca,ta_precio_producto.mto_precio, ta_precio_producto.mto_moneda FROM tv_producto JOIN tv_existencia ON tv_producto.cod_interno = tv_existencia.cod_interno JOIN td_producto_adicional on tv_producto.cod_interno = td_producto_adicional.cod_interno JOIN ta_marca ON tv_producto.cod_marca = ta_marca.cod_marca JOIN ta_precio_producto ON tv_producto.cod_interno = ta_precio_producto.cod_interno JOIN tv_barra ON tv_producto.cod_interno = tv_barra.cod_interno JOIN td_departamento ON tv_producto.cod_departamento = td_departamento.cod_departamento where DBA.ta_precio_producto.cod_precio = 0 AND tv_existencia.saldo_producto > 0 AND cod_barra2 = CONVERT(char,'%s') ORDER BY tv_producto.cod_interno" % _codigo
    cursor.execute(sql)
    productos_b = cursor.fetchall()
    cnxn.commit()
    return render_template("inventario/productos_b.html", productos_b=productos_b)

@app.route('/rotacion_producto', methods=['POST'])
def rotacion_producto():
    _Rif = 'J-50032880-0'
    _fechaInicio = request.form['txtFechaInicio']
    _fechaFin = request.form['txtFechaFin']
    if _fechaInicio == '' or _fechaFin == "":
        flash('Recuerde llenar todos los campos')
        return redirect(url_for('reporte_rotacion'))

    cursor = cnxn.cursor()

    #Ejecución de función de existencia de productos
    #rotacion = "{CALL sp_dwr_1000_0126('J-50032880-0','2022-12-10','2022-12-16')}"
    rotacion = "{CALL sp_dwr_1000_0126(%s,%s,%s)}"
    datos = (_Rif,_fechaInicio,_fechaFin)
    cursor.execute(rotacion,datos)

    rotacion_b = cursor.fetchall()
    cnxn.commit()
    return render_template("inventario/rotacion.html", rotacion_b=rotacion_b)



@app.route('/store', methods=['POST'])
def storage():
    _ubicacion = request.form['txtUbicacion']

    if _ubicacion == '':
        flash('Recuerde llenar todos los campos')
        return redirect(url_for('create'))

    sql = "INSERT INTO `ubicaciones` (`cod_ubica`, `descrip_ubica`) VALUES (NULL, %s);"
    datos = (_ubicacion)

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()
    return redirect('/')


@app.route('/unidades')
def unidades():
    sql = "SELECT * FROM `unidades_medida`"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)

    unidades = cursor.fetchall()
    conn.commit()
    return render_template("inventario/unidades.html", unidades=unidades)


@app.route('/store_unidades', methods=['POST'])
def store_unidades():
    _unidades = request.form['txtDescripcionUnidad']

    if _unidades == '':
        flash('Recuerde llenar todos los campos')
        return redirect(url_for('inventario/unidades'))

    sql = "INSERT INTO `unidades_medida` (`id_unidad`, `desc_unidad`) VALUES (NULL, %s);"
    datos = (_unidades)

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()
    return redirect('/')


@app.route('/store_paletas', methods=['POST'])
def store_paletas():
    _Descripcion = request.form['txtDescripcion']
    _CodDivision = request.form['txtCodDivision']

    if _Descripcion == '' or _CodDivision == '':
        flash('Recuerde llenar todos los campos')
        return redirect(url_for('paletas'))

    sql = "INSERT INTO `paleta` (`cod_paleta`, `nombre_paleta`, `cod_division`) VALUES (NULL, %s,%s);"
    datos = (_Descripcion, _CodDivision)

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()
    return redirect('/')


@app.route('/store_columnas', methods=['POST'])
def store_columnas():
    _columna = request.form['txtDescripcion']

    if _columna == '':
        flash('Recuerde llenar todos los campos')
        return redirect(url_for('columna'))

    sql = "INSERT INTO `columnas` (`cod_columna`, `descrip_columna`) VALUES (NULL, %s);"
    datos = (_columna)

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()
    return redirect('/')


@app.route('/destroy/<int:id>')
def destroy(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM `ubicaciones` WHERE cod_ubica = %s", (id))

    conn.commit()
    return redirect('/')


@app.route('/edit/<int:id>')
def edit(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ubicaciones WHERE cod_ubica =%s", (id))

    ubicacion = cursor.fetchall()

    conn.commit()
    return render_template('inventario/edit.html', ubicacion=ubicacion)


@app.route('/update', methods=['POST'])
def update():
    _ubicacion = request.form['txtUbicacion']
    id = request.form['txtID']

    sql = "UPDATE ubicaciones SET descrip_ubica = %s WHERE cod_ubica = %s;"
    datos = (_ubicacion, id)

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()
    # return render_template('inventario/index.html')
    return redirect('/')


@app.route('/existencias')
def existencias():
    sql = "SELECT * FROM columnas"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)

    lista_columnas = cursor.fetchall()
    conn.commit()

    sql2 = "SELECT * FROM estantes_productos"
    conn2 = mysql.connect()
    cursor = conn2.cursor()
    cursor.execute(sql2)

    lista_estantes = cursor.fetchall()
    conn2.commit()

    sql3 = "SELECT * FROM unidades_medida"
    conn3 = mysql.connect()
    cursor = conn3.cursor()
    cursor.execute(sql3)

    lista_unidad = cursor.fetchall()
    conn3.commit()

    return render_template("inventario/existencias.html", lista_columnas=lista_columnas, lista_estantes=lista_estantes, lista_unidad=lista_unidad)


@app.route('/listar_existencia')
def listar_existencia():
    sql = "SELECT * FROM `existencia_producto`"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    lista_existencia = cursor.fetchall()
    conn.commit()

    return render_template("inventario/listar_existencias.html", lista_existencia=lista_existencia)


@app.route('/store_existencia', methods=['POST'])
def store_existencia():
    _cod_producto = request.form['txtCodigoProducto']
    _cod_estante = request.form['txtCodEstante']
    _columna = request.form['txtColumna']
    _nivel = request.form['txtNivel']
    _paleta = request.form['txtPaleta']
    _fecha_movimiento = datetime.datetime.now()
    _unidad = request.form['txtCodUnidad']
    # _existencia_inicial = request.form['txtExistenciaInicial']
    _existencia_inicial = request.form['txtExistenciaFinal']
    _existencia_final = request.form['txtExistenciaFinal']
    _usuario = 1

    if _cod_producto == '':
        flash('Recuerde llenar todos los campos')
        return redirect(url_for('existencia'))

    sql = "INSERT INTO `existencia_producto`(`cod_producto`, `cod_estante`, `cod_columna`, `nivel`, `paleta`, `fecha_movimiento`, `existencia_inicial`, `existencia_final`, `id_unidad`, `cod_usuario`) VALUES (%s, %s,%s,%s,%s,%s,%s,%s,%s,%s);"

    datos = (_cod_producto, _cod_estante, _columna, _nivel, _paleta,
             _fecha_movimiento, _existencia_inicial, _existencia_final, _unidad, _usuario)

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()
    return redirect('/')


@app.route('/listar_unidades')
def listar_unidades():
    sql = "SELECT * FROM unidades_medida"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)

    unidades = cursor.fetchall()
    conn.commit()

    return render_template("inventario/listar_unidades.html", unidades=unidades)


@app.route('/entradas')
def entradas():
    return render_template("inventario/index.html")


@app.route('/salidas')
def salidas():
    return render_template("inventario/index.html")


@app.route('/recibir_pedido')
def recibir_pedido():
    return render_template("inventario/index.html")


@app.route('/registrar_pedido')
def registrar_pedido():
    return render_template("inventario/index.html")


@ app.route('/aprobar_pedido')
def aprobar_pedido():
    return render_template("inventario/index.html")


@app.route('/entrada_stock')
def entrada_stock():
    return render_template("inventario/index.html")


@app.route('/salida_stock')
def salida_stock():
    return render_template("inventario/index.html")


@app.route('/vencimiento')
def vencimiento():
    return render_template("inventario/index.html")


@app.route('/activar_producto')
def activar_producto():
    return render_template("inventario/index.html")


@ app.route('/reporte_movimientos')
def reporte_movimientos():
    return render_template("inventario/index.html")


@ app.route('/reporte_pedidos')
def reporte_pedidos():
    return render_template("inventario/index.html")


@ app.route('/reporte_oasis')
def reporte_oasis():
    return render_template("inventario/reporte_oasis.html")

@ app.route('/reporte_rotacion')
def reporte_rotacion():
    return render_template("inventario/reporte_rotacion.html")

@app.route('/rotacion')
def rotacion():
    return render_template("inventario/rotacion.html")


@app.route('/tipo_busqueda')
def tipo_busqueda():
    return render_template("inventario/productos.html")

if __name__ == '__main__':
    # DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run(port=5000, debug=True)
