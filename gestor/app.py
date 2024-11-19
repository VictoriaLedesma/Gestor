import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from modelos.modelos import db, Usuario, Cuenta, TipoGasto, Transaccion

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/gestor"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "clave_secreta"
Bootstrap(app)

# Variable global para controlar la visibilidad


@app.route("/", methods=["GET", "POST"])
def inicio():
    if "usuario" not in session:
        return redirect(url_for("login"))
    usuario_id = session["usuario_id"]
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import io
    import base64


    mes=datetime.datetime.now().month - 1 
    
    meses = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    # Datos para el gráfico de barras
    totalIngreso = 0
    totalEgreso = 0
    categorias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    ingresos = [0] * len(categorias)
    egresos = [0] * len(categorias)

    for transaccion in Transaccion.query.filter_by(id_usuario=usuario_id).all():
        if transaccion.tipo == "gasto":
            egresos[transaccion.fecha.weekday()] += transaccion.monto
            totalIngreso += transaccion.monto
        elif transaccion.tipo == "ingreso":
            ingresos[transaccion.fecha.weekday()] += transaccion.monto
            totalEgreso += transaccion.monto
    fig, ax = plt.subplots()

# Ajustar la posición de las barras
    x = range(len(categorias))  # Posiciones base para las categorías
    ancho_barra = 0.4  # Ancho de cada barra

# Dibujar las barras con un desplazamiento

    colorEgresos="#3D63FF"
    colorIngresos="#D25AC8"

    ax.bar([pos - ancho_barra / 2 for pos in x], ingresos, width=ancho_barra, label="Ingresos", color= colorIngresos)
    ax.bar([pos + ancho_barra / 2 for pos in x], egresos, width=ancho_barra, label="Egresos",   color= colorEgresos, alpha=0.7)

# Ajustar etiquetas y leyenda
    ax.set_xticks(x)
    ax.set_xticklabels(categorias)
    ax.set_title("Transacciones de la semana")
    ax.legend()

# Convertir gráfico de barras a HTML
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode("utf-8")
    grafico_barras_html = f'<img src="data:image/png;base64,{image_base64}" />'
    buf.close()
    plt.close(fig)


     # Datos para el gráfico de torta
    import math
    import matplotlib.pyplot as plt

# Calculando los valores
    etiquetas = ["Alquiler", "Alimentos", "Transporte", "Otros"]
    if transacciones := Transaccion.query.filter_by(id_usuario=usuario_id, tipo="gasto").all() == []:
        valores = [25, 25, 25, 25]
    else:
        valores = [
    sum(transaccion.monto for transaccion in Transaccion.query.filter_by(id_usuario=usuario_id, tipo="gasto", id_tipo=1).all()) or 0,
    sum(transaccion.monto for transaccion in Transaccion.query.filter_by(id_usuario=usuario_id, tipo="gasto", id_tipo=2).all()) or 0,
    sum(transaccion.monto for transaccion in Transaccion.query.filter_by(id_usuario=usuario_id, tipo="gasto", id_tipo=3).all()) or 0,
    sum(transaccion.monto for transaccion in Transaccion.query.filter_by(id_usuario=usuario_id, tipo="gasto", id_tipo=4).all()) or 0
]

# Reemplazar NaN por 0

# Crear gráfico
    fig, ax = plt.subplots()
    ax.set_title("Distribución de Egresos")
    colores = ["#3D63FF", "#D45F5F", "#30B9FE", "#38E184"]
    ax.pie(valores, labels=etiquetas, autopct="%1.1f%%", colors=colores)
    plt.show()

    # Convertir gráfico de torta a HTML
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode("utf-8")
    grafico_torta_html = f'<img src="data:image/png;base64,{image_base64}" />'
    buf.close()
    plt.close(fig)

    tipos_gastos = obtener_categorias()
    saldo=Cuenta.query.filter_by(id_usuario=usuario_id).first().saldo
   
    lista_gastos = []
    lista_ingresos = []
    transacciones_gastos = Transaccion.query.filter_by(id_usuario=usuario_id, tipo="gasto").order_by(Transaccion.fecha.desc()).limit(3).all()
    transacciones_ingresos = Transaccion.query.filter_by(id_usuario=usuario_id, tipo="ingreso").order_by(Transaccion.fecha.desc()).limit(3).all()

    for transaccion in transacciones_gastos:
        categoria = TipoGasto.query.filter_by(id_tipo=transaccion.id_tipo).first().nombre_tipo
        monto = transaccion.monto
        lista_gastos.append({"categoria": categoria, "monto": monto})

    for transaccion in transacciones_ingresos:
        monto = transaccion.monto
        lista_ingresos.append({"monto": monto})

    # Asegurarse de que las listas tengan exactamente 3 elementos
    while len(lista_gastos) < 3:
        lista_gastos.append({"categoria": "", "monto": 0})

    while len(lista_ingresos) < 3:
        lista_ingresos.append({"monto": 0})
        


    return render_template(
        "inicio.html",
        usuario=session["usuario"],
        grafico_barras_html=grafico_barras_html,
        grafico_torta_html=grafico_torta_html,
        tipos_gastos=tipos_gastos,
        saldo=saldo,
        lista_ingresos=lista_ingresos,
        lista_gastos=lista_gastos,
        totalIngreso=totalIngreso,
        totalEgreso=totalEgreso,
        mes=meses[mes]
        
    )


def obtener_categorias():
    categorias = TipoGasto.query.all()
    return categorias


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Busca al usuario por correo
        user = Usuario.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            # Autenticación exitosa
            session["usuario"] = user.nombre
            session["usuario_id"] = user.id_usuario
            return redirect(url_for("inicio"))
        else:
            error = "Correo o contraseña incorrectos."

    return render_template("login.html", error=error)


@app.route("/registro", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Verificar que las contraseñas coinciden
        if password != confirm_password:
            error = "Las contraseñas no coinciden."
        else:
            # Verificar si el correo ya está registrado
            user = Usuario.query.filter_by(email=email).first()
            if user:
                error = "El correo electrónico ya está registrado."
            else:
                # Guardar el nuevo usuario
                hashed_password = generate_password_hash(
                    password, method="pbkdf2:sha256"
                )
                new_user = Usuario(
                    nombre=nombre,
                    apellido=apellido,
                    email=email,
                    password=hashed_password,
                )
                db.session.add(new_user)
                idUsuario=Usuario.query.filter_by(email=email).first().id_usuario
                new_account = Cuenta(
                    nombre_cuenta=nombre,
                    saldo=0.00,
                    id_usuario=idUsuario,
                )
                db.session.add(new_account)
               
                db.session.commit()

                flash("Te has registrado correctamente. Ahora puedes iniciar sesión.")
                return redirect(url_for("login"))

    return render_template("registro.html", error=error)


@app.route('/detalle/<caso>', methods=["GET"])
def detalle(caso):
    if "usuario" not in session:
        return redirect(url_for("login"))
    usuario_id = session["usuario_id"]
    mes=datetime.datetime.now().month - 1 
    
    meses = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]

    totalIngreso = 0
    totalEgreso = 0
    lista = []  # Inicializar la variable lista

    if caso == "ingresos":
       for transaccion in Transaccion.query.filter_by(id_usuario=usuario_id, tipo="ingreso").all():
        monto = transaccion.monto
        lista.append({"categoria": "Ingresos", "monto": monto, "fecha": transaccion.fecha, "descripcion":"---"})
        totalIngreso += monto
    elif caso == "egresos":
        for transaccion in Transaccion.query.filter_by(id_usuario=usuario_id, tipo="gasto").all():
            categoria = TipoGasto.query.filter_by(id_tipo=transaccion.id_tipo).first().nombre_tipo
            monto = transaccion.monto
            
            lista.append({"categoria": categoria, "monto": monto, "fecha": transaccion.fecha, "descripcion": transaccion.descripcion})
    totalEgreso = sum(transaccion.monto for transaccion in Transaccion.query.filter_by(id_usuario=usuario_id, tipo="gasto").all())
    return render_template(
        "ingresos.html",
        usuario=session["usuario"],
        lista=lista,
        mes=meses[mes],
        totalIngreso=totalIngreso,
        totalEgreso=totalEgreso,
    
    )






    
    return render_template("ingresos.html", lista=lista, tipo=tipo)

    
    
    


@app.route("/agregar_gasto", methods=["POST"])
def agregar_gasto():
    if request.method == "POST":
        descripcion = request.form["descripcion"]
        monto = request.form["monto"]
        tipo_gasto = request.form["categoria"]
        # fecha = request.form['fecha']

        # Asegúrate de que el usuario esté logueado
        if "usuario_id" in session:
            usuario_id = session["usuario_id"]
            idCuenta=Cuenta.query.filter_by(id_usuario=usuario_id).first().id_cuenta
            
        
            # Crear la nueva transacción de gasto
            nueva_transaccion = Transaccion(
                id_usuario=usuario_id,
                id_cuenta=idCuenta,  # Ajusta según corresponda
                descripcion=descripcion,
                monto=monto,
                tipo="gasto",  # O ajusta según corresponda
                id_tipo=tipo_gasto,  # Asegúrate de que tipo_gasto sea el ID de un tipo válido
            )
            
            montonuevo = float(Cuenta.query.filter_by(id_usuario=usuario_id).first().saldo) - float(monto)
            db.session.query(Cuenta).filter_by(id_usuario=usuario_id).update({"saldo": montonuevo})
            db.session.add(nueva_transaccion)
            db.session.commit()

            flash("Gasto agregado correctamente.")
            return redirect(
                url_for("inicio")
            )  # Redirigir al inicio después de agregar el gasto

    # Si el método es GET, solo mostrar el formulario (no hay tal formulario, es un modal, revisar)
    # return render_template('agregar_gasto.html')


@app.route("/agregar_ingreso", methods=["POST"])
def agregar_ingreso():
    if request.method == "POST":
        monto = request.form["monto"]

        # Asegúrate de que el usuario esté logueado
        if "usuario_id" in session:
            usuario_id = session["usuario_id"]
            cuenta=Cuenta.query.filter_by(id_usuario=usuario_id).first()
            # Crear la nueva transacción de gasto
            nueva_transaccion = Transaccion(
                id_usuario=usuario_id,
                id_cuenta=cuenta.id_cuenta,  # Ajusta según corresponda
                # Ajusta según corresponda
                monto=monto,
                tipo="ingreso",  # O ajusta según corresponda
            )
            montonuevo = float(cuenta.saldo) + float(monto)
            db.session.query(Cuenta).filter_by(id_usuario=usuario_id).update({"saldo": montonuevo})
            db.session.add(nueva_transaccion)
            db.session.commit()

            flash("Ingreso agregado correctamente.")
            return redirect(
                url_for("inicio")
            )  # Redirigir al inicio después de agregar el gasto


@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("login"))


# Configuración de la base de datos
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/gestor"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "clave_secreta"


db.init_app(app)


if __name__ == "__main__":
    app.run(debug=True)
