# routes/main.py
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import Mesure
from services import detecter_alertes, categoriser_imc

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def accueil():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    # Stats globales (chiffres "vanity" pour la landing)
    from models import User, Mesure
    stats_globales = {
        "users": User.query.count(),
        "mesures": Mesure.query.count(),
    }
    return render_template("accueil.html", stats=stats_globales)

@main_bp.route("/dashboard")
@login_required
def dashboard():
    # Toutes les mesures, triées par date
    mesures = (Mesure.query
               .filter_by(utilisateur_id=current_user.id)
               .order_by(Mesure.date_mesure.desc())
               .all())

    # Dernière mesure
    derniere = mesures[0] if mesures else None

    # Alertes récentes (sur les 10 dernières mesures)
    alertes = []
    for m in mesures[:10]:
        for a in detecter_alertes(m, current_user.age):
            alertes.append({**a, "date": m.date_mesure})
    alertes = alertes[:5]  # max 5

    # Catégorisation IMC actuelle
    categorie_imc = None
    if derniere and derniere.imc:
        categorie_imc = categoriser_imc(float(derniere.imc), current_user.age)

    return render_template(
        "dashboard.html",
        derniere=derniere,
        total_mesures=len(mesures),
        alertes=alertes,
        categorie_imc=categorie_imc,
    )

