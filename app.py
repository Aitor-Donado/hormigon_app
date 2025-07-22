import os
from flask import Flask, render_template, request, make_response, redirect, url_for, flash
import pickle
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
import jwt
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'cambia_esto_por_una_clave_secreta_segura')

# Configuración de SQLAlchemy para PostgreSQL
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'postgres')
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'hormigon_db')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'db')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT', '5432')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de usuario
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    contrasena = db.Column(db.String(200), nullable=False)

# Cargar el modelo y el scaler al iniciar la aplicación
model = pickle.load(open('static/final_model.pkl', 'rb'))
scaler = pickle.load(open('static/scaler.pkl', 'rb'))

JWT_SECRET = os.environ.get('JWT_SECRET', 'cambia_esto_por_una_clave_jwt_segura')
JWT_ALGORITHM = 'HS256'

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
            usuario = Usuario.query.filter_by(nombre=nombre).first()
            if usuario and check_password_hash(usuario.contrasena, contrasena):
                roles = ['usuario']
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
            contrasena_hash = generate_password_hash(contrasena)
            nuevo_usuario = Usuario(nombre=nombre, apellido=apellido, contrasena=contrasena_hash)
            db.session.add(nuevo_usuario)
            db.session.commit()
            roles = ['usuario']
            token = crear_jwt(nombre, roles)
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('jwt', token, httponly=True)
            flash('Usuario registrado exitosamente')
            return resp
        except IntegrityError:
            db.session.rollback()
            mensaje = 'El nombre de usuario ya existe.'
        except Exception as e:
            db.session.rollback()
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
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)