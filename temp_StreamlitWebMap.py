import streamlit as st
import folium
import requests
from streamlit_folium import st_folium
from shapely.geometry import shape

# AGOL Feature Layer REST URL
feature_layer_url = "https://services3.arcgis.com/90zScd1lzl2oLYC1/arcgis/rest/services/DirectionalPrefixZonest/FeatureServer/0/query"

# Function to query AGOL feature layer
def query_features(prefix):
    params = {
        "where": f"Prefix='{prefix}'",  # Dynamic filtering based on user input
        "outFields": "*",  # Retrieve all fields
        "f": "geojson",  # GeoJSON format for use with folium
        "returnGeometry": "true",  # Include geometry
    }
    response = requests.get(feature_layer_url, params=params)
    if response.status_code == 200:
        return response.json()  # Return GeoJSON for rendering
    else:
        st.error(f"Failed to query features: {response.status_code}")
        return None

# Streamlit App
st.title("Dynamic Map Viewer with Filtering")

# User Input for Prefix
prefix = st.text_input("Enter prefix to filter (e.g., 'SE')", value="SE")

# Query the features based on user input
geojson_data = query_features(prefix)

# Render the map with folium
if geojson_data and "features" in geojson_data and geojson_data["features"]:
    try:
        # Handle non-point geometries (e.g., polygons) by calculating the centroid
        first_geometry = geojson_data["features"][0]["geometry"]
        shapely_geometry = shape(first_geometry)
        centroid = shapely_geometry.centroid
        map_center = [centroid.y, centroid.x]

        # Create a folium map centered on the first feature's centroid
        m = folium.Map(location=map_center, zoom_start=12)

        # Add GeoJSON layer to map
        folium.GeoJson(
            geojson_data,
            name="Filtered Features",
            style_function=lambda x: {
                "fillColor": "red",
                "color": "red",
                "weight": 2,
                "fillOpacity": 0.5,
            },
        ).add_to(m)

        # Display the map in Streamlit
        st_folium(m, width=700, height=500)

    except Exception as e:
        st.error(f"An error occurred while processing geometries: {e}")
else:
    st.warning("No features found for the entered prefix.")
