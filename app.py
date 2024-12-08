from datetime import datetime, timezone
from flask import Flask, redirect, render_template,request, session
from config.sql_config import connect_sql
from config.mongo_config import connect_mongo
from modelos.Alumno import Alumno, registrar_alumno, obtener_seguidos
import os

app = Flask(__name__)
app.secret_key = os.urandom(24) 

# Configura la base de datos
connect_sql(app)
db_mongo = connect_mongo()

@app.route('/')
def index():
    if 'usuario' in session:
        return redirect('/home')
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    # Verificar si el usuario ya está en la sesión
    if 'usuario' in session:
        return redirect('/home')

    if request.method == 'POST':
        
        id = request.form['id']
        contrasenia = request.form['contrasenia']

        usuario = Alumno.query.filter_by(id=id).first()

        # Verificar si el usuario existe
        if usuario is None:
            return render_template('login.html', error="El usuario no existe")

        # Verificar si la contraseña es correcta
        if usuario.contrasenia != contrasenia:
            return render_template('login.html', error="Contraseña incorrecta")
        
        print(f"Usuario encontrado: {usuario}")

        if id and usuario.contrasenia == contrasenia:
            # Guardar el usuario en la sesión
            session['usuario'] = usuario.id
            session['nombre'] = usuario.nombre
            session['rol'] = usuario.rol

            return redirect('/home')
            
    return render_template('login.html')

@app.route('/registro', methods=['GET','POST'])
def registrar():

    # Verificar si el usuario ya está en la sesión
    if 'usuario' in session:
        return redirect('/home')

    if request.method == 'POST':
        try:
            #obtener los datos del formulario
            #nombre, apellido, id, contrasenia, carrera, semestre
            nombre = request.form.get('nombre')
            apellido = request.form.get('apellido')
            id = request.form.get('id')
            contrasenia = request.form.get('contrasenia')
            carrera = request.form.get('carrera')
            semestre = request.form.get('semestre')

            # imprimir los datos recibidos
            print(f"Datos recibidos: nombre={nombre}, apellido={apellido}, id={id}, contrasenia={contrasenia}, carrera={carrera}, semestre={semestre}")

            #llamar a la función de registro
            registrar_alumno(id, nombre, apellido, contrasenia, carrera, semestre)

            
            return redirect('/home')
        except Exception as e:
            print(f"Error al registrar el alumno: {e}")
    return render_template('registro.html')

@app.route('/home', methods=['GET','POST'])
def home():

    # Verifica que el usuario esté en la sesión
    if 'usuario' not in session:
        return render_template('login.html')
    
    usuario = session['usuario']  # Recupera el usuario desde la sesión
    nombre = session['nombre']
    rol = session['rol']


    try:
        # Verificar si el usuario es admin
        if rol == 'admin':
            # Si es admin, obtener todos los posts
            posts = list(db_mongo.posts.find().sort('fecha', -1))
            return render_template('home.html', usuario=usuario, nombre=nombre, posts=posts)
        
        # Obtener los IDs de los usuarios seguidos
        ids_seguidos = obtener_seguidos(usuario)

        # Si el usuario no sigue a nadie, mostrar el mensaje
        if not ids_seguidos:
            mensaje = "Sigue a otros alumnos para ver sus posts."
            posts = []
            return render_template('home.html', usuario=usuario, nombre=nombre, posts=posts, mensaje=mensaje)
        
        # Si sigue a otros, obtener los posts de esos usuarios
        posts = list(db_mongo.posts.find({"id_alumno": {"$in": ids_seguidos}}).sort('fecha', -1))
    
    except Exception as e:
        print(f"Error al obtener los posts: {e}")
        posts = []  # Lista vacía si hay error

    if request.method == 'POST':
        try:
            # Obtener el contenido del post
            contenido = request.form.get('contenido')
            # Insertar el nuevo post en la base de datos
            db_mongo.posts.insert_one({
                'id_alumno': usuario,
                'nombre': nombre,
                'contenido': contenido,
                'fecha': datetime.now(timezone.utc).isoformat(),
                'likes': 0
            })
            print("Post insertado con éxito")
            return redirect('/home')
        except Exception as e:
            print(f"Error al insertar el post: {e}")
    
    
    return render_template('home.html', usuario=usuario, nombre = nombre, posts=posts)


@app.route('/explorar', methods=['GET'])
def explorar():
    # Verifica que el usuario esté autenticado
    if 'usuario' not in session:
        return redirect('/login')
    
    usuario = session['usuario']
    nombre = session['nombre']
    
    # Obtiene los IDs de los usuarios que ya está siguiendo
    usuarios_seguidos_ids = obtener_seguidos(usuario)

    # Obtiene todos los usuarios que NO está siguiendo
    usuarios_para_seguir = Alumno.query.filter(
        Alumno.id != usuario,  # Excluir al usuario actual
        ~Alumno.id.in_(usuarios_seguidos_ids)  # Excluir los que ya sigue
    ).all()

    return render_template('explorar.html', nombre = nombre, usuarios=usuarios_para_seguir)


@app.route('/logout')
def logout():
    session.pop('usuario', None)
    session.pop('nombre', None)
    session.pop('rol', None)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)




