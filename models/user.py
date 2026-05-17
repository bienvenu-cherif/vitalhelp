# models/user.py
from datetime import datetime
from flask_login import UserMixin
from extensions import db, bcrypt


class User(db.Model, UserMixin):
    """
    Table 'users' — Utilisateur de VitalHelp.
    Hérite de UserMixin pour Flask-Login (is_authenticated, get_id, etc.)
    """

    __tablename__ = "users"

    # --- Clé primaire ---
    id = db.Column(db.Integer, primary_key=True)

    # --- Identifiants ---
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # --- Profil personnel (pour IMC + IA) ---
    nom = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    taille_cm = db.Column(db.Integer, nullable=False)
    sexe = db.Column(db.String(10), nullable=False)

    # --- Métadonnées ---
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # --- Contraintes de validation (synchro avec ta DB) ---
    __table_args__ = (
        db.CheckConstraint("age >= 0 AND age <= 150", name="check_age"),
        db.CheckConstraint("taille_cm >= 40 AND taille_cm <= 300", name="check_taille"),
        db.CheckConstraint("sexe IN ('homme', 'femme')", name="check_sexe"),
    )

    # --- Méthodes utilitaires ---
    def set_password(self, password: str):
        """Hash le mot de passe avec bcrypt avant de le stocker"""
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        """Vérifie qu'un mot de passe correspond au hash stocké"""
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def imc(self):
        """Pas encore utilisé — on s'en sert au Module 4"""
        return None

    def __repr__(self):
        return f"<User {self.email}>"