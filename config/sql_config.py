# config/sql_config.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

# Instancia global de SQLAlchemy
db = SQLAlchemy()

# Cargar variables de entorno
load_dotenv()

# Obtener detalles de conexión desde las variables de entorno
USER = os.getenv('SQL_USER')
PASSWORD = os.getenv('SQL_PASSWORD')
HOST = os.getenv('SQL_HOST')
NAME = os.getenv('SQL_DATABASE')

def connect_sql(app):
    try:
        

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


def backup_sql():
    try:
        # Backup de SQL
        backup_folder = f"backup/sql/{datetime.now().strftime('%Y%m%d%H%M%S')}/"
        os.makedirs(backup_folder, exist_ok=True)
        backup_file = f"{backup_folder}backup.sql"

        command = f"mysqldump -u {USER} -p{PASSWORD} {NAME} > {backup_file}"
        os.system(command)
        print(f"Backup de SQL realizado con éxito en {backup_folder}")
        return "Backup de la base de datos SQL realizado con éxito "
    except Exception as e:
        print(f"Error al realizar el backup de SQL: {e}")
        return f"Error al realizar el backup de SQL"
        




