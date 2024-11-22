import streamlit as st

# Streamlit app title
st.title("Dynamic AGOL Map Viewer with Filtering")

# User input for prefix
prefix = st.text_input("Enter prefix to filter (e.g., 'SE')", value="SE")

# Construct the dynamic Web App URL with 'where' clause
web_app_url = f"https://majcs.maps.arcgis.com/apps/mapviewer/index.html?webmap=fcc64d756cc24d2eb48f2337bf8ac6d8&where=Prefix='{prefix}'"

# Embed the filtered Web Map in Streamlit
st.components.v1.html(
    f'<iframe src="{web_app_url}" width="100%" height="600" frameborder="0"></iframe>',
    height=600,
)
