"""Module contenant les exceptions personnalisées de l'application"""

class ApplicationError(Exception):
    """Classe de base pour toutes les exceptions de l'application"""
    def __init__(self, message="Une erreur est survenue dans l'application"):
        self.message = message
        super().__init__(self.message)


class DatabaseError(ApplicationError):
    """Exception levée pour les erreurs liées à la base de données"""
    def __init__(self, message="Erreur de base de données"):
        super().__init__(message)


class ValidationError(ApplicationError):
    """Exception levée pour les erreurs de validation des données"""
    def __init__(self, message="Erreur de validation des données"):
        super().__init__(message)


class AuthenticationError(ApplicationError):
    """Exception levée pour les erreurs d'authentification"""
    def __init__(self, message="Erreur d'authentification"):
        super().__init__(message)


class AuthorizationError(ApplicationError):
    """Exception levée pour les erreurs d'autorisation (permissions)"""
    def __init__(self, message="Vous n'avez pas les droits nécessaires pour cette action"):
        super().__init__(message)


class ResourceNotFoundError(ApplicationError):
    """Exception levée quand une ressource n'est pas trouvée"""
    def __init__(self, resource_type="La ressource", resource_id=None):
        message = f"{resource_type}"
        if resource_id:
            message += f" avec l'identifiant '{resource_id}'"
        message += " n'a pas été trouvée"
        super().__init__(message)


class DuplicateResourceError(ApplicationError):
    """Exception levée quand on essaie de créer une ressource qui existe déjà"""
    def __init__(self, resource_type="La ressource", identifier=None):
        message = f"{resource_type}"
        if identifier:
            message += f" avec l'identifiant '{identifier}'"
        message += " existe déjà"
        super().__init__(message) 