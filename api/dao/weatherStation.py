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
            cypher = """MATCH (w:WeatherStation {weatherStationId: $weatherStation_id})
                        RETURN
                            w.weatherStationLatitude_decimal_deg as Latitude,
                            w.weatherStationLongitude_decimal_deg as Longitude,
                            w.weatherStationStartDate as Start_Date,
                            w.weatherStationDirectionFromField_m as Direction_From_Field,
                            w.weatherStationDistanceFromField as Distance_From_Field
                        """
            result = tx.run(cypher, weatherStation_id=weatherStation_id)
            return result.to_df()
        
        with self.driver.session() as session:
            return session.execute_read(get_weather_station_info)
    
    # get number of weather observations of a weather station
    def get_weather_observation(self, weatherStation_id):
        
        def get_weather_observation(tx):
            cypher = """MATCH (w:WeatherStation {weatherStationId: $weatherStation_id})-[:recordsWeatherForField]-(f:Field)-[:weatherAtField]-(o:WeatherObservation)
                        RETURN
                            o.openPanEvaporation as Open_Pan_Evaporation,
                            o.precipitation as Precipitation,
                            o.relativeHumidityPercent as Relative_Humidity_Percent,
                            o.soilTemp10cm as Soil_Temperature_10cm,
                            o.soilTemp5cm as Soil_Temperature_5cm,
                            o.solarRadiationBareSoil as Solar_Radiation_Bare_Soil,
                            o.tempMax as Max_Temperature,
                            o.tempMin as Min_Temperature,
                            o.weatherObservationDate as Date,
                            o.windSpeed as Wind_Speed
                        ORDER BY o.weatherObservationDate ASC"""
            result = tx.run(cypher, weatherStation_id=weatherStation_id)
            return result.to_df()

        with self.driver.session() as session:
            result = session.execute_read(get_weather_observation)

            return result
    
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
            
        