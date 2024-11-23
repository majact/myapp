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
        prefixzones_url (str): The AGOL feature layer URL.
    """
    st.write(f"Prefixes to query: {disallowed_prefixes}")  # Debug

    # Check if prefixes are unchanged; if so, reuse the existing map data
    if st.session_state.last_prefixes == disallowed_prefixes:
        st.info("Using cached GeoJSON data.")
    else:
        # Update session state with the new prefixes
        st.session_state.last_prefixes = disallowed_prefixes

        # Prepare a combined GeoJSON for new query results
        combined_geojson = {"type": "FeatureCollection", "features": []}

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

        if response.status_code == 200:
            geojson_data = response.json()
            if "features" in geojson_data:
                combined_geojson["features"].extend(geojson_data["features"])
                st.session_state.combined_geojson = combined_geojson  # Cache the result
                st.write(f"Combined GeoJSON: {combined_geojson}")
        else:
            st.error(f"API request failed with status code {response.status_code}")
            return

    # Use the cached GeoJSON data
    combined_geojson = st.session_state.combined_geojson

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
