import streamlit as st

# Set Streamlit app title
st.title("AGOL Web Map Display in Streamlit")

# Define the URL for your AGOL Web Map or Web App
web_map_url = "https://majcs.maps.arcgis.com/apps/mapviewer/index.html?webmap=fcc64d756cc24d2eb48f2337bf8ac6d8"

# Embed the Web Map using an iframe
st.components.v1.html(
    f'<iframe src="{web_map_url}" width="100%" height="600" frameborder="0"></iframe>',
    height=600,
)
