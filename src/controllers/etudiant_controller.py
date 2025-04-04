from typing import List, Optional
import re

from src.models.etudiant import Etudiant
from src.services.etudiant.etudiant_service import EtudiantService
from src.services.export_import_service import ExportImportService
from src.services.notification_service import NotificationService
from src.utils.console.console import Console, Couleur
from src.utils.logger import Logger
from src.utils.exception.exceptions import ValidationError, ResourceNotFoundError

class EtudiantController:
    """Contrôleur pour gérer les interactions liées aux étudiants"""
    
    def __init__(self):
        """Initialise le contrôleur avec les services nécessaires"""
        self.etudiant_service = EtudiantService()
        self.export_import_service = ExportImportService()
        self.notification_service = NotificationService()
        self.logger = Logger.get_instance()
    
    def saisir_etudiant(self) -> Optional[str]:
        """
        Saisie les informations d'un nouvel étudiant
        
        Returns:
            L'ID de l'étudiant créé ou None si la création a échoué
        """
        Console.titre("Ajout d'un nouvel étudiant")
        
        # Saisie des informations
        nom = Console.saisie("Nom", True)
        prenom = Console.saisie("Prénom", True)
        
        # Validation du téléphone
        while True:
            telephone = Console.saisie("Téléphone", True)
            if re.match(r'^\d{9,10}$', telephone):
                break
            Console.erreur("Numéro de téléphone invalide. Veuillez entrer 9 ou 10 chiffres.")
        
        classe = Console.saisie("Classe", True)
        
        # Saisie des notes
        notes = {}
        ajouter_notes = Console.confirmation("Voulez-vous ajouter des notes maintenant?")
        
        if ajouter_notes:
            while True:
                matiere = Console.saisie("Matière (ou laisser vide pour terminer)")
                if not matiere:
                    break
                
                while True:
                    try:
                        note_str = Console.saisie(f"Note pour {matiere} (0-20)")
                        note = float(note_str)
                        if 0 <= note <= 20:
                            notes[matiere] = note
                            break
                        Console.erreur("La note doit être comprise entre 0 et 20.")
                    except ValueError:
                        Console.erreur("Veuillez entrer un nombre valide.")
        
        # Création de l'étudiant
        try:
            etudiant = Etudiant(nom=nom, prenom=prenom, telephone=telephone, classe=classe, notes=notes)
            etudiant_id = self.etudiant_service.ajouter_etudiant(etudiant)
            
            Console.succes(f"Étudiant ajouté avec succès! ID: {etudiant_id}")
            self.logger.info(f"Nouvel étudiant créé: {prenom} {nom} ({etudiant_id})")
            
            # Vérifier si on doit envoyer une notification pour moyenne faible
            if etudiant.moyenne < 10 and etudiant.notes:
                self.notification_service.notifier_moyenne_faible(etudiant)
                self.logger.info(f"Notification de moyenne faible envoyée pour l'étudiant {etudiant_id}")
            
            return etudiant_id
            
        except ValidationError as e:
            Console.erreur(f"Erreur de validation: {e}")
            self.logger.error(f"Erreur de validation lors de la création d'un étudiant: {e}")
            return None
        except Exception as e:
            Console.erreur(f"Erreur lors de l'ajout de l'étudiant: {e}")
            self.logger.error(f"Erreur lors de l'ajout d'un étudiant: {e}")
            return None
    
    def afficher_etudiants(self, etudiants: Optional[List[Etudiant]] = None) -> None:
        """
        Affiche une liste d'étudiants sous forme de tableau
        
        Args:
            etudiants: Liste des étudiants à afficher (si None, affiche tous les étudiants)
        """
        if etudiants is None:
            etudiants = self.etudiant_service.lister_etudiants()
            self.logger.info(f"Affichage de tous les étudiants ({len(etudiants)} trouvés)")
        
        if not etudiants:
            Console.info("Aucun étudiant trouvé.")
            return
        
        Console.titre("Liste des étudiants")
        
        donnees = []
        for etudiant in etudiants:
            donnees.append({
                "ID": etudiant._id if etudiant._id else 'N/A',
                "Nom": etudiant.nom,
                "Prénom": etudiant.prenom,
                "Téléphone": etudiant.telephone,
                "Classe": etudiant.classe,
                "Moyenne": f"{etudiant.moyenne:.2f}"
            })
        
        Console.tableau(donnees)
    
    def rechercher_etudiant(self) -> None:
        """Interface de recherche d'étudiants"""
        Console.titre("Recherche d'étudiants")
        
        options = [
            "Par nom",
            "Par prénom",
            "Par téléphone",
            "Par classe"
        ]
        
        choix = Console.menu("Type de recherche", options)
        
        critere = {}
        if choix == "1":
            nom = Console.saisie("Nom", True)
            critere = {"nom": {"$regex": nom, "$options": "i"}}
            self.logger.info(f"Recherche d'étudiants par nom: {nom}")
        elif choix == "2":
            prenom = Console.saisie("Prénom", True)
            critere = {"prenom": {"$regex": prenom, "$options": "i"}}
            self.logger.info(f"Recherche d'étudiants par prénom: {prenom}")
        elif choix == "3":
            telephone = Console.saisie("Téléphone", True)
            critere = {"telephone": telephone}
            self.logger.info(f"Recherche d'étudiants par téléphone: {telephone}")
        elif choix == "4":
            classe = Console.saisie("Classe", True)
            critere = {"classe": {"$regex": classe, "$options": "i"}}
            self.logger.info(f"Recherche d'étudiants par classe: {classe}")
        else:
            Console.erreur("Choix invalide.")
            return
        
        etudiants = self.etudiant_service.rechercher_etudiants(critere)
        self.logger.info(f"Résultat de recherche: {len(etudiants)} étudiant(s) trouvé(s)")
        self.afficher_etudiants(etudiants)
    
    def modifier_notes(self) -> None:
        """Interface de modification des notes d'un étudiant"""
        telephone = Console.saisie("Entrez le téléphone de l'étudiant", True)
        
        try:
            etudiant = self.etudiant_service.obtenir_etudiant_par_telephone(telephone)
            if not etudiant:
                raise ResourceNotFoundError("étudiant", "téléphone", telephone)
            
            # Vérifier que l'ID de l'étudiant est valide
            if not etudiant._id:
                Console.erreur("Impossible de modifier les notes: l'étudiant n'a pas d'identifiant valide.")
                self.logger.error(f"Tentative de modification des notes d'un étudiant sans ID valide (téléphone: {telephone})")
                return
                
            Console.titre(f"Notes de {etudiant.prenom} {etudiant.nom}")
            Console.info(f"Classe: {etudiant.classe}")
            
            if etudiant.notes:
                notes_data = []
                for matiere, note in etudiant.notes.items():
                    notes_data.append({
                        "Matière": matiere,
                        "Note": f"{note}/20"
                    })
                Console.tableau(notes_data)
                Console.info(f"Moyenne actuelle: {etudiant.moyenne:.2f}/20")
            else:
                Console.info("Aucune note enregistrée")
            
            options = [
                "Ajouter/Modifier une note",
                "Supprimer une note",
                "Retour"
            ]
            
            choix = Console.menu("Actions", options)
            
            if choix == "1":
                matiere = Console.saisie("Matière", True)
                
                while True:
                    try:
                        note_str = Console.saisie(f"Note pour {matiere} (0-20)", True)
                        note = float(note_str)
                        if 0 <= note <= 20:
                            etudiant.ajouter_note(matiere, note)
                            break
                        Console.erreur("La note doit être comprise entre 0 et 20.")
                    except ValueError:
                        Console.erreur("Veuillez entrer un nombre valide.")
                
                # Mettre à jour l'étudiant dans la base de données
                self.logger.info(f"Tentative de mise à jour de l'étudiant {etudiant._id} pour ajouter la note {matiere}: {note}")
                if self.etudiant_service.mettre_a_jour_etudiant(etudiant):
                    Console.succes(f"Note ajoutée/modifiée avec succès. Nouvelle moyenne: {etudiant.moyenne:.2f}/20")
                    self.logger.info(f"Note de {matiere} ({note}/20) ajoutée pour l'étudiant {etudiant._id}")
                    
                    # Envoyer des notifications
                    self.notification_service.notifier_nouvelle_note(etudiant, matiere, note)
                    
                    if etudiant.moyenne < 10:
                        self.notification_service.notifier_moyenne_faible(etudiant)
                        self.logger.info(f"Notification de moyenne faible envoyée pour l'étudiant {etudiant._id}")
                    
                else:
                    Console.erreur("Erreur lors de la mise à jour des notes.")
                
            elif choix == "2":
                if not etudiant.notes:
                    Console.info("Aucune note à supprimer.")
                    return
                
                matieres = list(etudiant.notes.keys())
                options_matieres = [f"{matiere}: {etudiant.notes[matiere]}/20" for matiere in matieres]
                options_matieres.append("Annuler")
                
                choix_matiere = Console.menu("Choisissez la matière à supprimer", options_matieres)
                
                try:
                    index = int(choix_matiere) - 1
                    if 0 <= index < len(matieres):
                        matiere = matieres[index]
                        
                        if Console.confirmation(f"Êtes-vous sûr de vouloir supprimer la note de {matiere}?"):
                            del etudiant.notes[matiere]
                            
                            if self.etudiant_service.mettre_a_jour_etudiant(etudiant):
                                Console.succes(f"Note supprimée avec succès. Nouvelle moyenne: {etudiant.moyenne:.2f}/20")
                                self.logger.info(f"Note de {matiere} supprimée pour l'étudiant {etudiant._id}")
                            else:
                                Console.erreur("Erreur lors de la mise à jour des notes.")
                                self.logger.error(f"Erreur lors de la suppression de la note de {matiere} pour l'étudiant {etudiant._id}")
                except ValueError:
                    Console.erreur("Choix invalide.")
                
        except ResourceNotFoundError as e:
            Console.erreur(f"Erreur: {e}")
            self.logger.warning(f"Tentative de modification de notes: {e}")
        except Exception as e:
            Console.erreur(f"Une erreur s'est produite: {e}")
            self.logger.error(f"Erreur lors de la modification des notes: {e}")
    
    def supprimer_etudiant(self) -> None:
        """Interface de suppression d'un étudiant"""
        telephone = Console.saisie("Entrez le téléphone de l'étudiant à supprimer", True)
        
        try:
            etudiant = self.etudiant_service.obtenir_etudiant_par_telephone(telephone)
            if not etudiant:
                raise ResourceNotFoundError("étudiant", "téléphone", telephone)
            
            Console.titre(f"Étudiant trouvé: {etudiant.prenom} {etudiant.nom}")
            Console.info(f"Classe: {etudiant.classe}")
            
            if Console.confirmation(f"Êtes-vous sûr de vouloir supprimer cet étudiant?"):
                if self.etudiant_service.supprimer_etudiant(etudiant._id):
                    Console.succes("Étudiant supprimé avec succès.")
                    self.logger.info(f"Étudiant supprimé: {etudiant._id} ({etudiant.prenom} {etudiant.nom})")
                else:
                    Console.erreur("Erreur lors de la suppression de l'étudiant.")
                    self.logger.error(f"Échec de la suppression de l'étudiant {etudiant._id}")
        
        except ResourceNotFoundError as e:
            Console.erreur(f"Erreur: {e}")
            self.logger.warning(f"Tentative de suppression: {e}")
        except Exception as e:
            Console.erreur(f"Une erreur s'est produite: {e}")
            self.logger.error(f"Erreur lors de la suppression d'un étudiant: {e}")
    
    def exporter_donnees(self) -> None:
        """Interface d'exportation des données"""
        Console.titre("Exportation des données")
        
        options_etudiants = [
            "Tous les étudiants",
            "Par classe"
        ]
        
        choix_etudiants = Console.menu("Sélection des étudiants", options_etudiants)
        
        etudiants = None
        if choix_etudiants == "2":
            classe = Console.saisie("Classe", True)
            etudiants = self.etudiant_service.lister_etudiants_par_classe(classe)
            if not etudiants:
                Console.avertissement(f"Aucun étudiant trouvé pour la classe {classe}.")
                return
            self.logger.info(f"Exportation des étudiants de la classe {classe} ({len(etudiants)} étudiants)")
        else:
            self.logger.info("Exportation de tous les étudiants")
        
        options_format = [
            "CSV",
            "JSON",
            "Excel",
            "PDF"
        ]
        
        choix_format = Console.menu("Format d'exportation", options_format)
        
        chemin_fichier = Console.saisie("Nom du fichier (avec extension)", True)
        
        try:
            if choix_format == "1":
                chemin = self.export_import_service.exporter_csv(etudiants, chemin_fichier)
                self.logger.info(f"Exportation CSV réussie: {chemin}")
            elif choix_format == "2":
                chemin = self.export_import_service.exporter_json(etudiants, chemin_fichier)
                self.logger.info(f"Exportation JSON réussie: {chemin}")
            elif choix_format == "3":
                chemin = self.export_import_service.exporter_excel(etudiants, chemin_fichier)
                self.logger.info(f"Exportation Excel réussie: {chemin}")
            elif choix_format == "4":
                chemin = self.export_import_service.exporter_pdf(etudiants, chemin_fichier)
                self.logger.info(f"Exportation PDF réussie: {chemin}")
            else:
                Console.erreur("Format non supporté.")
                return
            
            Console.succes(f"Données exportées avec succès vers: {chemin}")
        except Exception as e:
            Console.erreur(f"Erreur lors de l'exportation: {e}")
            self.logger.error(f"Erreur lors de l'exportation: {e}")
    
    def importer_donnees(self) -> None:
        """Interface d'importation des données"""
        Console.titre("Importation des données")
        
        options_format = [
            "CSV",
            "JSON",
            "Excel"
        ]
        
        choix_format = Console.menu("Format du fichier à importer", options_format)
        
        chemin_fichier = Console.saisie("Chemin du fichier", True)
        
        try:
            if choix_format == "1":
                count = self.export_import_service.importer_csv(chemin_fichier)
                format_nom = "CSV"
            elif choix_format == "2":
                count = self.export_import_service.importer_json(chemin_fichier)
                format_nom = "JSON"
            elif choix_format == "3":
                count = self.export_import_service.importer_excel(chemin_fichier)
                format_nom = "Excel"
            else:
                Console.erreur("Format non supporté.")
                return
            
            if count > 0:
                Console.succes(f"{count} étudiant(s) importé(s) avec succès.")
                self.logger.info(f"Importation {format_nom} réussie: {count} étudiant(s) importé(s) depuis {chemin_fichier}")
            else:
                Console.avertissement("Aucun étudiant importé.")
                self.logger.warning(f"Importation {format_nom} sans données: {chemin_fichier}")
                
        except FileNotFoundError:
            Console.erreur(f"Le fichier {chemin_fichier} n'existe pas.")
            self.logger.error(f"Erreur d'importation: fichier non trouvé: {chemin_fichier}")
        except Exception as e:
            Console.erreur(f"Erreur lors de l'importation: {e}")
            self.logger.error(f"Erreur lors de l'importation depuis {chemin_fichier}: {e}")
    
    def afficher_statistiques(self) -> None:
        """Affiche des statistiques sur les étudiants"""
        Console.titre("Statistiques des étudiants")
        
        # Compter le nombre total d'étudiants
        etudiants = self.etudiant_service.lister_etudiants()
        nb_total = len(etudiants)
        
        if nb_total == 0:
            Console.info("Aucun étudiant enregistré dans le système.")
            return
        
        # Calculer des statistiques
        classes = {}
        nb_avec_notes = 0
        somme_moyennes = 0
        moyennes_par_classe = {}
        
        for etudiant in etudiants:
            # Compter par classe
            if etudiant.classe in classes:
                classes[etudiant.classe] += 1
            else:
                classes[etudiant.classe] = 1
                moyennes_par_classe[etudiant.classe] = []
            
            # Statistiques sur les notes
            if etudiant.notes:
                nb_avec_notes += 1
                somme_moyennes += etudiant.moyenne
                moyennes_par_classe[etudiant.classe].append(etudiant.moyenne)
        
        # Afficher le nombre d'étudiants
        Console.info(f"Nombre total d'étudiants: {Console.couleur(str(nb_total), Couleur.VERT)}")
        Console.info(f"Nombre d'étudiants avec notes: {Console.couleur(str(nb_avec_notes), Couleur.VERT)} ({nb_avec_notes/nb_total*100:.1f}%)")
        
        # Afficher la répartition par classe
        Console.titre("Répartition par classe", niveau=2)
        
        donnees_classes = []
        for classe, nombre in classes.items():
            donnees_classes.append({
                "Classe": classe,
                "Nombre d'étudiants": nombre,
                "Pourcentage": f"{nombre/nb_total*100:.1f}%"
            })
        
        Console.tableau(donnees_classes)
        
        # Afficher les statistiques de moyenne
        if nb_avec_notes > 0:
            Console.titre("Statistiques de moyenne", niveau=2)
            
            moyenne_generale = somme_moyennes / nb_avec_notes
            Console.info(f"Moyenne générale: {Console.couleur(f'{moyenne_generale:.2f}/20', Couleur.GRAS)}")
            
            # Statistiques par classe
            donnees_moyennes = []
            for classe, moyennes in moyennes_par_classe.items():
                if moyennes:
                    moy_classe = sum(moyennes) / len(moyennes)
                    donnees_moyennes.append({
                        "Classe": classe,
                        "Nombre d'étudiants avec notes": len(moyennes),
                        "Moyenne de classe": f"{moy_classe:.2f}/20"
                    })
            
            if donnees_moyennes:
                Console.tableau(donnees_moyennes)
            
            # Afficher la répartition des résultats
            nb_insuffisant = sum(1 for e in etudiants if e.notes and e.moyenne < 10)
            nb_passable = sum(1 for e in etudiants if e.notes and 10 <= e.moyenne < 12)
            nb_assez_bien = sum(1 for e in etudiants if e.notes and 12 <= e.moyenne < 14)
            nb_bien = sum(1 for e in etudiants if e.notes and 14 <= e.moyenne < 16)
            nb_tres_bien = sum(1 for e in etudiants if e.notes and e.moyenne >= 16)
            
            Console.titre("Répartition des moyennes", niveau=2)
            
            donnees_repartition = [
                {"Mention": Console.couleur("Très bien", Couleur.VERT), "Nombre": nb_tres_bien, "Pourcentage": f"{nb_tres_bien/nb_avec_notes*100:.1f}%"},
                {"Mention": Console.couleur("Bien", Couleur.VERT), "Nombre": nb_bien, "Pourcentage": f"{nb_bien/nb_avec_notes*100:.1f}%"},
                {"Mention": Console.couleur("Assez bien", Couleur.CYAN), "Nombre": nb_assez_bien, "Pourcentage": f"{nb_assez_bien/nb_avec_notes*100:.1f}%"},
                {"Mention": Console.couleur("Passable", Couleur.JAUNE), "Nombre": nb_passable, "Pourcentage": f"{nb_passable/nb_avec_notes*100:.1f}%"},
                {"Mention": Console.couleur("Insuffisant", Couleur.ROUGE), "Nombre": nb_insuffisant, "Pourcentage": f"{nb_insuffisant/nb_avec_notes*100:.1f}%"}
            ]
            
            Console.tableau(donnees_repartition)
            
        self.logger.info("Consultation des statistiques des étudiants") 