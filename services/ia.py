# services/ia.py
"""
Service IA — Communique avec Llama 3.3 (via Groq) pour analyser les mesures santé.
"""
import os
import json
from groq import Groq

# Initialisation du client (lit GROQ_API_KEY depuis l'env)
_client = None


def _get_client():
    """Lazy init du client pour pouvoir mocker en test."""
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY manquant dans .env")
        _client = Groq(api_key=api_key)
    return _client


# --- Construction du prompt ---
SYSTEM_PROMPT = """Tu es VitalHelp AI, un assistant médical bienveillant et prudent.
Tu analyses les données de santé d'un patient et tu lui donnes une interprétation claire en français.

RÈGLES STRICTES :
1. Tu réponds UNIQUEMENT en JSON valide, sans aucun texte avant ou après.
2. Tu ne poses jamais de diagnostic médical définitif. Tu suggères, tu alertes, tu recommandes.
3. Tu rappelles systématiquement de consulter un médecin pour un avis professionnel.
4. Tu utilises un ton chaleureux, accessible, mais professionnel.
5. Tes réponses sont en français.

SCHEMA JSON OBLIGATOIRE :
{
  "score_global": <entier 0-100>,
  "resume": "<phrase courte de 1-2 lignes>",
  "interpretation": "<paragraphe de 3-5 phrases analysant les tendances et l'état général>",
  "risques": ["<risque 1>", "<risque 2>", ...],
  "recommandations": ["<reco 1>", "<reco 2>", "<reco 3>", ...]
}

Le score_global évalue la santé globale : 100 = excellent, 80+ = bon, 60-79 = correct, 40-59 = à surveiller, <40 = préoccupant.
"""


def construire_donnees(user, mesures):
    """Formate les mesures de manière concise pour l'IA."""
    profil = f"Patient : {user.nom}, {user.age} ans, {user.sexe}, taille {user.taille_cm} cm.\n"
    profil += f"Nombre total de mesures : {len(mesures)}\n\n"

    # On limite aux 20 dernières pour ne pas saturer le contexte
    profil += "Dernières mesures (les plus récentes en haut) :\n"
    for m in mesures[:20]:
        d = m.date_mesure.strftime("%d/%m/%Y")
        ligne = f"- {d} : "
        details = []
        if m.poids_kg: details.append(f"poids={m.poids_kg}kg")
        if m.imc: details.append(f"IMC={m.imc}")
        if m.tension_sys: details.append(f"TA={m.tension_sys}/{m.tension_dia}")
        if m.glycemie_gl: details.append(f"glycémie={m.glycemie_gl}g/L")
        if m.freq_cardiaque: details.append(f"FC={m.freq_cardiaque}bpm")
        ligne += ", ".join(details) if details else "(vide)"
        profil += ligne + "\n"
    return profil


def analyser(user, mesures):
    """
    Lance une analyse IA des mesures de l'utilisateur.
    Retourne un dict : {score_global, resume, interpretation, risques, recommandations}
    Lève une exception en cas d'erreur réseau ou API.
    """
    if not mesures:
        raise ValueError("Aucune mesure à analyser.")

    donnees = construire_donnees(user, mesures)
    prompt_user = f"{donnees}\n\nAnalyse ces données et renvoie le JSON demandé."

    client = _get_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt_user},
        ],
        temperature=0.4,
        response_format={"type": "json_object"},  # Force du JSON valide
        max_tokens=1024,
    )

    raw = response.choices[0].message.content
    data = json.loads(raw)

    # Validation basique du schéma
    score = int(data.get("score_global", 60))
    score = max(0, min(100, score))  # clamp 0-100

    return {
        "score_global": score,
        "resume": str(data.get("resume", "")).strip()[:500],
        "interpretation": str(data.get("interpretation", "")).strip()[:2000],
        "risques": [str(r).strip() for r in data.get("risques", [])][:10],
        "recommandations": [str(r).strip() for r in data.get("recommandations", [])][:10],
    }