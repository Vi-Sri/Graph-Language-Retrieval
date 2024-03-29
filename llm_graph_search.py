import os
import json 
import pandas as pd
from langchain.graphs.neo4j_graph import Neo4jGraph
from langchain.vectorstores.neo4j_vector import Neo4jVector
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import GraphCypherQAChain
from langchain.chat_models.openai import ChatOpenAI
from utils import *
from dotenv import load_dotenv
import os
import warnings
warnings.filterwarnings('ignore')
from openai import OpenAI

load_dotenv()

# Configuration class
class Config:
    def __init__(self, 
                 openai_api_key, 
                 neo4j_url, 
                 neo4j_username, 
                 neo4j_password,
                 embedding_model,
                 data_path):
        self.openai_api_key = openai_api_key
        self.neo4j_url = neo4j_url
        self.neo4j_username = neo4j_username
        self.neo4j_password = neo4j_password
        self.embedding_model = embedding_model
        self.data_path = data_path

# Get the config from the environment variables 
def get_config(config):
    config["openai_api_key"] = os.environ.get("OPENAI_API_KEY")
    config["neo4j_url"] = os.environ.get("NEO4J_URI")
    config["neo4j_username"] = os.environ.get("NEO4J_USER")
    config["neo4j_password"] = os.environ.get("NEO4J_PASSWORD")
    config["embedding_model"] = os.environ.get("EMBEDDING_MODEL")
    config["data_path"] = os.environ.get("DATA_PATH")
    return config

# Connect to Neo4j
def embed_entities(entity_type, config:Config)->Neo4jVector:
    vector_index = Neo4jVector.from_existing_graph(
        OpenAIEmbeddings(model=config.embedding_model),
        url=config.neo4j_url,
        username=config.neo4j_username,
        password=config.neo4j_password,
        index_name=entity_type,
        node_label=entity_type,
        text_node_properties=['value'],
        embedding_node_property='embedding',
    )
    vector_index._driver.close()
    return vector_index

def define_query(prompt, system_prompt, model="gpt-4-1106-preview"):
    completion = client.chat.completions.create(
        model=model,
        temperature=0,
        response_format= {
            "type": "json_object"
        },
    messages=[
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": prompt
        }
        ]
    )
    return completion.choices[0].message.content

def create_embedding(text, config:Config):
    result = client.embeddings.create(model=config.embedding_model, input=text)
    return result.data[0].embedding

def query_graph(graph:Neo4jGraph, response, config:Config):
    embeddingsParams = {}
    query = create_query(response)
    query_data = json.loads(response)
    for key, val in query_data.items():
        embeddingsParams[f"{key}Embedding"] = create_embedding(val, config)
    result = graph.query(query, params=embeddingsParams)
    return result

def create_query(text, threshold=0.81):
    entity_relationship_match = {
        "category": "hasCategory",
        "characteristic": "hasCharacteristic",
        "measurement": "hasMeasurement", 
        "brand": "hasBrand",
        "color": "hasColor",
        "age_group": "isFor"
    }
    query_data = json.loads(text)
    # Creating embeddings
    embeddings_data = []
    for key, val in query_data.items():
        if key != 'product':
            embeddings_data.append(f"${key}Embedding AS {key}Embedding")
    query = "WITH " + ",\n".join(e for e in embeddings_data)
    # Matching products to each entity
    query += "\nMATCH (p:Product)\nMATCH "
    match_data = []
    for key, val in query_data.items():
        if key != 'product':
            relationship = entity_relationship_match[key]
            match_data.append(f"(p)-[:{relationship}]->({key}Var:{key})")
    query += ",\n".join(e for e in match_data)
    similarity_data = []
    for key, val in query_data.items():
        if key != 'product':
            similarity_data.append(f"gds.similarity.cosine({key}Var.embedding, ${key}Embedding) > {threshold}")
    query += "\nWHERE "
    query += " AND ".join(e for e in similarity_data)
    query += "\nRETURN p"
    return query


if __name__ == "__main__":
    config = dict()
    config = get_config(config)
    config = Config(**config)
    # Connect to Neo4j
    graph = Neo4jGraph(url=config.neo4j_url,
                       username=config.neo4j_username,
                       password=config.neo4j_password)
    # Extract product data
    df = get_product_pd("amazon_product_kg.json")
    entities_list = df['entity_type'].unique()
    print(entities_list)
    vector_embedding_dict = dict()
    for entity in entities_list:
        print(f"Embedding {entity} entities")
        # Embed entities
        # vector_embedding_dict[entity] = embed_entities(entity, config)
    client = OpenAI()
    user_requests = [
        "Which blue dresses are suitable for women?",
    ]
    system_prompt = get_system_prompt()
    for query in user_requests:
        print(f"User Query: {query}")
        response = define_query(query, system_prompt)
        query = create_query(response)
        result = query_graph(graph, response, config)
        print(f"Response: {response}")
        print(f"Generated Cipher query: {query}")
        print(f"{result}")
        print(f"Found {len(result)} matching product(s):\n")
        for r in result:
            print(f"{r['p']['name']} ({r['p']['id']})")
    graph._driver.close()
    
    








