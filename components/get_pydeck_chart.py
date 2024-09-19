import pydeck as pdk
import streamlit as st

# Import Mapbox API from streamlit_secrets
MAPBOX_API_KEY = st.secrets["MAP_BOX_API"]

# A function to get the terrain tiles takes in latitude, longitude
def get_pydeck_chart(longitude, latitude):
    # AWS Open Data Terrain Tiles
    TERRAIN_IMAGE = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"

    # Define how to parse elevation tiles
    ELEVATION_DECODER = {"rScaler": 256, "gScaler": 1, "bScaler": 1 / 256, "offset": -32768}

    SURFACE_IMAGE = f"https://api.mapbox.com/v4/mapbox.satellite/{{z}}/{{x}}/{{y}}@2x.png?access_token={MAPBOX_API_KEY}"

    terrain_layer = pdk.Layer(
        "TerrainLayer", elevation_decoder=ELEVATION_DECODER, texture=SURFACE_IMAGE, elevation_data=TERRAIN_IMAGE
    )

    # Create a new layer for the pin point using IconLayer
    icon_data = [{
        "coordinates": [longitude, latitude],
        "icon_data": {
            "url": "https://img.icons8.com/color/48/000000/marker.png",
            "width": 128,
            "height": 50,
            "anchorY": 128
        }
    }]

    icon_layer = pdk.Layer(
        type="IconLayer",
        data=icon_data,
        get_icon="icon_data",
        get_size=4,
        size_scale=10,
        get_position="coordinates",
        pickable=True,
        auto_highlight=True
    )

    view_state = pdk.ViewState(latitude=latitude, longitude=longitude, zoom=11.5, bearing=0, pitch=60)
    
    # Include both terrain_layer and icon_layer in the Deck
    r = pdk.Deck(layers=[terrain_layer, icon_layer], initial_view_state=view_state)

    return r