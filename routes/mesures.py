# routes/mesures.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from extensions import db
from models import Mesure
from forms import MesureForm
from services import calculer_imc, detecter_alertes

mesures_bp = Blueprint("mesures", __name__, url_prefix="/mesures")


@mesures_bp.route("/", methods=["GET"])
@login_required
def liste():
    """Affiche l'historique des mesures de l'utilisateur connecté."""
    mesures = (Mesure.query
               .filter_by(utilisateur_id=current_user.id)
               .order_by(Mesure.date_mesure.desc())
               .all())
    # On attache les alertes à chaque mesure pour l'affichage
    for m in mesures:
        m.alertes = detecter_alertes(m, current_user.age)
    return render_template("mesures/liste.html", mesures=mesures)


@mesures_bp.route("/ajouter", methods=["GET", "POST"])
@login_required
def ajouter():
    """Page d'ajout d'une nouvelle mesure."""
    form = MesureForm()
    if form.validate_on_submit():
        if not form.at_least_one_value():
            flash("Saisissez au moins une valeur.", "error")
            return render_template("mesures/ajouter.html", form=form)

        # Création de la mesure
        mesure = Mesure(
            utilisateur_id=current_user.id,
            poids_kg=form.poids_kg.data,
            tension_sys=form.tension_sys.data,
            tension_dia=form.tension_dia.data,
            glycemie_gl=form.glycemie_gl.data,
            freq_cardiaque=form.freq_cardiaque.data,
            note=form.note.data.strip() if form.note.data else None,
        )
        # Calcul auto de l'IMC si poids présent
        mesure.imc = calculer_imc(form.poids_kg.data, current_user.taille_cm)

        db.session.add(mesure)
        db.session.commit()

        # Détection des alertes pour feedback immédiat
        alertes = detecter_alertes(mesure, current_user.age)
        if alertes:
            for a in alertes:
                flash(f"⚠️ {a['message']}", "warning" if a["niveau"] == "warning" else "error")
        else:
            flash("✅ Mesure enregistrée — toutes les valeurs sont dans les normes.", "success")

        return redirect(url_for("mesures.liste"))

    return render_template("mesures/ajouter.html", form=form)


@mesures_bp.route("/supprimer/<int:mesure_id>", methods=["POST"])
@login_required
def supprimer(mesure_id):
    """Supprime une mesure (uniquement si elle appartient à l'utilisateur)."""
    mesure = Mesure.query.get_or_404(mesure_id)
    if mesure.utilisateur_id != current_user.id:
        abort(403)  # Interdit : la mesure d'un autre utilisateur
    db.session.delete(mesure)
    db.session.commit()
    flash("Mesure supprimée.", "info")
    return redirect(url_for("mesures.liste"))