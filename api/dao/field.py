import pandas as pd

class FieldDAO:

    def __init__(self, driver):
        self.driver = driver
    
    # get the unique ID of all experimental units
    def get_all_ids(self):
        # transaction function
        def get_fiel_ids(tx):
            cypher = "MATCH (f:Field) RETURN f as field"
            result = tx.run(cypher)
            return [record["field"]['fieldId'] for record in result]
        
        # execute transaction
        with self.driver.session() as session:
            return session.execute_read(get_fiel_ids)
    
    
    # get latitude and longitude of a field
    def get_lat_long_dataframe(self, field_id):
        # transaction function
        def get_lat_long(tx):
            cypher = "MATCH (f:Field {fieldId: $field_id}) RETURN f.latitude_decimal_deg as latitude, f.longitude_decimal_deg as longitude"
            result = tx.run(cypher, field_id=field_id)
            return result.single()
        
        # execute transaction
        with self.driver.session() as session:
            result = session.execute_read(get_lat_long)
            longtitue = result['longitude']
            latitude = result['latitude']
            df = pd.DataFrame({
                'latitude': [latitude],
                'longitude': [longtitue]
            })
            return df
    
    # get rainfall data of a field
    def get_rainfall_df(self, field_id):

        # transaction function
        def get_rainfall(tx):
            cypher = """MATCH (f:Field {fieldId: $field_id})<-[:weatherAtField]-(w:WeatherObservation)
                        WITH w.date AS date, w.precipitation_mm_per_d AS precipitation
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
                        ORDER BY period ASC"""
            result = tx.run(cypher, field_id=field_id)
            date = []
            precipitation = []
            
            for record in result:
                date.append(record['period'])
                precipitation.append(record['totalPrecipitation'])
            return date, precipitation
        
        # execute transaction
        with self.driver.session() as session:
            date, precipitation = session.execute_read(get_rainfall)
            df = pd.DataFrame({
                'Period': date,
                'TotalPrecipitation': precipitation
            })
            return df
            
    # get all experimental units in a field
    def get_all_experimental_unit(self, field_id):
        # transaction function
        def get_exp_units(tx):
            cypher = """MATCH (f:Field {fieldId: $field_id})<-[:locatedInField]-(u:ExperimentalUnit)
                        RETURN
                            u.expUnitId as id,
                            u.startDate as Start_Date,
                            u.endDate as End_Date,
                            u.expUnitSize as Size
                        ORDER BY u.expUnitStartDate"""
            result = tx.run(cypher, field_id=field_id)
            return result.to_df()
        # execute transaction
        with self.driver.session() as session:
            return session.execute_read(get_exp_units)
    
    
    # get all publications related to a field
    def get_publications(self, field_id):
        # transaction function
        def get_publications(tx):
            cypher = """MATCH (f:Field {fieldId: $field_id})<-[:hasField]-(s:Site)<-[:studiesSite]-(p:Publication)
                RETURN p.title as Title,
                p.author as Author,
                p.correspondingAuthor as Corresponding_Author,
                p.identifier as Reference,
                p.citation as Citation
                """
            result = tx.run(cypher, field_id=field_id)
            return result.to_df()
        # execute transaction
        with self.driver.session() as session:
            return session.execute_read(get_publications)
    
    # get soil description of a field
    def get_soil_description(self, field_id):
        # transaction function
        def get_soil_description(tx):
            cypher = """MATCH (f:Field {fieldId: $field_id})<-[:appliedInField]-(s:Soil) RETURN s.soilSeries as Soil_Series"""
            result = tx.run(cypher, field_id=field_id)
            return result.single()
        
        # execute transaction
        with self.driver.session() as session:
            result = session.execute_read(get_soil_description)
            soil_series = result['Soil_Series']
            return soil_series
    
    # get some extra information of a field from site
    def get_field_info(self, field_id):
        # transaction function
        def get_field_info(tx):
            cypher = """MATCH (f:Field {fieldId: $field_id})<-[:hasField]-(s:Site)
                        WITH s, keys(s) AS keys
                            UNWIND keys AS key
                            RETURN key, apoc.map.get(s, key) AS property
                    """
            result = tx.run(cypher, field_id=field_id)
            return result.to_df()
        
        # execute transaction
        with self.driver.session() as session:
            return session.execute_read(get_field_info)
    
    
    # get weather station information of a field
    def get_weather_station(self, field_id):
        # transaction function
        def get_weather_station(tx):
            cypher = """MATCH (f:Field {fieldId: $field_id})<-[:recordsWeatherForField]-(w:WeatherStation)
                        RETURN w.weatherStationId as Weather_Station_ID"""
            result = tx.run(cypher, field_id=field_id)
            return result.to_df()
        
        # execute transaction
        with self.driver.session() as session:
            return session.execute_read(get_weather_station)
