import os
import json 
import pandas as pd
from langchain.graphs.neo4j_graph import Neo4jGraph
from langchain.vectorstores.neo4j_vector import Neo4jVector
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import GraphCypherQAChain
from langchain.chat_models import ChatOpenAI
from utils import *
from dotenv import load_dotenv
import os
import warnings
warnings.filterwarnings('ignore')

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
        vector_embedding_dict[entity] = embed_entities(entity, config)
    # Search query for similar entities
    documents = vector_embedding_dict['characteristic'].similarity_search_with_score("waterproof", 3)
    # Result
    print("Top 1 Match Content :", documents[0][0])
    print("Top 1 Match Score :", documents[0][1])
    graph._driver.close()
    
    








