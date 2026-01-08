# ======================================================
# Kafka Producer – Blood Pressure Observations (FHIR)
# ======================================================
# Ce script :
# 1) Génère une observation de pression artérielle au format FHIR
# 2) La sérialise en JSON
# 3) L’envoie vers un topic Kafka
#
# Objectif pédagogique :
# - Comprendre Kafka Producer
# - Respecter un standard médical (FHIR)
# - Avoir un code clair, propre, commenté
# ======================================================


# ---------- IMPORTS ----------

# KafkaProducer permet d'envoyer des messages à Kafka
from kafka import KafkaProducer

# json permet de transformer un dictionnaire Python en texte JSON
import json

# time permet de contrôler le rythme d'envoi des messages
import time

# On importe notre générateur FHIR déjà fonctionnel
from producer.fhir_generator import generate_blood_pressure_observation


# ---------- PARAMÈTRES CONFIGURABLES ----------

# Adresse du broker Kafka
# 'localhost:9092' signifie :
# - Kafka tourne sur la même machine
# - Port par défaut de Kafka
KAFKA_BROKER = "localhost:9092"

# Nom du topic Kafka
# Tous les messages seront envoyés dans ce topic
TOPIC_NAME = "blood_pressure_fhir"


# ---------- CRÉATION DU PRODUCER ----------

# KafkaProducer se charge de la connexion au broker Kafka
# value_serializer transforme automatiquement nos données en JSON bytes
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)


# ---------- BOUCLE PRINCIPALE ----------

print("Kafka Producer démarré...")
print(f"Envoi des messages vers le topic : {TOPIC_NAME}")

while True:
    # 1) Générer une observation FHIR (dictionnaire Python)
    observation = generate_blood_pressure_observation()

    # 2) Envoyer l'observation vers Kafka
    producer.send(TOPIC_NAME, observation)

    # 3) Log lisible pour suivre l'exécution
    print("Observation envoyée à Kafka :")
    print(json.dumps(observation, indent=2))

    # 4) Pause de 5 secondes entre chaque message
    # (évite de spammer Kafka)
    time.sleep(5)
