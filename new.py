import streamlit as st
import pandas as pd

# Example dataset
data = {
    "LSt_Name": ["MAIN", "PINE", "OAK", "MAIN", "PINE", "CEDAR"],
    "MSAGComm_L": ["TIGARD", "HILLSBORO", "SHERWOOD", "CORNELIUS", "TUALATIN", "TIGARD"]
}
regional_data = pd.DataFrame(data)

# City search areas
city_search_areas = {
    "TIGARD": ["TIGARD", "HILLSBORO", "SHERWOOD"],
    "HILLSBORO": ["HILLSBORO", "CORNELIUS"],
    "SHERWOOD": ["SHERWOOD", "TUALATIN"]
}

# Streamlit interface
st.title("Proof of Concept: Filter and Check Name")

# Dropdown for mailing city selection
selected_city = st.selectbox("Select your agency's mailing city:", options=list(city_search_areas.keys()))

# Input for proposed name
proposed_name = st.text_input("Enter the proposed street name:")

if st.button("Check Name"):
    if not proposed_name.strip():
        st.warning("Please enter a valid street name.")
    else:
        # Filter data for the selected city
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
