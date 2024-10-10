import neo4j
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
        for node in result.nodes:
            val  = {}
            val["id"] = node.element_id
            val["label"] = list(node.labels)[0]
            val["name"] = val["label"]
            val["instance count"] = self.get_sample_count(val["label"])
            nodes.append({"data": val})

        edges = []
        for edge in result.relationships:
            edges.append({"data": {"id": edge.element_id, "label": edge.type, "source": edge.start_node.element_id, "target": edge.end_node.element_id}})

        elements = {"nodes": nodes, "edges": edges}
        return elements
        
    # Fetch sample count of any input node type
    def get_sample_count(self, node_type):
        query = f"MATCH (n:{node_type}) RETURN count(n) as count"
        with self.driver.session() as session:
            records = session.run(query)
            return records.single()["count"]
        
    # Fetch data attributes of any input node type
    def get_node_attributes(self, node_type):
        query = f"MATCH (n:{node_type}) WITH n LIMIT 1 UNWIND keys(n) as key RETURN key"
        with self.driver.session() as session:
            records = session.run(query, node_type=node_type)
            attributes = [record["key"] for record in records]
        return attributes
