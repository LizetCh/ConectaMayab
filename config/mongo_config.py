from pymongo.mongo_client import MongoClient
import os
from datetime import datetime
import subprocess
from dotenv import load_dotenv

load_dotenv()

# Obtener detalles de conexión de mongo
MONGO_USER = os.getenv('MONGO_USER')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')

uri = f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@cluster0.9xwfo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

def connect_mongo():
  try:
    
    # Crear nuevo cliente y conectar a la base de datos
    mongo_client = MongoClient(uri, ssl=True, tlsAllowInvalidCertificates=True)
    db_mongo = mongo_client['alumnos']

    
    print("Conexión a MongoDB exitosa.")
    return db_mongo
  
  except Exception as e:
    print(f"Error al conectar a la base de datos: {e}")

# Función para hacer el respaldo de MongoDB usando mongodump
def backup_mongo():
    try:
        # Crear una carpeta de respaldo si no existe
        backup_folder = f"backup/mongo/{datetime.now().strftime('%Y%m%d%H%M%S')}/"
        os.makedirs(backup_folder, exist_ok=True)
        
        # Comando para realizar el backup de MongoDB Atlas usando la URI de conexión
        command = [
            "mongodump",
            f"--uri={uri}",
            f"--db=alumnos",
            f"--collection=posts",
            f"--out={backup_folder}"
        ]
        
        # Ejecutar el comando mongodump
        subprocess.run(command, check=True)
        print("Backup de MongoDB realizado con éxito en", backup_folder)
        return "Backup de MongoDB realizado con éxito"
    
    except subprocess.CalledProcessError as e:
        print(f"Error al realizar el backup de MongoDB: {e}")
        return f"Error al realizar el backup de MongoDB"
        
    except Exception as e:
        print(f"Error inesperado: {e}")
  
