# Kafka Producer

# Le script suivant :
# 1) Génère des observations de pression artérielle au format FHIR
# 2) Associe chaque observation à un patient fixe
# 3) Sérialise les données en JSON
# 4) Les envoie vers un topic Kafka toutes les 15 secondes

# Les importations

# KafkaProducer permet d'envoyer des messages à Kafka
from kafka import KafkaProducer

# json permet de transformer un dictionnaire Python en texte JSON
import json

# time permet de contrôler le rythme d'envoi des messages
import time

# random permet de faire varier doucement les mesures
import random

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

# Paramètres médicaux réalistes (bornes de sécurité)
SYSTOLIC_MIN = 80
SYSTOLIC_MAX = 181
DIASTOLIC_MIN = 50
DIASTOLIC_MAX = 121

# Variation maximale par mesure (simulation d'une évolution progressive)
# Dans la vraie vie, la tension varie généralement "doucement" (sauf cas extrême)
MAX_DELTA_SYS = 6
MAX_DELTA_DIA = 4


# Création du producer Kafka

# KafkaProducer se charge de la connexion au broker Kafka
# value_serializer transforme automatiquement nos données en JSON bytes
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)


# --- Initialisation d'un "état" par patient ---
# Ici, on rend la génération plus logique :
# - chaque patient commence avec une pression de base
# - puis la pression évolue progressivement à chaque cycle
patient_state = {}

for pid in PATIENT_IDS:
    # On donne à chaque patient une "base" différente (un patient peut être plus hypertendu qu'un autre)
    base_sys = random.randint(110, 150)
    base_dia = random.randint(70, 95)

    patient_state[pid] = {
        "systolic": base_sys,
        "diastolic": base_dia
    }


# Boucle principale

print("Kafka Producer démarré...")
print(f"Envoi des messages vers le topic : {TOPIC_NAME}")
print("Génération des mesures pour 5 patients fixes, toutes les 15 secondes.")

while True:
    # Pour chaque patient, on génère une mesure à chaque cycle
    for patient_id in PATIENT_IDS:

        # 1) Récupérer la dernière valeur du patient (mémoire)
        prev_sys = patient_state[patient_id]["systolic"]
        prev_dia = patient_state[patient_id]["diastolic"]

        # 2) Faire varier doucement la mesure (random walk)
        # On ajoute une petite variation aléatoire autour de la valeur précédente
        new_sys = prev_sys + random.randint(-MAX_DELTA_SYS, MAX_DELTA_SYS)
        new_dia = prev_dia + random.randint(-MAX_DELTA_DIA, MAX_DELTA_DIA)

        # 3) Garder des valeurs réalistes (clamp dans les bornes)
        new_sys = max(SYSTOLIC_MIN, min(SYSTOLIC_MAX, new_sys))
        new_dia = max(DIASTOLIC_MIN, min(DIASTOLIC_MAX, new_dia))

        # 4) Mettre à jour l'état du patient (mémoire)
        patient_state[patient_id]["systolic"] = new_sys
        patient_state[patient_id]["diastolic"] = new_dia

        # 5) Générer une observation FHIR (dictionnaire Python)
        # Ici on passe patient_id + valeurs => génération cohérente dans le temps
        observation = generate_blood_pressure_observation(patient_id, new_sys, new_dia)

        # 6) Envoyer l'observation vers Kafka
        producer.send(TOPIC_NAME, observation)

        # 7) Log lisible pour suivre l'exécution (évite de spammer tout le JSON)
        print(f"[{patient_id}] sys={new_sys} dia={new_dia} | t={observation['effectiveDateTime']}")

    # 8) Pause de 5 secondes avant la prochaine série de mesures
    # Chaque patient aura donc une nouvelle mesure toutes les 15 secondes
    time.sleep(15)