# routes/donnees.py
"""
Endpoints JSON qui alimentent Chart.js côté navigateur.
"""
from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from models import Mesure, Objectif
from services import moyenne_mobile

donnees_bp = Blueprint("donnees", __name__, url_prefix="/donnees")


@donnees_bp.route("/courbes")
@login_required
def courbes():
    """
    Retourne les données pour les 4 courbes du dashboard.
    Format :
    {
      "labels": ["12 jan", "15 jan", ...],
      "poids": { "valeurs": [...], "moyenne_mobile": [...], "objectif": 70 },
      "tension_sys": { ... },
      ...
    }
    """
    mesures = (Mesure.query
               .filter_by(utilisateur_id=current_user.id)
               .order_by(Mesure.date_mesure.asc())
               .all())

    # Labels (axes X) — format français court
    labels = [m.date_mesure.strftime("%d %b") for m in mesures]

    # Construit les datasets
    def serie(champ):
        return [float(getattr(m, champ)) if getattr(m, champ) is not None else None for m in mesures]

    poids        = serie("poids_kg")
    tension_sys  = serie("tension_sys")
    tension_dia  = serie("tension_dia")
    glycemie     = serie("glycemie_gl")
    freq         = serie("freq_cardiaque")
    imc          = serie("imc")

    # Objectifs actifs (un par type d'indicateur) → on prend le plus récent
    objectifs_par_type = {}
    for obj in Objectif.query.filter_by(utilisateur_id=current_user.id, completed=False).order_by(Objectif.created_at.desc()).all():
        if obj.type_indicateur not in objectifs_par_type:
            objectifs_par_type[obj.type_indicateur] = float(obj.valeur_cible)

    return jsonify({
        "labels": labels,
        "poids": {
            "valeurs": poids,
            "moyenne_mobile": moyenne_mobile(poids, 3),
            "objectif": objectifs_par_type.get("poids"),
        },
        "tension_sys": {
            "valeurs": tension_sys,
            "moyenne_mobile": moyenne_mobile(tension_sys, 3),
            "objectif": objectifs_par_type.get("tension_sys"),
        },
        "tension_dia": {
            "valeurs": tension_dia,
            "moyenne_mobile": moyenne_mobile(tension_dia, 3),
            "objectif": objectifs_par_type.get("tension_dia"),
        },
        "glycemie": {
            "valeurs": glycemie,
            "moyenne_mobile": moyenne_mobile(glycemie, 3),
            "objectif": objectifs_par_type.get("glycemie"),
        },
        "freq_cardiaque": {
            "valeurs": freq,
            "moyenne_mobile": moyenne_mobile(freq, 3),
            "objectif": objectifs_par_type.get("freq_cardiaque"),
        },
        "imc": {
            "valeurs": imc,
            "moyenne_mobile": moyenne_mobile(imc, 3),
            "objectif": objectifs_par_type.get("imc"),
        },
    })