# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

# Configuration Flask-Login
login_manager.login_view = "auth.connexion"           # Page de redirection si non connecté
login_manager.login_message = "Connectez-vous pour accéder à cette page."
login_manager.login_message_category = "warning"     # Pour le styling flash


@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login appelle cette fonction à chaque requête
    pour recharger l'utilisateur à partir de l'ID stocké en session.
    """
    from models import User
    return User.query.get(int(user_id))