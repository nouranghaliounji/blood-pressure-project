# fichier : fhir_generator.py
# role  : Génération de données de pression artérielle
# format  : FHIR (Observation)
# Le but de notre script est de simuler des mesures médicales réelles
# et constitue l'entrée du pipeline Kafka

# Les imports Pythons

# json : pour afficher les données proprement en JSON
import json

# datetime : pour gérer les dates/heures au format standard
from datetime import datetime, timezone

# Observation : objet FHIR officiel pour représenter une observation médicale
from fhir.resources.observation import Observation


# Fonction principale

def generate_blood_pressure_observation(patient_id: str, systolic: float, diastolic: float):
    """
    Cette fonction génère UNE observation médicale
    de pression artérielle au format FHIR.

    Elle ne fait aucune analyse, dans le sens où :
    - il n'y aura pas de détection d’anomalie
    - pas de logique métier
    - mais uniquement de la génération de données

    Ici, on ne génère PAS des valeurs au hasard :
    - le patient_id et les valeurs systolic/diastolic sont fournis par le producer
    - cela permet au producer de simuler une évolution réaliste dans le temps
    """

    # Génération du timestamp

    # Format ISO 8601 (standard médical et informatique)
    timestamp = datetime.now(timezone.utc).isoformat()

    # Construction de l'objet FHIR Observation

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

        # Les composants de la mesure
        # La pression artérielle contient DEUX valeurs :
        # - systolique
        # - diastolique
        component=[

            # Pression systolique
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
                    "value": float(systolic),
                    "unit": "mmHg",
                    "system": "http://unitsofmeasure.org",
                    "code": "mm[Hg]"
                }
            },

            # Pression diastolique
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
                    "value": float(diastolic),
                    "unit": "mmHg",
                    "system": "http://unitsofmeasure.org",
                    "code": "mm[Hg]"
                }
            }
        ]
    )

    # Conversion de l'objet FHIR vers un dictionnaire Python
    # (donc prêt à être sérialisé en JSON pour Kafka)
    return observation.model_dump(mode="json")


# Points d'entrée du script :

# Ce bloc s'exécute uniquement si le fichier est lancé directement
# Il permet de tester le générateur localement
if __name__ == "__main__":

    # Exemple de test manuel (patient fixe + valeurs fixes)
    obs = generate_blood_pressure_observation("PAT-001", 120, 80)

    # Affichage du résultat en JSON lisible
    print(json.dumps(obs, indent=2))

    # Pour plus de lisibilité :
    print("Patient :", obs['subject']['reference'])
    print("Date :", obs['effectiveDateTime'])
    for comp in obs['component']:
        code = comp['code']['coding'][0]['display']
        value = comp['valueQuantity']['value']
        unit = comp['valueQuantity']['unit']
        print(f"{code}: {value} {unit}")
