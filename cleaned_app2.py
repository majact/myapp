import requests
import pandas as pd
import streamlit as st

# URL for the public feature layer
layer_url = "https://services3.arcgis.com/90zScd1lzl2oLYC1/arcgis/rest/services/RCL_AddressAssignment_gdb/FeatureServer/0/query"

# Query parameters
params = {
    "where": "1=1",  # Select all records
    "outFields": "*",  # Get all fields
    "f": "json"       # Return data in JSON format
}

# Fetch data from the feature layer
try:
    response = requests.get(layer_url, params=params)
    response.raise_for_status()  # Raise an exception for HTTP errors
    data = response.json()

    # Convert features to a Pandas DataFrame
    features = data["features"]
    attributes = [feature["attributes"] for feature in features]
    existing_data = pd.DataFrame(attributes)

    st.success("Street data loaded successfully.")
    st.write(existing_data.head())  # Display a sample of the data

except requests.RequestException as e:
    st.error(f"Error fetching data: {e}")
