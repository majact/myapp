import streamlit as st
import requests

# Input for Prefix value
prefix = st.text_input("Enter Prefix to query (e.g., 'SE')", value="SE")

# Construct the query URL
query_url = "https://services3.arcgis.com/90zScd1lzl2oLYC1/arcgis/rest/services/DirectionalPrefixZonest/FeatureServer/0/query"
params = {
    "where": f"Prefix='{prefix}'",
    "outFields": "*",
    "f": "json"
}

# Query the feature layer
response = requests.get(query_url, params=params)

# Display results
if response.status_code == 200:
    data = response.json()
    if data.get("features"):
        st.write(f"Features matching Prefix='{prefix}':", data["features"])
    else:
        st.write(f"No features found for Prefix='{prefix}'.")
else:
    st.error(f"Error querying feature layer: {response.status_code}")
