from shapely.geometry import shape
import folium
from streamlit_folium import st_folium

# Function to query AGOL feature layer for polygons matching disallowed prefixes
def query_features_by_prefix(prefix):
    params = {
        "where": f"Prefix='{prefix}'",  # Query dynamically based on prefix
        "outFields": "*",
        "f": "geojson",  # Return GeoJSON format for folium
        "returnGeometry": "true",
    }
    response = requests.get(api_url, params=params)  # Use the existing `api_url` variable
    if response.status_code == 200:
        return response.json()  # Return GeoJSON data
    else:
        st.error(f"Failed to query features for prefix '{prefix}': {response.status_code}")
        return None

# Function to dynamically render a map with disallowed prefix polygons
def render_disallowed_prefix_map(disallowed_prefixes):
    combined_geojson = {"type": "FeatureCollection", "features": []}
    for prefix in disallowed_prefixes:
        geojson_data = query_features_by_prefix(prefix)
        if geojson_data and "features" in geojson_data:
            combined_geojson["features"].extend(geojson_data["features"])

    if combined_geojson["features"]:
        # Use the centroid of the first feature for map centering
        first_geometry = combined_geojson["features"][0]["geometry"]
        shapely_geometry = shape(first_geometry)
        centroid = shapely_geometry.centroid
        map_center = [centroid.y, centroid.x]

        # Create a folium map
        m = folium.Map(location=map_center, zoom_start=12)

        # Add GeoJSON layer to map
        folium.GeoJson(
            combined_geojson,
            name="Disallowed Features",
            style_function=lambda x: {
                "fillColor": "red",
                "color": "red",
                "weight": 2,
                "fillOpacity": 0.5,
            },
        ).add_to(m)

        # Display the map
        st_folium(m, width=700, height=500)
    else:
        st.warning("No disallowed prefixes found on the map.")
