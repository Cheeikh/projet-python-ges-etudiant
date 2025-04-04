from dotenv import load_dotenv
import traceback

from src.controllers.etudiant_controller import EtudiantController
from src.controllers.utilisateur_controller import UtilisateurController
from src.models.utilisateur import Role
from src.utils.console.console import Console, Couleur
from src.utils.logger import Logger
from src.utils.exception.exceptions import ApplicationError

# Chargement des variables d'environnement
load_dotenv()

class GestionEtudiantsApp:
    """Classe principale de l'application de gestion des étudiants"""
    
    def __init__(self):
        """Initialise l'application"""
        self.etudiant_controller = EtudiantController()
        self.utilisateur_controller = UtilisateurController()
        self.session = None
        self.logger = Logger.get_instance()
        
    def afficher_en_tete(self):
        """Affiche l'en-tête de l'application"""
        Console.effacer_ecran()
        print(Console.couleur("=" * 80, Couleur.CYAN))
        print(Console.couleur("               SYSTÈME DE GESTION DES ÉTUDIANTS", Couleur.CYAN + Couleur.GRAS))
        print(Console.couleur("=" * 80, Couleur.CYAN))
        
        if self.session:
            utilisateur = self.session['utilisateur']
            print(f"Utilisateur connecté: {Console.couleur(utilisateur['username'], Couleur.VERT)} | Rôle: {Console.couleur(utilisateur['role'], Couleur.MAGENTA)}")
            print("-" * 80)
    
    def menu_principal(self):
        """Affiche le menu principal de l'application"""
        try:
            self.logger.info("Démarrage de l'application")
            while True:
                self.afficher_en_tete()
                
                if not self.session:
                    # Menu de connexion
                    choix = Console.menu("MENU PRINCIPAL", [
                        "Se connecter",
                        "Quitter"
                    ])
                    
                    if choix == "1":
                        self.session = self.utilisateur_controller.authentifier()
                        if self.session:
                            self.logger.info(f"Connexion réussie: {self.session['utilisateur']['username']} ({self.session['utilisateur']['role']})")
                    elif choix == "2":
                        Console.succes("Au revoir!")
                        self.logger.info("Fermeture de l'application")
                        break
                    else:
                        Console.erreur("Choix invalide.")
                        Console.pause()
                else:
                    # Menu selon le rôle
                    role = self.session['utilisateur']['role']
                    
                    if role == Role.ADMIN.value:
                        self.menu_admin()
                    elif role == Role.ENSEIGNANT.value:
                        self.menu_enseignant()
                    elif role == Role.ETUDIANT.value:
                        self.menu_etudiant()
                    else:
                        Console.erreur(f"Rôle non pris en charge: {role}")
                        Console.pause()
        except ApplicationError as e:
            Console.erreur(f"Erreur d'application: {e}")
            self.logger.error(f"Erreur d'application: {e}")
            Console.pause()
        except Exception as e:
            Console.erreur(f"Une erreur inattendue s'est produite: {e}")
            self.logger.error(f"Erreur inattendue: {str(e)}\n{traceback.format_exc()}")
            Console.pause()
    
    def menu_admin(self):
        """Affiche le menu pour les administrateurs"""
        while True:
            self.afficher_en_tete()
            
            choix = Console.menu("MENU ADMINISTRATEUR", [
                "Gérer les étudiants",
                "Gérer les utilisateurs",
                "Se déconnecter",
                "Quitter"
            ])
            
            if choix == "1":
                self.menu_gestion_etudiants()
            elif choix == "2":
                self.menu_gestion_utilisateurs()
            elif choix == "3":
                self.logger.info(f"Déconnexion: {self.session['utilisateur']['username']}")
                self.session = None
                break
            elif choix == "4":
                Console.succes("Au revoir!")
                self.logger.info("Fermeture de l'application")
                exit(0)
            else:
                Console.erreur("Choix invalide.")
                Console.pause()
    
    def menu_enseignant(self):
        """Affiche le menu pour les enseignants"""
        while True:
            self.afficher_en_tete()
            
            choix = Console.menu("MENU ENSEIGNANT", [
                "Consulter les étudiants",
                "Gérer les notes",
                "Statistiques",
                "Se déconnecter",
                "Quitter"
            ])
            
            if choix == "1":
                self.etudiant_controller.afficher_etudiants()
                Console.pause()
            elif choix == "2":
                self.etudiant_controller.modifier_notes()
                Console.pause()
            elif choix == "3":
                self.etudiant_controller.afficher_statistiques()
                Console.pause()
            elif choix == "4":
                self.logger.info(f"Déconnexion: {self.session['utilisateur']['username']}")
                self.session = None
                break
            elif choix == "5":
                Console.succes("Au revoir!")
                self.logger.info("Fermeture de l'application")
                exit(0)
            else:
                Console.erreur("Choix invalide.")
                Console.pause()
    
    def menu_etudiant(self):
        """Affiche le menu pour les étudiants"""
        while True:
            self.afficher_en_tete()
            
            choix = Console.menu("MENU ÉTUDIANT", [
                "Consulter mes notes",
                "Se déconnecter",
                "Quitter"
            ])
            
            if choix == "1":
                # Récupérer l'étudiant associé à l'utilisateur
                id_etudiant = self.session['utilisateur'].get('id_etudiant')
                if id_etudiant:
                    etudiant = self.etudiant_controller.etudiant_service.obtenir_etudiant(id_etudiant)
                    if etudiant:
                        Console.titre(f"Notes de {etudiant.prenom} {etudiant.nom}")
                        print(f"Classe: {Console.couleur(etudiant.classe, Couleur.CYAN)}")
                        print(Console.couleur("Notes:", Couleur.GRAS))
                        
                        if etudiant.notes:
                            # Afficher les notes sous forme de tableau
                            notes_data = []
                            for matiere, note in etudiant.notes.items():
                                notes_data.append({
                                    "Matière": matiere,
                                    "Note": f"{note}/20",
                                    "Mention": self._get_mention(note)
                                })
                            Console.tableau(notes_data)
                            
                            # Afficher la moyenne
                            mention = self._get_mention(etudiant.moyenne)
                            print(f"\nMoyenne générale: {Console.couleur(f'{etudiant.moyenne:.2f}/20', Couleur.GRAS)} - {mention}")
                        else:
                            Console.info("Aucune note enregistrée")
                    else:
                        Console.erreur("Impossible de récupérer vos informations.")
                else:
                    Console.avertissement("Aucun étudiant associé à votre compte.")
                Console.pause()
            elif choix == "2":
                self.logger.info(f"Déconnexion: {self.session['utilisateur']['username']}")
                self.session = None
                break
            elif choix == "3":
                Console.succes("Au revoir!")
                self.logger.info("Fermeture de l'application")
                exit(0)
            else:
                Console.erreur("Choix invalide.")
                Console.pause()
    
    def _get_mention(self, note: float) -> str:
        """
        Retourne la mention correspondant à une note
        
        Args:
            note: La note entre 0 et 20
            
        Returns:
            La mention correspondante
        """
        if note >= 16:
            return Console.couleur("Très bien", Couleur.VERT)
        elif note >= 14:
            return Console.couleur("Bien", Couleur.VERT)
        elif note >= 12:
            return Console.couleur("Assez bien", Couleur.CYAN)
        elif note >= 10:
            return Console.couleur("Passable", Couleur.JAUNE)
        else:
            return Console.couleur("Insuffisant", Couleur.ROUGE)
    
    def menu_gestion_etudiants(self):
        """Affiche le menu de gestion des étudiants"""
        while True:
            self.afficher_en_tete()
            
            choix = Console.menu("GESTION DES ÉTUDIANTS", [
                "Ajouter un étudiant",
                "Afficher tous les étudiants",
                "Rechercher un étudiant",
                "Modifier les notes d'un étudiant",
                "Supprimer un étudiant",
                "Exporter les données",
                "Importer des données",
                "Statistiques",
                "Retour"
            ])
            
            if choix == "1":
                self.etudiant_controller.saisir_etudiant()
                Console.pause()
            elif choix == "2":
                self.etudiant_controller.afficher_etudiants()
                Console.pause()
            elif choix == "3":
                self.etudiant_controller.rechercher_etudiant()
                Console.pause()
            elif choix == "4":
                self.etudiant_controller.modifier_notes()
                Console.pause()
            elif choix == "5":
                self.etudiant_controller.supprimer_etudiant()
                Console.pause()
            elif choix == "6":
                self.etudiant_controller.exporter_donnees()
                Console.pause()
            elif choix == "7":
                self.etudiant_controller.importer_donnees()
                Console.pause()
            elif choix == "8":
                self.etudiant_controller.afficher_statistiques()
                Console.pause()
            elif choix == "9":
                break
            else:
                Console.erreur("Choix invalide.")
                Console.pause()
    
    def menu_gestion_utilisateurs(self):
        """Affiche le menu de gestion des utilisateurs"""
        while True:
            self.afficher_en_tete()
            
            choix = Console.menu("GESTION DES UTILISATEURS", [
                "Créer un utilisateur",
                "Afficher tous les utilisateurs",
                "Afficher par rôle",
                "Modifier un utilisateur",
                "Supprimer un utilisateur",
                "Retour"
            ])
            
            if choix == "1":
                self.utilisateur_controller.creer_utilisateur()
                Console.pause()
            elif choix == "2":
                self.utilisateur_controller.afficher_utilisateurs()
                Console.pause()
            elif choix == "3":
                self.utilisateur_controller.afficher_utilisateurs_par_role()
                Console.pause()
            elif choix == "4":
                self.utilisateur_controller.modifier_utilisateur()
                Console.pause()
            elif choix == "5":
                self.utilisateur_controller.supprimer_utilisateur()
                Console.pause()
            elif choix == "6":
                break
            else:
                Console.erreur("Choix invalide.")
                Console.pause()

def main():
    """Point d'entrée de l'application"""
    try:
        # Créer l'utilisateur admin par défaut si aucun utilisateur n'existe
        utilisateur_controller = UtilisateurController()
        utilisateurs = utilisateur_controller.utilisateur_service.lister_utilisateurs()
        
        if not utilisateurs:
            Console.info("Première exécution: création de l'utilisateur administrateur par défaut")
            admin = utilisateur_controller.creer_utilisateur()
            
            if not admin:
                Console.erreur("Erreur lors de la création de l'administrateur. Arrêt du programme.")
                return
        else:
            # Demander à l'utilisateur s'il souhaite créer un nouveau compte
            Console.titre("Gestion des comptes")
            choix = Console.menu("Que souhaitez-vous faire?", [
                "Se connecter avec un compte existant",
                "Créer un nouveau compte",
                "Quitter"
            ])
            
            if choix == "2":
                utilisateur_controller.creer_utilisateur()
                Console.pause()
            elif choix == "3":
                Console.succes("Au revoir!")
                return
            # Si choix == "1" ou autre, on continue normalement
        
        # Lancer l'application
        app = GestionEtudiantsApp()
        app.menu_principal()
    except Exception as e:
        logger = Logger.get_instance()
        logger.error(f"Erreur fatale: {str(e)}\n{traceback.format_exc()}")
        Console.erreur(f"Une erreur fatale s'est produite: {e}")
        Console.erreur("Consultez les logs pour plus de détails.")

if __name__ == "__main__":
    main() 