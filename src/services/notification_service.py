import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from src.models.etudiant import Etudiant

# Chargement des variables d'environnement
load_dotenv()

class NotificationService:
    """Service de gestion des notifications"""
    
    def __init__(self):
        """Initialise le service avec les paramètres d'email"""
        self.email_host = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
        self.email_port = int(os.getenv('EMAIL_PORT', 587))
        self.email_user = os.getenv('EMAIL_USER', '')
        self.email_password = os.getenv('EMAIL_PASSWORD', '')
        
        # Flag pour activer/désactiver les notifications (utile pour les tests)
        self.notifications_actives = os.getenv('NOTIFICATIONS_ACTIVES', 'false').lower() == 'true'
    
    def envoyer_email(self, destinataire: str, sujet: str, contenu: str) -> bool:
        """
        Envoie un email
        
        Args:
            destinataire: Adresse email du destinataire
            sujet: Sujet de l'email
            contenu: Contenu HTML de l'email
            
        Returns:
            True si l'envoi a réussi, False sinon
        """
        if not self.notifications_actives:
            print(f"[NOTIFICATION DÉSACTIVÉE] Email à {destinataire}: {sujet}")
            return True
        
        try:
            # Créer le message
            message = MIMEMultipart()
            message['From'] = self.email_user
            message['To'] = destinataire
            message['Subject'] = sujet
            
            # Ajouter le contenu HTML
            message.attach(MIMEText(contenu, 'html'))
            
            # Connexion au serveur SMTP
            with smtplib.SMTP(self.email_host, self.email_port) as serveur:
                serveur.starttls()
                serveur.login(self.email_user, self.email_password)
                serveur.send_message(message)
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {e}")
            return False
    
    def notifier_nouvelle_note(self, etudiant: Etudiant, matiere: str, note: float) -> bool:
        """
        Notifie l'étudiant d'une nouvelle note
        
        Args:
            etudiant: L'étudiant concerné
            matiere: La matière concernée
            note: La note attribuée
            
        Returns:
            True si la notification a été envoyée, False sinon
        """
        # Simuler un email (on suppose qu'on a l'email de l'étudiant)
        email = f"{etudiant.prenom.lower()}.{etudiant.nom.lower()}@example.com"
        
        sujet = f"Nouvelle note en {matiere}"
        
        contenu = f"""
        <html>
        <body>
            <h2>Bonjour {etudiant.prenom} {etudiant.nom},</h2>
            <p>Une nouvelle note vous a été attribuée:</p>
            <ul>
                <li><strong>Matière:</strong> {matiere}</li>
                <li><strong>Note:</strong> {note}/20</li>
            </ul>
            <p>Votre moyenne générale est maintenant de {etudiant.moyenne:.2f}/20.</p>
            <p>Bonne journée!</p>
        </body>
        </html>
        """
        
        return self.envoyer_email(email, sujet, contenu)
    
    def notifier_moyenne_faible(self, etudiant: Etudiant) -> bool:
        """
        Notifie l'étudiant si sa moyenne est en dessous de 10
        
        Args:
            etudiant: L'étudiant concerné
            
        Returns:
            True si la notification a été envoyée, False sinon
        """
        if etudiant.moyenne >= 10:
            return False
        
        # Simuler un email
        email = f"{etudiant.prenom.lower()}.{etudiant.nom.lower()}@example.com"
        
        sujet = "Alerte: Moyenne en dessous de 10/20"
        
        contenu = f"""
        <html>
        <body>
            <h2>Bonjour {etudiant.prenom} {etudiant.nom},</h2>
            <p>Attention, votre moyenne générale est actuellement de <strong>{etudiant.moyenne:.2f}/20</strong>.</p>
            <p>Nous vous invitons à prendre rendez-vous avec vos enseignants pour discuter de vos difficultés et trouver des solutions.</p>
            <p>Bonne journée!</p>
        </body>
        </html>
        """
        
        return self.envoyer_email(email, sujet, contenu)
    
    def envoyer_rapport_classe(self, classe: str, etudiants: List[Etudiant], moyenne_classe: float) -> bool:
        """
        Envoie un rapport sur les résultats d'une classe aux enseignants
        
        Args:
            classe: La classe concernée
            etudiants: Liste des étudiants de la classe
            moyenne_classe: Moyenne générale de la classe
            
        Returns:
            True si la notification a été envoyée, False sinon
        """
        # Simuler un email aux enseignants
        email = f"enseignants.{classe.lower()}@example.com"
        
        sujet = f"Rapport des résultats de la classe {classe}"
        
        # Construire le tableau des résultats
        tableau_etudiants = ""
        for i, etudiant in enumerate(etudiants, 1):
            tableau_etudiants += f"""
            <tr>
                <td>{i}</td>
                <td>{etudiant.nom}</td>
                <td>{etudiant.prenom}</td>
                <td>{etudiant.moyenne:.2f}/20</td>
            </tr>
            """
        
        contenu = f"""
        <html>
        <body>
            <h2>Rapport de la classe {classe}</h2>
            <p>Moyenne générale de la classe: <strong>{moyenne_classe:.2f}/20</strong></p>
            
            <h3>Classement des étudiants:</h3>
            <table border="1" cellpadding="5">
                <tr>
                    <th>Rang</th>
                    <th>Nom</th>
                    <th>Prénom</th>
                    <th>Moyenne</th>
                </tr>
                {tableau_etudiants}
            </table>
            
            <p>Bonne journée!</p>
        </body>
        </html>
        """
        
        return self.envoyer_email(email, sujet, contenu) 