# routes/partage.py
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from extensions import db
from models import LienPartage, Mesure, User
from forms import LienPartageForm
from services import detecter_alertes, moyenne_mobile

# === Blueprint privé (gestion par l'utilisateur) ===
partage_bp = Blueprint("partage", __name__, url_prefix="/partage")


@partage_bp.route("/", methods=["GET", "POST"])
@login_required
def liste():
    form = LienPartageForm()
    if form.validate_on_submit():
        lien = LienPartage(
            utilisateur_id=current_user.id,
            token=LienPartage.generer_token(),
            expires_at=datetime.utcnow() + timedelta(days=form.duree_jours.data),
        )
        db.session.add(lien)
        db.session.commit()
        flash("🔗 Lien généré — copiez-le ci-dessous.", "success")
        return redirect(url_for("partage.liste"))

    liens = (LienPartage.query
             .filter_by(utilisateur_id=current_user.id)
             .order_by(LienPartage.created_at.desc())
             .all())
    return render_template("partage/liste.html", form=form, liens=liens)


@partage_bp.route("/revoquer/<int:lien_id>", methods=["POST"])
@login_required
def revoquer(lien_id):
    lien = LienPartage.query.get_or_404(lien_id)
    if lien.utilisateur_id != current_user.id:
        abort(403)
    lien.revoked = True
    db.session.commit()
    flash("Lien révoqué.", "info")
    return redirect(url_for("partage.liste"))


@partage_bp.route("/supprimer/<int:lien_id>", methods=["POST"])
@login_required
def supprimer(lien_id):
    lien = LienPartage.query.get_or_404(lien_id)
    if lien.utilisateur_id != current_user.id:
        abort(403)
    db.session.delete(lien)
    db.session.commit()
    flash("Lien supprimé.", "info")
    return redirect(url_for("partage.liste"))


# === Blueprint PUBLIC (sans auth) ===
public_bp = Blueprint("public", __name__, url_prefix="/share")


@public_bp.route("/<token>")
def dossier(token):
    """Page publique consultée par le médecin — sans login."""
    lien = LienPartage.query.filter_by(token=token).first()
    if not lien:
        abort(404)
    if lien.revoked:
        return render_template("partage/lien_invalide.html",
                               raison="Ce lien a été révoqué par le patient."), 410
    if lien.est_expire:
        return render_template("partage/lien_invalide.html",
                               raison="Ce lien a expiré."), 410

    patient = User.query.get(lien.utilisateur_id)
    mesures = (Mesure.query
               .filter_by(utilisateur_id=patient.id)
               .order_by(Mesure.date_mesure.asc())
               .all())

    # Stats résumées
    derniere = mesures[-1] if mesures else None

    # Alertes des 10 dernières
    alertes_recentes = []
    for m in mesures[-10:][::-1]:
        for a in detecter_alertes(m, patient.age):
            alertes_recentes.append({**a, "date": m.date_mesure})

    return render_template(
        "partage/dossier_public.html",
        patient=patient,
        mesures=mesures,
        derniere=derniere,
        alertes_recentes=alertes_recentes,
        lien=lien,
    )


@public_bp.route("/<token>/donnees")
def donnees_publiques(token):
    """Endpoint JSON pour Chart.js sur la page publique."""
    from flask import jsonify
    lien = LienPartage.query.filter_by(token=token).first()
    if not lien or not lien.est_valide:
        abort(404)

    mesures = (Mesure.query
               .filter_by(utilisateur_id=lien.utilisateur_id)
               .order_by(Mesure.date_mesure.asc())
               .all())

    labels = [m.date_mesure.strftime("%d %b") for m in mesures]

    def serie(champ):
        return [float(getattr(m, champ)) if getattr(m, champ) is not None else None for m in mesures]

    poids = serie("poids_kg")
    tension_sys = serie("tension_sys")
    tension_dia = serie("tension_dia")
    glycemie = serie("glycemie_gl")
    freq = serie("freq_cardiaque")

    return jsonify({
        "labels": labels,
        "poids":          {"valeurs": poids,       "moyenne_mobile": moyenne_mobile(poids, 3)},
        "tension_sys":    {"valeurs": tension_sys, "moyenne_mobile": None},
        "tension_dia":    {"valeurs": tension_dia, "moyenne_mobile": None},
        "glycemie":       {"valeurs": glycemie,    "moyenne_mobile": moyenne_mobile(glycemie, 3)},
        "freq_cardiaque": {"valeurs": freq,        "moyenne_mobile": moyenne_mobile(freq, 3)},
    })