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


def set_config(config):
    config["url"] = "neo4j+s://a27d7ab9.databases.neo4j.io:7687"
    config["username"] = "neo4j"
    config["password"] = "UPxug86AK63ZzUQPfLQ4J0MwgD8F5-fhhAgrKxIU6WU"
    return config


if __name__ == "__main__":
    config = dict()
    config = set_config(config)
    graph = Neo4jGraph(url=config["url"],
                       username=config["username"],
                       password=config["password"])
    init_neo4j_db(get_product_json(FILE_PATH), graph)
    graph._driver.close()
    
    








