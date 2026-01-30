"""
Ce fichier gère le stockage des observations de pression artérielle après analyse.

La logique appliquée :
- Si la mesure est normale, on la garde en local pour l'historique.
- Si la mesure est anormale, on l’envoie vers Elasticsearch
  pour pouvoir la surveiller en temps réel dans Kibana.

"""

# =========================
# Bibliothèques utilisées
# =========================

import json
import os
from datetime import datetime
from elasticsearch import Elasticsearch


########### PARTIE 1 : Stockage local des cas NORMAUX ###########


# Dossier principal des données
BASE_DIR = "data"

# Sous-dossier réservé aux observations non critiques
NORMAL_DIR = os.path.join(BASE_DIR, "normal")


def save_normal_observation(observation: dict):
    """
    Sauvegarde une observation normale en fichier JSON.
    Organisation par date.
    """

    #Créer le dossier si besoin
    os.makedirs(NORMAL_DIR, exist_ok=True)

    # Nom unique basé sur la date et l'heure pour éviter les doublons 
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"obs_{timestamp}.json"
    filepath = os.path.join(NORMAL_DIR, filename)

    # Sauvegarde en JSON lisible 
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(observation, f, indent=2)

    print(f"💾 Sauvegardé en local : {filepath}")



########### PARTIE 2 : Indexation des ANOMALIES dans Elasticsearch ###########


# Connexion à Elasticsearch  
es = Elasticsearch("http://localhost:9200")

# Index qui regroupe les alertes médicales
INDEX_NAME = "blood_pressure_anomalies"


def index_anomaly(patient, systolic, diastolic, anomalies, timestamp):
    """
    Envoie une observation anormale vers Elasticsearch.
    """

    # Données envoyées dans l'index
    doc = {
        "patient_id": patient,
        "systolic_pressure": systolic,
        "diastolic_pressure": diastolic,
        "anomaly_type": anomalies,
        "timestamp": timestamp
    }
    
    # Indexation
    es.index(index=INDEX_NAME, document=doc)

    print("📦 Donnée indexée dans Elasticsearch")
