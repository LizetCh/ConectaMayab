from config.sql_config import db

class Comunidad(db.Model):
    __tablename__ = 'comunidades'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    