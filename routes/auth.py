# routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User
from forms import InscriptionForm, ConnexionForm, ProfilForm

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/inscription", methods=["GET", "POST"])
def inscription():
    # Déjà connecté ? On le renvoie au dashboard
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = InscriptionForm()
    if form.validate_on_submit():
        # 1. Créer l'utilisateur
        user = User(
            nom=form.nom.data.strip(),
            email=form.email.data.lower().strip(),
            age=form.age.data,
            taille_cm=form.taille_cm.data,
            sexe=form.sexe.data,
        )
        # 2. Hasher le mot de passe (jamais en clair !)
        user.set_password(form.password.data)
        # 3. Sauver en DB
        db.session.add(user)
        db.session.commit()
        # 4. Connecter automatiquement
        login_user(user)
        flash(f"Bienvenue {user.nom} ! Votre journal est prêt.", "success")
        return redirect(url_for("main.dashboard"))

    return render_template("auth/inscription.html", form=form)


@auth_bp.route("/connexion", methods=["GET", "POST"])
def connexion():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = ConnexionForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)  # remember=True : cookie persistant
            flash(f"Bon retour {user.nom} !", "success")
            # Si on essayait d'accéder à une page protégée, on y retourne
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.dashboard"))
        flash("Identifiants invalides.", "error")

    return render_template("auth/connexion.html", form=form)


@auth_bp.route("/deconnexion")
@login_required
def deconnexion():
    logout_user()
    flash("Vous êtes déconnecté.", "info")
    return redirect(url_for("main.accueil"))

@auth_bp.route("/profil", methods=["GET", "POST"])
@login_required
def profil():
    form = ProfilForm(obj=current_user)
    if form.validate_on_submit():
        current_user.nom = form.nom.data.strip()
        current_user.age = form.age.data
        current_user.taille_cm = form.taille_cm.data
        current_user.sexe = form.sexe.data
        db.session.commit()
        flash("✅ Profil mis à jour.", "success")
        return redirect(url_for("auth.profil"))
    return render_template("auth/profil.html", form=form)