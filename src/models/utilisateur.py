from typing import Dict, Optional, Any
import json
import bcrypt
from enum import Enum

class Role(Enum):
    """Énumération des rôles disponibles"""
    ADMIN = "admin"
    ENSEIGNANT = "enseignant"
    ETUDIANT = "etudiant"

class Utilisateur:
    """Classe représentant un utilisateur du système"""
    
    def __init__(self, username: str, email: str, role: Role, 
                 password_hash: str = None, id_etudiant: Optional[str] = None, 
                 _id: Optional[str] = None):
        """
        Initialise un nouvel utilisateur
        
        Args:
            username: Nom d'utilisateur unique
            email: Email de l'utilisateur
            role: Rôle de l'utilisateur (admin, enseignant, étudiant)
            password_hash: Hash du mot de passe (déjà hashé)
            id_etudiant: ID de l'étudiant associé (si rôle étudiant)
            _id: Identifiant MongoDB (optionnel)
        """
        self.username = username
        self.email = email
        self.role = role if isinstance(role, Role) else Role(role)
        self.password_hash = password_hash
        self.id_etudiant = id_etudiant
        self._id = _id
    
    def set_password(self, password: str) -> None:
        """
        Définit le mot de passe de l'utilisateur (hashé)
        
        Args:
            password: Mot de passe en clair
        """
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """
        Vérifie si le mot de passe correspond
        
        Args:
            password: Mot de passe à vérifier
            
        Returns:
            True si le mot de passe correspond, False sinon
        """
        password_bytes = password.encode('utf-8')
        hash_bytes = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'utilisateur en dictionnaire pour MongoDB"""
        return {
            "username": self.username,
            "email": self.email,
            "role": self.role.value,
            "password_hash": self.password_hash,
            "id_etudiant": self.id_etudiant,
            "_id": self._id
        }
    
    def to_json(self) -> str:
        """Convertit l'utilisateur en JSON pour Redis"""
        data = self.to_dict()
        if data["_id"]:
            data["_id"] = str(data["_id"])
        return json.dumps(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Utilisateur':
        """Crée un utilisateur à partir d'un dictionnaire MongoDB"""
        return cls(
            username=data.get("username"),
            email=data.get("email"),
            role=data.get("role"),
            password_hash=data.get("password_hash"),
            id_etudiant=data.get("id_etudiant"),
            _id=str(data.get("_id")) if data.get("_id") else None
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Utilisateur':
        """Crée un utilisateur à partir d'une chaîne JSON"""
        return cls.from_dict(json.loads(json_str)) 