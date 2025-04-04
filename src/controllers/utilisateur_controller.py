from typing import List, Dict, Any, Optional
import re

from src.models.utilisateur import Utilisateur, Role
from src.services.utilisateur_service import UtilisateurService
from src.utils.console.console import Console, Couleur
from src.utils.logger import Logger
from src.utils.exception.exceptions import ValidationError, ResourceNotFoundError, AuthenticationError

class UtilisateurController:
    """Contrôleur pour gérer les interactions liées aux utilisateurs"""
    
    def __init__(self):
        """Initialise le contrôleur avec les services nécessaires"""
        self.utilisateur_service = UtilisateurService()
        self.logger = Logger.get_instance()
    
    def creer_utilisateur(self) -> Optional[str]:
        """
        Saisie les informations d'un nouvel utilisateur
        
        Returns:
            L'ID de l'utilisateur créé ou None si la création a échoué
        """
        Console.titre("Création d'un nouvel utilisateur")
        
        # Saisie des informations
        username = Console.saisie("Nom d'utilisateur", True)
        
        # Saisie et validation de l'email
        while True:
            email = Console.saisie("Email", True)
            if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                break
            Console.erreur("Format d'email invalide.")
        
        # Choix du rôle
        options_role = [
            "Admin",
            "Enseignant",
            "Étudiant"
        ]
        
        role_choix = Console.menu("Choisissez un rôle", options_role)
        
        id_etudiant = None
        if role_choix == "1":
            role = Role.ADMIN
        elif role_choix == "2":
            role = Role.ENSEIGNANT
        elif role_choix == "3":
            role = Role.ETUDIANT
            id_etudiant = Console.saisie("ID de l'étudiant associé", True)
        else:
            Console.erreur("Choix invalide.")
            return None
        
        # Saisie du mot de passe
        while True:
            password = Console.saisie("Mot de passe", True)
            password_confirm = Console.saisie("Confirmez le mot de passe", True)
            
            if password == password_confirm:
                break
            Console.erreur("Les mots de passe ne correspondent pas.")
        
        # Création de l'utilisateur
        try:
            utilisateur = Utilisateur(
                username=username,
                email=email,
                role=role,
                id_etudiant=id_etudiant if role == Role.ETUDIANT else None
            )
            
            utilisateur_id = self.utilisateur_service.ajouter_utilisateur(utilisateur, password)
            Console.succes(f"Utilisateur créé avec succès! ID: {utilisateur_id}")
            self.logger.info(f"Nouvel utilisateur créé: {username}, rôle: {role.value} (ID: {utilisateur_id})")
            return utilisateur_id
            
        except ValidationError as e:
            Console.erreur(f"Erreur de validation: {e}")
            self.logger.error(f"Erreur de validation lors de la création d'un utilisateur: {e}")
            return None
        except Exception as e:
            Console.erreur(f"Erreur lors de la création de l'utilisateur: {e}")
            self.logger.error(f"Erreur lors de la création d'un utilisateur: {e}")
            return None
    
    def afficher_utilisateurs(self, utilisateurs: Optional[List[Utilisateur]] = None) -> None:
        """
        Affiche une liste d'utilisateurs sous forme de tableau
        
        Args:
            utilisateurs: Liste des utilisateurs à afficher (si None, affiche tous les utilisateurs)
        """
        if utilisateurs is None:
            utilisateurs = self.utilisateur_service.lister_utilisateurs()
            self.logger.info(f"Affichage de tous les utilisateurs ({len(utilisateurs)} trouvés)")
        
        if not utilisateurs:
            Console.info("Aucun utilisateur trouvé.")
            return
        
        Console.titre("Liste des utilisateurs")
        
        donnees = []
        for utilisateur in utilisateurs:
            # Coloriser le rôle en fonction de sa valeur
            couleur_role = Couleur.CYAN
            if utilisateur.role == Role.ADMIN:
                couleur_role = Couleur.ROUGE
            elif utilisateur.role == Role.ENSEIGNANT:
                couleur_role = Couleur.VERT
            
            donnees.append({
                "ID": utilisateur._id if utilisateur._id else 'N/A',
                "Nom d'utilisateur": utilisateur.username,
                "Email": utilisateur.email,
                "Rôle": Console.couleur(utilisateur.role.value, couleur_role)
            })
        
        Console.tableau(donnees)
    
    def authentifier(self) -> Optional[Dict[str, Any]]:
        """
        Interface d'authentification
        
        Returns:
            Les informations de session si l'authentification réussit, None sinon
        """
        Console.titre("Authentification")
        
        username = Console.saisie("Nom d'utilisateur", True)
        password = Console.saisie("Mot de passe", True)
        
        try:
            session = self.utilisateur_service.authentifier(username, password)
            
            if session:
                Console.succes(f"Bienvenue, {session['utilisateur']['username']}!")
                self.logger.info(f"Utilisateur connecté: {username} (rôle: {session['utilisateur']['role']})")
                return session
            else:
                raise AuthenticationError()
                
        except AuthenticationError:
            Console.erreur("Échec de l'authentification. Nom d'utilisateur ou mot de passe incorrect.")
            self.logger.warning(f"Tentative d'authentification échouée pour l'utilisateur: {username}")
            return None
        except Exception as e:
            Console.erreur(f"Erreur lors de l'authentification: {e}")
            self.logger.error(f"Erreur lors de l'authentification: {e}")
            return None
    
    def modifier_utilisateur(self) -> bool:
        """
        Interface de modification d'un utilisateur
        
        Returns:
            True si la modification a réussi, False sinon
        """
        username = Console.saisie("Entrez le nom d'utilisateur à modifier", True)
        
        try:
            utilisateur = self.utilisateur_service.obtenir_utilisateur_par_username(username)
            if not utilisateur:
                raise ResourceNotFoundError("utilisateur", "nom d'utilisateur", username)
            
            Console.titre(f"Modification de l'utilisateur: {utilisateur.username}")
            Console.info(f"Email: {utilisateur.email}")
            Console.info(f"Rôle actuel: {Console.couleur(utilisateur.role.value, Couleur.CYAN)}")
            
            options = [
                "Email",
                "Mot de passe",
                "Rôle",
                "Retour"
            ]
            
            choix = Console.menu("Que souhaitez-vous modifier?", options)
            
            if choix == "1":
                # Saisie et validation de l'email
                while True:
                    email = Console.saisie("Nouvel email", True)
                    if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                        break
                    Console.erreur("Format d'email invalide.")
                
                utilisateur.email = email
                self.logger.info(f"Modification de l'email pour l'utilisateur {utilisateur._id} ({utilisateur.username})")
                
            elif choix == "2":
                # Saisie et confirmation du mot de passe
                while True:
                    password = Console.saisie("Nouveau mot de passe", True)
                    password_confirm = Console.saisie("Confirmez le mot de passe", True)
                    
                    if password == password_confirm:
                        break
                    Console.erreur("Les mots de passe ne correspondent pas.")
                
                self.utilisateur_service.changer_mot_de_passe(utilisateur._id, password)
                self.logger.info(f"Modification du mot de passe pour l'utilisateur {utilisateur._id} ({utilisateur.username})")
                
            elif choix == "3":
                options_role = [
                    "Admin",
                    "Enseignant",
                    "Étudiant"
                ]
                
                role_choix = Console.menu("Choisissez un rôle", options_role)
                
                if role_choix == "1":
                    utilisateur.role = Role.ADMIN
                    utilisateur.id_etudiant = None
                elif role_choix == "2":
                    utilisateur.role = Role.ENSEIGNANT
                    utilisateur.id_etudiant = None
                elif role_choix == "3":
                    utilisateur.role = Role.ETUDIANT
                    id_etudiant = Console.saisie("ID de l'étudiant associé", True)
                    utilisateur.id_etudiant = id_etudiant
                else:
                    Console.erreur("Choix invalide.")
                    return False
                
                self.logger.info(f"Modification du rôle pour l'utilisateur {utilisateur._id} ({utilisateur.username}): {utilisateur.role.value}")
                
            elif choix == "4":
                return False
            else:
                Console.erreur("Choix invalide.")
                return False
            
            # Mise à jour de l'utilisateur
            if self.utilisateur_service.mettre_a_jour_utilisateur(utilisateur):
                Console.succes("Utilisateur mis à jour avec succès!")
                return True
            else:
                Console.erreur("Erreur lors de la mise à jour de l'utilisateur.")
                self.logger.error(f"Échec de la mise à jour de l'utilisateur {utilisateur._id} ({utilisateur.username})")
                return False
                
        except ResourceNotFoundError as e:
            Console.erreur(f"Erreur: {e}")
            self.logger.warning(f"Tentative de modification: {e}")
            return False
        except Exception as e:
            Console.erreur(f"Une erreur s'est produite: {e}")
            self.logger.error(f"Erreur lors de la modification d'un utilisateur: {e}")
            return False
    
    def supprimer_utilisateur(self) -> bool:
        """
        Interface de suppression d'un utilisateur
        
        Returns:
            True si la suppression a réussi, False sinon
        """
        username = Console.saisie("Entrez le nom d'utilisateur à supprimer", True)
        
        try:
            utilisateur = self.utilisateur_service.obtenir_utilisateur_par_username(username)
            if not utilisateur:
                raise ResourceNotFoundError("utilisateur", "nom d'utilisateur", username)
            
            Console.titre(f"Suppression de l'utilisateur: {utilisateur.username}")
            Console.info(f"Email: {utilisateur.email}")
            Console.info(f"Rôle: {Console.couleur(utilisateur.role.value, Couleur.CYAN)}")
            
            if Console.confirmation("Êtes-vous sûr de vouloir supprimer cet utilisateur?"):
                if self.utilisateur_service.supprimer_utilisateur(utilisateur._id):
                    Console.succes("Utilisateur supprimé avec succès.")
                    self.logger.info(f"Utilisateur supprimé: {utilisateur._id} ({utilisateur.username})")
                    return True
                else:
                    Console.erreur("Erreur lors de la suppression de l'utilisateur.")
                    self.logger.error(f"Échec de la suppression de l'utilisateur {utilisateur._id} ({utilisateur.username})")
                    return False
            
            return False
            
        except ResourceNotFoundError as e:
            Console.erreur(f"Erreur: {e}")
            self.logger.warning(f"Tentative de suppression: {e}")
            return False
        except Exception as e:
            Console.erreur(f"Une erreur s'est produite: {e}")
            self.logger.error(f"Erreur lors de la suppression d'un utilisateur: {e}")
            return False
    
    def afficher_utilisateurs_par_role(self) -> None:
        """Interface d'affichage des utilisateurs par rôle"""
        Console.titre("Affichage des utilisateurs par rôle")
        
        options = [
            "Administrateurs",
            "Enseignants",
            "Étudiants"
        ]
        
        choix = Console.menu("Sélectionnez un rôle", options)
        
        if choix == "1":
            utilisateurs = self.utilisateur_service.lister_utilisateurs_par_role(Role.ADMIN)
            self.logger.info(f"Affichage des administrateurs ({len(utilisateurs)} trouvés)")
            self.afficher_utilisateurs(utilisateurs)
        elif choix == "2":
            utilisateurs = self.utilisateur_service.lister_utilisateurs_par_role(Role.ENSEIGNANT)
            self.logger.info(f"Affichage des enseignants ({len(utilisateurs)} trouvés)")
            self.afficher_utilisateurs(utilisateurs)
        elif choix == "3":
            utilisateurs = self.utilisateur_service.lister_utilisateurs_par_role(Role.ETUDIANT)
            self.logger.info(f"Affichage des étudiants ({len(utilisateurs)} trouvés)")
            self.afficher_utilisateurs(utilisateurs)
        else:
            Console.erreur("Choix invalide.") 