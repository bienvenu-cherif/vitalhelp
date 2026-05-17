# routes/analyse.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Mesure, AnalyseIA
from services import analyser_ia

analyse_bp = Blueprint("analyse", __name__, url_prefix="/analyse")


@analyse_bp.route("/")
@login_required
def index():
    """Affiche la dernière analyse + historique."""
    analyses = (AnalyseIA.query
                .filter_by(utilisateur_id=current_user.id)
                .order_by(AnalyseIA.created_at.desc())
                .all())
    derniere = analyses[0] if analyses else None
    historique = analyses[1:6]  # 5 précédentes
    return render_template("analyse/index.html", derniere=derniere, historique=historique)


@analyse_bp.route("/lancer", methods=["POST"])
@login_required
def lancer():
    """Lance une nouvelle analyse IA."""
    mesures = (Mesure.query
               .filter_by(utilisateur_id=current_user.id)
               .order_by(Mesure.date_mesure.desc())
               .all())

    if not mesures:
        flash("Ajoutez au moins une mesure avant de lancer une analyse IA.", "warning")
        return redirect(url_for("analyse.index"))

    try:
        resultat = analyser_ia(current_user, mesures)
    except Exception as e:
        flash(f"Erreur lors de l'analyse IA : {e}", "error")
        return redirect(url_for("analyse.index"))

    # Sauvegarde en DB
    analyse = AnalyseIA(
        utilisateur_id=current_user.id,
        score_global=resultat["score_global"],
        resume=resultat["resume"],
        interpretation=resultat["interpretation"],
        risques=resultat["risques"],
        recommandations=resultat["recommandations"],
        nb_mesures_analysees=len(mesures),
    )
    db.session.add(analyse)
    db.session.commit()

    flash(f"✨ Analyse générée — Score : {resultat['score_global']}/100", "success")
    return redirect(url_for("analyse.index"))


@analyse_bp.route("/historique/<int:analyse_id>")
@login_required
def detail(analyse_id):
    """Affiche une analyse précise depuis l'historique."""
    analyse = AnalyseIA.query.get_or_404(analyse_id)
    if analyse.utilisateur_id != current_user.id:
        from flask import abort
        abort(403)
    return render_template("analyse/detail.html", analyse=analyse)