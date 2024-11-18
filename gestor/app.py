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

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import io
    import base64

    # Datos para el gráfico de barras
    categorias = ["Enero", "Febrero", "Marzo", "Abril"]
    ingresos = [3000, 4000, 3500, 5000]
    egresos = [2000, 2500, 3000, 2800]

    fig, ax = plt.subplots()
    ax.bar(categorias, ingresos, label="Ingresos", color="green")
    ax.bar(categorias, egresos, label="Egresos", color="red", alpha=0.7)
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
    etiquetas = ["Alquiler", "Alimentos", "Transporte", "Otros"]
    valores = [1200, 800, 400, 600]

    fig, ax = plt.subplots()
    ax.pie(valores, labels=etiquetas, autopct="%1.1f%%")
    ax.set_title("Distribución de Egresos")

    # Convertir gráfico de torta a HTML
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode("utf-8")
    grafico_torta_html = f'<img src="data:image/png;base64,{image_base64}" />'
    buf.close()
    plt.close(fig)

    tipos_gastos = obtener_categorias()

    # Pasar la variable div_visible al template
    return render_template(
        "inicio.html",
        usuario=session["usuario"],
        grafico_barras_html=grafico_barras_html,
        grafico_torta_html=grafico_torta_html,
        tipos_gastos=tipos_gastos,
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


@app.route("/mostrar", methods=["GET", "POST"])
def mostrar():

    if request.method == "POST":
        # Recuperamos los datos del formulario
        monto = request.form["amount"]
        descripcion = request.form["description"]
        categoria = request.form["category"]

        # Obtener el usuario de la sesión
        if "usuario_id" in session:
            usuario_id = session["usuario_id"]

            # Obtener la cuenta y tipo de gasto asociados al usuario
            cuenta = Cuenta.query.filter_by(id_usuario=usuario_id).first()
            # tipo_gasto = TipoGasto.query.filter_by(id_tipo=categoria).first()
            # tipos_gasto = TipoGasto.query.all()

    # Recuperamos el saldo y otros datos para mostrar en la plantilla
    usuario = Usuario.query.filter_by(id_usuario=session.get("usuario_id")).first()
    cuentas = Cuenta.query.filter_by(id_usuario=session.get("usuario_id")).all()
    transacciones = Transaccion.query.filter_by(
        id_usuario=session.get("usuario_id")
    ).all()

    # Calcular saldo disponible, ingresos y egresos
    saldo_disponible = sum(cuenta.saldo for cuenta in cuentas)
    ingresos = sum(t.monto for t in transacciones if t.tipo == "ingreso")
    egresos = sum(t.monto for t in transacciones if t.tipo == "gasto")

    return render_template(
        "inicio.html",
        usuario=usuario.nombre,
        saldo_disponible=saldo_disponible,
        ingresos=ingresos,
        egresos=egresos,
    )


@app.route("/ingresos")
def ingresos():
    # Aquí puedes manejar la lógica relacionada con ingresos
    return render_template("ingresos.html")


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
