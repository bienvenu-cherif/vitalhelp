# models/lien_partage.py
from datetime import datetime, timedelta
import secrets
from extensions import db


class LienPartage(db.Model):
    """
    Table 'liens_partage' — Liens publics expirables permettant au médecin
    de consulter le dossier du patient sans créer de compte.
    """

    __tablename__ = "liens_partage"

    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"),
                               nullable=False, index=True)

    token       = db.Column(db.String(64), unique=True, nullable=False, index=True)
    expires_at  = db.Column(db.DateTime, nullable=True)  # NULL = jamais
    revoked     = db.Column(db.Boolean, nullable=False, default=False)
    created_at  = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    utilisateur = db.relationship("User", backref=db.backref("liens_partage", lazy=True, cascade="all, delete"))

    @staticmethod
    def generer_token():
        """Token URL-safe de 192 bits — imprévisible."""
        return secrets.token_urlsafe(24)

    @property
    def est_expire(self):
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at

    @property
    def est_valide(self):
        return not self.revoked and not self.est_expire

    def __repr__(self):
        return f"<LienPartage {self.token[:8]}…>"