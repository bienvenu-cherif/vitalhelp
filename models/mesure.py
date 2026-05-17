# models/mesure.py
from datetime import datetime
from extensions import db


class Mesure(db.Model):
    """
    Table 'mesures' — Enregistrement ponctuel des indicateurs de santé.
    Une ligne = une saisie utilisateur à un moment donné.
    """

    __tablename__ = "mesures"

    # --- Clé primaire ---
    id = db.Column(db.Integer, primary_key=True)

    # --- Clé étrangère vers users ---
    utilisateur_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # --- Indicateurs (tous optionnels : on peut saisir juste 1 valeur) ---
    poids_kg        = db.Column(db.Numeric(5, 2), nullable=True)   # ex: 72.40
    tension_sys     = db.Column(db.Integer, nullable=True)
    tension_dia     = db.Column(db.Integer, nullable=True)
    glycemie_gl     = db.Column(db.Numeric(4, 2), nullable=True)   # ex: 0.95
    freq_cardiaque  = db.Column(db.Integer, nullable=True)
    imc             = db.Column(db.Numeric(4, 1), nullable=True)   # ex: 23.7

    # --- Métadonnées ---
    note         = db.Column(db.Text, nullable=True)
    date_mesure  = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    created_at   = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # --- Relation inverse vers User ---
    utilisateur = db.relationship("User", backref=db.backref("mesures", lazy=True, cascade="all, delete"))

    # --- Contraintes médicales (CHECK) ---
    __table_args__ = (
        db.CheckConstraint("poids_kg IS NULL OR (poids_kg >= 1 AND poids_kg <= 500)", name="check_poids"),
        db.CheckConstraint("tension_sys IS NULL OR (tension_sys >= 50 AND tension_sys <= 300)", name="check_tension_sys"),
        db.CheckConstraint("tension_dia IS NULL OR (tension_dia >= 30 AND tension_dia <= 200)", name="check_tension_dia"),
        db.CheckConstraint("glycemie_gl IS NULL OR (glycemie_gl >= 0 AND glycemie_gl <= 10)", name="check_glycemie"),
        db.CheckConstraint("freq_cardiaque IS NULL OR (freq_cardiaque >= 20 AND freq_cardiaque <= 300)", name="check_freq"),
    )

    def __repr__(self):
        return f"<Mesure u={self.utilisateur_id} {self.date_mesure}>"