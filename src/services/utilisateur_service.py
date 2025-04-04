import json
import os
from typing import List, Dict, Any, Optional
from bson import ObjectId
import time
import uuid

from src.models.utilisateur import Utilisateur, Role
from src.config.database import Database

class UtilisateurService:
    """Service de gestion des utilisateurs"""
    
    def __init__(self):
        """Initialise le service avec les connexions aux bases de données"""
        self.db = Database.get_db()
        self.redis = Database.get_redis_connection()
        self.collection = self.db.utilisateurs
        self.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')
    
    def ajouter_utilisateur(self, utilisateur: Utilisateur, password: str) -> str:
        """
        Ajoute un utilisateur à la base de données
        
        Args:
            utilisateur: L'utilisateur à ajouter
            password: Le mot de passe en clair
            
        Returns:
            L'ID de l'utilisateur créé
            
        Raises:
            ValueError: Si le nom d'utilisateur existe déjà
        """
        # Vérifier si le nom d'utilisateur existe déjà
        if self.collection.find_one({"username": utilisateur.username}):
            raise ValueError(f"Un utilisateur avec le nom '{utilisateur.username}' existe déjà")
        
        # Hasher le mot de passe
        utilisateur.set_password(password)
        
        # Insérer dans MongoDB
        result = self.collection.insert_one(utilisateur.to_dict())
        utilisateur._id = str(result.inserted_id)
        
        # Mettre à jour le cache Redis
        self.redis.set(f"utilisateur:{utilisateur._id}", utilisateur.to_json())
        self.redis.set(f"utilisateur:username:{utilisateur.username}", utilisateur._id)
        
        return utilisateur._id
    
    def obtenir_utilisateur(self, utilisateur_id: str) -> Optional[Utilisateur]:
        """
        Récupère un utilisateur par son ID
        
        Args:
            utilisateur_id: L'ID de l'utilisateur
            
        Returns:
            L'utilisateur trouvé ou None si aucun utilisateur n'est trouvé
        """
        # Essayer d'abord Redis
        utilisateur_json = self.redis.get(f"utilisateur:{utilisateur_id}")
        if utilisateur_json:
            return Utilisateur.from_json(utilisateur_json)
        
        # Sinon, chercher dans MongoDB
        data = self.collection.find_one({"_id": ObjectId(utilisateur_id)})
        if not data:
            return None
        
        # Mettre en cache dans Redis
        utilisateur = Utilisateur.from_dict(data)
        self.redis.set(f"utilisateur:{utilisateur._id}", utilisateur.to_json())
        
        return utilisateur
    
    def obtenir_utilisateur_par_username(self, username: str) -> Optional[Utilisateur]:
        """
        Récupère un utilisateur par son nom d'utilisateur
        
        Args:
            username: Le nom d'utilisateur
            
        Returns:
            L'utilisateur trouvé ou None si aucun utilisateur n'est trouvé
        """
        # Vérifier d'abord dans Redis
        utilisateur_id = self.redis.get(f"utilisateur:username:{username}")
        if utilisateur_id:
            return self.obtenir_utilisateur(utilisateur_id)
        
        # Sinon, chercher dans MongoDB
        data = self.collection.find_one({"username": username})
        if not data:
            return None
        
        utilisateur = Utilisateur.from_dict(data)
        
        # Mettre en cache dans Redis
        self.redis.set(f"utilisateur:{utilisateur._id}", utilisateur.to_json())
        self.redis.set(f"utilisateur:username:{username}", utilisateur._id)
        
        return utilisateur
    
    def authentifier(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authentifie un utilisateur
        
        Args:
            username: Le nom d'utilisateur
            password: Le mot de passe
            
        Returns:
            Dictionnaire contenant le token de session et les infos de l'utilisateur,
            ou None si l'authentification échoue
        """
        utilisateur = self.obtenir_utilisateur_par_username(username)
        
        if not utilisateur or not utilisateur.check_password(password):
            return None
        
        # Générer un token de session
        session_token = str(uuid.uuid4())
        expiration = int(time.time()) + 24 * 60 * 60  # 24 heures
        
        session_data = {
            "utilisateur_id": utilisateur._id,
            "username": utilisateur.username,
            "role": utilisateur.role.value,
            "expiration": expiration
        }
        
        # Stocker la session dans Redis
        self.redis.set(f"session:{session_token}", json.dumps(session_data))
        self.redis.expire(f"session:{session_token}", 24 * 60 * 60)  # 24 heures
        
        return {
            "token": session_token,
            "utilisateur": {
                "id": utilisateur._id,
                "username": utilisateur.username,
                "email": utilisateur.email,
                "role": utilisateur.role.value
            },
            "expiration": expiration
        }
    
    def verifier_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """
        Vérifie si une session est valide
        
        Args:
            session_token: Le token de session
            
        Returns:
            Les informations de session ou None si la session est invalide ou expirée
        """
        session_json = self.redis.get(f"session:{session_token}")
        if not session_json:
            return None
        
        session_data = json.loads(session_json)
        
        # Vérifier l'expiration
        if session_data.get("expiration", 0) < int(time.time()):
            self.redis.delete(f"session:{session_token}")
            return None
        
        return session_data
    
    def deconnecter(self, session_token: str) -> bool:
        """
        Déconnecte un utilisateur en supprimant sa session
        
        Args:
            session_token: Le token de session
            
        Returns:
            True si la déconnexion a réussi, False sinon
        """
        return bool(self.redis.delete(f"session:{session_token}"))
    
    def mettre_a_jour_utilisateur(self, utilisateur: Utilisateur) -> bool:
        """
        Met à jour un utilisateur
        
        Args:
            utilisateur: L'utilisateur à mettre à jour
            
        Returns:
            True si la mise à jour a réussi, False sinon
        """
        if not utilisateur._id:
            return False
        
        resultat = self.collection.update_one(
            {"_id": ObjectId(utilisateur._id)},
            {"$set": {
                "username": utilisateur.username,
                "email": utilisateur.email,
                "role": utilisateur.role.value,
                "password_hash": utilisateur.password_hash,
                "id_etudiant": utilisateur.id_etudiant
            }}
        )
        
        # Mettre à jour le cache Redis
        if resultat.modified_count > 0:
            self.redis.set(f"utilisateur:{utilisateur._id}", utilisateur.to_json())
            self.redis.set(f"utilisateur:username:{utilisateur.username}", utilisateur._id)
            return True
        
        return False
    
    def supprimer_utilisateur(self, utilisateur_id: str) -> bool:
        """
        Supprime un utilisateur
        
        Args:
            utilisateur_id: L'ID de l'utilisateur à supprimer
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        # Récupérer l'utilisateur pour avoir son username avant suppression
        utilisateur = self.obtenir_utilisateur(utilisateur_id)
        if not utilisateur:
            return False
        
        resultat = self.collection.delete_one({"_id": ObjectId(utilisateur_id)})
        
        # Supprimer les entrées dans Redis
        if resultat.deleted_count > 0:
            self.redis.delete(f"utilisateur:{utilisateur_id}")
            self.redis.delete(f"utilisateur:username:{utilisateur.username}")
            return True
        
        return False
    
    def lister_utilisateurs(self) -> List[Utilisateur]:
        """
        Liste tous les utilisateurs
        
        Returns:
            Liste de tous les utilisateurs
        """
        resultats = self.collection.find()
        return [Utilisateur.from_dict(data) for data in resultats]
    
    def lister_utilisateurs_par_role(self, role: Role) -> List[Utilisateur]:
        """
        Liste tous les utilisateurs ayant un rôle spécifique
        
        Args:
            role: Le rôle recherché
            
        Returns:
            Liste des utilisateurs ayant ce rôle
        """
        role_value = role.value if isinstance(role, Role) else role
        resultats = self.collection.find({"role": role_value})
        return [Utilisateur.from_dict(data) for data in resultats] 