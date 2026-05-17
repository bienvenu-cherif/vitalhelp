\# 🩺 VitalHelp — Journal de santé personnel



> \*« Votre santé, racontée au jour le jour. »\*



VitalHelp est une application web qui transforme vos mesures quotidiennes

(poids, tension, glycémie, fréquence cardiaque) en un récit clair, interprété

par une IA, et partageable avec votre médecin en un clic.



🌐 \*\*Démo en ligne\*\* : https://vitalhelp.onrender.com \*(à mettre à jour)\*



\---



\## ✨ Fonctionnalités



\- 🔐 \*\*Authentification\*\* sécurisée (bcrypt + sessions Flask)

\- 📊 \*\*Saisie de mesures\*\* : poids, tension, glycémie, fréquence cardiaque

\- 🧮 \*\*Calcul automatique de l'IMC\*\* + catégorisation par âge

\- 🚨 \*\*Détection des valeurs hors normes\*\* OMS (hypertension, diabète, etc.)

\- 📈 \*\*Courbes Chart.js\*\* avec moyennes mobiles + ligne d'objectif + seuils d'alerte

\- 🎯 \*\*Objectifs personnels\*\* avec barres de progression

\- 🧠 \*\*Coach IA Llama 3.3\*\* (via Groq) : interprétation + risques + recommandations

\- 🔗 \*\*Partage médecin\*\* : lien public expirable et révocable

\- 🖨 \*\*Impression\*\* du dossier patient pour le médecin

\- 🎨 \*\*Design Organic \& Earthy\*\* avec hero cinématique



\---



\## 🛠 Stack technique



| Couche | Technologie |

|---|---|

| Backend | Flask · Flask-SQLAlchemy · Flask-Login · Flask-WTF |

| Base de données | PostgreSQL |

| Frontend | Jinja2 · HTML/CSS · Chart.js |

| IA | Llama 3.3 70B (via Groq API) |

| Hébergement | Render (web) · Neon (PostgreSQL) |



\---



\## 🚀 Installation locale



\### Prérequis

\- Python 3.11+

\- PostgreSQL 16+ avec pgAdmin

\- Une clé API Groq gratuite : https://console.groq.com



\### Étapes



\\`\\`\\`bash

\# 1. Cloner le repo

git clone https://github.com/<ton-username>/vitalhelp.git

cd vitalhelp



\# 2. Environnement virtuel

python -m venv venv

venv\\Scripts\\activate            # Windows

\# source venv/bin/activate       # Mac/Linux



\# 3. Dépendances

pip install -r requirements.txt



\# 4. Configuration

copy .env.example .env           # Windows

\# cp .env.example .env           # Mac/Linux

\# Édite .env avec tes vraies valeurs



\# 5. Créer la base dans pgAdmin

\# (clic droit Databases → Create → "vitalhelp")



\# 6. Lancer l'application

python app.py

\\`\\`\\`



Ouvre http://localhost:5000 🎉



\---



\## 📂 Structure



\\`\\`\\`

vitalhelp/

├── app.py                  # Point d'entrée

├── config.py               # Configuration centrale

├── extensions.py           # Init SQLAlchemy, Login, Bcrypt

├── requirements.txt

├── Procfile                # Pour Render (gunicorn)

├── runtime.txt             # Version Python

├── schema.sql              # Schéma SQL pur (référence)

│

├── models/                 # SQLAlchemy : users, mesures, objectifs, ...

├── routes/                 # Blueprints Flask

├── forms/                  # Flask-WTF

├── services/               # Logique métier (IMC, alertes, IA)

├── templates/              # Jinja2

└── static/                 # CSS, JS, images

\\`\\`\\`



\---



\## 🗄 Schéma de base de données



5 tables PostgreSQL avec contraintes CHECK :



\- \*\*users\*\* — comptes utilisateurs (email, password\_hash, profil)

\- \*\*mesures\*\* — relevés santé avec calcul IMC auto

\- \*\*objectifs\*\* — cibles personnelles avec progression

\- \*\*analyses\_ia\*\* — historique des analyses Llama

\- \*\*liens\_partage\*\* — tokens publics expirables



Voir \[`schema.sql`](./schema.sql) pour le SQL complet.



\---



\## 🧠 IA — Llama 3.3 via Groq



\- Modèle : `llama-3.3-70b-versatile`

\- Réponse en \*\*JSON structuré\*\* (score, interprétation, risques, recommandations)

\- 100% gratuit (30 req/min)



\---



\## ⚠️ Disclaimer médical



VitalHelp est un \*\*outil de prévention\*\*, pas de diagnostic. Consultez toujours

votre médecin pour un avis professionnel.



\---



\## 📜 Licence



MIT — Libre d'utilisation et de modification.



\---



\## 👨‍💻 Auteur



Projet académique réalisé dans le cadre du cours de Bases de données.



