# 🚆 SNCF — Pipeline Ponctualité Transilien & RER

![Google Cloud](https://img.shields.io/badge/Google%20Cloud-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)
![BigQuery](https://img.shields.io/badge/BigQuery-4285F4?style=for-the-badge&logo=googlebigquery&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Looker Studio](https://img.shields.io/badge/Looker%20Studio-4285F4?style=for-the-badge&logo=looker&logoColor=white)

## 📊 Présentation

Pipeline de données complet pour analyser la **ponctualité des lignes Transilien et RER en Île-de-France** sur la période 2024-2026.

Les données sont extraites automatiquement depuis l'API SNCF Open Data, transformées en couches Bronze → Staging → Gold sur BigQuery, et visualisées dans un dashboard Looker Studio interactif.

---

## 🏗️ Architecture

```
SNCF Open Data API
        │
        ▼
Cloud Storage (GCS)       ← raw JSON
        │
        ▼
BigQuery sncf_raw         ← données brutes
        │
        ▼
BigQuery sncf_staging     ← nettoyage & enrichissement
        │
        ▼
BigQuery sncf_gold        ← schéma en étoile
        │
        ▼
Looker Studio             ← dashboard interactif
        │
Cloud Composer / Airflow  ← orchestration (en cours)
```

---

## 🛠️ Stack Technique

| Outil | Rôle |
|---|---|
| **SNCF Open Data API** | Source de données — ponctualité mensuelle |
| **Cloud Storage (GCS)** | Stockage des fichiers JSON bruts |
| **BigQuery** | Data Warehouse — raw / staging / gold |
| **Python** | Script d'ingestion API → GCS → BigQuery |
| **Looker Studio** | Dashboard interactif |
| **Cloud Composer / Airflow** | Orchestration du pipeline *(en cours)* |

---

## 📐 Modèle de données

### Staging — `sncf_staging.ponctualite_transilien`

| Colonne | Type | Description |
|---|---|---|
| `date` | STRING | Année-Mois (YYYY-MM) |
| `annee` | INT64 | Année extraite |
| `mois` | INT64 | Mois extrait |
| `nom_mois` | STRING | Nom du mois en français |
| `service` | STRING | RER ou TRANSILIEN |
| `ligne` | STRING | Lettre de la ligne (A, B, H...) |
| `nom_de_la_ligne` | STRING | Nom complet de la ligne |
| `taux_de_ponctualite` | FLOAT | % voyageurs arrivés à l'heure |
| `taux_retard` | FLOAT | % voyageurs en retard |
| `voyageurs_en_retard` | FLOAT | Ratio voyageurs à l'heure / en retard |
| `categorie_ponctualite` | STRING | Excellent / Bon / Moyen / Mauvais |

### Gold — `sncf_gold.fact_ponctualite`

| Colonne | Type | Description |
|---|---|---|
| `date` | STRING | Clé de date |
| `annee` | INT64 | Année |
| `mois` | INT64 | Mois |
| `trimestre` | STRING | T1 / T2 / T3 / T4 |
| `ligne` | STRING | Lettre de la ligne |
| `service` | STRING | RER ou TRANSILIEN |
| `categorie_ponctualite` | STRING | Etat de ponctualité |
| `taux_de_ponctualite` | FLOAT | % ponctualité |
| `taux_retard` | FLOAT | % retard |
| `ingestion_timestamp` | TIMESTAMP | Date d'ingestion |

---

## 📊 Dashboard Looker Studio

### KPIs suivis

| KPI | Description |
|---|---|
| **Ponctualité** | % voyageurs arrivés avec < 5 min de retard |
| **Retard** | % voyageurs arrivés avec > 5 min de retard |
| **Fiabilité** | Nombre de voyageurs à l'heure pour 1 en retard |
| **État** | Excellent ≥95% · Bon ≥90% · Moyen ≥85% · Mauvais <85% |

### Visuels

- Évolution du taux de ponctualité par mois (courbe)
- Ponctualité par service et par ligne (barres)
- Filtres : Année · Trimestre · Mois · Service · Ligne

---

## 🔄 Orchestration Airflow *(En cours)*

> **Cette section est en cours de développement.**
>
> Un DAG Cloud Composer / Airflow est en cours de construction pour automatiser l'ensemble du pipeline :
>
> ```
> Appel API SNCF → GCS → BigQuery raw → staging → gold
> ```
>
> Planification : mensuelle (nouvelles données SNCF disponibles chaque mois)
>
> Le code du DAG sera disponible dans le dossier `/dags` prochainement.

---

## 🚀 Comment Utiliser

### Prérequis
- Compte Google Cloud Platform (projet actif)
- Clé API SNCF Open Data — [ressources.data.sncf.com](https://ressources.data.sncf.com)
- Python 3.9+

### Installation

```bash
git clone https://github.com/NacerEddine2911/sncf-punctuality-pipeline
cd sncf-punctuality-pipeline
pip install google-cloud-bigquery google-cloud-storage requests
```

### Configuration

Dans `scripts/ingestion.py` remplace :

```python
API_KEY    = "TA_CLE_API_SNCF"
PROJECT_ID = "TON_PROJECT_ID_GCP"
BUCKET_NAME = "sncf-raw"
```

### Exécution

```bash
python scripts/ingestion.py
```

---

## 📁 Structure du Projet

```
📁 sncf-punctuality-pipeline
├── 📁 scripts/
│   └── ingestion.py         ← extraction API → GCS → BigQuery raw
├── 📁 sql/
│   ├── staging.sql          ← transformation raw → staging
│   └── gold.sql             ← modélisation staging → gold
├── 📁 dags/
│   └── sncf_pipeline.py     ← DAG Airflow (en cours)
├── 📁 captures/
│   └── dashboard.png        ← screenshot Looker Studio
└── README.md
```

---

## 📥 Source des Données

Données issues de **SNCF Open Data** — accès gratuit :

👉 [Ponctualité mensuelle Transilien — ressources.data.sncf.com](https://ressources.data.sncf.com)

Dataset : `ponctualite-mensuelle-transilien`
Périmètre : Transilien & RER · Île-de-France · 2024-2026
Mise à jour : mensuelle

---

## 📊 Glossaire

| Terme | Définition |
|---|---|
| Ponctualité | % voyageurs arrivés avec moins de 5 min de retard |
| Retard | 100% - Ponctualité |
| Fiabilité | Nb voyageurs à l'heure pour 1 voyageur en retard |
| Excellent | Taux ≥ 95% |
| Bon | Taux ≥ 90% |
| Moyen | Taux ≥ 85% |
| Mauvais | Taux < 85% |

---

> **Stack** : Google Cloud Platform · BigQuery · Cloud Storage · Python · Looker Studio · Cloud Composer / Airflow
