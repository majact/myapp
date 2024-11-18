import streamlit as st
import requests

# Streamlit App Title
st.title("Test App: Fetching Feature Layer Data")

# URL for the public feature layer
layer_url = "https://services3.arcgis.com/90zScd1lzl2oLYC1/arcgis/rest/services/RCL_AddressAssignment_gdb/FeatureServer/0/query"

# Query parameters
params = {
    "where": "1=1",  # Select all records
    "outFields": "*",  # Get all fields
    "f": "json"       # Return data in JSON format
}

# Button to trigger data fetch
if st.button("Fetch Data"):
    try:
        # Fetch data from the feature layer
        response = requests.get(layer_url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Show success message
        st.success("Data fetched successfully!")
        
        # Parse and display a portion of the data
        data = response.json()
        if "features" in data:
            st.write(f"Number of records fetched: {len(data['features'])}")
            # Display the first record as an example
            st.json(data["features"][0])
        else:
            st.warning("No features found in the response.")

    except requests.RequestException as e:
        st.error(f"Error fetching data: {e}")
