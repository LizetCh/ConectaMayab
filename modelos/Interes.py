from config.sql_config import db

class Interes(db.Model):
    __tablename__ = 'intereses'
    id = db.Column(db.Integer, primary_key=True)
    interes = db.Column(db.String(100), nullable=False)
