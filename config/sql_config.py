# config/sql_config.py
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

# Instancia global de SQLAlchemy
db = SQLAlchemy()

# Cargar variables de entorno
load_dotenv()

def connect_sql(app):
    try:
        # Obtener detalles de conexión desde las variables de entorno
        USER = os.getenv('SQL_USER')
        PASSWORD = os.getenv('SQL_PASSWORD')
        HOST = os.getenv('SQL_HOST')
        NAME = os.getenv('SQL_DATABASE')

        print(f"USER: {USER}, PASSWORD: {PASSWORD}, HOST: {HOST}, NAME: {NAME}")

        # Configuración de la base de datos
        app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{NAME}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Inicializar SQLAlchemy con la app
        db.init_app(app)

        # Crear todas las tablas definidas (esto se hace solo una vez al principio)
        with app.app_context():
            db.create_all()

        print("Conexión a SQL exitosa.")
    except Exception as e:
        print(f"Error al configurar la base de datos: {e}")




