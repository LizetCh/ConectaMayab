from datetime import datetime, timezone, timedelta
from bson import ObjectId
from flask import Flask, flash, redirect, render_template,request, session
from config.sql_config import backup_sql, connect_sql
from config.mongo_config import connect_mongo, backup_mongo
from modelos.Alumno import Alumno, registrar_alumno, obtener_seguidos, actualizar_bio
from modelos.Seguidos import seguir
import os

app = Flask(__name__)
app.secret_key = os.urandom(24) 

app.permanent_session_lifetime = timedelta(days=7)  # Duración de la sesión

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
            session.permanent = True
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

            if not nombre or not apellido or not id or not contrasenia or not carrera or not semestre:
                return render_template('registro.html', error="Todos los campos son obligatorios")
            
            if Alumno.query.filter_by(id=id).first():
                return render_template('registro.html', error="El usuario ya existe")

            #llamar a la función de registro
            nuevo_usuario = registrar_alumno(id, nombre, apellido, contrasenia, carrera, semestre)

            session['usuario'] = nuevo_usuario.id
            session['nombre'] = nuevo_usuario.nombre
            session['rol'] = nuevo_usuario.rol
            
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

    # Verifica que los valores estén correctos
    print(f"Usuario ID: {usuario}")
    print(f"Nombre: {nombre}")
    print(f"Rol: {rol}")


    if request.method == 'POST':
        try:
            # Obtener el contenido del post
            contenido = request.form.get('contenido')
            if contenido:
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
            return render_template('home.html', usuario=usuario, nombre=nombre, rol=rol, posts=posts, error="Error al insertar el post")
    
    # Obtener los posts de la base de datos
    try:
        mensaje = None
        # Verificar si el usuario es admin
        if rol == 'admin':
            # Si es admin, obtener todos los posts
            posts = list(db_mongo.posts.find().sort('fecha', -1))
        else:
            # Obtener los IDs de los usuarios seguidos
            ids_seguidos = obtener_seguidos(usuario)
            ids_seguidos.append(usuario)  # Agregar el ID del usuario actual
            posts = list(db_mongo.posts.find({"id_alumno": {"$in": ids_seguidos}}).sort('fecha', -1))
            
            # Si el usuario no sigue a nadie, mostrar el mensaje
            if not posts:
                if ids_seguidos.count(usuario) == 1:
                    mensaje = "Sigue a otros alumnos para ver sus posts."
                else:
                    mensaje = "Aún no hay posts..."
                    posts = [] 
           
        return render_template('home.html', usuario=usuario, nombre=nombre, posts=posts, rol=rol, mensaje=mensaje)
    except Exception as e:
        print(f"Error al obtener los posts: {e}")
        posts = []  # Lista vacía si hay error
    
    return render_template('home.html', usuario=usuario, nombre = nombre, rol=rol, posts=posts)


@app.route('/explorar', methods=['GET', 'POST'])
def explorar():
    # Verifica que el usuario esté autenticado
    if 'usuario' not in session:
        return redirect('/login')
    
    usuario = session['usuario']
    nombre = session['nombre']
    rol = session['rol']


    #obtiene todos los usuarios menos el usuario actual
    todos_usuarios = Alumno.query.filter(Alumno.id != usuario).all()
    
    # Obtiene los IDs de los usuarios que ya está siguiendo
    usuarios_seguidos_ids = obtener_seguidos(usuario)

    #lista de todos los usuarios, especificando si ya los sigue o no
    usuarios = []
    for alumno in todos_usuarios:
        usuarios.append({
            'id': alumno.id,
            'nombre': alumno.nombre,
            'apellido': alumno.apellidos,
            'carrera': alumno.carrera.nombre,
            'semestre': alumno.semestre.semestre,
            'siguiendo': alumno.id in usuarios_seguidos_ids

        })

    if request.method == 'POST':
        id_a_seguir = request.form.get('id_a_seguir')  # Usuario al que se desea seguir
        seguir(usuario, id_a_seguir)
        return redirect('/explorar')
        

    return render_template('explorar.html', nombre = nombre, usuarios=usuarios, rol=rol)


@app.route('/backup', methods=['GET', 'POST'])
def backup():
    mensaje = None

    # Verifica que el usuario esté en la sesión
    if 'usuario' not in session:
        return render_template('login.html')
    
    #verificar si el usuario es admin
    if session['rol'] != 'admin':
        return redirect('/home')
    
    usuario = session['usuario']
    nombre = session['nombre']
    rol = session['rol']


    if request.method == 'POST':
        if 'backup_sql' in request.form:
            mensaje = backup_sql()
            render_template('backup.html',mensaje=mensaje)
        elif 'backup_mongo' in request.form:
            mensaje = backup_mongo()
            render_template('backup.html',mensaje=mensaje)


    return render_template('backup.html',usuario=usuario, nombre= nombre, mensaje=mensaje, rol=rol)


@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    # Verifica que el usuario esté en la sesión
    if 'usuario' not in session:
        return redirect('/login')
    
    usuario = session['usuario']
    nombre = session['nombre']
    rol = session['rol']
    
    alumno = Alumno.query.filter(Alumno.id == usuario).first()

    if alumno:
        semestre = alumno.semestre.semestre  
        carrera = alumno.carrera.nombre
        bio = alumno.bio    
    else:
        semestre = None
        carrera = None


    # Obtener los posts de la base de datos
    
    posts = []
    try:
        mensaje = None
        
        posts = list(db_mongo.posts.find({'id_alumno': usuario}).sort('fecha', -1))
        if posts:
            print("Posts personales obtenidos con éxito")
        else:
            mensaje = "Aún no has escrito ningún post..."   
                 
                   
    except Exception as e:
        print(f"Error al obtener los posts: {e}")

    return render_template('perfil.html', usuario=usuario, nombre=nombre, rol=rol, semestre=semestre, carrera=carrera, bio=bio, mensaje=mensaje, posts=posts)

@app.route('/edit-bio')
def edit_bio():
    
    if 'usuario' not in session:
        return render_template('login.html')

    usuario = session['usuario']
    alumno = Alumno.query.filter(Alumno.id == usuario).first()
    return render_template('perfil.html', nombre=alumno.nombre, semestre=alumno.semestre.semestre,
                           carrera=alumno.carrera.nombre, bio=alumno.bio, bio_edit_mode=True)

@app.route('/update-bio', methods=['POST'])
def update_bio():

    if 'usuario' not in session:
        return render_template('login.html')

    new_bio = request.form['bio']
    print(f"Nueva biografía: {new_bio}")
    usuario = session['usuario']
    actualizar_bio(usuario, new_bio)  # Actualizamos la biografía en la base de datos
    
    return redirect('/perfil')


@app.route('/editar_post', methods=['POST'])
def editar_post():
    post_id = request.form.get('post_id')
    nuevo_contenido = request.form.get('contenido')

    # Actualizar contenido del post en MongoDB
    db_mongo.posts.update_one(
        {'_id': ObjectId(post_id)},
        {'$set': {'contenido': nuevo_contenido}}
    )
    flash('Post actualizado con éxito')

    return redirect('/perfil')

@app.route('/eliminar_post', methods=['POST'])
def eliminar_post():
    post_id = request.form.get('post_id')

    # Eliminar post en MongoDB
    db_mongo.posts.delete_one({'_id': ObjectId(post_id)})
    print('Post eliminado con éxito')

    return redirect('/perfil')



@app.route('/logout')
def logout():
    session.pop('usuario', None)
    session.pop('nombre', None)
    session.pop('rol', None)
    return redirect('/')






if __name__ == '__main__':
    app.run(debug=True)




