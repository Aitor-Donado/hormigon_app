# Aplicación Web para Predecir Dureza del Hormigón

## Funcionalidades técnicas añadidas

- **Registro de usuarios:** Permite crear usuarios con nombre, apellido y contraseña mediante un formulario protegido por CSRF.
- **Almacenamiento seguro de contraseñas:** Las contraseñas se almacenan de forma segura usando hash (bcrypt/werkzeug).
- **Inicio de sesión (login):** Los usuarios pueden autenticarse mediante un formulario de login. Si el login es exitoso, se genera un JWT con el nombre y los roles del usuario.
- **Gestión de sesión con JWT:** El estado de la sesión se guarda en una cookie segura que contiene un JWT firmado. En cada request, la aplicación valida el JWT para identificar al usuario y sus roles.
- **Protección CSRF:** Todos los formularios usan tokens CSRF para evitar ataques de tipo Cross-Site Request Forgery.
- **Cookies seguras:** El nombre de usuario y el JWT se almacenan en cookies con la opción `httponly` para mayor seguridad.
- **Roles de usuario:** El JWT incluye los roles del usuario, permitiendo una futura gestión de permisos y acceso a funcionalidades según el rol.
- **Mensajes personalizados:** Si el usuario está autenticado, se muestra un mensaje de bienvenida en la página principal.

---

Voy a crear una aplicación web sencilla con Flask para el backend y un formulario HTML básico para el frontend que permita predecir la dureza del hormigón usando un modelo entrenado con el algoritmo XGBoost.

## Estructura del proyecto

```
hormigon_app/
│
├── app.py                  # Backend Flask
├── templates/
│   └── index.html          # Frontend básico
├── static/
├── final_model.pkl         # Modelo entrenado
└── scaler.pkl              # Scaler guardado
```

## Instrucciones para ejecutar la aplicación

1. Guarda los archivos en la estructura de carpetas indicada.
2. Asegúrate de tener instaladas las dependencias necesarias:
   ```
   pip install flask pandas numpy scikit-learn xgboost
   ```
3. Ejecuta la aplicación con:
   ```
   python app.py
   ```
4. Abre tu navegador en http://localhost:5000

## Funcionamiento

1. El usuario ingresa los parámetros del hormigón en el formulario web.
2. Al enviar el formulario, los datos se envían al backend Flask.
3. Flask procesa los datos:
   - Convierte los valores a float
   - Crea un DataFrame
   - Aplica el scaler a los datos
   - Usa el modelo para hacer la predicción
4. El resultado se muestra al usuario en la misma página.

La aplicación es muy básica pero completamente funcional. Puedes mejorarla añadiendo:
- Mensajes de error más descriptivos
- Gráficos o visualizaciones adicionales

