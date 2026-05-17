# forms/objectif_forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class ObjectifForm(FlaskForm):
    titre = StringField("Titre", validators=[DataRequired(), Length(min=2, max=150)])
    type_indicateur = SelectField("Indicateur", choices=[
        ("poids", "Poids (kg)"),
        ("tension_sys", "Tension systolique (mmHg)"),
        ("tension_dia", "Tension diastolique (mmHg)"),
        ("glycemie", "Glycémie (g/L)"),
        ("freq_cardiaque", "Fréquence cardiaque (bpm)"),
        ("imc", "IMC"),
    ], validators=[DataRequired()])
    valeur_depart = DecimalField("Valeur de départ", places=2,
                                  validators=[DataRequired(), NumberRange(min=0, max=500)])
    valeur_cible = DecimalField("Valeur cible", places=2,
                                 validators=[DataRequired(), NumberRange(min=0, max=500)])
    deadline = DateField("Échéance (optionnel)", validators=[Optional()], format="%Y-%m-%d")
    submit = SubmitField("Créer l'objectif")