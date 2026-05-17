# forms/partage_forms.py
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class LienPartageForm(FlaskForm):
    duree_jours = IntegerField(
        "Durée de validité (jours)",
        validators=[DataRequired(), NumberRange(min=1, max=365)],
        default=30,
    )
    submit = SubmitField("Générer le lien")