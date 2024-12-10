import streamlit as st
import pandas as pd
import requests

# AGOL feature layer URL
api_url = "https://services3.arcgis.com/90zScd1lzl2oLYC1/arcgis/rest/services/RCL_AddressAssignment_gdb/FeatureServer/0/query"

# City search areas
city_search_areas = {
    "TIGARD": ["TIGARD", "HILLSBORO", "SHERWOOD"],
    "HILLSBORO": ["HILLSBORO", "CORNELIUS"],
    "SHERWOOD": ["SHERWOOD", "TUALATIN"]
}

# Streamlit interface
st.title("Proof of Concept: Filter and Check Name (AGOL Integration)")

# Dropdown for mailing city selection
selected_city = st.selectbox("Select your agency's mailing city:", options=list(city_search_areas.keys()))

# Input for proposed name
proposed_name = st.text_input("Enter the proposed street name:")

# Function to fetch data from AGOL feature layer
@st.cache
def fetch_data():
    params = {
        "where": "1=1",  # Retrieve all records
        "outFields": "LSt_Name,MSAGComm_L",  # Select relevant fields
        "f": "json",  # Format as JSON
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        features = response.json().get("features", [])
        return pd.DataFrame([feature["attributes"] for feature in features])
    else:
        st.error(f"Failed to load data from AGOL. Status code: {response.status_code}")
        return pd.DataFrame()  # Return empty DataFrame if the request fails

# Load data from AGOL
regional_data = fetch_data()

if st.button("Check Name"):
    if not proposed_name.strip():
        st.warning("Please enter a valid street name.")
    else:
        # Filter data for the selected city
        if not regional_data.empty and selected_city:
            search_cities = city_search_areas[selected_city]
            filtered_data = regional_data[regional_data["MSAGComm_L"].isin(search_cities)]

            # Debugging: Display filtered data
            st.write(f"Filtered Data (for {selected_city}):")
            st.write(filtered_data)

            # Check if proposed name exists in filtered data
            if proposed_name.upper() in filtered_data["LSt_Name"].values:
                st.success(f"The street name '{proposed_name}' already exists in the selected area.")
            else:
                st.info(f"The street name '{proposed_name}' is available in the selected area.")
        else:
            st.warning("No data to display. Check your dataset or city selection.")
