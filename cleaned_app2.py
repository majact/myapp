import streamlit as st
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import pandas as pd

# Initialize GIS
gis = GIS()  # Anonymous access for public feature layers

# Feature layer URL
layer_url = "https://services3.arcgis.com/90zScd1lzl2oLYC1/arcgis/rest/services/RCL_AddressAssignment_gdb/FeatureServer/0"
layer = FeatureLayer(layer_url)

# Fetch data
try:
    features = layer.query(where="1=1", out_fields="*").features
    data = pd.DataFrame([f.attributes for f in features])
    st.write("Feature Layer Data:")
    st.dataframe(data)
except Exception as e:
    st.error(f"Failed to load feature layer: {e}")
