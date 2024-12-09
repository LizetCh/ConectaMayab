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


def seguir(usuario, id_a_seguir):
    
    try:
        # Verificar si ya se está siguiendo
        ya_seguidos = Seguidos.query.filter_by(id_seguidor=usuario, id_siguiendo=id_a_seguir).first()
        if not ya_seguidos:
            nuevo_seguido = Seguidos(id_seguidor=usuario, id_siguiendo=id_a_seguir)
            db.session.add(nuevo_seguido)
            db.session.commit()
            print(f"Usuario {usuario} ahora sigue a {id_a_seguir}")
        else:
            print(f"Ya estás siguiendo al usuario {id_a_seguir}")
    except Exception as e:
            db.session.rollback()
            print(f"Error al seguir usuario: {e}")
