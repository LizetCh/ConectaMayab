#modelos/Carrera.py
# Carrera model

from config.sql_config import db

class Carrera(db.Model):
    __tablename__ = 'carreras'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)