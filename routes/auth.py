# routes/auth.py
import os
from hashlib import md5

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User
from forms import InscriptionForm, ConnexionForm, ProfilForm
from werkzeug.utils import secure_filename

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/inscription", methods=["GET", "POST"])
def inscription():
    # Déjà connecté ? On le renvoie au dashboard
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = InscriptionForm()
    if form.validate_on_submit():
        avatar_url = None
        avatar_file = form.avatar.data
        if avatar_file and getattr(avatar_file, 'filename', None):
            avatar_url = save_avatar_file(avatar_file, form.email.data.lower().strip())

        # 1. Créer l'utilisateur
        user = User(
            nom=form.nom.data.strip(),
            email=form.email.data.lower().strip(),
            age=form.age.data,
            taille_cm=form.taille_cm.data,
            sexe=form.sexe.data,
            avatar_url=avatar_url,
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
        try:
            user = User.query.filter_by(email=form.email.data.lower().strip()).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=True)  # remember=True : cookie persistant
                flash(f"Bon retour {user.nom} !", "success")
                # Si on essayait d'accéder à une page protégée, on y retourne
                next_page = request.args.get("next")
                return redirect(next_page or url_for("main.dashboard"))
            flash("Identifiants invalides.", "error")
        except Exception:
            current_app.logger.exception("Erreur pendant la tentative de connexion")
            flash("Erreur serveur : impossible de vérifier vos identifiants. Réessayez plus tard.", "error")

    return render_template("auth/connexion.html", form=form)


@auth_bp.route("/avatar")
def avatar():
    email = request.args.get("email", "", type=str).lower().strip()
    if not email:
        return jsonify(found=False)

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify(found=False)

    gravatar_hash = md5(user.email.encode("utf-8")).hexdigest()
    avatar_url = getattr(user, "avatar_url", None) or f"https://www.gravatar.com/avatar/{gravatar_hash}?d=identicon&s=280"
    return jsonify(found=True, name=user.nom, avatar=avatar_url)


@auth_bp.route("/deconnexion")
@login_required
def deconnexion():
    logout_user()
    flash("Vous êtes déconnecté.", "info")
    return redirect(url_for("main.accueil"))


def save_avatar_file(file_storage, identifier):
    if not file_storage or not getattr(file_storage, "filename", None):
        return None

    filename = secure_filename(file_storage.filename)
    if not filename:
        return None

    ext = filename.rsplit('.', 1)[-1].lower()
    unique_name = f"{md5((identifier + filename).encode('utf-8')).hexdigest()}.{ext}"
    upload_folder = current_app.config.get("UPLOAD_FOLDER") or os.path.join(current_app.root_path, "static", "uploads", "avatars")
    os.makedirs(upload_folder, exist_ok=True)
    avatar_path = os.path.join(upload_folder, unique_name)
    file_storage.save(avatar_path)
    return url_for("static", filename=f"uploads/avatars/{unique_name}")


@auth_bp.route("/profil", methods=["GET", "POST"])
@login_required
def profil():
    form = ProfilForm(obj=current_user)
    if form.validate_on_submit():
        current_user.nom = form.nom.data.strip()
        current_user.age = form.age.data
        current_user.taille_cm = form.taille_cm.data
        current_user.sexe = form.sexe.data

        avatar_file = form.avatar.data
        if avatar_file and getattr(avatar_file, 'filename', None):
            if current_user.avatar_url and current_user.avatar_url.startswith('/static/uploads/avatars/'):
                old_avatar_path = os.path.join(current_app.root_path, current_user.avatar_url.lstrip('/'))
                if os.path.exists(old_avatar_path):
                    try:
                        os.remove(old_avatar_path)
                    except OSError:
                        pass
            current_user.avatar_url = save_avatar_file(avatar_file, current_user.email.lower().strip())

        db.session.commit()
        flash("✅ Profil mis à jour.", "success")
        return redirect(url_for("auth.profil"))
    return render_template("auth/profil.html", form=form)