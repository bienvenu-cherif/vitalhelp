# services/sante.py
"""
Service "Santé" — Logique médicale pure (calculs + détection d'alertes).
Ne dépend ni de Flask ni de la DB → facile à tester unitairement.
"""

from decimal import Decimal


def calculer_imc(poids_kg, taille_cm):
    """
    Calcule l'IMC (Indice de Masse Corporelle).
    Formule : poids (kg) / taille (m)²
    Retourne None si les données ne sont pas exploitables.
    """
    if not poids_kg or not taille_cm or taille_cm <= 0:
        return None
    taille_m = Decimal(taille_cm) / Decimal(100)
    imc = Decimal(poids_kg) / (taille_m * taille_m)
    return round(imc, 1)


def categoriser_imc(imc, age):
    """
    Catégorise l'IMC en fonction de l'âge.
    Pour les adultes (>=18 ans), les seuils OMS standards s'appliquent.
    Pour les enfants/ados, ce serait plus complexe (courbes de croissance),
    on simplifie ici avec une note.
    """
    if imc is None:
        return None
    if age < 18:
        return "Référez-vous aux courbes pédiatriques (avis médical recommandé)"
    if imc < 18.5:
        return "Maigreur"
    if imc < 25:
        return "Corpulence normale"
    if imc < 30:
        return "Surpoids"
    if imc < 35:
        return "Obésité modérée"
    if imc < 40:
        return "Obésité sévère"
    return "Obésité morbide"


def detecter_alertes(mesure, age):
    """
    Analyse une mesure et retourne une liste d'alertes médicales.
    Renvoie une liste de dictionnaires : [{niveau, message}, ...]
    Niveaux possibles : 'danger', 'warning', 'info'
    """
    alertes = []

    # --- Tension artérielle ---
    sys, dia = mesure.tension_sys, mesure.tension_dia
    if sys and dia:
        if sys >= 180 or dia >= 110:
            alertes.append({"niveau": "danger", "message": f"Crise hypertensive ({sys}/{dia} mmHg) — consultez d'urgence."})
        elif sys >= 140 or dia >= 90:
            alertes.append({"niveau": "warning", "message": f"Hypertension ({sys}/{dia} mmHg). Norme : <140/90."})
        elif sys < 90 or dia < 60:
            alertes.append({"niveau": "warning", "message": f"Hypotension ({sys}/{dia} mmHg)."})

    # --- Glycémie ---
    g = mesure.glycemie_gl
    if g:
        g = float(g)
        if g >= 1.26:
            alertes.append({"niveau": "warning", "message": f"Glycémie élevée à jeun ({g} g/L). Risque de diabète."})
        elif g >= 1.10:
            alertes.append({"niveau": "info", "message": f"Glycémie limite ({g} g/L). Surveillez."})
        elif g < 0.7:
            alertes.append({"niveau": "warning", "message": f"Hypoglycémie ({g} g/L)."})

    # --- Fréquence cardiaque ---
    fc = mesure.freq_cardiaque
    if fc:
        if fc > 120:
            alertes.append({"niveau": "danger", "message": f"Tachycardie sévère ({fc} bpm)."})
        elif fc > 100:
            alertes.append({"niveau": "warning", "message": f"Tachycardie ({fc} bpm)."})
        elif fc < 50:
            alertes.append({"niveau": "warning", "message": f"Bradycardie ({fc} bpm)."})

    # --- IMC ---
    imc = mesure.imc
    if imc:
        imc = float(imc)
        if imc >= 40:
            alertes.append({"niveau": "danger", "message": f"IMC {imc} — obésité morbide."})
        elif imc >= 30:
            alertes.append({"niveau": "warning", "message": f"IMC {imc} — obésité."})
        elif imc >= 25:
            alertes.append({"niveau": "info", "message": f"IMC {imc} — surpoids."})
        elif imc < 18.5:
            alertes.append({"niveau": "info", "message": f"IMC {imc} — maigreur."})

    return alertes

# services/sante.py — à AJOUTER à la fin

def moyenne_mobile(valeurs, fenetre=3):
    """
    Calcule la moyenne mobile sur une série de valeurs.
    'valeurs' peut contenir des None (mesures manquantes) — on les ignore.
    Retourne une liste de la même longueur (None où impossible de calculer).
    """
    resultats = []
    for i in range(len(valeurs)):
        # Fenêtre : du début jusqu'à i, max 'fenetre' valeurs non-nulles
        debut = max(0, i - fenetre + 1)
        tranche = [v for v in valeurs[debut:i + 1] if v is not None]
        if tranche:
            resultats.append(round(sum(float(v) for v in tranche) / len(tranche), 2))
        else:
            resultats.append(None)
    return resultats


def calculer_progression(objectif, valeur_actuelle):
    """
    Calcule le pourcentage de progression d'un objectif.
    - Si on va dans le bon sens (vers la cible) : entre 0 et 100%
    - Si on est plus loin qu'au départ : 0%
    - Si on a atteint ou dépassé : 100%
    """
    if valeur_actuelle is None:
        return 0

    depart = float(objectif.valeur_depart)
    cible = float(objectif.valeur_cible)
    actuelle = float(valeur_actuelle)

    total = abs(cible - depart)
    if total == 0:
        return 100  # Cible = départ → déjà atteint

    parcouru = abs(actuelle - depart)

    # Vérifier le sens : actuelle doit être entre depart et cible (dans la bonne direction)
    sens_objectif = 1 if cible > depart else -1
    sens_actuel = 1 if actuelle >= depart else -1

    if sens_objectif != sens_actuel:
        return 0  # Mauvais sens

    pourcentage = (parcouru / total) * 100
    return min(100, max(0, round(pourcentage)))