import logging
import os
from datetime import datetime

class Logger:
    """Classe pour gérer les logs de l'application"""
    
    _instance = None
    
    @staticmethod
    def get_instance():
        """Récupère l'instance unique du logger (pattern Singleton)"""
        if Logger._instance is None:
            Logger._instance = Logger()
        return Logger._instance
    
    def __init__(self):
        """Initialise le logger avec une sortie console et fichier"""
        if Logger._instance is not None:
            raise Exception("Cette classe est un singleton, utilisez get_instance()")
            
        # Création du répertoire logs s'il n'existe pas
        os.makedirs("logs", exist_ok=True)
        
        # Nom du fichier de log avec horodatage
        date_str = datetime.now().strftime("%Y-%m-%d")
        fichier_log = f"logs/gestion_etudiants_{date_str}.log"
        
        # Configurer le logger
        self.logger = logging.getLogger("gestion_etudiants")
        self.logger.setLevel(logging.INFO)
        
        # Éviter les handlers en double
        if not self.logger.handlers:
            # Format du log
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            
            # Handler pour la console
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(logging.INFO)
            
            # Handler pour le fichier
            file_handler = logging.FileHandler(fichier_log, encoding='utf-8')
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.INFO)
            
            # Ajouter les handlers
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
    
    def info(self, message):
        """Enregistre un message de niveau INFO"""
        self.logger.info(message)
    
    def warning(self, message):
        """Enregistre un message de niveau WARNING"""
        self.logger.warning(message)
    
    def error(self, message):
        """Enregistre un message de niveau ERROR"""
        self.logger.error(message)
    
    def debug(self, message):
        """Enregistre un message de niveau DEBUG"""
        self.logger.debug(message) 