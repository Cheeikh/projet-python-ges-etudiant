"""Module pour améliorer l'affichage console"""
import os
from typing import List, Dict, Any, Optional, Union

class Couleur:
    """Constantes de couleurs ANSI pour la console"""
    RESET = "\033[0m"
    GRAS = "\033[1m"
    SOULIGNE = "\033[4m"
    
    # Couleurs du texte
    NOIR = "\033[30m"
    ROUGE = "\033[31m"
    VERT = "\033[32m"
    JAUNE = "\033[33m"
    BLEU = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    BLANC = "\033[37m"
    
    # Couleurs d'arrière-plan
    BG_NOIR = "\033[40m"
    BG_ROUGE = "\033[41m"
    BG_VERT = "\033[42m"
    BG_JAUNE = "\033[43m"
    BG_BLEU = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_BLANC = "\033[47m"


class Console:
    """Classe utilitaire pour améliorer l'affichage console"""
    
    @staticmethod
    def effacer_ecran():
        """Efface l'écran de la console"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def couleur(texte: str, couleur: str) -> str:
        """
        Applique une couleur à un texte
        
        Args:
            texte: Le texte à colorer
            couleur: La couleur à appliquer (constante de la classe Couleur)
            
        Returns:
            Le texte coloré
        """
        return f"{couleur}{texte}{Couleur.RESET}"
    
    @staticmethod
    def titre(texte: str, niveau: int = 1) -> None:
        """
        Affiche un titre en gras et souligné
        
        Args:
            texte: Le texte du titre
            niveau: Niveau du titre (1 pour titre principal, 2 pour sous-titre, etc.)
        """
        if niveau == 1:
            print(f"\n{Couleur.GRAS}{Couleur.SOULIGNE}{texte}{Couleur.RESET}\n")
        else:
            print(f"\n{Couleur.GRAS}{texte}{Couleur.RESET}")
            print("-" * len(texte))
    
    @staticmethod
    def info(texte: str) -> None:
        """
        Affiche un message d'information en bleu
        
        Args:
            texte: Le message à afficher
        """
        print(f"{Couleur.BLEU}[INFO] {texte}{Couleur.RESET}")
    
    @staticmethod
    def succes(texte: str) -> None:
        """
        Affiche un message de succès en vert
        
        Args:
            texte: Le message à afficher
        """
        print(f"{Couleur.VERT}[SUCCÈS] {texte}{Couleur.RESET}")
    
    @staticmethod
    def avertissement(texte: str) -> None:
        """
        Affiche un message d'avertissement en jaune
        
        Args:
            texte: Le message à afficher
        """
        print(f"{Couleur.JAUNE}[AVERTISSEMENT] {texte}{Couleur.RESET}")
    
    @staticmethod
    def erreur(texte: str) -> None:
        """
        Affiche un message d'erreur en rouge
        
        Args:
            texte: Le message à afficher
        """
        print(f"{Couleur.ROUGE}[ERREUR] {texte}{Couleur.RESET}")
    
    @staticmethod
    def tableau(donnees: List[Dict[str, Any]], colonnes: Optional[List[str]] = None, 
                largeurs: Optional[Dict[str, int]] = None) -> None:
        """
        Affiche un tableau formaté à partir de données
        
        Args:
            donnees: Liste de dictionnaires contenant les données
            colonnes: Liste des colonnes à afficher (clés des dictionnaires)
            largeurs: Dictionnaire des largeurs de colonnes
        """
        if not donnees:
            Console.info("Aucune donnée à afficher")
            return
        
        # Si les colonnes ne sont pas spécifiées, utiliser toutes les clés du premier dictionnaire
        if not colonnes:
            colonnes = list(donnees[0].keys())
        
        # Si les largeurs ne sont pas spécifiées, calculer automatiquement
        if not largeurs:
            largeurs = {}
            for colonne in colonnes:
                # Trouver la longueur maximale entre l'en-tête et les valeurs
                largeur_entete = len(str(colonne))
                largeur_max = max([len(str(d.get(colonne, ""))) for d in donnees] + [largeur_entete])
                largeurs[colonne] = largeur_max + 2  # +2 pour l'espacement
        
        # Calcul de la largeur totale du tableau
        largeur_totale = sum(largeurs.values()) + len(colonnes) + 1
        
        # Ligne horizontale
        ligne_h = "+" + "-" * (largeur_totale - 2) + "+"
        
        # En-tête du tableau
        print(ligne_h)
        ligne_entete = "|"
        for colonne in colonnes:
            largeur = largeurs.get(colonne, 15)
            ligne_entete += f" {Couleur.GRAS}{colonne.center(largeur - 2)}{Couleur.RESET} |"
        print(ligne_entete)
        print(ligne_h)
        
        # Données
        for d in donnees:
            ligne = "|"
            for colonne in colonnes:
                largeur = largeurs.get(colonne, 15)
                valeur = str(d.get(colonne, ""))
                ligne += f" {valeur.ljust(largeur - 2)} |"
            print(ligne)
        
        # Ligne de fin
        print(ligne_h)
    
    @staticmethod
    def menu(titre: str, options: List[str]) -> str:
        """
        Affiche un menu d'options et retourne le choix de l'utilisateur
        
        Args:
            titre: Le titre du menu
            options: Liste des options à afficher
            
        Returns:
            Le choix de l'utilisateur
        """
        Console.titre(titre)
        
        for i, option in enumerate(options, 1):
            print(f"{Couleur.CYAN}{i}.{Couleur.RESET} {option}")
        
        return input(f"\n{Couleur.GRAS}Votre choix: {Couleur.RESET}")
    
    @staticmethod
    def confirmation(message: str) -> bool:
        """
        Demande une confirmation à l'utilisateur
        
        Args:
            message: Le message de confirmation
            
        Returns:
            True si l'utilisateur confirme, False sinon
        """
        reponse = input(f"{Couleur.JAUNE}{message} (o/n): {Couleur.RESET}").lower()
        return reponse == 'o' or reponse == 'oui'
    
    @staticmethod
    def saisie(message: str, obligatoire: bool = False) -> str:
        """
        Demande une saisie à l'utilisateur
        
        Args:
            message: Le message de demande
            obligatoire: Si True, redemande jusqu'à obtenir une valeur
            
        Returns:
            La saisie de l'utilisateur
        """
        while True:
            valeur = input(f"{message}: ").strip()
            if not obligatoire or valeur:
                return valeur
            print(f"{Couleur.ROUGE}Cette valeur est obligatoire.{Couleur.RESET}")
    
    @staticmethod
    def pause():
        """Pause l'exécution jusqu'à ce que l'utilisateur appuie sur Entrée"""
        input(f"\n{Couleur.GRAS}Appuyez sur Entrée pour continuer...{Couleur.RESET}") 