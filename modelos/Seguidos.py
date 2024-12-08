from sqlalchemy import Integer, ForeignKey, PrimaryKeyConstraint, CheckConstraint
from config.sql_config import db


class Seguidos(db.Model):
    __tablename__ = 'seguidos'

    id_seguidor = db.Column(Integer, ForeignKey('alumnos.id', ondelete='CASCADE'), nullable=False)
    id_siguiendo = db.Column(Integer, ForeignKey('alumnos.id', ondelete='CASCADE'), nullable=False)

    # Define la clave primaria compuesta
    __table_args__ = (
        PrimaryKeyConstraint('id_seguidor', 'id_siguiendo', name='seguidos_pk'),
        CheckConstraint('id_seguidor != id_siguiendo', name='check_no_autoseguirse'),
    )


