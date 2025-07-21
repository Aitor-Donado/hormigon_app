from flask import Flask, render_template, request, make_response, redirect, url_for, flash #, jsonify
import pickle
import pandas as pd
#import numpy as np
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cambia_esto_por_una_clave_secreta_segura'

# Cargar el modelo y el scaler al iniciar la aplicación
model = pickle.load(open('static/final_model.pkl', 'rb'))
scaler = pickle.load(open('static/scaler.pkl', 'rb'))

JWT_SECRET = 'cambia_esto_por_una_clave_jwt_segura'
JWT_ALGORITHM = 'HS256'

# Inicializar la base de datos y crear la tabla de usuarios si no existe
def init_db():
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    apellido TEXT NOT NULL,
                    contrasena TEXT NOT NULL
                )''')
    conn.commit()
    conn.close()

init_db()

def crear_jwt(nombre, roles):
    now = datetime.utcnow()
    payload = {
        'nombre': nombre,
        'roles': roles,
        'exp': int((now + timedelta(hours=3)).timestamp()),
        'iat': int(now.timestamp())
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def decodificar_jwt(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        print("❌ Token expirado")
    except jwt.InvalidTokenError as e:
        print(f"❌ Token inválido: {e}")
    except Exception as e:
        print(f"❌ Error desconocido al decodificar el token: {e}")
    return None

class RegistroForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    apellido = StringField('Apellido', validators=[DataRequired(), Length(max=100)])
    contrasena = PasswordField('Contraseña', validators=[DataRequired(), Length(min=4)])
    submit = SubmitField('Registrar')

class LoginForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=100)])
    contrasena = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Ingresar')

@app.route('/login', methods=['GET', 'POST'])
def login():
    mensaje = None
    form = LoginForm()
    if form.validate_on_submit():
        nombre = form.nombre.data
        contrasena = form.contrasena.data or ''
        try:
            conn = sqlite3.connect('usuarios.db')
            c = conn.cursor()
            c.execute('SELECT contrasena FROM usuarios WHERE nombre = ?', (nombre,))
            row = c.fetchone()
            conn.close()

            if row and check_password_hash(row[0], contrasena):
                roles = ['usuario']  # Asignar roles solo si el login es exitoso
                token = crear_jwt(nombre, roles)
                resp = make_response(redirect(url_for('index')))
                resp.set_cookie('jwt', token, httponly=True)
                flash('Ingreso exitoso')
                return resp
            else:
                mensaje = 'Usuario o contraseña incorrectos.'
        except Exception as e:
            mensaje = f'Error al ingresar: {str(e)}'
    return render_template('index.html', mensaje=mensaje, form=form, view='login')

@app.route('/', methods=['GET', 'POST'])
def index():
    usuario = None
    roles = []
    token = request.cookies.get('jwt')
    if token:
        payload = decodificar_jwt(token)
        print(f"Payload decodificado: {payload}")
        if payload:
            usuario = payload.get('nombre')
            print(f"Usuario autenticado: {usuario}")
            roles = payload.get('roles', [])
    mensaje = None
    prediction_text = None
    show_result = False
    if request.method == 'POST':
        try:
            cement = float(request.form['cement'])
            slag = float(request.form['slag'])
            ash = float(request.form['ash'])
            water = float(request.form['water'])
            superplastic = float(request.form['superplastic'])
            coarseagg = float(request.form['coarseagg'])
            fineagg = float(request.form['fineagg'])
            age = float(request.form['age'])
            input_data = pd.DataFrame({
                'cement': [cement],
                'slag': [slag],
                'ash': [ash],
                'water': [water],
                'superplastic': [superplastic],
                'coarseagg': [coarseagg],
                'fineagg': [fineagg],
                'age': [age]
            })
            scaled_data = scaler.transform(input_data)
            prediction = model.predict(scaled_data)
            prediction_rounded = round(prediction[0], 2)
            prediction_text = f'La dureza estimada del hormigón es: {prediction_rounded} MPa'
            show_result = True
        except Exception as e:
            prediction_text = f'Error: {str(e)}'
            show_result = True
    return render_template('index.html', view='predict', usuario=usuario, roles=roles, show_result=show_result, prediction_text=prediction_text)

@app.route('/register', methods=['GET', 'POST'])
def register():
    mensaje = None
    form = RegistroForm()
    if form.validate_on_submit():
        nombre = form.nombre.data
        apellido = form.apellido.data
        contrasena = form.contrasena.data or ''
        try:
            # Hashear la contraseña antes de guardarla
            contrasena_hash = generate_password_hash(contrasena)
            conn = sqlite3.connect('usuarios.db')
            c = conn.cursor()
            c.execute('INSERT INTO usuarios (nombre, apellido, contrasena) VALUES (?, ?, ?)',
                      (nombre, apellido, contrasena_hash))
            conn.commit()
            conn.close()
            # Login automático tras registro
            roles = ['usuario']
            token = crear_jwt(nombre, roles)
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('jwt', token, httponly=True)
            flash('Usuario registrado exitosamente')
            return resp
        except Exception as e:
            mensaje = f'Error al registrar usuario: {str(e)}'
        return render_template('index.html', mensaje=mensaje, form=form, view='register')
    return render_template('index.html', mensaje=mensaje, form=form, view='register')

@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('jwt', '', expires=0)
    flash('Sesión cerrada correctamente')
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 
    # app.run(debug=True)