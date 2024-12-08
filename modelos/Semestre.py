
from config.sql_config import db

class Semestre(db.Model):
    __tablename__ = 'semestres'
    id = db.Column(db.Integer, primary_key=True)
    semestre = db.Column(db.String(10), nullable=False)

