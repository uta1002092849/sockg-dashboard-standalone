from SPARQLWrapper import SPARQLWrapper, JSON
import collections

# SOCKG knowledge graph class
class SOCKG:
    def __init__(self, sparql_endpoint):
        
        # Initialize the SPARQLWrapper with the endpoint URL
        self.sparql = SPARQLWrapper(sparql_endpoint)
        self.sparql.setReturnFormat(JSON)
        self.adjacency_list = collections.defaultdict(list)
        self.class_reference_link = {}
        
        # For pyvis graph, initialize to None if get_pyvis_graph is not called
        self.pyvis_knowledge_graph = None
    
        # Initialize the ontology parameters
        self.classes = set()                # fancy way of saying nodes
        self.object_properties = set()      # fancy way of saying edges

        # Call initialization routines
        self.get_ontology_graph()

        
    def get_ontology_graph(self):
        '''
        Initilize rountines to get populate knowledge graph self variables. Populate the following:
        - self.adjacency_list: A dictionary where the key is a node type and the value is a list of tuples. Each tuple contains the relation and the node type it connects to.
        - self.class_reference_link: A dictionary where the key is a class (node type) and the value is the reference USDA link for that node type.
        - self.classes: A set of all node types in the knowledge graph.
        - self.object_properties: A set of all relations in the knowledge graph.

        :param: None
        :return: None
        '''
        # Define the SPARQL query to get all classes/or nodes types
        get_ontology_query = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX type: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>

            SELECT DISTINCT
                (STRAFTER(STR(?start), "/soil-carbon-ontology/") AS ?startNodeType)
                (STRAFTER(STR(?rel), "/soil-carbon-ontology/") AS ?relationType)
                (STRAFTER(STR(?end), "/soil-carbon-ontology/") AS ?endNodeType)
                ?start_reference_link
                ?end_reference_link
            WHERE {
                
                BIND("Reference not available" AS ?default_reference_link)
                
                ?rel rdf:type owl:ObjectProperty .
                ?rel rdfs:domain ?start.
                ?rel rdfs:range ?end.
                
                OPTIONAL { ?start rdfs:seeAlso ?start_link . }
                OPTIONAL { ?end rdfs:seeAlso ?end_link . }
                
                bind(coalesce(?start_link, ?default_reference_link) as ?start_reference_link)
                bind(coalesce(?end_link, ?default_reference_link) as ?end_reference_link)
            }
        """
        
        # Run the query
        try:
            self.sparql.setQuery(get_ontology_query)
            results = self.sparql.queryAndConvert()
            for result in results["results"]["bindings"]:
                start_node_type = result["startNodeType"]["value"]
                relation = result["relationType"]["value"]
                end_node_type = result["endNodeType"]["value"]
                self.adjacency_list[start_node_type].append((relation, end_node_type))
                self.class_reference_link[start_node_type] = result["start_reference_link"]["value"]
                self.class_reference_link[end_node_type] = result["end_reference_link"]["value"]
                self.classes.add(start_node_type)
                self.classes.add(end_node_type)
                self.object_properties.add(relation)
        except Exception as e:
            print(f"Error retrieving knownledge graph schema: {e}")

    def get_all_classes(self):
        """
        Return all classes in the ontology graph. Result is directly from self.classes, which is initialized in declaration.
        :param: None
        :return: A string list of all classes in the ontology graph
        """
        return list(self.classes)

    def get_all_edges(self):
        """
        Return all object properties or relation in the ontology graph. Result is directly from self.object_properties, which is initialized in declaration.
        :param: None
        :return: A string list of all object properties in the ontology graph
        """
        return list(self.object_properties)
    
    def get_instance_count(self, class_type):
        """
        Return the total count of instances for a given class type. This will be usefull to determine limit and offset for pagination when number of instances is large.
        :param class_type: A string representing the class type to get instance count for
        :return: An integer representing the total count of instances for the given class type
        """
        total_count = 0
        if class_type not in self.get_all_classes():
            print(f"Class: {class_type} not found in the ontology graph")
        else:
            get_instance_count_query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX onto: <http://www.semanticweb.org/zzy/ontologies/2024/0/soil-carbon-ontology/>

                SELECT (COUNT(?instance_uri) AS ?totalCount)
                WHERE {{
                    ?instance_uri rdf:type onto:{class_type} .
                }}
            """.format(class_type=class_type)

            # Run the query
            try:
                self.sparql.setQuery(get_instance_count_query)
                results = self.sparql.queryAndConvert()
                total_count = int(results["results"]["bindings"][0]["totalCount"]["value"])
            except Exception as e:
                print(f"Error retrieving instance count for node {class_type}: {e}")
        return total_count
    
    def get_data_properties_from_class_v2(self, class_type):
        
        # get a single instance of the class
        result = self.get_node_instance_from_class_v2(class_type, "instance_uri", 1, 0)
        rows = result['rows']
        node_uri = rows[0]['uri']
        
        # get all data properties for the instance
        result = self.get_data_property_from_instance(node_uri)
        data_attributes = list(result.keys())
        return data_attributes
    
    def get_data_properties_from_class(self, class_type):
        """
        Given a class type, return all data properties for that class type. This is typically not used as numerical data is commonly in triple with the instance. Include for completeness.
        :param class_type: A string representing the class type to get data properties for
        :return: A list of dictionaries containing the following keys: name, data_type, reference_link
        """
        attributes = []
        if class_type not in self.get_all_classes():
            print(f"Class: {class_type} not found in the ontology graph")
        else:
            node_uri = "http://www.semanticweb.org/zzy/ontologies/2024/0/soil-carbon-ontology/" + class_type
            get_attributes_query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX type: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX owl: <http://www.w3.org/2002/07/owl#>

                SELECT DISTINCT
                (STRAFTER(STR(?node), "/soil-carbon-ontology/") AS ?nodeType)
                (STRAFTER(STR(?attri), "/soil-carbon-ontology/") AS ?attribute)
                (STRAFTER(STR(?datatype), "/XMLSchema#") AS ?dataType)
                ?reference_link
                WHERE {{
                    ?attri rdf:type owl:DatatypeProperty .
                    ?attri rdfs:domain <{node_uri}> .
                    ?attri rdfs:range ?datatype.
                    ?attri rdfs:seeAlso ?reference_link
                }}
            """.format(node_uri=node_uri)

            # Run the query
            try:
                self.sparql.setQuery(get_attributes_query)
                results = self.sparql.queryAndConvert()
                
                # A list of tuples containing the attribute name, data type, and reference link
                for result in results["results"]["bindings"]:
                    attribute = result["attribute"]["value"]
                    data_type = result["dataType"]["value"]
                    reference_link = result["reference_link"]["value"]
                    # format each row as a dictionary
                    row = {"name": attribute, "data_type": data_type, "reference_link": reference_link}
                    attributes.append(row)
            except Exception as e:
                print(f"Error retrieving attributes for node {class_type}: {e}")
        return attributes
    

    def getVisJsGraph(self):
        """
        Return the ontology graph in a format that can be used to visualize with VisJs.
        :param: None
        :return: A dictionary containing the nodes and edges of the ontology graph. See https://visjs.github.io/vis-network/docs/network/ for more information.
        """
        nodes, edges = [], []
        seen_nodes = set()
        for start_node in self.adjacency_list:
            for relation, end_node in self.adjacency_list[start_node]:
                if start_node not in seen_nodes:
                    nodes.append({"id": start_node, "label": start_node, "group": start_node})
                    seen_nodes.add(start_node)
                if end_node not in seen_nodes:
                    nodes.append({"id": end_node, "label": end_node, "group": end_node})
                    seen_nodes.add(end_node)
                edges.append({"from": start_node, "to": end_node, "title": relation, "arrows": "to"})
        return {"nodes": nodes, "edges": edges}
    
    def get_node_instance_from_class(self, class_type, property_name, limit=10, offset=0):
        """
        Given a class type, limit, and offset, return all instances for that class type. This is typically used to get all instances for a given class type.
        :param class_type: A string representing the class type to get instances for
        :param limit: An integer representing the number of instances to return, default is 10
        :param offset: An integer representing the starting point to return instances, default is 0. This is useful for pagination, where the next set of instances will be offset + limit
        :return: A list of strings containing the instance URIs for the given class type. For example, "neo4j://graph.individuals#1234"
        """

        if class_type not in self.get_all_classes():
            print(f"Class {class_type} not found in the ontology graph")
        else:
            get_attributes_query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX onto: <http://www.semanticweb.org/zzy/ontologies/2024/0/soil-carbon-ontology/>

                SELECT 
                    ?instance_uri ?value
                WHERE {{
                    
                    BIND("Not available" AS ?default_value)
                    
                    ?instance_uri rdf:type onto:{class_type} .
                    OPTIONAL {{?instance_uri onto:{property} ?propertyValue .}}
                    
                    bind(coalesce(?propertyValue, ?default_value) as ?value)
                }}
                LIMIT {limit}
                OFFSET {offset}
            """.format(class_type=class_type, property=property_name, limit=limit, offset=offset)
            node_uris = []
            # Run the query
            try:
                self.sparql.setQuery(get_attributes_query)
                results = self.sparql.queryAndConvert()
                for result in results["results"]["bindings"]:
                    if property_name == "null" or property_name == "instance_uri":
                        uri = result["instance_uri"]["value"]
                    else:
                        uri = result["value"]["value"]
                    node_uris.append(uri)
                return node_uris
            except Exception as e:
                print(f"Error retrieving attributes for node {class_type}: {e}")
    
    def get_node_instance_from_class_v2(self, class_type, property_type, limit=10, offset=0):
        """
        Given a class type, limit, and offset, return all instances for that class type. This is typically used to get all instances for a given class type.
        :param class_type: A string representing the class type to get instances for
        :param limit: An integer representing the number of instances to return, default is 10
        :param offset: An integer representing the starting point to return instances, default is 0. This is useful for pagination, where the next set of instances will be offset + limit
        :return: A list of strings containing the instance URIs for the given class type. For example, "neo4j://graph.individuals#1234"
        """

        if class_type not in self.get_all_classes():
            print(f"Class {class_type} not found in the ontology graph")
        else:
            get_attributes_query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX onto: <http://www.semanticweb.org/zzy/ontologies/2024/0/soil-carbon-ontology/>
                PREFIX owl: <http://www.w3.org/2002/07/owl#>

                SELECT 
                    ?instance_uri
                    ?value
                WHERE {{

                    BIND("Not available" AS ?default_value)

                    ?instance_uri rdf:type onto:{class_type} .
                    OPTIONAL {{?instance_uri onto:{property_type} ?propertyValue .}}

                    bind(coalesce(?propertyValue, ?default_value) as ?value)

                }}
                LIMIT {limit}
                OFFSET {offset}
            """.format(class_type=class_type, property_type=property_type, limit=limit, offset=offset)
            # Run the query
            try:
                self.sparql.setQuery(get_attributes_query)
                results = self.sparql.queryAndConvert()

                # return result in ajax friendly format
                res = {}

                # get total count of instances
                res["total"] = self.get_instance_count(class_type)
                res['totalNotFiltered'] = res["total"]
                res['rows'] = []

                id = (offset + 1)

                for result in results["results"]["bindings"]:
                    row = {}
                    row["id"] = id
                    id += 1
                    row["uri"] = result["instance_uri"]["value"]
                    row["property_value"] = (result["value"]["value"] if str(result["value"]["value"]) != "NaN" else "Not available")
                    res['rows'].append(row)
                return res
            except Exception as e:
                print(f"Error retrieving attributes for node {class_type}: {e}")
    
    def get_data_property_from_instance(self, node_uri):
        """
        Given a node instance, return all data properties for that node instance. Data properties are typically numerical values associated with the instance, excluding the relations to other instances (these relations will be considered as object porperty).
        :param node_uri: A string representing the node instance to get data properties for
        :return: A dictionary containing the attribute name and value. For example, {"pH": 6.5, "temperature": 25}
        """    
        # assume uri is in the form "neo4j://graph.individuals#<node_id>"
        get_attributes_query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX onto: <http://www.semanticweb.org/zzy/ontologies/2024/0/soil-carbon-ontology/>
                PREFIX owl: <http://www.w3.org/2002/07/owl#>

                SELECT 
                    (STRAFTER(STR(?attri), "/soil-carbon-ontology/") AS ?dataAttribute)
                    ?value
                WHERE {{
                    <{node_uri}> ?attri ?value .
                    ?attri rdf:type owl:DatatypeProperty .
                }}
        """.format(node_uri=node_uri)
        # Run the query
        try:
            self.sparql.setQuery(get_attributes_query)
            results = self.sparql.queryAndConvert()
            
            # A dictionary containing the attribute name and value
            attribute_val = {}

            # A list of tuples containing the attribute name, data type, and reference link
            for result in results["results"]["bindings"]:
                data_attribute = result["dataAttribute"]["value"]
                value = (result["value"]["value"] if str(result["value"]["value"]) != "NaN" else "Not available")
                attribute_val[data_attribute] = value
            return attribute_val
        except Exception as e:
            print(f"Error retrieving attributes for node {node_uri}: {e}")

    def get_object_property_from_instance(self, node_uri):
        """
        Given a node instance, return all object properties for that node instance. Object properties are relations to other instances, excluding the numerical values associated with the instance (these values will be considered as data porperty).
        :param node_uri: A string representing the node instance to get object properties for
        :return: A list of tuples containing the attribute name and reference link. For example, [("hasParent", "neo4j://graph.individuals#1234"), ("hasChild", "neo4j://graph.individuals#5678")]
        """
        # assume uri is in the form "neo4j://graph.individuals#<node_id>"
        get_attributes_query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX onto: <http://www.semanticweb.org/zzy/ontologies/2024/0/soil-carbon-ontology/>
                PREFIX owl: <http://www.w3.org/2002/07/owl#>

                SELECT 
                    (STRAFTER(STR(?attri), "/soil-carbon-ontology/") AS ?objectAttribute)
                    ?neighbor
                WHERE {{
                    <{node_uri}> ?attri ?neighbor .
                    ?attri rdf:type owl:ObjectProperty .
                }}
        """.format(node_uri=node_uri)

        # Run the query
        try:
            self.sparql.setQuery(get_attributes_query)
            results = self.sparql.queryAndConvert()
            
            # A dictionary containing the attribute name and value
            neighbors = []

            # A list of tuples containing the attribute name, data type, and reference link
            for result in results["results"]["bindings"]:
                data_attribute = result["objectAttribute"]["value"]
                neighbor = result["neighbor"]["value"]
                neighbors.append((data_attribute, neighbor))
        except Exception as e:
            print(f"Error retrieving attributes for node {node_uri}: {e}")
        return neighbors
    
    def get_class_type_from_instance(self, node_uri):
        """
        Given a node instance uri, return the class type of that instance.
        :param node_uri: A string representing the node instance to get class type for
        :return: A string representing the class type of the given node instance. For example, "Soil"
        """
        class_type = None
        # assume uri is in the form "neo4j://graph.individuals#<node_id>"
        get_attributes_query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                SELECT 
                    (STRAFTER(STR(?class), "/soil-carbon-ontology/") AS ?classType)
                WHERE {{
                    <{node_uri}> rdf:type ?class .
                }}
        """.format(node_uri=node_uri)
        # Run the query
        try:
            self.sparql.setQuery(get_attributes_query)
            results = self.sparql.queryAndConvert()

            for result in results["results"]["bindings"]:
                class_type = result["classType"]["value"]
        except Exception as e:
            print(f"Error retrieving attributes for node {node_uri}: {e}")
        return class_type
    
    def _get_uri_through_connection(self, startURI, connectionType):
        """
        Given an start node's uri, return end node uri that connected with start through an relation.
        :param startURI: A string representing the start node's uri
        :param connectionType: A string representing the relation between start and end node
        :return: A list of strings containing the end node URIs for the given start node. For example, "neo4j://graph.individuals#1234"
        """
        uri = []
        
        # assume uri is in the form "neo4j://graph.individuals#<node_id>"
        endURIs =  """
            PREFIX onto: <http://www.semanticweb.org/zzy/ontologies/2024/0/soil-carbon-ontology/>
            SELECT ?endURI
            WHERE {{
                # Forward direction
                {{ <{startURI}> onto:{connection} ?endURI. }}
                # Reverse direction
                UNION
                {{ ?endURI onto:{connection} <{startURI}>. }}
            }}
        """.format(startURI=startURI, connection=connectionType)


        # Run the query
        try:
            self.sparql.setQuery(endURIs)
            results = self.sparql.queryAndConvert()
            for result in results["results"]["bindings"]:
                uri.append(result["endURI"]["value"])
        except Exception as e:
            print(f"Error retrieving end node for start node {startURI}: {e}")
        return uri
    
    def get_all_experimentalUnit_for_field(self, field_instance):
        """
        Given a field instance, return all experimental unit instances for that field instance.
        :param field_instance: A string representing the field instance to get experimental unit instances for
        :return: A list of strings containing the experimental unit URIs for the given field instance. For example, "neo4j://graph.individuals#1234"
        """
        return self._get_uri_through_connection(field_instance, "locatedInField")
    
    def get_all_soilPhysicalSample_for_expUnit(self, expUnit_instance):
        """
        Given an experimental unit instance, return all soil physical sample instances for that experimental unit instance.
        :param expUnit_instance: A string representing the experimental unit instance to get soil physical sample instances for
        :return: A list of strings containing the soil physical sample URIs for the given experimental unit instance. For example, "neo4j://graph.individuals#1234"
        """
        return self._get_uri_through_connection(expUnit_instance, "hasPhySample")
    
    def get_all_soilChemicalSample_for_expUnit(self, expUnit_instance):
        """
        Given an experimental unit instance, return all soil chemical sample instances for that experimental unit instance.
        :param expUnit_instance: A string representing the experimental unit instance to get soil chemical sample instances for
        :return: A list of strings containing the soil chemical sample URIs for the given experimental unit instance. For example, "neo4j://graph.individuals#1234"
        """
        return self._get_uri_through_connection(expUnit_instance, "hasChemSample")
    
    def get_all_soilBiologicalSample_for_expUnit(self, expUnit_instance):
        """
        Given an experimental unit instance, return all soil biological sample instances for that experimental unit instance.
        :param expUnit_instance: A string representing the experimental unit instance to get soil biological sample instances for
        :return: A list of strings containing the soil biological sample URIs for the given experimental unit instance. For example, "neo4j://graph.individuals#1234"
        """
        return self._get_uri_through_connection(expUnit_instance, "hasBioSample")
    
    def get_all_field_ids(self):
        """
        Return all field instances in the ontology graph.
        :param: None
        :return: A list of strings containing the field instance URIs. For example, "neo4j://graph.individuals#1234"
        """
        return self.get_node_instance_from_class("Field", "fieldId")
    
    