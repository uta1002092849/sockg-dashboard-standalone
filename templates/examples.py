# This file contains examples of questions and queries that can be used as a few-shot prompt for the model.
# Few-shot is then selected from these examples using semantic similarity embeddings.

# references: https://python.langchain.com/v0.2/docs/how_to/graph_prompting/
# fewshot examples
examples = [
    {
        "question": "How to find average soil carbon?",
        "query": "MATCH (u:ExperimentalUnit)-[:hasChemSample]->(c:SoilChemicalSample) WHERE (c.totalSoilCarbon) IS NOT NULL AND NOT isNaN(c.totalSoilCarbon) RETURN u.expUnit_UID, (c.totalSoilCarbon) as averageSoilCarbonForTargetedUnit",
    },
    {
        "question": "How to compute the total number of experimental unit per treatment?",
        "query": "MATCH (u:Treatment)-[:appliedInExpUnit]->(e:ExperimentalUnit) RETURN u.treatmentDescriptor as treatment, count(e) AS numberOfExpUnit",
    },
    {
        "question": "How to compute the precipitation for a specific field over Q1, Q2, Q3, Q4?",
        "query": """MATCH (f:Field)<-[:weatherAtField]-(w:WeatherObservation)
WHERE f.fieldId = $neodash_field_fieldid_5
WITH w.weatherObservationDate AS date, w.precipitation AS precipitation
WITH date, precipitation,
     toInteger(substring(date, 0, 4)) AS year,
     toInteger(substring(date, 5, 2)) AS month
WITH year,
    CASE
        WHEN month IN [1, 2, 3] THEN 'Q1'
        WHEN month IN [4, 5, 6] THEN 'Q2'
        WHEN month IN [7, 8, 9] THEN 'Q3'
        ELSE 'Q4'
    END AS quarter,
    precipitation
WITH year + '-' + quarter AS period, SUM(precipitation) AS totalPrecipitation
RETURN period, round(totalPrecipitation, 3) AS totalPrecipitation
ORDER BY period"""
    },
    {
        "question": "How to get a list of experimental units located in a specific field?",
        "query": "MATCH (u:ExperimentalUnit)-[:locatedInField]->(f:Field) WHERE f.fieldId = $field_id RETURN u.expUnit_UID AS Experimental_unit"
    },
    {
        "question": "How to get soil property of a specific field?",
        "query": "MATCH (f:Field)<-[:appliedInField]-(s:Soil) WHERE f.fieldId = $field_id RETURN s.soilSeries"
    },
    {
        "question": "How get a list of research conducted on a specific filed?",
        "query": "MATCH path =(f:Field)<-[:hasField]-(s:Site)<-[:studiesSite]-(p:Publication) WHERE f.fieldId = $neodash_field_fieldid_5 RETURN p.publicationTitle as Title, p.publicationAuthor as Author, p.publicationDate as publicationDate, p.publicationIdentifier as Reference ORDER BY p.publicationDate"
    },
    {
        "question": "Return all Fields. For each field, return the name and the number of Experimental Units it has.",
        "query": """MATCH (f:Field)
WITH f, f.fieldId AS fieldId
OPTIONAL MATCH (u:ExperimentalUnit)-[:locatedInField]->(f)
RETURN f.fieldId AS fieldName, count(u) AS numExpUnits"""
    },
]