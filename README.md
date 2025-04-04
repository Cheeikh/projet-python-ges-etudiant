# Système de Gestion des Étudiants

Ce projet est une application Python en ligne de commande permettant de gérer les informations des étudiants d'un établissement. Il utilise MongoDB pour le stockage permanent des données et Redis pour l'optimisation des accès.

## Fonctionnalités

### Gestion des étudiants
- Ajout, modification, recherche et suppression d'étudiants
- Validation des données (téléphone unique, notes entre 0 et 20)
- Tri des étudiants par moyenne
- Exportation et importation des données (CSV, JSON, Excel, PDF)

### Gestion des utilisateurs
- Système d'authentification avec différents rôles (admin, enseignant, étudiant)
- Stockage sécurisé des mots de passe avec bcrypt
- Gestion des sessions utilisateurs via Redis

### Statistiques et rapports
- Calcul de la moyenne générale d'une classe
- Classement des étudiants (top 10)
- Génération de rapports
- Affichage de statistiques détaillées avec répartition par classe et mention

### Notifications
- Alertes pour les nouvelles notes et moyennes faibles

### Interface utilisateur
- Interface en ligne de commande colorée et ergonomique
- Menus interactifs et tableaux formatés
- Indications visuelles par couleur selon le type de message (erreur, succès, etc.)

### Logging et gestion des erreurs
- Système de journalisation complet (fichier et console)
- Gestion avancée des exceptions avec messages appropriés
- Traçabilité des actions utilisateur

## Architecture

Le projet suit les principes SOLID et est organisé selon une architecture MVC (Modèle-Vue-Contrôleur):

```
src/
├── config/           # Configuration (MongoDB, Redis)
├── models/           # Modèles de données
├── controllers/      # Contrôleurs pour les interactions utilisateur
├── services/         # Services métier
└── utils/            # Utilitaires divers
    ├── console.py    # Gestion de l'affichage console amélioré
    ├── exceptions.py # Exceptions personnalisées
    ├── logger.py     # Système de journalisation
    └── ...           # Autres utilitaires
```

## Prérequis

- Python 3.8+
- MongoDB
- Redis

## Installation

1. Clonez le dépôt:
```bash
git clone <url-du-depot>
cd gestionetudiant
```

2. Installez les dépendances:
```bash
pip install -r requirements.txt
```

3. Configurez les variables d'environnement (ou modifiez le fichier `.env`):
```
MONGODB_URI=mongodb://localhost:27017
DB_NAME=gestion_etudiants
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
SECRET_KEY=votre_cle_secrete
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=votre_email@gmail.com
EMAIL_PASSWORD=votre_mot_de_passe
NOTIFICATIONS_ACTIVES=false
```

## Utilisation

Lancez l'application:
```bash
python src/main.py
```

Lors de la première exécution, vous serez invité à créer un utilisateur administrateur. Ensuite, vous pourrez vous connecter et utiliser les différentes fonctionnalités selon votre rôle:

- **Administrateur**: Accès complet à toutes les fonctionnalités
- **Enseignant**: Consultation des étudiants, ajout/modification des notes, accès aux statistiques
- **Étudiant**: Consultation de ses propres notes

## Structure des données

### Collection `etudiants`
```json
{
  "_id": ObjectId,
  "nom": "string",
  "prenom": "string",
  "telephone": "string",
  "classe": "string",
  "notes": {
    "matiere1": float,
    "matiere2": float,
    ...
  }
}
```

### Collection `utilisateurs`
```json
{
  "_id": ObjectId,
  "username": "string",
  "email": "string",
  "role": "admin|enseignant|etudiant",
  "password_hash": "string",
  "id_etudiant": "string"
}
```

## Mise en cache Redis

L'application utilise Redis pour plusieurs aspects:
- Mise en cache des données fréquemment consultées
- Gestion des sessions utilisateurs
- Optimisation des recherches par téléphone

## Journalisation

L'application maintient un journal des événements importants dans le répertoire `logs/`. Chaque jour, un nouveau fichier de journalisation est créé au format `gestion_etudiants_YYYY-MM-DD.log`. Les journaux contiennent des informations sur:
- Connexions/déconnexions des utilisateurs
- Créations, modifications et suppressions d'étudiants et utilisateurs
- Erreurs rencontrées lors de l'exécution
- Statistiques consultées

## Gestion des erreurs

L'application utilise un système d'exceptions personnalisées pour gérer de manière appropriée les différentes erreurs:
- Erreurs de validation des données
- Erreurs d'authentification et d'autorisation
- Erreurs de base de données
- Ressources non trouvées ou en double

## Auteurs

- [Votre nom] - [Votre email] 