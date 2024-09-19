import pandas as pd

class ExperimentalUnitDAO:

    def __init__(self, driver):
        self.driver = driver
    
    # get the unique ID of all experimental units
    def get_all_ids(self):
        def get_exp_units(tx):
            cypher = "MATCH (u:ExperimentalUnit) RETURN u as exp_units"
            result = tx.run(cypher)
            return [record["exp_units"]["expUnit_UID"] for record in result]
        
        with self.driver.session() as session:
            return session.execute_read(get_exp_units)

    # Get experimental unit information
    def get_exp_unit_info(self, expUnit_id):
            def get_exp_unit_info(tx):
                cypher = """MATCH (u:ExperimentalUnit {expUnit_UID: $expUnit_id})
                            WITH u, keys(u) AS keys
                            UNWIND keys AS key
                            RETURN key, apoc.map.get(u, key) AS property"""
                result = tx.run(cypher, expUnit_id=expUnit_id)
                return result.to_df()
            
            with self.driver.session() as session:
                return session.execute_read(get_exp_unit_info)
    
    # get all treatments applied to an experimental unit
    def get_all_treatments(self, expUnit_id):
        
        def get_treatments(tx):
            cypher = """MATCH (u:ExperimentalUnit {expUnit_UID: $expUnit_id})<-[:appliedInExpUnit]-(t:Treatment)
                        RETURN
                            t.treatmentId AS ID,
                            t.treatmentDescriptor AS Name,
                            t.treatmentStartDate AS Start_Date,
                            t.treatmentEndDate AS End_Date
                        ORDER BY t.treatmentStartDate ASC"""
            result = tx.run(cypher, expUnit_id=expUnit_id)
            return result.to_df()
        
        with self.driver.session() as session:
            return session.execute_read(get_treatments)
    
    # get grain yield of an experimental unit over time
    def get_grain_yield(self, expUnit_id):
        def get_grain_yield(tx):
            cypher = """MATCH (u:ExperimentalUnit {expUnit_UID: $expUnit_id})-[:isHarvested]->(h:Harvest)
                        RETURN
                            h.harvestDate AS Date,
                            h.harvestedGrainYield_kg_per_ha AS grainYield,
                            h.harvestedCrop AS crop
                        ORDER BY h.harvestDate ASC"""
            result = tx.run(cypher, expUnit_id=expUnit_id)
            return result.to_df()
        
        with self.driver.session() as session:
            return session.execute_read(get_grain_yield)
    
    # get soil carbon storage of an experimental unit over time
    def get_soil_carbon(self, expUnit_id):
        
        def get_soil_carbon(tx):
            cypher = """MATCH (u:ExperimentalUnit {expUnit_UID: $expUnit_id})-[:hasChemSample]->(s:SoilChemicalSample)
                        RETURN
                            s.soilChemLowerDepth_cm as LowerDepth,
                            s.soilChemUpperDepth_cm as UpperDepth,
                            s.soilChemDate as Date,
                            s.totalSoilCarbon_gC_per_kg as SoilCarbon
                        ORDER BY s.soilChemDate ASC"""
            result = tx.run(cypher, expUnit_id=expUnit_id)
            return result.to_df()
        
        with self.driver.session() as session:
            return session.execute_read(get_soil_carbon)
    
    # get soil physical properties of an experimental unit over time
    def get_soil_physical_properties(self, expUnit_id):
        
        def get_physical_properties(tx):
            cypher = """MATCH (u:ExperimentalUnit {expUnit_UID: $expUnit_id})-[:hasPhySample]->(s:SoilPhysicalSample)
                        RETURN
                            s
                        ORDER BY s.soilPhysDate ASC"""
            result = tx.run(cypher, expUnit_id=expUnit_id)
            return result.to_df()
        
        with self.driver.session() as session:
            return session.execute_read(get_physical_properties)
        
    
    # get soil Chemical properties of an experimental unit over time
    def get_soil_chemical_properties(self, expUnit_id):
        
        def get_chemical_properties(tx):
            cypher = """MATCH (u:ExperimentalUnit {expUnit_UID: $expUnit_id})-[:hasChemSample]->(s:SoilChemicalSample)
                        RETURN
                            s.soilChemDate as Date,
                            s.totalSoilCarbon_gC_per_kg as Carbon,
                            s.soilAmmonium_mgN_per_kg as Ammonium,
                            s.soilNitrate_mgN_per_kg as Nitrate,
                            s.soilPh as PH,
                            s.totalSoilNitrogen_gN_per_kg as Nitrogen,
                            s.soilChemLowerDepth_cm as LowerDepth,
                            s.soilChemUpperDepth_cm as UpperDepth
                        ORDER BY s.soilChemDate ASC"""
            result = tx.run(cypher, expUnit_id=expUnit_id)
            return result.to_df()
        
        with self.driver.session() as session:
            return session.execute_read(get_chemical_properties)
    
    # Get soil biological properties of an experimental unit over time
    def get_soil_biological_properties(self, expUnit_id):
        def get_biological_properties(tx):
            cypher = """
            MATCH (u:ExperimentalUnit {expUnit_UID: $expUnit_id})-[:hasBioSample]->(s:SoilBiologicalSample)
            RETURN apoc.map.fromPairs([key IN keys(s) | [key, s[key]]]) AS properties
            ORDER BY s.soilBiolDate ASC
            """
            result = tx.run(cypher, expUnit_id=expUnit_id)
            # Convert the result to a pandas DataFrame
            data = [record['properties'] for record in result]
            return pd.DataFrame(data)
        
        with self.driver.session() as session:
            return session.execute_read(get_biological_properties)
