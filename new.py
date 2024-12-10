import streamlit as st
import pandas as pd
import requests

# AGOL feature layer URL
api_url = "https://services3.arcgis.com/90zScd1lzl2oLYC1/arcgis/rest/services/RCL_AddressAssignment_gdb/FeatureServer/0/query"

# Define community groups
community_groups = {
    "TIGARD": ["TIGARD", "SHERWOOD", "TUALATIN"],
    "HILLSBORO": ["HILLSBORO"],
    "FOREST GROVE": ["FOREST GROVE"],
}

# Streamlit UI
st.title("Community-Based Street Name Checker")

# Dropdown for community selection
selected_community = st.selectbox("Select your community:", options=list(community_groups.keys()))

# Input for proposed name
proposed_name = st.text_input("Enter the proposed street name:")

# Fetch data from AGOL
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

# Load the full dataset once
regional_data = fetch_data()

if not regional_data.empty:
    st.write(f"Loaded {len(regional_data)} total records from AGOL.")  # Debugging: Total dataset size

    # Filter data dynamically based on the selected community
    allowed_communities = community_groups[selected_community]
    filtered_data = regional_data[regional_data["MSAGComm_L"].isin(allowed_communities)]

    st.write(f"Filtered {len(filtered_data)} records for communities: {', '.join(allowed_communities)}")  # Debugging: Filtered size
    st.write(filtered_data.head())  # Show a sample of filtered records for verification

    if st.button("Check Name"):
        if not proposed_name.strip():
            st.warning("Please enter a valid street name.")
        else:
            # Check if the proposed name exists in the filtered data
            if proposed_name.upper() in filtered_data["LSt_Name"].values:
                st.success(f"The street name '{proposed_name}' already exists in the selected area.")
            else:
                st.info(f"The street name '{proposed_name}' is available in the selected area.")
else:
    st.error("Failed to load any data. Please check your AGOL layer or connection.")
