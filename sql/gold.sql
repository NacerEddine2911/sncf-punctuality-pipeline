-- Gold
/* 
CREATE OR REPLACE TABLE sncf_gold.dim_date AS
SELECT DISTINCT
    date,
    CAST(SUBSTR(date, 1, 4) AS INT64) AS annee,
    CAST(SUBSTR(date, 6, 2) AS INT64) AS mois,
    FORMAT_DATE('%B', PARSE_DATE('%Y-%m', date)) AS nom_mois,
    CASE CAST(SUBSTR(date, 6, 2) AS INT64)
        WHEN 1 THEN 'T1' WHEN 2 THEN 'T1' WHEN 3 THEN 'T1'
        WHEN 4 THEN 'T2' WHEN 5 THEN 'T2' WHEN 6 THEN 'T2'
        WHEN 7 THEN 'T3' WHEN 8 THEN 'T3' WHEN 9 THEN 'T3'
        ELSE 'T4'
    END AS trimestre
FROM sncf_staging.ponctualite_transilien
WHERE date IS NOT NULL
ORDER BY date
*/
/*
CREATE OR REPLACE TABLE sncf_gold.dim_ligne AS
SELECT DISTINCT
    ligne,
    nom_de_la_ligne,
    service
FROM sncf_staging.ponctualite_transilien
WHERE ligne IS NOT NULL
ORDER BY ligne
*/

/*
CREATE OR REPLACE TABLE sncf_gold.dim_service AS
SELECT DISTINCT
    service,
    CASE service
        WHEN 'RER' THEN 'Réseau Express Régional'
        WHEN 'TRANSILIEN' THEN 'Transilien'
        ELSE service
    END AS service_label
FROM sncf_staging.ponctualite_transilien
WHERE service IS NOT NULL
*/

/*
CREATE OR REPLACE TABLE sncf_gold.dim_categorie AS
SELECT DISTINCT
    categorie_ponctualite,
    CASE categorie_ponctualite
        WHEN 'Excellent' THEN 1
        WHEN 'Bon'       THEN 2
        WHEN 'Moyen'     THEN 3
        WHEN 'Mauvais'   THEN 4
    END AS ordre_affichage
FROM sncf_staging.ponctualite_transilien
WHERE categorie_ponctualite IS NOT NULL
*/

CREATE OR REPLACE TABLE sncf_gold.fact_ponctualite AS
SELECT
    s.date,
    s.ligne,
    s.service,
    s.categorie_ponctualite,
    s.taux_de_ponctualite,
    s.pct_voyageurs_a_lheure,
    ROUND(100 - s.taux_de_ponctualite, 2) AS taux_retard,
    s.ingestion_timestamp
FROM sncf_staging.ponctualite_transilien s
WHERE s.date IS NOT NULL
AND s.taux_de_ponctualite IS NOT NULL
ORDER BY s.date DESC