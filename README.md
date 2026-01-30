#  Système de Surveillance de la Pression Artérielle  
## Architecture temps réel avec Apache Kafka

---

##  Présentation du projet

Ce projet met en place un **système de surveillance de la pression artérielle en temps réel** basé sur **Apache Kafka**.  
Il simule des données médicales, les analyse en continu, détecte les situations anormales et stocke les résultats pour visualisation.

 Objectif pédagogique : **illustrer une architecture de streaming de données** appliquée à un cas d’usage santé.

---

## Architecture globale du système

Générateur FHIR → Kafka Producer → Topic Kafka → Kafka Consumer
↓
Analyse & Décision
↓ ↓
Stockage local (normal) Elasticsearch (anomalies)
↓
Kibana


---

##  Technologies utilisées

- **Python 3**
- **Apache Kafka** (via Docker)
- **FHIR (HL7)** – standard médical
- **Elasticsearch**
- **Kibana**
- **Docker & Docker Compose**
- **kafka-python**
- **fhir.resources**

---

## Structure du projet
blood-pressure-project/
│
├── producer/
│ ├── kafka_producer.py # Kafka Producer
│ └── fhir_generator.py # Génération d'observations FHIR
│
├── src/
│ ├── kafka_consumer.py # Kafka Consumer
│ ├── analyze_observation.py # Analyse médicale
│ └── storage_handler.py # Stockage & Elasticsearch
│
├── data/
│ └── normal/ # Données normales (JSON)
│
├── docker-compose.yml
├── requirements.txt
├── .gitignore
└── README.md




---

##  Répartition du travail

- **Personne 1 — Ingestion des données** (Reina Baltagi) 
  - Génération des observations médicales (FHIR)
  - Kafka Producer

- **Personne 2 — Analyse & Kafka Consumer** (Nouran Ghaliounji) 
  - Extraction des données FHIR
  - Analyse de la pression artérielle
  - Classification des patients
  - Décision de stockage

- **Personne 3 — Stockage & Visualisation** (Houda El Baidak) 
  - Indexation Elasticsearch
  - Dashboards Kibana

---

## Format des données médicales (FHIR)

Chaque message Kafka contient une **Observation FHIR** avec :
- Identifiant patient
- Horodatage
- Pression systolique
- Pression diastolique

Le format FHIR garantit :
- un standard médical reconnu
- des données structurées
- une interopérabilité élevée

---

##  Analyse de la pression artérielle

Les règles médicales implémentées sont basées sur les recommandations cliniques :

| Catégorie | Condition |
|----------|----------|
| Normal | Systolique < 120 **ET** Diastolique < 80 |
| Elevated | 120 ≤ Systolique ≤ 129 **ET** Diastolique < 80 |
| Hypertension – Stade 1 | 130–139 **OU** 80–89 |
| Hypertension – Stade 2 | ≥ 140 **OU** ≥ 90 |
| Crise hypertensive | >= 180 **OU** >= 120 |
| Hypotension | < 90 **OU** < 60 |

--> Chaque mesure est **classifiée automatiquement**.



## Kafka Producer

Le Kafka Producer :
- simule un groupe de patients fixes
- génère des mesures réalistes
- applique des variations progressives
- envoie les observations vers le topic Kafka

### Lancer le producer

```bash
python -m producer.kafka_producer
```
## Kafka Consumer

Le Kafka Consumer constitue le cœur décisionnel du système.

Il :

- écoute le topic Kafka en continu

- reçoit chaque observation dès son arrivée

- extrait les valeurs médicales

- applique les règles d’analyse

- décide du stockage

Lancer le consumer:
```bash
python -m src.kafka_consumer
```


## Stratégie de stockage

Mesures normales: 

- Stockage local au format JSON

Mesures anormales: 

- Indexation dans Elasticsearch
- Exploitables via Kibana


## Visualisation avec Kibana
Kibana permet :
- le suivi des patients à risque
- l’analyse de la répartition des anomalies
- la visualisation temporelle
- l’identificationn des situations critiques

![KIBANA DASHBOARD](https://github.com/user-attachments/assets/994504e0-9d54-42c0-864c-69bbeb26ddfb)




## Infrastructure Docker
Tous les services sont déployés via Docker :
- Kafka
- Zookeeper
- Elasticsearch
- Kibana

Pour démmarer: 
```bash
docker compose up -d
```
Pour arrêter: 
```bash
docker compose down
```


