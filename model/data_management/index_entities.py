import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import os

ES_HOST = "http://localhost:9200"
PRODUCTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'central_data', 'cleaned-flipkart-products.csv')

def create_es_client():
    return Elasticsearch(ES_HOST)

def index_brands_and_categories():
    es_client = create_es_client()
    try:
        df = pd.read_csv(PRODUCTS_PATH)
    except FileNotFoundError:
        print(f"Error: Cleaned products file not found at {PRODUCTS_PATH}")
        return

    BRAND_INDEX = "brands_index"
    if es_client.indices.exists(index=BRAND_INDEX):
        es_client.indices.delete(index=BRAND_INDEX)
    es_client.indices.create(index=BRAND_INDEX)
    
    unique_brands = df['brand'].dropna().unique()
    brand_actions = [{"_index": BRAND_INDEX, "_source": {"name": brand}} for brand in unique_brands]
    bulk(es_client, brand_actions)
    print(f"✅ Indexed {len(brand_actions)} unique brands.")

    CATEGORY_INDEX = "categories_index"
    if es_client.indices.exists(index=CATEGORY_INDEX):
        es_client.indices.delete(index=CATEGORY_INDEX)
    es_client.indices.create(index=CATEGORY_INDEX)

    unique_categories = df['department'].dropna().unique()
    category_actions = [{"_index": CATEGORY_INDEX, "_source": {"name": cat}} for cat in unique_categories]
    bulk(es_client, category_actions)
    print(f"✅ Indexed {len(category_actions)} unique categories.")

if __name__ == "__main__":
    index_brands_and_categories()