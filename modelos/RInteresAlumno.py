from config.sql_config import db

class RInteresAlumno(db.Model):
    __tablename__ = 'r_intereses_alumnos'
    interes_id = db.Column(db.Integer, db.ForeignKey('intereses.id'), primary_key=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumnos.id'), primary_key=True)

    