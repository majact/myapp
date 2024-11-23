from streamlit_folium import st_folium
import streamlit as st
import folium
import requests

def render_disallowed_prefix_map(disallowed_prefixes, prefixzones_url):
    """
    Renders a Folium map with polygons matching the disallowed prefixes.

    Args:
        disallowed_prefixes (list): A collection of disallowed prefixes.
        prefixzones_url (str): The AGOL feature layer query URL.
    """
    # Debug: Print the incoming prefixes
    st.write(f"Prefixes to query: {disallowed_prefixes}")  # Debugging in Streamlit

    # Prepare a combined GeoJSON to hold all matching polygons
    combined_geojson = {"type": "FeatureCollection", "features": []}

    # Handle empty prefix list gracefully
    if not disallowed_prefixes:
        st.warning("No disallowed prefixes provided.")
        return

    # Construct the SQL `OR` clause
    where_clause = " OR ".join([f"Prefix='{prefix}'" for prefix in disallowed_prefixes])

    # Prepare query parameters
    params = {
        "where": where_clause,
        "outFields": "*",
        "f": "geojson",
        "returnGeometry": "true",
    }

    # Perform the API request
    response = requests.get(prefixzones_url, params=params)

    # Debug: Log the query URL and response status
    st.write(f"Query URL: {response.url}")  # Debugging query
    if response.status_code == 200:
        geojson_data = response.json()
        if "features" in geojson_data:
            combined_geojson["features"].extend(geojson_data["features"])
            st.write(f"Combined GeoJSON: {combined_geojson}")  # Debugging GeoJSON
    else:
        st.error(f"API request failed with status code {response.status_code}")
        return

    # Check if any polygons were found
    if combined_geojson["features"]:
        # Center map on the first polygon's centroid
        first_geometry = combined_geojson["features"][0]["geometry"]
        shapely_geometry = shape(first_geometry)
        centroid = shapely_geometry.centroid
        map_center = [centroid.y, centroid.x]

        # Create a Folium map centered on the centroid
        m = folium.Map(location=map_center, zoom_start=12)

        # Add the GeoJSON layer to the map
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

        # Display the map in Streamlit
        st_folium(m, width=700, height=500)
    else:
        st.warning("No polygons found for the disallowed prefixes.")
