from shapely.geometry import shape

# Render the map with folium
if geojson_data and "features" in geojson_data and geojson_data["features"]:
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
else:
    st.warning("No features found for the entered prefix.")
