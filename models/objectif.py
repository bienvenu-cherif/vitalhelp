# models/objectif.py
from datetime import datetime
from extensions import db


class Objectif(db.Model):
    """
    Table 'objectifs' — Cibles personnelles de l'utilisateur.
    Ex: "Atteindre 68 kg d'ici 3 mois" / "Faire baisser la tension systolique à 120"
    """

    __tablename__ = "objectifs"

    # --- Types d'indicateurs autorisés ---
    TYPES_VALIDES = ("poids", "tension_sys", "tension_dia", "glycemie", "freq_cardiaque", "imc")

    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    titre          = db.Column(db.String(150), nullable=False)
    type_indicateur = db.Column(db.String(20), nullable=False)
    valeur_depart  = db.Column(db.Numeric(6, 2), nullable=False)
    valeur_cible   = db.Column(db.Numeric(6, 2), nullable=False)
    deadline       = db.Column(db.Date, nullable=True)
    completed      = db.Column(db.Boolean, nullable=False, default=False)
    created_at     = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    utilisateur = db.relationship("User", backref=db.backref("objectifs", lazy=True, cascade="all, delete"))

    __table_args__ = (
        db.CheckConstraint(
            "type_indicateur IN ('poids', 'tension_sys', 'tension_dia', 'glycemie', 'freq_cardiaque', 'imc')",
            name="check_type_indicateur"
        ),
        db.CheckConstraint("valeur_depart >= 0 AND valeur_depart <= 500", name="check_depart"),
        db.CheckConstraint("valeur_cible  >= 0 AND valeur_cible  <= 500", name="check_cible"),
    )

    def __repr__(self):
        return f"<Objectif {self.type_indicateur}={self.valeur_cible}>"
