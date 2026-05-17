# forms/auth_forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, ValidationError
from models import User


class InscriptionForm(FlaskForm):
    """Formulaire d'inscription avec validation côté serveur"""

    nom = StringField("Nom complet", validators=[
        DataRequired(message="Le nom est obligatoire"),
        Length(min=2, max=100, message="Entre 2 et 100 caractères")
    ])
    email = StringField("Email", validators=[
        DataRequired(message="L'email est obligatoire"),
        Email(message="Email invalide")
    ])
    password = PasswordField("Mot de passe", validators=[
        DataRequired(),
        Length(min=6, message="Minimum 6 caractères")
    ])
    password_confirm = PasswordField("Confirmer le mot de passe", validators=[
        DataRequired(),
        EqualTo("password", message="Les mots de passe ne correspondent pas")
    ])
    age = IntegerField("Âge", validators=[
        DataRequired(),
        NumberRange(min=0, max=150, message="Âge entre 0 et 150")
    ])
    taille_cm = IntegerField("Taille (cm)", validators=[
        DataRequired(),
        NumberRange(min=40, max=300, message="Taille entre 40 et 300 cm")
    ])
    sexe = SelectField("Sexe", choices=[("homme", "Homme"), ("femme", "Femme")],
                       validators=[DataRequired()])
    submit = SubmitField("Créer mon journal")

    def validate_email(self, field):
        """Validation custom : email déjà utilisé ?"""
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError("Cet email est déjà utilisé.")


class ConnexionForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    submit = SubmitField("Se connecter")


class ProfilForm(FlaskForm):
    """Édition du profil utilisateur"""
    nom = StringField("Nom complet", validators=[DataRequired(), Length(min=2, max=100)])
    age = IntegerField("Âge", validators=[DataRequired(), NumberRange(min=0, max=150)])
    taille_cm = IntegerField("Taille (cm)", validators=[DataRequired(), NumberRange(min=40, max=300)])
    sexe = SelectField("Sexe", choices=[("homme", "Homme"), ("femme", "Femme")],
                       validators=[DataRequired()])
    submit = SubmitField("Enregistrer")