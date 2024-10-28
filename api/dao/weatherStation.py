import pandas as pd
class weatherStationDAO:
    def __init__(self, driver):
        self.driver = driver
    
    # get the unique ID of all experimental units
    def get_all_ids(self):

        def get_weather_station_id(tx):
            cypher = "MATCH (w:WeatherStation) return w as weather_stations"
            result = tx.run(cypher)
            return [record["weather_stations"]["weatherStationId"] for record in result]
        
        with self.driver.session() as session:
            return session.execute_read(get_weather_station_id)

    
    # get all relevant information of a weather station
    def get_weather_station_info(self, weatherStation_id):
    
        def get_weather_station_info(tx):
                cypher = """MATCH (u:WeatherStation {weatherStationId: $weatherStation_id})
                            WITH u, keys(u) AS keys
                            UNWIND keys AS key
                            RETURN key, apoc.map.get(u, key) AS property"""
                result = tx.run(cypher, weatherStation_id=weatherStation_id)
                return result.to_df()
            
        with self.driver.session() as session:
            return session.execute_read(get_weather_station_info)
    
    # get number of weather observations of a weather station
    def get_weather_observation(self, weatherStation_id):
        
        def get_weather_observation(tx):
            cypher = """MATCH (w:WeatherStation {weatherStationId: $weatherStation_id})-[:weatherRecordedBy]->(o:WeatherObservation)
                        RETURN apoc.map.fromPairs([key IN keys(o) | [key, o[key]]]) AS properties"""
            result = tx.run(cypher, weatherStation_id=weatherStation_id)
            data = [record["properties"] for record in result]
            dataframe = pd.DataFrame(data)
            # drop columns with all null values
            dataframe = dataframe.dropna(axis=1, how='all')
            # # drop columns with all zero values
            dataframe = dataframe.loc[:, (dataframe != 0).any(axis=0)]
            # drop rows with all null values
            dataframe = dataframe.dropna(axis=0, how='all')
            # fill null values with 'Not Available'
            dataframe = dataframe.fillna('Not Available')
            return dataframe

        with self.driver.session() as session:
            return session.execute_read(get_weather_observation)
    
    # get which field this weather station is associated with
    def get_field(self, weatherStation_id):
        
        def get_field_association(tx):
            cypher = """MATCH (w:WeatherStation {weatherStationId: $weatherStation_id})-[:recordsWeatherForField]->(f:Field)
                        RETURN f.fieldId as Field_Name"""
            result = tx.run(cypher, weatherStation_id=weatherStation_id)
            return result.to_df()
        
        with self.driver.session() as session:
            return session.execute_read(get_field_association)
    
    # get site information of a weather station
    def get_site(self, weatherStation_id):
        
        def get_site_info(tx):
            cypher = """MATCH (w:WeatherStation {weatherStationId: $weatherStation_id})-[:recordsWeatherForSite]->(s:Site)
                        RETURN s.siteId as Site_Name
                        """
            result = tx.run(cypher, weatherStation_id=weatherStation_id)
            return result.to_df()
        
        with self.driver.session() as session:
            return session.execute_read(get_site_info)
            
        