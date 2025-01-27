import requests
import pandas as pd
import json
import io  # Import the io module for StringIO
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import re
import plotly.figure_factory as ff
import time


##### page config starts here
st.set_page_config(page_title="Toronto Signature Sites", page_icon="🌟", layout="wide")

st.title("Toronto Signature Sites")

st.write("Visualization using Streamlit")
##### page config ends here

###### side bar starts here
with st.sidebar:
   st.header("About the Dataset")
   st.markdown('''
   This dataset showcases a curated selection of significant industrial and commercial properties available for sale or lease in Toronto. 
   
   The dataset has been published by Economic Development & Culture.
   
   Link to the dataset: https://open.toronto.ca/dataset/toronto-signature-sites/

   ''')

###### side bar ends here

###### Feteching data from API starts here
with st.spinner("Fetching data through API ..."):
   # Base URL for the Toronto Open Data CKAN API
   base_url = "https://ckan0.cf.opendata.inter.prod-toronto.ca"

   # API endpoint to retrieve package metadata
   url = base_url + "/api/3/action/package_show"
   params = {"id": "toronto-signature-sites"}

   # Retrieve package metadata
   response = requests.get(url, params=params)
   package = response.json()

   # Dictionary to store resource data
   resources_data = {}

   # Loop through the resources in the package
   for idx, resource in enumerate(package["result"]["resources"]):
      # Check if the resource is active and has a datastore
      if resource["datastore_active"]:
         print(f"Retrieving data for resource: {resource['name']} (ID: {resource['id']})")

         # Get the data in CSV format
         resource_url = base_url + "/datastore/dump/" + resource["id"]
         resource_dump_data = requests.get(resource_url).content.decode("utf-8")

         # Convert CSV data to a DataFrame using io.StringIO
         df = pd.read_csv(io.StringIO(resource_dump_data))



         # Store the DataFrame in the dictionary
         resources_data[resource["name"]] = df

###### Feteching data from API ends here

##### KPIs starts here
coli,colii,coliii,coliv = st.columns(4)
with coli:
   # Define card content using HTML and inline CSS
   card_html = f"""
   <div style="
      border: 1px solid #ddd; 
      border-radius: 0.25rem; 
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); 
      padding: 1.5rem; 
      margin: 1rem 0; 
      background-color: #fff;">
      <p style="margin-top: 0; color: #555;">Total available sites:</p>
      <h4 style="margin-bottom: 1rem; color: #007bff;">
         {df["objectid"].count()}
      </h4>
   </div>
   """

   # Render the card in Streamlit
   st.markdown(card_html, unsafe_allow_html=True)

##### KPIs ends here

##### First level container starts here

#### map data wrangling starts here
df["coordinates"] = df["geometry"].apply(lambda x: json.loads(x)["coordinates"])

df[["longitude","latitude"]] = pd.DataFrame(df["coordinates"].tolist(), index=df.index)
#### map data wrangling ends here

#### grouping by district starts here

df_district = df.groupby("district",)["site_name"].count().reset_index()

df_district.columns = ["District","Number of Sites"]
#### grouping by district ends here


#### grouping by property_type_primary starts here
df_property = df.groupby("property_type_primary",)["site_name"].count().reset_index()
df_property.columns = ["Property Type","Number of Sites"]
#### grouping by property_type_primary ends here

col1, col2 = st.columns(2)
#### map Visualization 
with col1:
   st.map(df[["longitude","latitude"]])

with col2:

   #### for pie chart
   fig = px.pie(
    df_district,
    names="District",
    values="Number of Sites",
    title="Proportion of Sites by District",
    color_discrete_sequence=px.colors.diverging.RdYlBu,
   )

   # Display pie chart in Streamlit
   st.plotly_chart(fig)





##### First level container ends here

#### cleaning "total_site_area_acres" starts here

#helper function
def split_float_value(value):
   value = str(value)

   pattern = r"(\d+(\.\d+)?)(?:\s*acres|\s*\(.*\))?|-"
   
   if "sq" in value:
      pass
   else:
      matches = re.findall(pattern, value)
      split_values = [match[0] for match in matches]
      return split_values

#initializing empty list
df_total_area_acres = []

for value in df["total_site_area_acres"]:
   result = split_float_value(value)
   if result:
      df_total_area_acres.append(float(result[0]))

#### cleaning "total_site_area_acres" ends here

#### second level container starts here
#### For bar chart
fig = px.bar(
   df_property,
   x="Property Type",               # X-axis: Districts
   y="Number of Sites",        # Y-axis: Number of Sites
   title="Number of Sites by Property Type",  # Chart title
   color="Property Type",           # Color the bars by District
   color_discrete_sequence=px.colors.qualitative.Set2,
   labels={"Property Type": "Property Type", "Number of Sites": "Count of Sites"}
   )

# Display the chart in Streamlit
st.plotly_chart(fig)
#### second level container ends here   

#### third level container starts here
##### For distogram
   
hist_data = [df_total_area_acres]

group_labels = ['Distribution of available areas (acres)']

fig = ff.create_distplot(
      hist_data, group_labels, bin_size=[.1])
st.plotly_chart(fig, use_container_width=True, theme="streamlit")
#### third level container ends here