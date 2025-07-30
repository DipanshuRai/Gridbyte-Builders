import pandas as pd
from elasticsearch import Elasticsearch
from tqdm import tqdm

ES_HOST = "http://localhost:9200"
INDEX_NAME = "autosuggest_index"
SUGGESTER_NAME = "product-suggester"

def create_index():
    es = Elasticsearch(ES_HOST)

    if es.indices.exists(index=INDEX_NAME):
        print(f"Index '{INDEX_NAME}' already exists. Deleting it for re-indexing.")
        es.indices.delete(index=INDEX_NAME)

    mapping = {
        "mappings": {
            "properties": {
                "title": {"type": "text"},
                "suggest": {
                    "type": "completion"
                }
            }
        }
    }

    es.indices.create(index=INDEX_NAME, body=mapping)
    print(f"Index '{INDEX_NAME}' created successfully.")

def index_suggestions():
    es = Elasticsearch(ES_HOST)
    df = pd.read_csv('../central_data/cleaned-amazon-products.csv')
    df.dropna(subset=['title'], inplace=True)

    print(f"Indexing {len(df)} titles for autosuggestions...")

    for i, row in tqdm(df.iterrows(), total=len(df)):
        doc = {
            "title": row['title'],
            "suggest": {
                "input": row['title'].split(),
                "weight": 1  # You can customize this using popularity
            }
        }
        es.index(index=INDEX_NAME, body=doc)

    print("✅ Autosuggest indexing complete.")

if __name__ == "__main__":
    create_index()
    index_suggestions()
