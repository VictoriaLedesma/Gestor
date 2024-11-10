from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from modelos.modelos import db, Usuario, Cuenta, TipoGasto, Transaccion


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://usuario:contraseña@localhost/gestor'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'clave_secreta'

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
            return redirect(url_for('home'))
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
                hashed_password = generate_password_hash(password, method='sha256')
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
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://usuario:contraseña@localhost/nombre_base_datos'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'clave_secreta'


db.init_app(app)

if __name__ == "__main__":
    app.run(debug=True)
