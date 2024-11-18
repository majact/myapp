# Import necessary libraries
import requests  # HTTP requests library
import pandas as pd  # Data manipulation library

# Define the URL for the feature layer containing street data
layer_url = "https://services3.arcgis.com/90zScd1lzl2oLYC1/arcgis/rest/services/RCL_AddressAssignment_gdb/FeatureServer/0/query"

# Query all data from the feature layer using the REST API
params = {
    "where": "1=1",  # Select all records
    "outFields": "*",  # Retrieve all fields
    "f": "json"  # Format the response as JSON
}

response = requests.get(layer_url, params=params)  # Send GET request
if response.status_code == 200:
    # Convert response to Pandas DataFrame
    features = response.json().get("features", [])
    existing_data = pd.DataFrame([feature["attributes"] for feature in features])
    print("Street data loaded successfully.")
else:
    print(f"Failed to load data. Status code: {response.status_code}")
