import os
import json 
import pandas as pd
from langchain.graphs.neo4j_graph import Neo4jGraph
from langchain.vectorstores.neo4j_vector import Neo4jVector
from langchain.embeddings.openai import OpenAIEmbeddings
from utils import *
from dotenv import load_dotenv

load_dotenv()

FILE_PATH = "amazon_product_kg.json"

class Config:
    def __init__(self, openai_api_key, neo4j_url, neo4j_username, neo4j_password, data_path):
        self.openai_api_key = openai_api_key
        self.neo4j_url = neo4j_url
        self.neo4j_username = neo4j_username
        self.neo4j_password = neo4j_password
        self.data_path = data_path

def get_config(config):
    config["openai_api_key"] = os.environ.get("OPENAI_API_KEY")
    config["neo4j_url"] = os.environ.get("NEO4J_URI")
    config["neo4j_username"] = os.environ.get("NEO4J_USER")
    config["neo4j_password"] = os.environ.get("NEO4J_PASSWORD")
    config["data_path"] = os.environ.get("DATA_PATH")
    return config


if __name__ == "__main__":
    config = dict()
    config = get_config(config)
    config = Config(**config)
    graph = Neo4jGraph(url=config.neo4j_url,
                       username=config.neo4j_username,
                       password=config.neo4j_password)
    init_neo4j_db(get_product_json(FILE_PATH), graph)
    graph._driver.close()
    
    








