from streamlit_folium import st_folium
import streamlit as st
import folium
import requests
prefixzones_url = "https://services3.arcgis.com/90zScd1lzl2oLYC1/arcgis/rest/services/DirectionalPrefixZonest/FeatureServer/0/query"

def render_disallowed_prefix_map(disallowed_prefixes, prefixzones_url):
    """
    Renders a Folium map with polygons matching the disallowed prefixes.

    Args:
        disallowed_prefixes (list): A collection of disallowed prefixes.
        prefixzones_url (str): The AGOL feature layer query URL.
    """
    st.write(f"Prefixes to query: {disallowed_prefixes}")  # Debugging prefixes

    combined_geojson = {"type": "FeatureCollection", "features": []}

    if not disallowed_prefixes:
        st.warning("No disallowed prefixes provided.")
        return

    where_clause = " OR ".join([f"Prefix='{prefix}'" for prefix in disallowed_prefixes])
    # where_clause = " OR ".join([f"Prefix='{prefix.strip()}'" for prefix in disallowed_prefixes])

    params = {
        "where": where_clause,
        "outFields": "*",
        "f": "geojson",
        "returnGeometry": "true",
    }

    # Perform the API request
    response = requests.get(prefixzones_url, params=params)

    # Debugging statements to validate the query and response
    st.write(f"Query URL: {response.url}")  # Shows the full query URL
    st.write(f"Response Status Code: {response.status_code}")  # Confirms if the request was successful

    if response.status_code == 200:
        geojson_data = response.json()
        st.write(f"GeoJSON Data: {geojson_data}")  # Displays the full GeoJSON response
        if "features" in geojson_data:
            combined_geojson["features"].extend(geojson_data["features"])
            st.write(f"Combined Features: {combined_geojson['features']}")  # Displays the combined features
        else:
            st.warning("No features found in the GeoJSON response.")
            return
    else:
        st.error(f"Query failed with status code {response.status_code}.")
        return

    if not combined_geojson["features"]:
        st.warning("No polygons found to render.")
        return
    else:
        st.write(f"Features to Render: {combined_geojson['features']}")

    first_geometry = combined_geojson["features"][0]["geometry"]
    shapely_geometry = shape(first_geometry)
    centroid = shapely_geometry.centroid
    map_center = [centroid.y, centroid.x]

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
