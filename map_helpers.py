from streamlit_folium import st_folium
import folium

def render_disallowed_prefix_map(disallowed_prefixes, api_url):
    """
    Renders a Folium map with polygons matching the disallowed prefixes.

    Args:
        disallowed_prefixes (list or set): A collection of disallowed prefixes.
        api_url (str): The AGOL feature layer URL.
    """
    # Prepare a combined GeoJSON to hold all matching polygons
    combined_geojson = {"type": "FeatureCollection", "features": []}

    # Query for each disallowed prefix
    for prefix in disallowed_prefixes:
        params = {
            "where": f"Prefix='{prefix}'",  # Filter by the current prefix
            "outFields": "*",
            "f": "geojson",
            "returnGeometry": "true",
        }
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            geojson_data = response.json()
            if "features" in geojson_data:
                combined_geojson["features"].extend(geojson_data["features"])
        else:
            st.error(f"Failed to query prefix '{prefix}': {response.status_code}")

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
