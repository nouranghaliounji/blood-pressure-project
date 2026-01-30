# Kafka Producer

# Le script suivant :
# 1) Génère des observations de pression artérielle au format FHIR
# 2) Associe chaque observation à un patient fixe
# 3) Sérialise les données en JSON
# 4) Les envoie vers un topic Kafka toutes les 5 secondes



# Les importations


# KafkaProducer permet d'envoyer des messages à Kafka
from kafka import KafkaProducer

# json permet de transformer un dictionnaire Python en texte JSON
import json

# time permet de contrôler le rythme d'envoi des messages
import time

# On importe notre générateur FHIR déjà fonctionnel
from producer.fhir_generator import generate_blood_pressure_observation



# Les paramètres configurables


# Adresse du broker Kafka
# 'localhost:9092' signifie :
# - Kafka tourne sur la même machine
# - Port par défaut de Kafka
KAFKA_BROKER = "localhost:9092"

# Nom du topic Kafka
# Tous les messages seront envoyés dans ce topic
TOPIC_NAME = "blood_pressure_fhir"

# Liste de patients fixes
# Ces patients représentent un petit groupe suivi en temps réel
PATIENT_IDS = [
    "PAT-001",
    "PAT-002",
    "PAT-003",
    "PAT-004",
    "PAT-005"
]



# Création du producer Kafka


# KafkaProducer se charge de la connexion au broker Kafka
# value_serializer transforme automatiquement nos données en JSON bytes
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)



# Boucle principale


print("Kafka Producer démarré...")
print(f"Envoi des messages vers le topic : {TOPIC_NAME}")
print("Génération des mesures pour 5 patients fixes, toutes les 5 secondes.")

while True:
    # Pour chaque patient, on génère une mesure à chaque cycle
    for patient_id in PATIENT_IDS:
        # 1) Générer une observation FHIR (dictionnaire Python)
        observation = generate_blood_pressure_observation()

        # 2) Associer l'observation au patient courant
        # On modifie uniquement la référence du patient
        # La structure FHIR reste strictement identique
        observation["subject"]["reference"] = f"Patient/{patient_id}"

        # 3) Envoyer l'observation vers Kafka
        producer.send(TOPIC_NAME, observation)

        # 4) Log lisible pour suivre l'exécution
        print(f"Observation envoyée pour le patient {patient_id} :")
        print(json.dumps(observation, indent=2))

    # 5) Pause de 5 secondes avant la prochaine série de mesures
    # Chaque patient aura donc une nouvelle mesure toutes les 5 secondes
    time.sleep(5)
