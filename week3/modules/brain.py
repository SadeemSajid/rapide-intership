from neo4j import GraphDatabase, RoutingControl

from google import genai

import json
import bcrypt

from dotenv import load_dotenv
import os

# ENVS
load_dotenv()
NEO_URI = os.getenv("NEO_URI")
NEO_AUTH = (os.getenv("NEO_USER"), os.getenv("NEO_PASS"))
GEMINI_API = os.getenv("GEMINI_API")
USERNAME = os.getenv("AUTH_USER")

# DB DRIVER & LLM
neoDb = GraphDatabase.driver(NEO_URI, auth=NEO_AUTH)
llm = genai.Client(api_key=GEMINI_API)
LLM_MODEL = "gemini-2.0-flash"


"""Uploads a list of data elements to Neo4J. 
Return confirmation bool."""
def upload_data(data: list) -> bool:
    try:
        for elem in data:
            json_elem = json.dumps(elem)
            neoDb.execute_query(
                "MATCH (u:User {username: $username}) CREATE (d:Data {data: $data})-[:BELONGS_TO]->(u)",
                username=USERNAME, data=json_elem, database="neo4j"
            )
        return True
    except Exception as e:
        print(e)
        return False

"""Deletes session data from Neo4J"""
def delete_data() -> bool:
    neoDb.execute_query(
        "MATCH (d)-[:BELONGS_TO]->(u:User {username: $username}) DETACH DELETE d",
        username=USERNAME, database="neo4j"
    )
    
    
def get_code(data_elem, prompt: str) -> str:
    
    response = llm.models.generate_content(
        model=LLM_MODEL,
        contents=[f"""You are a python developer.
        You need to write python code which loads a dataset from Neo4J, converts it into JSON, and manipulates it according to the prompt provided.
        It then writes the new dataset according to the requirements in a file called 'output.json'.
        Do not generate anything else. Do not write comments in the code. You may assume that all libraries needed are present in the environment.""" + """
        The dataset is to be fetched by the following cypher query: MATCH (d:Data)-[:BELONGS_TO]->(:User {""" + f"""username: {USERNAME}""" + """}) RETURN d
        This will return Neo4J nodes with the property 'data' which has a JSON string inside it. All JSON strings have similar structure.
        Make sure to convert the JSON string to programmatic JSON in python which has key-value pairs using the json library.
        A sample data element is provided for you to follow its structure. Neo4J connection details are also provided.""" + f"""
        DATA SAMPLE:{data_elem}
        PROMPT: {prompt}
        NEO4J URI: {NEO_URI}
        NEO4J Username: {NEO_AUTH[0]}
        NEO4J Password: {NEO_AUTH[1]}"""]
    )

    return response.text