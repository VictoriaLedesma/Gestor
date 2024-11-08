from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

# Simula una base de datos de usuarios
usuarios = {"usuario1": "1234"}

@app.route("/")
def home():
    if 'usuario' in session:
        return render_template("home.html", usuario=session['usuario'])
    return redirect(url_for('login'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]
        if usuario in usuarios and usuarios[usuario] == password:
            session['usuario'] = usuario
            return redirect(url_for('home'))
        else:
            flash("Usuario o contraseña incorrectos")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
