-- Staging Table 
CREATE OR REPLACE TABLE sncf_staging.ponctualite_transilien AS
SELECT
    -- Date
    date,
    CAST(SUBSTR(date, 1, 4) AS INT64) AS annee,
    CAST(SUBSTR(date, 6, 2) AS INT64) AS mois,
    FORMAT_DATE('%B', PARSE_DATE('%Y-%m', date)) AS nom_mois,

    -- Infos ligne
    UPPER(service) AS service,
    UPPER(ligne) AS ligne,
    nom_de_la_ligne,

    -- KPIs
    ROUND(taux_de_ponctualite, 2) AS taux_de_ponctualite,
    ROUND(
        (nombre_de_voyageurs_a_l_heure_pour_un_voyageur_en_retard /
        (nombre_de_voyageurs_a_l_heure_pour_un_voyageur_en_retard + 1)) * 100
    , 2) AS pct_voyageurs_a_lheure,

    -- Catégorie ponctualité
    CASE
        WHEN taux_de_ponctualite >= 95 THEN 'Excellent'
        WHEN taux_de_ponctualite >= 90 THEN 'Bon'
        WHEN taux_de_ponctualite >= 85 THEN 'Moyen'
        ELSE 'Mauvais'
    END AS categorie_ponctualite,

    -- Timestamp ingestion
    ingestion_timestamp

FROM sncf_raw.ponctualite_transilien
WHERE date IS NOT NULL
AND taux_de_ponctualite IS NOT NULL
ORDER BY date DESC, ligne
