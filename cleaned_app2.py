import streamlit as st
import requests
import pandas as pd

# Streamlit App Title
st.title("Street Data Viewer with Filters")

# URL for the public feature layer
layer_url = "https://services3.arcgis.com/90zScd1lzl2oLYC1/arcgis/rest/services/RCL_AddressAssignment_gdb/FeatureServer/0/query"

# Query parameters
params = {
    "where": "1=1",  # Select all records
    "outFields": "*",  # Get all fields
    "f": "json"       # Return data in JSON format
}

# Fetch data function
@st.cache_data
def fetch_street_data():
    try:
        response = requests.get(layer_url, params=params)
        response.raise_for_status()
        data = response.json()
        if "features" in data:
            features = data["features"]
            attributes = [feature["attributes"] for feature in features]
            return pd.DataFrame(attributes)
        else:
            st.warning("No features found.")
            return pd.DataFrame()
    except requests.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# Load the data
st.write("Fetching street data...")
street_data = fetch_street_data()

if not street_data.empty:
    st.success(f"Fetched {len(street_data)} records successfully!")

    # Add city name filter
    unique_cities = street_data['MSAGComm_L'].dropna().unique()
    selected_city = st.selectbox("Filter by City", options=["All"] + sorted(unique_cities.tolist()))

    # Add street name search
    search_query = st.text_input("Search for a Street Name", "").strip().upper()

    # Apply filters
    filtered_data = street_data.copy()

    if selected_city != "All":
        filtered_data = filtered_data[filtered_data['MSAGComm_L'] == selected_city]

    if search_query:
        filtered_data = filtered_data[filtered_data['LSt_Name'].str.upper().str.contains(search_query, na=False)]

    # Display filtered results
    if not filtered_data.empty:
        st.write(f"Showing {len(filtered_data)} records:")
        st.dataframe(filtered_data)
    else:
        st.warning("No records match your filters.")
else:
    st.warning("No data available.")
