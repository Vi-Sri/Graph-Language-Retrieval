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


def get_system_prompt():
    entity_types = {
        "product": "Item detailed type, for example 'high waist pants', 'outdoor plant pot', 'chef kitchen knife'",
        "category": "Item category, for example 'home decoration', 'women clothing', 'office supply'",
        "characteristic": "if present, item characteristics, for example 'waterproof', 'adhesive', 'easy to use'",
        "measurement": "if present, dimensions of the item", 
        "brand": "if present, brand of the item",
        "color": "if present, color of the item",
        "age_group": "target age group for the product, one of 'babies', 'children', 'teenagers', 'adults'. If suitable for multiple age groups, pick the oldest (latter in the list)."
    }

    relation_types = {
        "hasCategory": "item is of this category",
        "hasCharacteristic": "item has this characteristic",
        "hasMeasurement": "item is of this measurement",
        "hasBrand": "item is of this brand",
        "hasColor": "item is of this color", 
        "isFor": "item is for this age_group"
    }

    entity_relationship_match = {
        "category": "hasCategory",
        "characteristic": "hasCharacteristic",
        "measurement": "hasMeasurement", 
        "brand": "hasBrand",
        "color": "hasColor",
        "age_group": "isFor"
    }
    system_prompt = \
    f'''
        You are a helpful agent designed to fetch information from a graph database. 
        
        The graph database links products to the following entity types:
        {json.dumps(entity_types)}
        
        Each link has one of the following relationships:
        {json.dumps(relation_types)}

        Depending on the user prompt, determine if it possible to answer with the graph database.
            
        The graph database can match products with multiple relationships to several entities.
        
        Example user input:
        "Which blue clothing items are suitable for adults?"
        
        There are three relationships to analyse:
        1. The mention of the blue color means we will search for a color similar to "blue"
        2. The mention of the clothing items means we will search for a category similar to "clothing"
        3. The mention of adults means we will search for an age_group similar to "adults"
        
        
        Return a json object following the following rules:
        For each relationship to analyse, add a key value pair with the key being an exact match for one of the entity types provided, and the value being the value relevant to the user query.
        
        For the example provided, the expected output would be:
        {{
            "color": "blue",
            "category": "clothing",
            "age_group": "adults"
        }}
        
        If there are no relevant entities in the user prompt, return an empty json object.
    '''
    return system_prompt




