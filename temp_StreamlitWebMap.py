import streamlit as st

# Streamlit app title
st.title("Dynamic AGOL Web Map Test")

# Input for the disallowed prefix
prefix = st.text_input("Enter disallowed prefix (e.g., 'NW')", value="NW")

# AGOL Web Map URL with dynamic 'where' clause for the prefix filter
web_map_url = f"https://majcs.maps.arcgis.com/apps/mapviewer/index.html?webmap=fcc64d756cc24d2eb48f2337bf8ac6d8&where=Prefix='{prefix}'"

# Display the dynamic Web Map in an iframe
st.components.v1.html(
    f'<iframe src="{web_map_url}" width="100%" height="600" frameborder="0"></iframe>',
    height=600,
)
