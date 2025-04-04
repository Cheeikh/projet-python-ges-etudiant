from typing import Dict, List, Optional, Any
import json
from bson import ObjectId

class Etudiant:
    """Classe représentant un étudiant"""
    
    def __init__(self, nom: str, prenom: str, telephone: str, classe: str, 
                 notes: Dict[str, float] = None, _id: Optional[str] = None):
        """
        Initialise un nouvel étudiant
        
        Args:
            nom: Le nom de l'étudiant
            prenom: Le prénom de l'étudiant
            telephone: Le numéro de téléphone (doit être unique)
            classe: La classe de l'étudiant
            notes: Dictionnaire des notes par matière
            _id: Identifiant MongoDB (optionnel)
        """
        self.nom = nom
        self.prenom = prenom
        self.telephone = telephone
        self.classe = classe
        self.notes = notes or {}
        self._id = _id
    
    @property
    def moyenne(self) -> float:
        """Calcule la moyenne des notes de l'étudiant"""
        if not self.notes:
            return 0.0
        return sum(self.notes.values()) / len(self.notes)
    
    def ajouter_note(self, matiere: str, note: float) -> None:
        """
        Ajoute ou met à jour une note pour une matière
        
        Args:
            matiere: Le nom de la matière
            note: La note (entre 0 et 20)
        
        Raises:
            ValueError: Si la note n'est pas entre 0 et 20
        """
        if not 0 <= note <= 20:
            raise ValueError("La note doit être comprise entre 0 et 20")
        self.notes[matiere] = note
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'étudiant en dictionnaire pour MongoDB"""
        result = {
            "nom": self.nom,
            "prenom": self.prenom,
            "telephone": self.telephone,
            "classe": self.classe,
            "notes": self.notes
        }
        
        # N'inclure l'_id que s'il est défini
        if self._id:
            result["_id"] = ObjectId(self._id) if isinstance(self._id, str) else self._id
            
        return result
    
    def to_json(self) -> str:
        """Convertit l'étudiant en JSON pour Redis"""
        data = self.to_dict()
        if data["_id"] and isinstance(data["_id"], ObjectId):
            data["_id"] = str(data["_id"])
        return json.dumps(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Etudiant':
        """Crée un étudiant à partir d'un dictionnaire MongoDB"""
        # S'assurer que l'ID est correctement converti en chaîne
        id_value = None
        if "_id" in data and data["_id"] is not None:
            id_value = str(data["_id"])
            
        return cls(
            nom=data.get("nom"),
            prenom=data.get("prenom"),
            telephone=data.get("telephone"),
            classe=data.get("classe"),
            notes=data.get("notes", {}),
            _id=id_value
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Etudiant':
        """Crée un étudiant à partir d'une chaîne JSON"""
        return cls.from_dict(json.loads(json_str)) 