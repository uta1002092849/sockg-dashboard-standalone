class GeneralDAO:

    def __init__(self, driver):
        self.driver = driver
    
    # get the unique ID of all experimental units
    def run_query(self, cypher_query):
        
        with self.driver.session() as session:
            records = session.run(cypher_query)
        # records, _, _ = self.driver.execute_query(cypher_query)
            return records.to_df()
