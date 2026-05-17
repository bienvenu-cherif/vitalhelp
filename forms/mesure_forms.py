# forms/mesure_forms.py
from flask_wtf import FlaskForm
from wtforms import DecimalField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import Optional, NumberRange


class MesureForm(FlaskForm):
    """
    Formulaire de saisie d'une mesure.
    Tous les champs sont optionnels — on peut ne saisir qu'une seule valeur.
    Mais on s'assure côté serveur qu'il y a au moins 1 valeur.
    """
    poids_kg = DecimalField("Poids (kg)", places=2, validators=[
        Optional(), NumberRange(min=1, max=500, message="Entre 1 et 500 kg")
    ])
    tension_sys = IntegerField("Tension systolique (mmHg)", validators=[
        Optional(), NumberRange(min=50, max=300)
    ])
    tension_dia = IntegerField("Tension diastolique (mmHg)", validators=[
        Optional(), NumberRange(min=30, max=200)
    ])
    glycemie_gl = DecimalField("Glycémie (g/L)", places=2, validators=[
        Optional(), NumberRange(min=0, max=10)
    ])
    freq_cardiaque = IntegerField("Fréquence cardiaque (bpm)", validators=[
        Optional(), NumberRange(min=20, max=300)
    ])
    note = TextAreaField("Note (optionnel)", validators=[Optional()])
    submit = SubmitField("Enregistrer")

    def at_least_one_value(self):
        """Vérifie qu'au moins UN champ médical est rempli"""
        return any([
            self.poids_kg.data, self.tension_sys.data, self.tension_dia.data,
            self.glycemie_gl.data, self.freq_cardiaque.data
        ])