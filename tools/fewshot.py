from langchain.chains import GraphCypherQAChain
from langchain.prompts.prompt import PromptTemplate

from models.llms import gemini_pro
from models.llms import llama3
from neo4j_connector.graph import neo4j_graph


CYPHER_GENERATION_TEMPLATE = """
You are an expert Neo4j Developer translating user questions into Cypher to answer questions about sockg dataset and provide informations.
Convert the user's question based on the schema.

Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Do not be picky about the exact wording of the context

Fine Tuning:
ALWAYS USED AS TO RENAME THE COLUMN NAME TO THE EXPECTED OUTPUT NAME SPECIFIED IN THE QUESTION.
For example, never return count(u) as count, always return count(u) as totalNumberOfExperimentalUnits

Example Cypher Statements:

1. How to find average soil carbon for each experimental unit?
MATCH (u:ExperimentalUnit)-[:hasChemSample]->(c:SoilChemicalSample)
WHERE (c.totalSoilCarbon) IS NOT NULL AND NOT isNaN(c.totalSoilCarbon)
RETURN u.expUnit_UID, (c.totalSoilCarbon) as averageSoilCarbonForTargetedUnit

2. How to count total number of experimental units?
MATCH (u:ExperimentalUnit)
RETURN count(u) as totalNumberOfExperimentalUnits

3. How to compute the precipitation for a specific field over Q1, Q2, Q3, Q4?
MATCH (f:Field)<-[:weatherAtField]-(w:WeatherObservation)
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
ORDER BY period

Schema:
{schema}

Question:
{question}
"""

cypher_prompt = PromptTemplate.from_template(CYPHER_GENERATION_TEMPLATE)
cypher_qa = GraphCypherQAChain.from_llm(
    llama3,
    graph=neo4j_graph,
    verbose=True,
    cypher_prompt=cypher_prompt
)