from pymongo.mongo_client import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()



def connect_mongo():
  try:
    # Obtener detalles de conexión de mongo
    MONGO_USER = os.getenv('MONGO_USER')
    MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')

    uri = f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@cluster0.9xwfo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    # Crear nuevo cliente y conectar a la base de datos
    mongo_client = MongoClient(uri, ssl=True, tlsAllowInvalidCertificates=True)
    db_mongo = mongo_client['alumnos']

    
    print("Conexión a MongoDB exitosa.")
    return db_mongo
  
  except Exception as e:
    print(f"Error al conectar a la base de datos: {e}")

  
