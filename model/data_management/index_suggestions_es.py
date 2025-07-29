import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import os
import json

ES_HOST = "http://localhost:9200"
INDEX_NAME = "products_index"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
PRODUCTS_PATH = os.path.join(ROOT_DIR, 'central_data', 'cleaned-amazon-products.csv')
EMBEDDINGS_PATH = os.path.join(ROOT_DIR, 'central_data', 'product_embeddings.csv')


def create_es_client():
    return Elasticsearch(ES_HOST)

def create_index(client: Elasticsearch, embedding_dim: int):
    """Creates the Elasticsearch index with mappings for keyword and vector search."""
    if client.indices.exists(index=INDEX_NAME):
        print(f"Index '{INDEX_NAME}' already exists. Deleting it for re-indexing.")
        client.indices.delete(index=INDEX_NAME)

    mapping = {
        "properties": {
            "title": {"type": "text", "analyzer": "english"},
            "brand": {"type": "keyword"},
            "description": {"type": "text", "analyzer": "english"},
            "department": {"type": "keyword"},
            "embedding": {"type": "dense_vector", "dims": embedding_dim},
            "rating": {"type": "float"},
            "reviews_count": {"type": "integer"},
            "final_price": {"type": "integer"},
            "discount_percentage": {"type": "float"},
            "quality_score": {"type": "float"},
            "bought_past_month": {"type": "integer"}
        }
    }
    client.indices.create(index=INDEX_NAME, mappings=mapping)
    print(f"Index '{INDEX_NAME}' created with dense_vector mapping for embeddings.")

def index_products():
    """Reads product data and embeddings, and bulk-indexes them into Elasticsearch."""
    es_client = create_es_client()

    try:
        products_df = pd.read_csv(PRODUCTS_PATH)
        embeddings_df = pd.read_csv(EMBEDDINGS_PATH)
    except FileNotFoundError as e:
        print(f"Error: A required data file was not found. {e}")
        return

    data_df = pd.merge(products_df, embeddings_df, on='asin')
    data_df.fillna(0, inplace=True)

    first_embedding = json.loads(data_df['embedding'].iloc[0])
    embedding_dimension = len(first_embedding)
    
    create_index(es_client, embedding_dimension)

    actions = []
    print(f"Generating documents for {len(data_df)} products...")
    for _, row in data_df.iterrows():
        doc = {
            "title": row['title'],
            "brand": row['brand'],
            "description": row['description'],
            "department": row['department'],
            "embedding": json.loads(row['embedding']),
            "rating": row['rating'],
            "reviews_count": row['reviews_count'],
            "final_price": row['final_price'],
            "discount_percentage": row['discount_percentage'],
            "quality_score": row['quality_score'],
            "bought_past_month": row['bought_past_month']
        }
        actions.append({"_index": INDEX_NAME, "_id": row['asin'], "_source": doc})

    print(f"Indexing {len(actions)} products into Elasticsearch...")
    bulk(es_client, actions)
    print("✅ Product indexing complete.")

if __name__ == "__main__":
    index_products()