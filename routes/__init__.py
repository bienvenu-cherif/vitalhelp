from .main import main_bp
from .auth import auth_bp
from .mesures import mesures_bp
from .objectifs import objectifs_bp
from .donnees import donnees_bp
from .analyse import analyse_bp
from .partage import partage_bp, public_bp

__all__ = ["main_bp", "auth_bp", "mesures_bp", "objectifs_bp", "donnees_bp", "analyse_bp", "partage_bp", "public_bp"]