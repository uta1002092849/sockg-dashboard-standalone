import pandas as pd
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
    def get_all_expUnit(self, treatmentId):
        def get_expUnits(tx):
            cypher = """
            MATCH (treatment:Treatment {treatmentId: $treatmentId})-[:appliedInExpUnit]->(expUnit:ExperimentalUnit)
            RETURN 
                expUnit.expUnit_UID AS ID,
                expUnit.expUnitChangeInManagement AS description,
                expUnit.expUnitStartDate AS Start_Date,
                expUnit.expUnitEndDate AS End_Date
            ORDER BY expUnit.expUnitDescriptor ASC
            """
            parameters = {
                "treatmentId": treatmentId
            }

            result = tx.run(cypher, parameters)
            return result.to_df()
        
        with self.driver.session() as session:
            dataframe =  session.execute_read(get_expUnits)
            # convert end date to 'Present' if it is null
            dataframe['End_Date'] = dataframe['End_Date'].apply(lambda x: 'Present' if pd.isnull(x) else x)
            return dataframe