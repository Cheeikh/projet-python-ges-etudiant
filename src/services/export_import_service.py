import csv
import json
import pandas as pd
from typing import List, Optional
from fpdf import FPDF

from src.models.etudiant import Etudiant
from src.services.etudiant.etudiant_service import EtudiantService

class ExportImportService:
    """Service d'exportation et d'importation des données"""
    
    def __init__(self):
        """Initialise le service avec le service d'étudiants"""
        self.etudiant_service = EtudiantService()
    
    def exporter_csv(self, etudiants: Optional[List[Etudiant]] = None, chemin_fichier: str = "etudiants.csv") -> str:
        """
        Exporte les étudiants au format CSV
        
        Args:
            etudiants: Liste des étudiants à exporter (si None, exporte tous les étudiants)
            chemin_fichier: Chemin du fichier CSV à créer
            
        Returns:
            Le chemin du fichier créé
        """
        if etudiants is None:
            etudiants = self.etudiant_service.lister_etudiants()
        
        with open(chemin_fichier, 'w', newline='', encoding='utf-8') as fichier:
            writer = csv.writer(fichier)
            
            # Écrire l'en-tête
            writer.writerow(['ID', 'Nom', 'Prénom', 'Téléphone', 'Classe', 'Notes', 'Moyenne'])
            
            # Écrire les données
            for etudiant in etudiants:
                writer.writerow([
                    etudiant._id,
                    etudiant.nom,
                    etudiant.prenom,
                    etudiant.telephone,
                    etudiant.classe,
                    json.dumps(etudiant.notes),
                    f"{etudiant.moyenne:.2f}"
                ])
        
        return chemin_fichier
    
    def exporter_json(self, etudiants: Optional[List[Etudiant]] = None, chemin_fichier: str = "etudiants.json") -> str:
        """
        Exporte les étudiants au format JSON
        
        Args:
            etudiants: Liste des étudiants à exporter (si None, exporte tous les étudiants)
            chemin_fichier: Chemin du fichier JSON à créer
            
        Returns:
            Le chemin du fichier créé
        """
        if etudiants is None:
            etudiants = self.etudiant_service.lister_etudiants()
        
        data = []
        for etudiant in etudiants:
            etudiant_dict = etudiant.to_dict()
            etudiant_dict['moyenne'] = etudiant.moyenne
            data.append(etudiant_dict)
        
        with open(chemin_fichier, 'w', encoding='utf-8') as fichier:
            json.dump(data, fichier, ensure_ascii=False, indent=4)
        
        return chemin_fichier
    
    def exporter_excel(self, etudiants: Optional[List[Etudiant]] = None, chemin_fichier: str = "etudiants.xlsx") -> str:
        """
        Exporte les étudiants au format Excel
        
        Args:
            etudiants: Liste des étudiants à exporter (si None, exporte tous les étudiants)
            chemin_fichier: Chemin du fichier Excel à créer
            
        Returns:
            Le chemin du fichier créé
        """
        if etudiants is None:
            etudiants = self.etudiant_service.lister_etudiants()
        
        # Convertir en DataFrame
        data = []
        for etudiant in etudiants:
            etudiant_dict = {
                'ID': etudiant._id,
                'Nom': etudiant.nom,
                'Prénom': etudiant.prenom,
                'Téléphone': etudiant.telephone,
                'Classe': etudiant.classe,
                'Moyenne': etudiant.moyenne
            }
            
            # Ajouter les notes
            for matiere, note in etudiant.notes.items():
                etudiant_dict[f"Note {matiere}"] = note
            
            data.append(etudiant_dict)
        
        df = pd.DataFrame(data)
        df.to_excel(chemin_fichier, index=False)
        
        return chemin_fichier
    
    def exporter_pdf(self, etudiants: Optional[List[Etudiant]] = None, chemin_fichier: str = "etudiants.pdf") -> str:
        """
        Exporte les étudiants au format PDF
        
        Args:
            etudiants: Liste des étudiants à exporter (si None, exporte tous les étudiants)
            chemin_fichier: Chemin du fichier PDF à créer
            
        Returns:
            Le chemin du fichier créé
        """
        if etudiants is None:
            etudiants = self.etudiant_service.lister_etudiants()
        
        # Créer un PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Titre
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "Liste des étudiants", 0, 1, "C")
        pdf.ln(10)
        
        # En-têtes
        pdf.set_font("Arial", "B", 12)
        pdf.cell(40, 10, "Nom", 1)
        pdf.cell(40, 10, "Prénom", 1)
        pdf.cell(30, 10, "Téléphone", 1)
        pdf.cell(30, 10, "Classe", 1)
        pdf.cell(20, 10, "Moyenne", 1)
        pdf.ln()
        
        # Données
        pdf.set_font("Arial", "", 12)
        for etudiant in etudiants:
            pdf.cell(40, 10, etudiant.nom, 1)
            pdf.cell(40, 10, etudiant.prenom, 1)
            pdf.cell(30, 10, etudiant.telephone, 1)
            pdf.cell(30, 10, etudiant.classe, 1)
            pdf.cell(20, 10, f"{etudiant.moyenne:.2f}", 1)
            pdf.ln()
        
        pdf.output(chemin_fichier)
        
        return chemin_fichier
    
    def importer_csv(self, chemin_fichier: str) -> List[str]:
        """
        Importe des étudiants depuis un fichier CSV
        
        Args:
            chemin_fichier: Chemin du fichier CSV à importer
            
        Returns:
            Liste des IDs des étudiants importés
        """
        ids_importes = []
        
        with open(chemin_fichier, 'r', newline='', encoding='utf-8') as fichier:
            reader = csv.DictReader(fichier)
            
            for ligne in reader:
                try:
                    # Analyser les notes
                    notes = json.loads(ligne.get('Notes', '{}'))
                    
                    # Créer l'étudiant
                    etudiant = Etudiant(
                        nom=ligne.get('Nom', ''),
                        prenom=ligne.get('Prénom', ''),
                        telephone=ligne.get('Téléphone', ''),
                        classe=ligne.get('Classe', ''),
                        notes=notes
                    )
                    
                    # Ajouter l'étudiant
                    etudiant_id = self.etudiant_service.ajouter_etudiant(etudiant)
                    ids_importes.append(etudiant_id)
                    
                except ValueError as e:
                    # Gérer les erreurs de validation
                    print(f"Erreur lors de l'importation d'un étudiant: {e}")
        
        return ids_importes
    
    def importer_excel(self, chemin_fichier: str) -> List[str]:
        """
        Importe des étudiants depuis un fichier Excel
        
        Args:
            chemin_fichier: Chemin du fichier Excel à importer
            
        Returns:
            Liste des IDs des étudiants importés
        """
        ids_importes = []
        
        # Lire le fichier Excel
        df = pd.read_excel(chemin_fichier)
        
        for _, ligne in df.iterrows():
            try:
                # Extraire les notes
                notes = {}
                for colonne in ligne.index:
                    if colonne.startswith("Note "):
                        matiere = colonne[5:]  # Extraire le nom de la matière
                        notes[matiere] = float(ligne[colonne])
                
                # Créer l'étudiant
                etudiant = Etudiant(
                    nom=ligne.get('Nom', ''),
                    prenom=ligne.get('Prénom', ''),
                    telephone=ligne.get('Téléphone', ''),
                    classe=ligne.get('Classe', ''),
                    notes=notes
                )
                
                # Ajouter l'étudiant
                etudiant_id = self.etudiant_service.ajouter_etudiant(etudiant)
                ids_importes.append(etudiant_id)
                
            except ValueError as e:
                # Gérer les erreurs de validation
                print(f"Erreur lors de l'importation d'un étudiant: {e}")
        
        return ids_importes 