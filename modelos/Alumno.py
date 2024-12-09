
from config.sql_config import db
from modelos.Carrera import Carrera
from modelos.Semestre import Semestre
from modelos.Seguidos import Seguidos

# IDs de admins
admin_ids = ['000000', '478483']

# Alumno model

class Alumno(db.Model):
    __tablename__ = 'alumnos'
    id = db.Column(db.Integer, primary_key=True)
    contrasenia = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100))
    bio = db.Column(db.String(200))
    rol = db.Column(db.String(20), default="usuario")
    carrera_id = db.Column(db.Integer, db.ForeignKey('carreras.id'), nullable=False)
    semestre_id = db.Column(db.Integer, db.ForeignKey('semestres.id'), nullable=False)


    semestre = db.relationship('Semestre', backref='alumnos')
    carrera = db.relationship('Carrera', backref='alumnos')

    


# Funciones CRUD (crear, leer, actualizar, eliminar)
# id, nombre, apellido, contrasenia, carrera, semestre 
def registrar_alumno(id,nombre, apellidos, contrasenia, carrera, semestre):
    try:
        
        if str(id) in admin_ids:
            rol = 'admin'
        else:
            rol = 'usuario'
        
        nuevo_alumno = Alumno(
            id = id,
            nombre = nombre,
            apellidos = apellidos,
            contrasenia = contrasenia,
            carrera_id = carrera,
            semestre_id = semestre,
            rol = rol,
            bio = "No tiene biografía aún.."
            
        )
        #transacción
        db.session.add(nuevo_alumno)
        db.session.commit()
        print("Alumno creado con éxito") 
        return nuevo_alumno
    except Exception as e:
        db.session.rollback()  
        print(f'Error al registrar el alumno: {str(e)}')

def obtener_seguidos(usuario):
    try:
        # Obtener los usuarios seguidos
        seguidos = Seguidos.query.filter(Seguidos.id_seguidor == usuario).all()

        # Extraemos los ids de los usuarios seguidos
        ids_seguidos = [seguido.id_siguiendo for seguido in seguidos]

        return ids_seguidos
    
    except Exception as e:
        print(f'Error al obtener los seguidos: {str(e)}')
        return None
    
def actualizar_bio(usuario, new_bio):
        try:
            
            
            alumno = Alumno.query.filter(Alumno.id == usuario).first()


            alumno.bio = new_bio

            db.session.commit()
            print("Biografía actualizada con éxito")
        except Exception as e:
            db.session.rollback()
            print(f'Error al actualizar la biografía: {str(e)}')