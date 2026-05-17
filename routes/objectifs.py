# routes/objectifs.py
from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from extensions import db
from models import Objectif, Mesure
from forms import ObjectifForm
from services import calculer_progression

objectifs_bp = Blueprint("objectifs", __name__, url_prefix="/objectifs")

# Mapping type → champ dans la table Mesure
CHAMP_MESURE = {
    "poids": "poids_kg",
    "tension_sys": "tension_sys",
    "tension_dia": "tension_dia",
    "glycemie": "glycemie_gl",
    "freq_cardiaque": "freq_cardiaque",
    "imc": "imc",
}

UNITES = {
    "poids": "kg", "tension_sys": "mmHg", "tension_dia": "mmHg",
    "glycemie": "g/L", "freq_cardiaque": "bpm", "imc": "",
}


def _valeur_actuelle(user_id, type_indicateur):
    """Récupère la dernière valeur enregistrée pour cet indicateur."""
    champ = CHAMP_MESURE[type_indicateur]
    derniere = (Mesure.query
                .filter_by(utilisateur_id=user_id)
                .filter(getattr(Mesure, champ).isnot(None))
                .order_by(Mesure.date_mesure.desc())
                .first())
    if not derniere:
        return None
    return getattr(derniere, champ)


@objectifs_bp.route("/")
@login_required
def liste():
    objectifs = (Objectif.query
                 .filter_by(utilisateur_id=current_user.id)
                 .order_by(Objectif.created_at.desc())
                 .all())
    # Enrichit chaque objectif avec sa valeur actuelle + progression
    for obj in objectifs:
        obj.valeur_actuelle = _valeur_actuelle(current_user.id, obj.type_indicateur)
        obj.progression = calculer_progression(obj, obj.valeur_actuelle)
        obj.unite = UNITES.get(obj.type_indicateur, "")
    return render_template("objectifs/liste.html", objectifs=objectifs)


@objectifs_bp.route("/ajouter", methods=["GET", "POST"])
@login_required
def ajouter():
    form = ObjectifForm()
    if form.validate_on_submit():
        obj = Objectif(
            utilisateur_id=current_user.id,
            titre=form.titre.data.strip(),
            type_indicateur=form.type_indicateur.data,
            valeur_depart=form.valeur_depart.data,
            valeur_cible=form.valeur_cible.data,
            deadline=form.deadline.data,
        )
        db.session.add(obj)
        db.session.commit()
        flash("🎯 Objectif créé !", "success")
        return redirect(url_for("objectifs.liste"))
    return render_template("objectifs/ajouter.html", form=form)


@objectifs_bp.route("/supprimer/<int:obj_id>", methods=["POST"])
@login_required
def supprimer(obj_id):
    obj = Objectif.query.get_or_404(obj_id)
    if obj.utilisateur_id != current_user.id:
        abort(403)
    db.session.delete(obj)
    db.session.commit()
    flash("Objectif supprimé.", "info")
    return redirect(url_for("objectifs.liste"))