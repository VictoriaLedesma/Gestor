from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from modelos.modelos import db, Usuario, Cuenta, TipoGasto, Transaccion
import plotly.graph_objs as go
import plotly.io as pio

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/gestor'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'clave_secreta'
Bootstrap(app)
@app.route('/inicio')
def inicio():
    if 'usuario' in session:

        categorias = ["Enero", "Febrero", "Marzo", "Abril"]
        ingresos = [3000, 4000, 3500, 5000]
        egresos = [2000, 2500, 3000, 2800]

    # Crear barras
        barra_ingresos = go.Bar(name='Ingresos', x=categorias, y=ingresos, marker=dict(color='green'))
        barra_egresos = go.Bar(name='Egresos', x=categorias, y=egresos, marker=dict(color='red'))

    # Configurar diseño
        layout_barras = go.Layout(title='Ingresos y Egresos Mensuales', barmode='group')

    # Crear figura
        fig_barras = go.Figure(data=[barra_ingresos, barra_egresos], layout=layout_barras)
        config = {'displayModeBar': False,'responsive': True  }

    # Guardar el gráfico como HTML
  # Guardar el gráfico como HTML sin la barra de herramientas
        grafico_barras_html = pio.to_html(fig_barras, full_html=False,  config=config)


        etiquetas = ['Alquiler', 'Alimentos', 'Transporte', 'Otros']
        valores = [1200, 800, 400, 600]

        fig_torta = go.Figure(data=[go.Pie(labels=etiquetas, values=valores)])
        fig_torta.update_layout(title="Distribución de Egresos")
        grafico_torta_html = pio.to_html(fig_torta, full_html=False, config=config)

        return render_template('inicio.html',grafico_barras_html=grafico_barras_html,grafico_torta_html=grafico_torta_html)


        
    
    
    

    return redirect(url_for('login'))





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
        return render_template("home.html", usuario=session['usuario'])
    return redirect(url_for('login'))

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