import requests
import json
from google.cloud import bigquery
from google.cloud import storage
from datetime import datetime

# CONFIGURATION
PROJECT_ID  = "snf-pipeline"
BUCKET_NAME = "sncf-raw"
DATASET     = "sncf_raw"
TABLE       = "ponctualite_transilien"
API_KEY     = "a8d6fcd10ca592b3c6799f8b2a5b0cc3e62706fa2e463761f2ea4595"

# -----------------------------------
# 1. FETCH 2 DERNIÈRES ANNÉES
# -----------------------------------
def fetch_sncf_data():
    url = "https://ressources.data.sncf.com/api/explore/v2.1/catalog/datasets/ponctualite-mensuelle-transilien/records"
    all_data = []
    offset = 0
    limit = 100

    # Filtre sur les 2 dernières années
    current_year = datetime.now().year
    start_year = current_year - 2
    where_filter = "date >= '" + str(start_year) + "-01'"

    while True:
        params = {
            "limit": limit,
            "offset": offset,
            "order_by": "date DESC",
            "where": where_filter,
            "apikey": API_KEY
        }
        response = requests.get(url, params=params)
        data = response.json()
        results = data.get("results", [])

        if not results:
            break

        all_data.extend(results)
        offset += limit
        print("Recuperes : " + str(len(all_data)) + " / " + str(data["total_count"]))

        if len(all_data) >= data["total_count"]:
            break

    print("Total final : " + str(len(all_data)) + " enregistrements")
    return all_data

# -----------------------------------
# 2. SAVE RAW DATA TO GCS
# -----------------------------------
def save_to_gcs(data):
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = "raw/ponctualite_2ans_" + timestamp + ".json"
    blob = bucket.blob(filename)
    blob.upload_from_string(
        json.dumps(data),
        content_type="application/json"
    )
    print("Sauvegarde GCS : " + filename)

# -----------------------------------
# 3. LOAD DATA INTO BIGQUERY
# -----------------------------------
def load_to_bigquery(data):
    client = bigquery.Client()
    table_id = PROJECT_ID + "." + DATASET + "." + TABLE

    schema = [
        bigquery.SchemaField("date", "STRING"),
        bigquery.SchemaField("service", "STRING"),
        bigquery.SchemaField("ligne", "STRING"),
        bigquery.SchemaField("nom_de_la_ligne", "STRING"),
        bigquery.SchemaField("taux_de_ponctualite", "FLOAT"),
        bigquery.SchemaField("nombre_de_voyageurs_a_l_heure_pour_un_voyageur_en_retard", "FLOAT"),
        bigquery.SchemaField("ingestion_timestamp", "TIMESTAMP"),
    ]

    try:
        client.get_table(table_id)
        print("Table existante trouvee")
    except Exception:
        table = bigquery.Table(table_id, schema=schema)
        client.create_table(table)
        print("Table creee")

    timestamp = datetime.utcnow().isoformat()
    cleaned_data = []

    for row in data:
        new_row = {
            "date": row.get("date"),
            "service": row.get("service"),
            "ligne": row.get("ligne"),
            "nom_de_la_ligne": row.get("nom_de_la_ligne"),
            "taux_de_ponctualite": None,
            "nombre_de_voyageurs_a_l_heure_pour_un_voyageur_en_retard": None,
            "ingestion_timestamp": timestamp
        }
        try:
            if row.get("taux_de_ponctualite"):
                new_row["taux_de_ponctualite"] = float(row["taux_de_ponctualite"])
        except:
            pass
        try:
            if row.get("nombre_de_voyageurs_a_l_heure_pour_un_voyageur_en_retard"):
                new_row["nombre_de_voyageurs_a_l_heure_pour_un_voyageur_en_retard"] = float(
                    row["nombre_de_voyageurs_a_l_heure_pour_un_voyageur_en_retard"]
                )
        except:
            pass
        cleaned_data.append(new_row)

    job = client.load_table_from_json(cleaned_data, table_id)
    job.result()
    print("Lignes chargees : " + str(job.output_rows))

# -----------------------------------
# MAIN PIPELINE
# -----------------------------------
if __name__ == "__main__":
    print("Demarrage pipeline SNCF...")
    data = fetch_sncf_data()
    save_to_gcs(data)
    load_to_bigquery(data)
    print("Pipeline termine !")

