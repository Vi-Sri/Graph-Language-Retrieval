import os
import json 
import pandas as pd
import openai
import neo4j
from dotenv import load_dotenv
load_dotenv()

def get_product_json(file_path):
    with open(file_path, 'r') as file:
        amazon_product_json = json.load(file)
    return amazon_product_json

def get_product_pd(file_path):
    df_amzn = pd.read_json(file_path)
    return df_amzn

def sanitize(text):
    text = str(text).replace("'", "")\
        .replace('"', '')\
        .replace('{', '')\
        .replace('}', '')
    return text

def init_neo4j_db(jsonData, graph):
    i = 1
    for obj in jsonData:
        print(f"{i}. {obj['product_id']} -{obj['relationship']}-> {obj['entity_value']}")
        i += 1
        query = f'''
        MERGE (product:Product {{id: {obj['product_id']}}})
        ON CREATE SET product.name = "{sanitize(obj['product'])}", 
                       product.title = "{sanitize(obj['TITLE'])}", 
                       product.bullet_points = "{sanitize(obj['BULLET_POINTS'])}", 
                       product.size = {sanitize(obj['PRODUCT_LENGTH'])}

        MERGE (entity:{obj['entity_type']} {{value: "{sanitize(obj['entity_value'])}"}})

        MERGE (product)-[:{obj['relationship']}]->(entity)
        '''
        graph.query(query)
    print("Added all nodes and relationships to Neo4j database for given Ecommerce data.")





