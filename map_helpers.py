from streamlit_folium import st_folium
import streamlit as st
import folium
import requests
from shapely.geometry import shape

def render_disallowed_prefix_map(disallowed_prefixes, prefixzones_url):
    """
    Renders a Folium map with polygons matching the disallowed prefixes.

    Args:
        disallowed_prefixes (list): A collection of disallowed prefixes.
        prefixzones_url (str): The AGOL feature layer query URL.
    """
    st.write(f"Disallowed Prefixes: {disallowed_prefixes}")  # Debug: Ensure prefixes are correct

    # Handle empty prefix list
    if not disallowed_prefixes:
        st.warning("No disallowed prefixes provided. Nothing to render.")
        return

    # Construct the WHERE clause
    where_clause = " OR ".join([f"Prefix='{prefix}'" for prefix in disallowed_prefixes])

    # API query parameters
    params = {
        "where": where_clause,
        "outFields": "*",
        "f": "geojson",
        "returnGeometry": "true",
    }

    # Perform the API request
    st.write("Querying the feature layer...")  # Debugging
    response = requests.get(prefixzones_url, params=params)

    # Check for API request success
    if response.status_code != 200:
        st.error(f"API request failed with status code {response.status_code}.")
        return

    # Parse the response
    geojson_data = response.json()
    st.write(f"API Response Received: {geojson_data}")  # Debug: Show raw response

    # Extract features
    features = geojson_data.get("features", [])
    if not features:
        st.warning("No matching polygons found for the disallowed prefixes.")
        return

    # Combine features into a single GeoJSON object
    combined_geojson = {"type": "FeatureCollection", "features": features}
    st.write(f"Combined GeoJSON Features: {combined_geojson['features']}")  # Debug

    # Determine the map center (centroid of the first polygon)
    first_geometry = features[0]["geometry"]
    shapely_geometry = shape(first_geometry)
    centroid = shapely_geometry.centroid
    map_center = [centroid.y, centroid.x]

    # Create and render the map
    m = folium.Map(location=map_center, zoom_start=12)

    folium.GeoJson(
        combined_geojson,
        name="Disallowed Prefixes",
        style_function=lambda x: {
            "fillColor": "red",
            "color": "red",
            "weight": 2,
            "fillOpacity": 0.5,
        },
    ).add_to(m)

    st_folium(m, width=700, height=500)


# Example test usage
if __name__ == "__main__":
    st.title("Disallowed Prefix Map")

    # Example disallowed prefixes
    disallowed_prefixes = ['NW', 'SE', 'SW']
    prefixzones_url = "https://services3.arcgis.com/90zScd1lzl2oLYC1/arcgis/rest/services/DirectionalPrefixZonest/FeatureServer/0/query"

    render_disallowed_prefix_map(disallowed_prefixes, prefixzones_url)
