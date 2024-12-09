from config.sql_config import db

class RComunidadAlumno(db.Model):
    __tablename__ = 'r_comunidades_alumnos'
    comunidad_id = db.Column(db.Integer, db.ForeignKey('comunidades.id'), primary_key=True)
    alumnos_id = db.Column(db.Integer, db.ForeignKey('alumnos.id'), primary_key=True)

