# ============================================================
# FICHIER : fhir_generator.py
# RÔLE    : Génération de données de pression artérielle
# FORMAT  : FHIR (Observation)
#
# Ce script simule des mesures médicales réelles
# et constitue l'entrée du pipeline Kafka
# ============================================================


# =========================
# IMPORTS PYTHON
# =========================

# json : pour afficher les données proprement en JSON
import json

# random : pour générer des valeurs numériques aléatoires
import random

# datetime : pour gérer les dates/heures au format standard
from datetime import datetime

# Faker : librairie permettant de simuler des données réalistes
from faker import Faker

# Observation : objet FHIR officiel pour représenter une observation médicale
from fhir.resources.observation import Observation


# =========================
# INITIALISATION DES OUTILS
# =========================

# Initialisation de Faker
# Il permet de générer des identifiants patients réalistes
fake = Faker()

# =========================
# PARAMÈTRES MÉDICAUX
# =========================

# Seuils réalistes de pression artérielle systolique
# (valeurs larges volontairement pour inclure cas normaux + anormaux)
SYSTOLIC_MIN = 80
SYSTOLIC_MAX = 180

# Seuils réalistes de pression artérielle diastolique
DIASTOLIC_MIN = 50
DIASTOLIC_MAX = 120


# =========================
# FONCTION PRINCIPALE
# =========================

def generate_blood_pressure_observation():
    """
    Cette fonction génère UNE observation médicale
    de pression artérielle au format FHIR.

    Elle ne fait AUCUNE analyse :
    - pas de détection d’anomalie
    - pas de logique métier
    - uniquement de la génération de données
    """

    # -------------------------
    # Génération d'un identifiant patient unique
    # -------------------------
    # Exemple : PAT-4832
    patient_id = f"PAT-{fake.random_int(min=1000, max=9999)}"

    # -------------------------
    # Génération des valeurs de pression artérielle
    # -------------------------
    # systolic = pression systolique (max)
    systolic = random.randint(SYSTOLIC_MIN, SYSTOLIC_MAX)

    # diastolic = pression diastolique (min)
    diastolic = random.randint(DIASTOLIC_MIN, DIASTOLIC_MAX)

    # -------------------------
    # Génération du timestamp
    # -------------------------
    # Format ISO 8601 (standard médical et informatique)
    from datetime import timezone
    timestamp = datetime.now(timezone.utc).isoformat()


    # -------------------------
    # Construction de l'objet FHIR Observation
    # -------------------------
    # On respecte strictement le standard FHIR
    observation = Observation(

        # Statut de l'observation (final = mesure validée)
        status="final",

        # Catégorie médicale (signes vitaux)
        category=[
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "vital-signs",
                        "display": "Vital Signs"
                    }
                ]
            }
        ],

        # Code médical LOINC correspondant au panneau tension artérielle
        code={
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "85354-9",
                    "display": "Blood pressure panel"
                }
            ]
        },

        # Référence vers le patient concerné
        subject={
            "reference": f"Patient/{patient_id}"
        },

        # Date et heure de la mesure
        effectiveDateTime=timestamp,

        # -------------------------
        # Composants de la mesure
        # -------------------------
        # La pression artérielle contient DEUX valeurs :
        # - systolique
        # - diastolique
        component=[

            # --- Pression systolique ---
            {
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "8480-6",
                            "display": "Systolic blood pressure"
                        }
                    ]
                },
                "valueQuantity": {
                    "value": systolic,
                    "unit": "mmHg",
                    "system": "http://unitsofmeasure.org",
                    "code": "mm[Hg]"
                }
            },

            # --- Pression diastolique ---
            {
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "8462-4",
                            "display": "Diastolic blood pressure"
                        }
                    ]
                },
                "valueQuantity": {
                    "value": diastolic,
                    "unit": "mmHg",
                    "system": "http://unitsofmeasure.org",
                    "code": "mm[Hg]"
                }
            }
        ]
    )

    # Conversion de l'objet FHIR vers un dictionnaire Python
    # (prêt à être sérialisé en JSON pour Kafka)
    return observation.model_dump(mode="json")



# =========================
# POINT D'ENTRÉE DU SCRIPT
# =========================

# Ce bloc s'exécute uniquement si le fichier est lancé directement
# Il permet de tester le générateur localement
if __name__ == "__main__":

    # Génération d'une observation
    observation = generate_blood_pressure_observation()

    # Affichage du résultat en JSON lisible
    print(json.dumps(observation, indent=2))

# =========================
# POINT D'ENTRÉE DU SCRIPT
# =========================

if __name__ == "__main__":

    # Génération d'une observation
    obs = generate_blood_pressure_observation()

    # Affichage lisible dans le terminal
    print("Patient :", obs['subject']['reference'])
    print("Date :", obs['effectiveDateTime'])
    for comp in obs['component']:
        code = comp['code']['coding'][0]['display']
        value = comp['valueQuantity']['value']
        unit = comp['valueQuantity']['unit']
        print(f"{code}: {value} {unit}")

