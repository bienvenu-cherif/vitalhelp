# models/analyse_ia.py
from datetime import datetime
from extensions import db


class AnalyseIA(db.Model):
    """
    Table 'analyses_ia' — Historique des analyses IA générées.
    On stocke la réponse JSON brute pour la rejouer plus tard.
    """

    __tablename__ = "analyses_ia"

    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"),
                               nullable=False, index=True)

    score_global    = db.Column(db.Integer, nullable=False)
    resume          = db.Column(db.Text, nullable=False)
    interpretation  = db.Column(db.Text, nullable=False)
    risques         = db.Column(db.JSON, nullable=False)         # tableau JSON
    recommandations = db.Column(db.JSON, nullable=False)         # tableau JSON

    nb_mesures_analysees = db.Column(db.Integer, nullable=False, default=0)
    modele_utilise  = db.Column(db.String(50), nullable=False, default="llama-3.3-70b")
    created_at      = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    utilisateur = db.relationship("User", backref=db.backref("analyses_ia", lazy=True, cascade="all, delete"))

    __table_args__ = (
        db.CheckConstraint("score_global >= 0 AND score_global <= 100", name="check_score_ia"),
    )

    def __repr__(self):
        return f"<AnalyseIA u={self.utilisateur_id} score={self.score_global}>"