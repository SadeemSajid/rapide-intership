import streamlit as st

# Data handling
import json
import pandas as pd

# App logic
from modules import brain

# GLOBALS
data = ""

# Page configs
st.set_page_config(page_title="Cool App")
st.title("Cool :rainbow[Data Manipulation] Tool.")

# Tabs
load, manip, view = st.tabs(["Load Data", "Data Manipulation", "View Data"])

# LOAD DATA VIEW
with load:
    st.header(":lightning: Upload your data")
    st.write("**We currently support :orange[JSON] format only.**")
    

    # Upload JSON
    json_file = st.file_uploader("Choose a JSON file", accept_multiple_files=False)
    
    # Upload data to Neo4J
    if json_file:
        
        # Remove previous data
        brain.delete_data()
        data = json.load(json_file)
        
        # Load new data
        if brain.upload_data(data) == True:
            st.info(f"Loaded: {json_file.name}")
        else:
            st.error("Could not upload data. Try uploading the file again.")
            
# DATA MANIPULATION VIEW
with manip:
    st.header("Manipulate data w/ prompts")
    
    if data == "":
        st.info("No data currently uploaded.")
    else:
        prompt = st.text_input("Enter a prompt")
        
        # # Handle prompt
        # if prompt:
            
        #     # Generate Code
        #     code = brain.get_code(data[0], prompt)
           
        #     # Approve changes button
        #     if code != "" and st.button("Approve transformation!", type="primary"):
        #         pass
            
        #     st.write(code)
            

# VIEW DATA VIEW
with view:
    st.header("Live data view")
    
    if data != "":        
        # Load it into pandas
        df = pd.DataFrame(data)
        st.dataframe(df)
    else:
        st.info("No data currently uploaded.")