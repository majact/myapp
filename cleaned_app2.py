import streamlit as st
import requests
import pandas as pd
import re

# Streamlit App Title
st.title("Street Name Validation Tool")

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

# Helper functions for name validation
banned_name_starts = ["HILL", "BEAVER", "CEDAR", "MAPLE", "OAK", "MAIN", "MT", "PACIFIC", "WALNUT"]
arterial_names = [
    "ALLEN", "APIARY", "BALD PEAK", "BARBUR", "BARNES", "BASELINE", "BEAVERCREEK", "BEEF BEND",
    "BELMONT", "BERTHA", "BONITA", "BURNSIDE", "CANYON", "CAPITOL", "CORNELIUS", "CORNELL", "FARMINGTON",
    "HAWTHORNE", "INTERSTATE", "JACKSON", "MACADAM", "MAIN", "MURRAY", "PACIFIC", "POWELL", "STARK"
]

def is_disallowed_name(proposed_name):
    proposed_name = proposed_name.upper()
    if proposed_name in arterial_names:
        return f"'{proposed_name}' is disallowed because it is a major arterial road."
    for start in banned_name_starts:
        if proposed_name.startswith(start):
            return f"'{proposed_name}' is disallowed because it starts with '{start}'."
    return None

def detect_conflicts(proposed_name, data):
    conflicts = data[data['LSt_Name'].str.upper() == proposed_name.upper()]
    return conflicts

# Fetch the data
st.write("Fetching street data...")
street_data = fetch_street_data()

if not street_data.empty:
    st.success(f"Fetched {len(street_data)} records successfully!")

    # Input form for proposed street name
    proposed_name = st.text_input("Enter the proposed street name:", "").strip()

    if st.button("Validate"):
        if not proposed_name:
            st.warning("Please enter a street name.")
        else:
            # Check for disallowed names
            disallowed_reason = is_disallowed_name(proposed_name)
            if disallowed_reason:
                st.error(disallowed_reason)
            else:
                st.success(f"The proposed name '{proposed_name}' meets basic naming criteria.")
                
                # Check for conflicts in existing data
                conflicts = detect_conflicts(proposed_name, street_data)
                if not conflicts.empty:
                    st.warning(f"The name '{proposed_name}' conflicts with existing assignments:")
                    st.dataframe(conflicts)
                else:
                    st.success(f"The name '{proposed_name}' is unique and has no conflicts.")
