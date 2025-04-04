import json
from typing import List, Dict, Any, Optional, Union
from bson import ObjectId

from src.models.etudiant import Etudiant
from src.config.database import Database

class EtudiantService:
    """Service de gestion des étudiants"""
    
    def __init__(self):
        """Initialise le service avec les connexions aux bases de données"""
        self.db = Database.get_db()
        self.redis = Database.get_redis_connection()
        self.collection = self.db.etudiants
    
    def ajouter_etudiant(self, etudiant: Etudiant) -> str:
        """
        Ajoute un étudiant à la base de données
        
        Args:
            etudiant: L'étudiant à ajouter
            
        Returns:
            L'ID de l'étudiant créé
            
        Raises:
            ValueError: Si le numéro de téléphone existe déjà
        """
        # Vérifier si le téléphone existe déjà
        if self.collection.find_one({"telephone": etudiant.telephone}):
            raise ValueError(f"Un étudiant avec le numéro {etudiant.telephone} existe déjà")
        
        # Insérer dans MongoDB
        result = self.collection.insert_one(etudiant.to_dict())
        etudiant._id = str(result.inserted_id)
        
        # Ajouter dans Redis
        self.redis.set(f"etudiant:{etudiant._id}", etudiant.to_json())
        self.redis.set(f"etudiant:telephone:{etudiant.telephone}", etudiant._id)
        
        return etudiant._id
    
    def obtenir_etudiant(self, etudiant_id: str) -> Optional[Etudiant]:
        """
        Récupère un étudiant par son ID
        
        Args:
            etudiant_id: L'ID de l'étudiant
            
        Returns:
            L'étudiant trouvé ou None si aucun étudiant n'est trouvé
        """
        try:
            # Essayer d'abord Redis
            etudiant_json = self.redis.get(f"etudiant:{etudiant_id}")
            if etudiant_json:
                etudiant = Etudiant.from_json(etudiant_json)
                # Vérifier que l'ID est défini correctement
                if not etudiant._id:
                    etudiant._id = etudiant_id
                return etudiant
            
            # Sinon, chercher dans MongoDB
            try:
                object_id = ObjectId(etudiant_id)
                data = self.collection.find_one({"_id": object_id})
            except Exception:
                # Si l'ID n'est pas un ObjectId valide, retourner None
                from src.utils.logger import Logger
                logger = Logger.get_instance()
                logger.error(f"ID d'étudiant invalide: {etudiant_id}")
                return None
                
            if not data:
                return None
            
            # S'assurer que l'ID est correctement inclus dans les données
            data["_id"] = etudiant_id
                
            # Créer l'objet étudiant
            etudiant = Etudiant.from_dict(data)
            
            # Mettre en cache dans Redis
            self.redis.set(f"etudiant:{etudiant._id}", etudiant.to_json())
            
            return etudiant
            
        except Exception as e:
            # Log l'erreur
            from src.utils.logger import Logger
            logger = Logger.get_instance()
            logger.error(f"Erreur lors de la récupération de l'étudiant par ID {etudiant_id}: {e}")
            return None
    
    def obtenir_etudiant_par_telephone(self, telephone: str) -> Optional[Etudiant]:
        """
        Récupère un étudiant par son numéro de téléphone
        
        Args:
            telephone: Le numéro de téléphone
            
        Returns:
            L'étudiant trouvé ou None si aucun étudiant n'est trouvé
        """
        try:
            # Vérifier d'abord dans Redis
            etudiant_id = self.redis.get(f"etudiant:telephone:{telephone}")
            if etudiant_id:
                return self.obtenir_etudiant(etudiant_id)
            
            # Sinon, chercher dans MongoDB
            data = self.collection.find_one({"telephone": telephone})
            if not data:
                return None
                
            # S'assurer que l'ID est correctement inclus dans les données
            if "_id" in data and data["_id"] is not None:
                data["_id"] = str(data["_id"])
            else:
                # Log une erreur si l'ID est manquant
                from src.utils.logger import Logger
                logger = Logger.get_instance()
                logger.error(f"Étudiant trouvé avec téléphone {telephone} mais sans ID valide dans la base de données")
                return None
                
            etudiant = Etudiant.from_dict(data)
            
            # Vérifier que l'étudiant a bien un ID avant de le mettre en cache
            if not etudiant._id:
                from src.utils.logger import Logger
                logger = Logger.get_instance()
                logger.error(f"Impossible de créer un étudiant avec un ID valide à partir des données: {data}")
                return None
            
            # Mettre en cache dans Redis
            self.redis.set(f"etudiant:{etudiant._id}", etudiant.to_json())
            self.redis.set(f"etudiant:telephone:{telephone}", etudiant._id)
            
            return etudiant
            
        except Exception as e:
            # Log l'erreur
            from src.utils.logger import Logger
            logger = Logger.get_instance()
            logger.error(f"Erreur lors de la récupération de l'étudiant par téléphone {telephone}: {e}")
            return None
    
    def rechercher_etudiants(self, critere: Dict[str, Any]) -> List[Etudiant]:
        """
        Recherche des étudiants selon différents critères
        
        Args:
            critere: Dictionnaire des critères de recherche
            
        Returns:
            Liste des étudiants correspondants
        """
        resultats = self.collection.find(critere)
        etudiants = [Etudiant.from_dict(data) for data in resultats]
        
        return etudiants
    
    def lister_etudiants(self) -> List[Etudiant]:
        """
        Liste tous les étudiants
        
        Returns:
            Liste de tous les étudiants
        """
        resultats = self.collection.find()
        return [Etudiant.from_dict(data) for data in resultats]
    
    def lister_etudiants_par_classe(self, classe: str) -> List[Etudiant]:
        """
        Liste tous les étudiants d'une classe
        
        Args:
            classe: La classe recherchée
            
        Returns:
            Liste des étudiants de cette classe
        """
        return self.rechercher_etudiants({"classe": classe})
    
    def mettre_a_jour_etudiant(self, etudiant: Etudiant) -> bool:
        """
        Met à jour un étudiant
        
        Args:
            etudiant: L'étudiant à mettre à jour
            
        Returns:
            True si la mise à jour a réussi, False sinon
        """
        if not etudiant._id:
            return False
        
        try:
            # Convertir l'ID en ObjectId si c'est une chaîne
            object_id = ObjectId(etudiant._id) if isinstance(etudiant._id, str) else etudiant._id
            
            update_data = {
                "nom": etudiant.nom,
                "prenom": etudiant.prenom,
                "telephone": etudiant.telephone,
                "classe": etudiant.classe,
                "notes": etudiant.notes
            }
            
            resultat = self.collection.update_one(
                {"_id": object_id},
                {"$set": update_data}
            )
            
            # Mettre à jour le cache Redis
            if resultat.modified_count > 0:
                self.redis.set(f"etudiant:{etudiant._id}", etudiant.to_json())
                self.redis.set(f"etudiant:telephone:{etudiant.telephone}", etudiant._id)
                return True
            
            return False
        except Exception as e:
            # Importation conditionnelle pour éviter une dépendance circulaire
            from src.utils.logger import Logger
            logger = Logger.get_instance()
            logger.error(f"Erreur lors de la mise à jour de l'étudiant {etudiant._id}: {e}")
            return False
    
    def supprimer_etudiant(self, etudiant_id: str) -> bool:
        """
        Supprime un étudiant
        
        Args:
            etudiant_id: L'ID de l'étudiant à supprimer
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        # Récupérer l'étudiant pour avoir ses détails avant suppression
        etudiant = self.obtenir_etudiant(etudiant_id)
        if not etudiant:
            return False
        
        resultat = self.collection.delete_one({"_id": ObjectId(etudiant_id)})
        
        # Supprimer les entrées dans Redis
        if resultat.deleted_count > 0:
            self.redis.delete(f"etudiant:{etudiant_id}")
            self.redis.delete(f"etudiant:telephone:{etudiant.telephone}")
            return True
        
        return False
    
    def trier_etudiants_par_moyenne(self, etudiants: Optional[List[Etudiant]] = None) -> List[Etudiant]:
        """
        Trie les étudiants par moyenne décroissante
        
        Args:
            etudiants: Liste d'étudiants à trier (si None, récupère tous les étudiants)
            
        Returns:
            Liste des étudiants triés par moyenne décroissante
        """
        if etudiants is None:
            etudiants = self.lister_etudiants()
        
        return sorted(etudiants, key=lambda e: e.moyenne, reverse=True)
    
    def calculer_moyenne_classe(self, classe: str) -> float:
        """
        Calcule la moyenne générale d'une classe
        
        Args:
            classe: La classe dont on veut calculer la moyenne
            
        Returns:
            La moyenne générale de la classe
        """
        etudiants = self.lister_etudiants_par_classe(classe)
        if not etudiants:
            return 0.0
        
        return sum(etudiant.moyenne for etudiant in etudiants) / len(etudiants)
    
    def top_etudiants(self, limit: int = 10) -> List[Etudiant]:
        """
        Retourne les meilleurs étudiants par moyenne
        
        Args:
            limit: Nombre d'étudiants à retourner
            
        Returns:
            Liste des meilleurs étudiants
        """
        etudiants_tries = self.trier_etudiants_par_moyenne()
        return etudiants_tries[:limit] 