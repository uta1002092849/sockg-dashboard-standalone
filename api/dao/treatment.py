import pandas as pd
import re

def extract_numeric_value(descriptor):
    descriptor = str(descriptor)

    # Remove leading/trailing whitespace
    descriptor = descriptor.strip()
    
    # Check for non-numeric descriptors indicating zero, might need more
    if descriptor.lower() in ['none', 'none applied', 'check', 'no nitrogen', 'zero nitrogen fertilizer (zn)']:
        return 0
    
    # Extract all numeric values
    numbers = re.findall(r'\d+(?:\.\d+)?', descriptor)

    if numbers:
        # If there are multiple numbers, return the first one
        return float(numbers[0])
    
    # If we can't determine a numeric value, return 'unavailable'
    return None

class TreatmentDAO:
    def __init__(self, driver):
        self.driver = driver

    # get all treatments that sastified filter
    def get_filtered_treatments(self, selected_tillage, selected_rotation, belong_to_experiment, selected_nitrogen, selected_irrigation, selected_residue_removal, treatment_organic_management):
        
        def get_treatments(tx):
            cypher = """
            MATCH (treatment:Treatment)-[:hasRotation]->(rotation:Rotation)
            WHERE
                (treatment.tillageDescriptor IN $selected_tillage) AND
                (rotation.rotationDescriptor IN $selected_rotation) AND
                treatment.irrigation = $selected_irrigation AND
                treatment.treatmentOrganicManagement = $selected_organic_management AND
                (treatment.treatmentResidueRemoval IN $selected_residue_removal) AND
                (treatment.nitrogenTreatmentDescriptor IN $selected_nitrogen)
                """ + ("""
                AND EXISTS { MATCH (treatment)<-[:hasTreatment]-(:Experiment) }
                """ if belong_to_experiment else "") + """
            RETURN 
                treatment.treatmentId AS ID,
                treatment.treatmentDescriptor AS description,
                treatment.treatmentStartDate AS Start_Date,
                treatment.treatmentEndDate AS End_Date
            ORDER BY treatment.treatmentStartDate ASC
            """
            parameters = {
                "selected_tillage": selected_tillage,
                "selected_rotation": selected_rotation,
                "selected_irrigation": "Yes" if selected_irrigation else "No",
                "selected_organic_management": "Yes" if treatment_organic_management else "No",
                "selected_residue_removal": selected_residue_removal,
                "selected_nitrogen": selected_nitrogen
            }

            result = tx.run(cypher, parameters)
            return result.to_df()
        
        with self.driver.session() as session:
            dataframe =  session.execute_read(get_treatments)
            # convert end date to 'Present' if it is null
            dataframe['End_Date'] = dataframe['End_Date'].apply(lambda x: 'Present' if pd.isnull(x) else x)

            return dataframe
    

    # get all experimental units that belong to a treatment
    # def get_all_expUnit(self, treatmentId):
    #     def get_expUnits(tx):
    #         cypher = """
    #         MATCH (treatment:Treatment {treatmentId: $treatmentId})-[:appliedInExpUnit]->(expUnit:ExperimentalUnit)
    #         RETURN 
    #             expUnit.expUnit_UID AS ID,
    #             expUnit.expUnitChangeInManagement AS description,
    #             expUnit.expUnitStartDate AS Start_Date,
    #             expUnit.expUnitEndDate AS End_Date
    #         ORDER BY expUnit.expUnitDescriptor ASC
    #         """
    #         parameters = {
    #             "treatmentId": treatmentId
    #         }

    #         result = tx.run(cypher, parameters)
    #         return result.to_df()
        
    #     with self.driver.session() as session:
    #         dataframe =  session.execute_read(get_expUnits)
    #         # convert end date to 'Present' if it is null
    #         dataframe['End_Date'] = dataframe['End_Date'].apply(lambda x: 'Present' if pd.isnull(x) else x)
    #         return dataframe
        
    # Get all treatments along with their attributes
    def get_all_treatments(self):
        def get_treatments(tx):
            cypher = """
            MATCH (t:Treatment)-[:hasRotation]-(r:Rotation)
                RETURN apoc.map.fromPairs([key IN keys(t) | [key, t[key]]]) AS properties, r.rotationDescriptor as rotation_crop
            """
            result = tx.run(cypher)
            data = []
            for record in result:
                record['properties']['coverCrop'] = record['rotation_crop']
                data.append(record['properties'])
            dataframe = pd.DataFrame(data)
            
            # Convert all nan and None values to 'unknown'
            dataframe.fillna('unknown', inplace=True)

            # Add numeric values for nitrogen treatment
            dataframe['numericNitrogen'] = dataframe['nitrogenTreatmentDescriptor'].apply(extract_numeric_value)

            # remove columns that are all 'unknown'
            dataframe = dataframe.loc[:, (dataframe != 'unknown').any(axis=0)]

            return dataframe
        
        with self.driver.session() as session:
            return session.execute_read(get_treatments)
    
    # Get all yeildNUtrientUptake for a treatment
    def get_all_expUnit(self, treatmentId):
        def get_nutrient_yield(tx):
            cypher = """
            MATCH (t:Treatment {treatmentId: $treatmentId})-[:yieldNutrUptakeTreatment]-(u:YieldNutrientUptake)
            RETURN u.expUnitId as id
            """
            parameters = {
                "treatmentId": treatmentId
            }

            result = tx.run(cypher, parameters)
            expUnits = [record['id'] for record in result]    
            return expUnits    
        with self.driver.session() as session:
            return session.execute_read(get_nutrient_yield)
