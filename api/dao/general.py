import neo4j
import re

# Function to convert camel case to normal case
def camel_to_normal(camel_str):
    normal_str = re.sub(r'(?<!^)(?=[A-Z])', ' ', camel_str)
    return normal_str.title()

# Function to convert snake case to normal case
def snake_to_normal(snake_str):
    words = [word if word != 'per' else '/' for word in snake_str.split('_')]
    return ' '.join(words)

# Function to convert camel + snake case to normal case
def camel_snake_to_normal(camel_snake_str):
    underscore_index = camel_snake_str.find('_')
    if underscore_index != -1:
        normal_str = camel_to_normal(camel_snake_str[:underscore_index])
        normal_str += ' (' + snake_to_normal(camel_snake_str[underscore_index + 1:]) + ')'
        return normal_str
    else:   
        return camel_to_normal(camel_snake_str)

class GeneralDAO:

    def __init__(self, driver):
        self.driver = driver
    
    # get the unique ID of all experimental units
    def run_query(self, cypher_query):
        
        with self.driver.session() as session:
            records = session.run(cypher_query)
        # records, _, _ = self.driver.execute_query(cypher_query)
            return records.to_df()
        
    # Fetch ontology data
    def get_ontology_data(self):
        query = "call db.schema.visualization()"
        result = self.driver.execute_query(query, result_transformer_=neo4j.Result.graph)
        nodes = []
        look_up = {}
        for node in result.nodes:
            val  = {}
            val["id"] = list(node.labels)[0]
            look_up[node.element_id] = val["id"]
            val["instance count"] = self.get_sample_count(val["id"])
            val["caption"] = camel_snake_to_normal(val["id"])
            val["label"] = val["caption"]
            nodes.append({"data": val})

        edges = []
        for edge in result.relationships:
            edges.append({"data": {"id": edge.type, "caption": camel_snake_to_normal(edge.type), "label": camel_snake_to_normal(edge.type), "source": look_up[edge.start_node.element_id], "target": look_up[edge.end_node.element_id]}})

        elements = {"nodes": nodes, "edges": edges}
        return elements
        
    # Fetch sample count of any input node type
    def get_sample_count(self, node_type):
        query = f"MATCH (n:{node_type}) RETURN count(n) as count"
        with self.driver.session() as session:
            records = session.run(query)
            return records.single()["count"]
    
    # Fetch example value for node attribute
    def get_example_value(self, node_type, attribute):
        query = f"MATCH (n:{node_type}) WHERE n.{attribute} is not null AND TOSTRING(n.{attribute}) <> 'NaN' RETURN DISTINCT(n.{attribute}) AS example LIMIT 3"
        with self.driver.session() as session:
            records = session.run(query)
            # Check if there is any record
            if records.peek() is None:
                return None
            return [str(record["example"]) for record in records]
        
    # Fetch data attributes of any input node type
    def get_node_attributes(self, node_type):
        query = f"MATCH (n:{node_type}) WITH n LIMIT 1 UNWIND keys(n) as key RETURN key"
        with self.driver.session() as session:
            try:
                records = session.run(query, node_type=node_type)
                attributes_raw = [record["key"] for record in records]
                attributes_beatified = [camel_snake_to_normal(attribute) for attribute in attributes_raw]
                return attributes_raw, attributes_beatified
            except Exception as e:
                return []
    