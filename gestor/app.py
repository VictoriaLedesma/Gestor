from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from modelos.modelos import db, Usuario, Cuenta, TipoGasto, Transaccion

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/gestor'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'clave_secreta'
Bootstrap(app)

# Variable global para controlar la visibilidad

@app.route('/', methods=['GET', 'POST'])
def inicio():
    import matplotlib
    matplotlib.use('Agg')  # Configura el backend a 'Agg'
    import matplotlib.pyplot as plt

    import io
    import base64

    # Controlar la visibilidad del div

    # Datos para el gráfico de barras
    categorias = ["Enero", "Febrero", "Marzo", "Abril"]
    ingresos = [3000, 4000, 3500, 5000]
    egresos = [2000, 2500, 3000, 2800]

    fig, ax = plt.subplots()
    ax.bar(categorias, ingresos, label='Ingresos', color='green')
    ax.bar(categorias, egresos, label='Egresos', color='red', alpha=0.7)
    ax.legend()

    # Convertir gráfico de barras a HTML
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    grafico_barras_html = f'<img src="data:image/png;base64,{image_base64}" />'
    buf.close()
    plt.close(fig)

    # Datos para el gráfico de torta
    etiquetas = ['Alquiler', 'Alimentos', 'Transporte', 'Otros']
    valores = [1200, 800, 400, 600]

    fig, ax = plt.subplots()
    ax.pie(valores, labels=etiquetas, autopct='%1.1f%%')
    ax.set_title("Distribución de Egresos")

    # Convertir gráfico de torta a HTML
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    grafico_torta_html = f'<img src="data:image/png;base64,{image_base64}" />'
    buf.close()
    plt.close(fig)

    # Pasar la variable div_visible al template
    return render_template(
        'inicio.html',
        grafico_barras_html=grafico_barras_html,
        grafico_torta_html=grafico_torta_html,
    )

 


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Busca al usuario por correo
        user = Usuario.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            # Autenticación exitosa
            session['usuario'] = user.nombre
            return redirect(url_for('inicio'))
        else:
            error = "Correo o contraseña incorrectos."
    
    return render_template('login.html', error=error)

@app.route('/registro', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
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
                hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
                new_user = Usuario(nombre=nombre, email=email, password=hashed_password)
                db.session.add(new_user)
                db.session.commit()
                
                flash('Te has registrado correctamente. Ahora puedes iniciar sesión.')
                return redirect(url_for('login'))
    
    return render_template('registro.html', error=error)

@app.route("/")
def home():
    if 'usuario' in session:
        return render_template("inicio.html", usuario=session['usuario'])
    return redirect(url_for('login'))



@app.route('/home', methods=['GET', 'POST'])
def home_dashboard():
    if request.method == 'POST':
        # Recuperamos los datos del formulario
        monto = request.form['amount']
        descripcion = request.form['description']
        categoria = request.form['category']
        
        # Obtener el usuario de la sesión
        if 'usuario_id' in session:
            usuario_id = session['usuario_id']
            
            # Obtener la cuenta y tipo de gasto asociados al usuario
            cuenta = Cuenta.query.filter_by(id_usuario=usuario_id).first()
            tipo_gasto = TipoGasto.query.filter_by(id_tipo=categoria).first()
            tipos_gasto = TipoGasto.query.all()
            
            if cuenta and tipo_gasto:
                # Crear una nueva transacción
                nueva_transaccion = Transaccion(
                    id_usuario=usuario_id,
                    id_cuenta=cuenta.id_cuenta,
                    id_tipo=tipo_gasto.id_tipo,
                    descripcion=descripcion,
                    monto=monto,
                    tipo='gasto'  # O 'ingreso' según corresponda
                )
                
                # Guardamos la transacción en la base de datos
                db.session.add(nueva_transaccion)
                db.session.commit()
                
                flash('Gasto agregado correctamente.')
                return redirect(url_for('home_dashboard'))
    
    # Recuperamos el saldo y otros datos para mostrar en la plantilla
    usuario = Usuario.query.filter_by(id_usuario=session.get('usuario_id')).first()
    cuentas = Cuenta.query.filter_by(id_usuario=session.get('usuario_id')).all()
    transacciones = Transaccion.query.filter_by(id_usuario=session.get('usuario_id')).all()
    
    # Calcular saldo disponible, ingresos y egresos
    saldo_disponible = sum(cuenta.saldo for cuenta in cuentas)
    ingresos = sum(t.monto for t in transacciones if t.tipo == 'ingreso')
    egresos = sum(t.monto for t in transacciones if t.tipo == 'gasto')
    
    return render_template('inicio.html', usuario=usuario.nombre, saldo_disponible=saldo_disponible, ingresos=ingresos, egresos=egresos, tipos_gasto=tipos_gasto)




@app.route('/ingresos')
def ingresos():
    # Aquí puedes manejar la lógica relacionada con ingresos
    return render_template('ingresos.html')

@app.route('/agregar_gasto', methods=['GET', 'POST'])
def agregar_gasto():
    if request.method == 'POST':
        descripcion = request.form['descripcion']
        monto = request.form['monto']
        tipo_gasto = request.form['tipo_gasto']
        fecha = request.form['fecha']
        
        # Asegúrate de que el usuario esté logueado
        if 'usuario_id' in session:
            usuario_id = session['usuario_id']
            
            # Crear la nueva transacción de gasto
            nueva_transaccion = Transaccion(
                id_usuario=usuario_id,
                descripcion=descripcion,
                monto=monto,
                tipo='gasto',  # O ajusta según corresponda
                fecha=fecha,
                id_tipo=tipo_gasto  # Asegúrate de que tipo_gasto sea el ID de un tipo válido
            )
            
            db.session.add(nueva_transaccion)
            db.session.commit()
            
            flash('Gasto agregado correctamente.')
            return redirect(url_for('inicio'))  # Redirigir al inicio después de agregar el gasto
    
    # Si el método es GET, solo mostrar el formulario
    return render_template('agregar_gasto.html')


@app.route("/logout")
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/gestor'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'clave_secreta'


db.init_app(app)

if __name__ == "__main__":

    app.run(debug=True)


# INICIO
from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

# Sample data
income_transactions = [
    {"amount": 1234, "category": "Categoría", "date": "02/05/2024"},
    {"amount": 1234, "category": "Categoría", "date": "02/05/2024"},
    {"amount": 1234, "category": "Categoría", "date": "02/05/2024"},
]

expense_transactions = [
    {"amount": 1234, "category": "Categoría", "date": "02/05/2024"},
    {"amount": 1234, "category": "Categoría", "date": "02/05/2024"},
    {"amount": 1234, "category": "Categoría", "date": "02/05/2024"},
]

@app.route('/')
def home():
    data = {
        'available': 123456,
        'monthly_income': 123456,
        'monthly_expenses': 123456,
        'income_transactions': income_transactions,
        'expense_transactions': expense_transactions
    }
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)


# INGRESOS
from flask import Flask, render_template
from datetime import datetime
import io
import base64

app = Flask(__name__)

# Sample data
transactions = [
    {"amount": 1234, "category": "Categoría", "date": "02/05/2024"},
    {"amount": 1234, "category": "Categoría", "date": "02/05/2024"},
    {"amount": 1234, "category": "Categoría", "date": "02/05/2024"},
    {"amount": 1234, "category": "Categoría", "date": "02/05/2024"},
    {"amount": 1234, "category": "Categoría", "date": "02/05/2024"},
    {"amount": 1234, "category": "Categoría", "date": "02/05/2024"},
]

@app.route('/')
def home():
    data = {
        'available': 123456,
        'monthly_income': 123456,
        'monthly_expenses': 123456,
        'transactions': transactions
    }
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True) 