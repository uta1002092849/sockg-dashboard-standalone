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
    
    # Get filter information for an experimental unit
    def get_filters(self):
        def get_filters(tx):
            cypher = """MATCH (expUnit:ExperimentalUnit)-[:locatedInField]->(field:Field)<-[:hasField]-(site:Site)
                        OPTIONAL MATCH (site)-[:locatedInCity]->(city:City)
                        OPTIONAL MATCH (site)-[:locatedInCountry]->(country:Country)
                        OPTIONAL MATCH (site)-[:locatedInCounty]->(county:County)
                        OPTIONAL MATCH (site)-[:locatedInState]->(state:State)
                        RETURN
                        expUnit.expUnitId AS experimentalUnitId,
                        COALESCE(expUnit.startDate, "unk") AS startDate,
                        COALESCE(expUnit.endDate, "unk") AS endDate,
                        field.fieldId AS fieldId,
                        COALESCE(field.fieldLongitude_decimal_deg, "unk") AS fieldLongitude,
                        COALESCE(field.fieldLatitude_decimal_deg, "unk") AS fieldLatitude,
                        site.siteId AS siteId,
                        COALESCE(site.postalCodeNumber, 'unk') AS sitePostalCode,
                        COALESCE(site.siteSpatialDescription, 'unk') AS siteSpatialDescription,
                        COALESCE(city.cityName, 'unk') AS cityName,
                        COALESCE(county.countyName, 'unk') AS countyName,
                        COALESCE(state.stateProvince, "unk") AS stateName,
                        COALESCE(country.countryName, 'unk') AS countryName"""
            result = tx.run(cypher)
            return result.to_df()
        
        with self.driver.session() as session:
            return session.execute_read(get_filters)
    
    # Get total number of samples nodes connected to an experimental unit
    def get_sample_count(self, expUnit_id, sample_type):
        def get_sample_count(tx):
            cypher = """MATCH (u:ExperimentalUnit {expUnitId: $expUnit_id})-[]-(s)
                        WHERE ANY(label IN labels(s) WHERE label = $sample_type)
                        RETURN count(s) as count"""
            result = tx.run(cypher, expUnit_id=expUnit_id, sample_type=sample_type)
            return int(result.single()["count"])
        
        with self.driver.session() as session:
            return session.execute_read(get_sample_count)
    
    # Get the count of all samples connected to an experimental unit
    def get_all_measurement_sample_counts(self, expUnit_id):
        samples = ["GasSample", "SoilBiologicalSample", "BioMassEnergy", "SoilChemicalSample", "SoilPhysicalSample", "GasNutrientLoss", "BioMassCarbohydrate", "BioMassMineral", "WaterQualityArea", "WindErosionArea", "YieldNutrientUptake", "WaterQualityConc"]
        sample_counts = {}
        for sample in samples:
            sample_counts[sample] = self.get_sample_count(expUnit_id, sample)
        return sample_counts
        
    # Get the count of all planting and harvest samples connected to an experimental unit
    def get_all_planting_and_harvesting_sample_counts(self, expUnit_id):
        samples = ["Grazing","HarvestFraction", "PlantingEvent", "CropGrowthStage", "Harvest"]
        sample_counts = {}
        for sample in samples:
            sample_counts[sample] = self.get_sample_count(expUnit_id, sample)
        return sample_counts

    # Get all management events applied to an experimental unit
    def get_all_mamagement_events(self, expUnit_id):
        samples = ["Amendment", "Tillage", "ResidueManagementEvent","GrazingManagementEvent", "Treatment"]
        sample_counts = {}
        for sample in samples:
            sample_counts[sample] = self.get_sample_count(expUnit_id, sample)
        return sample_counts
    
    # Get data sample information for an experimental unit
    def get_all_data_samples(self, expUnit_id, sample_type):
        def get_data_samples(tx):
            cypher = """MATCH (u:ExperimentalUnit {expUnitId: $expUnit_id})-[]-(s)
                        WHERE ANY(label IN labels(s) WHERE label = $sample_type)
                        RETURN apoc.map.fromPairs([key IN keys(s) | [key, s[key]]]) AS properties"""
            result = tx.run(cypher, expUnit_id=expUnit_id, sample_type=sample_type)
            data = [record['properties'] for record in result]
            dataframe = pd.DataFrame(data)
            # drop columns with all missing values
            dataframe = dataframe.dropna(axis=1, how='all')
            # drop rows with all missing values
            dataframe = dataframe.dropna(axis=0, how='all')
            # replace None with "Not Available"
            dataframe = dataframe.fillna("Not Available")
            return dataframe
        
        with self.driver.session() as session:
            return session.execute_read(get_data_samples)