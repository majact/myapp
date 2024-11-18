import streamlit as st
from arcgis.gis import GIS  # ArcGIS API for Python
from arcgis.features import FeatureLayer  # FeatureLayer class
import pandas as pd  # Data manipulation library
import re  # Regular expressions for validation

# Initialize GIS for public access
gis = GIS()  # Anonymous access for public feature layers

# Define the URL for the feature layer containing street data
layer_url = "https://services3.arcgis.com/90zScd1lzl2oLYC1/arcgis/rest/services/RCL_AddressAssignment_gdb/FeatureServer/0"
layer = FeatureLayer(layer_url)

# Query all data from the feature layer and load it into a Pandas DataFrame
try:
    features = layer.query(where="1=1", out_fields="*").features
    existing_data = pd.DataFrame([f.attributes for f in features])
    st.success("Street data loaded successfully.")
except Exception as e:
    st.error(f"Error loading feature layer: {e}")
    st.stop()

# Disallowed names and criteria
business_names = []
city_names = ['BEAVERTON', 'TIGARD']
county_names = ['MALHEUR']
arterial_names = [
    "ALLEN", "APIARY", "BALD PEAK", "BARNES", "BASELINE", "BEECH", "CANYON", "DAVIS", "DIVISION",
    "EVERGREEN", "FARMINGTON", "GRAND", "GREENBURG", "HALL", "HALSEY", "HAWTHORNE", "INTERSTATE",
    "JACKSON", "JOHNSON CREEK", "LOMBARD", "MACADAM", "MAIN", "MURRAY", "PACIFIC", "POWELL",
    "RIVER", "STARK", "SUNNYSIDE", "TACOMA", "TAYLORS", "WALKER", "WOODSTOCK", "ZION"
]
banned_name_starts = ["HILL", "BEAVER", "CEDAR", "MAPLE", "OAK", "MAIN", "MT", "PACIFIC", "ST ", "WALNUT"]


# Function to check if a name is disallowed
def is_disallowed_name(proposed_name):
    proposed_name = proposed_name.upper()
    if proposed_name in business_names:
        return f"'{proposed_name}' is disallowed because it is a business name."
    if proposed_name in city_names:
        return f"'{proposed_name}' is disallowed because it is a city name."
    if proposed_name in county_names:
        return f"'{proposed_name}' is disallowed because it is a county name."
    if proposed_name in arterial_names:
        return f"'{proposed_name}' is disallowed because it is a major arterial road."
    for start in banned_name_starts:
        if proposed_name.startswith(start):
            return f"'{proposed_name}' is disallowed because it starts with '{start}'."
    return None


# User interface
st.title("Street Name Validation App")
st.write("Validate a proposed street name against naming conventions and conflicts.")

# Input form for street name
proposed_name = st.text_input("Enter the proposed street name:", "").strip()

if st.button("Validate"):
    if not proposed_name:
        st.warning("Please enter a street name to validate.")
    else:
        # Check disallowed names
        disallowed_reason = is_disallowed_name(proposed_name)
        if disallowed_reason:
            st.error(disallowed_reason)
        else:
            st.success(f"The proposed name '{proposed_name}' meets all naming criteria.")

            # Check for conflicts with existing data
            conflicts = existing_data[existing_data['LSt_Name'].str.upper() == proposed_name.upper()]
            if not conflicts.empty:
                st.warning(f"The name '{proposed_name}' is already assigned in the following records:")
                st.dataframe(conflicts)
            else:
                st.success(f"The name '{proposed_name}' is unique and has no conflicts in the existing data.")
