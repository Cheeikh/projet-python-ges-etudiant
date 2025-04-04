import os
import redis
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv
from src.utils.logger import Logger

# Chargement des variables d'environnement
load_dotenv()

class Database:
    """Classe singleton pour gérer les connexions aux bases de données"""
    _mongo_instance = None
    _redis_instance = None
    _logger = None
    
    @staticmethod
    def _get_logger():
        """Récupère l'instance du logger"""
        if Database._logger is None:
            Database._logger = Logger.get_instance()
        return Database._logger
    
    @staticmethod
    def get_mongo_connection():
        """Récupère une instance de connexion MongoDB"""
        if Database._mongo_instance is None:
            logger = Database._get_logger()
            mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
            
            # Options de connexion pour MongoDB Atlas avec timeouts augmentés
            connect_options = {
                'serverSelectionTimeoutMS': 30000,  # 30 secondes de timeout (augmenté)
                'connectTimeoutMS': 30000,         # 30 secondes pour la connexion (augmenté)
                'socketTimeoutMS': 30000,          # 30 secondes pour les opérations socket (ajouté)
                'retryWrites': True,
                'retryReads': True,                # Ajout de retryReads
                'maxIdleTimeMS': 60000,            # Temps maximum d'inactivité
                'appName': 'GestionEtudiants',     # Nom de l'application pour le monitoring
                'ssl': True                        # SSL explicite
            }
            
            try:
                Database._mongo_instance = MongoClient(mongodb_uri, **connect_options)
                # Test de connexion
                Database._mongo_instance.admin.command('ping')
                logger.info("Connexion à MongoDB établie avec succès")
            except ConnectionFailure as e:
                logger.error(f"Impossible de se connecter à MongoDB: {e}")
                raise
            except ServerSelectionTimeoutError as e:
                logger.error(f"Timeout lors de la connexion à MongoDB: {e}")
                raise
            except Exception as e:
                logger.error(f"Erreur inattendue lors de la connexion à MongoDB: {e}")
                raise
                
        return Database._mongo_instance
    
    @staticmethod
    def get_redis_connection():
        """Récupère une instance de connexion Redis"""
        if Database._redis_instance is None:
            logger = Database._get_logger()
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', 6379))
            redis_password = os.getenv('REDIS_PASSWORD', None)
            
            try:
                Database._redis_instance = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    password=redis_password,
                    decode_responses=True,
                    socket_timeout=15,           # Augmenté à 15 secondes
                    socket_connect_timeout=15    # Augmenté à 15 secondes
                )
                # Test de connexion
                Database._redis_instance.ping()
                logger.info("Connexion à Redis établie avec succès")
            except redis.ConnectionError as e:
                logger.error(f"Impossible de se connecter à Redis: {e}")
                raise
            except Exception as e:
                logger.error(f"Erreur inattendue lors de la connexion à Redis: {e}")
                raise
                
        return Database._redis_instance
    
    @staticmethod
    def get_db():
        """Récupère la base de données MongoDB"""
        client = Database.get_mongo_connection()
        db_name = os.getenv('DB_NAME', 'gestion_etudiants')
        return client[db_name] 