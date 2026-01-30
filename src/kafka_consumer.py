import json
from src.storage_handler import save_normal_observation, index_anomaly
# On utilise ces fonctions pour gérer le stockage :
# local pour les mesures normales, Elasticsearch pour les anomalies
from kafka import KafkaConsumer

from src.analyze_observation import (
    extract_bp_from_fhir_observation,
    analyze_blood_pressure,
)

BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "blood_pressure_fhir"   # si ça ne marche pas, on ajustera au topic réel du producer
GROUP_ID = "bp-consumer-group"


def main():
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        group_id=GROUP_ID,
        auto_offset_reset="latest",   # lit les nouveaux messages
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )

    print(f"✅ Consumer connecté. Topic='{TOPIC}', bootstrap='{BOOTSTRAP_SERVERS}'")
    print("📡 En attente de messages...\n")

    for msg in consumer:
        observation = msg.value  # déjà un dict grâce au value_deserializer

        systolic, diastolic = extract_bp_from_fhir_observation(observation)
        anomalies = analyze_blood_pressure(systolic, diastolic)

        patient = observation.get("subject", {}).get("reference", "Unknown")
        timestamp = observation.get("effectiveDateTime", "Unknown")

        if anomalies:
            print(f"🚨 ANOMALIE {anomalies} | patient={patient} | sys={systolic} dia={diastolic} | t={timestamp}")
            index_anomaly(patient, systolic, diastolic, anomalies, timestamp)
        else:
            print(f"✅ NORMAL | patient={patient} | sys={systolic} dia={diastolic} | t={timestamp}")
            save_normal_observation(observation)
            

if __name__ == "__main__":
    main()
