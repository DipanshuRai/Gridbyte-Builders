# File: model/data_management/index_autosuggest_data.py

import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import os

# --- Configuration ---
ES_HOST = "http://localhost:9200"  # Use https if you have security enabled
INDEX_NAME = "autosuggest_index"
PRODUCTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'central_data', 'cleaned-amazon-products.csv')

def create_es_client():
    """Creates the Elasticsearch client."""
    # If you enabled security (Option 1 from before), use this:
    # return Elasticsearch(
    #     hosts=["https://localhost:9200"],
    #     basic_auth=('elastic', 'YOUR_PASSWORD_HERE'),
    #     ca_certs='C:\\path\\to\\your\\http_ca.crt'
    # )
    
    # If you disabled security (Option 2), use this:
    return Elasticsearch(ES_HOST)

def create_suggester_index(client: Elasticsearch):
    """Creates the Elasticsearch index with the completion mapping."""
    if client.indices.exists(index=INDEX_NAME):
        print(f"Index '{INDEX_NAME}' already exists. Deleting it for re-indexing.")
        client.indices.delete(index=INDEX_NAME)

    # This mapping is crucial for the suggester feature
    mapping = {
        "properties": {
            "title": {"type": "text"},
            "suggest": {"type": "completion"},
            "image": {"type": "keyword"} 
        }
    }
    client.indices.create(index=INDEX_NAME, mappings=mapping)
    print(f"Index '{INDEX_NAME}' created with completion suggester mapping.")

def index_suggestions():
    """Reads product data and indexes it for autosuggestions."""
    es_client = create_es_client()
    if not es_client.ping():
        raise ConnectionError("Could not connect to Elasticsearch. Is it running?")

    try:
        products_df = pd.read_csv(PRODUCTS_PATH)
        products_df.dropna(subset=['title'], inplace=True)
        products_df['image_url'] = products_df['image_url'].fillna('')
    except FileNotFoundError:
        print(f"Error: Product data not found at {PRODUCTS_PATH}")
        return

    create_suggester_index(es_client)

    actions = []
    print(f"Generating documents for {len(products_df)} suggestions...")
    for _, row in products_df.iterrows():
        title = row['title']
        doc = {
            "title": title,
            "suggest": title,  # The field for the completion suggester
            "image": row['image_url']
        }
        actions.append({"_index": INDEX_NAME, "_source": doc})

    print(f"Indexing {len(actions)} suggestions into Elasticsearch...")
    bulk(es_client, actions)
    print("✅ Suggestion indexing complete.")

if __name__ == "__main__":
    index_suggestions()