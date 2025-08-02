import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import os

ES_HOST = "http://localhost:9200"
PRODUCTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'central_data', 'flipkart-products-with-hindi.csv')

def create_es_client():
    return Elasticsearch(ES_HOST)

def index_brands_and_categories():
    """
    Extracts unique brands and categories, including their Hindi translations,
    and indexes them into specialized Elasticsearch indices with proper mappings.
    """
    es_client = create_es_client()
    try:
        df = pd.read_csv(PRODUCTS_PATH)
        if 'brand_hi' not in df.columns: df['brand_hi'] = ''
        if 'department_hi' not in df.columns: df['department_hi'] = ''
        df.fillna({'brand': 'NA', 'brand_hi': 'NA', 'department': 'NA', 'department_hi': 'NA'}, inplace=True)
    except FileNotFoundError:
        print(f"Error: Cleaned products file not found at {PRODUCTS_PATH}")
        return

    BRAND_INDEX = "brands_index"
    if es_client.indices.exists(index=BRAND_INDEX):
        es_client.indices.delete(index=BRAND_INDEX)

    brand_mapping = {
        "properties": {
            "name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "name_hi": {"type": "text", "analyzer": "hindi"} # Use Hindi analyzer
        }
    }
    es_client.indices.create(index=BRAND_INDEX, mappings=brand_mapping)
    
    unique_brands_df = df[['brand', 'brand_hi']].drop_duplicates().dropna(subset=['brand'])
    brand_actions = [
        {"_index": BRAND_INDEX, "_source": {"name": row['brand'], "name_hi": row['brand_hi']}}
        for _, row in unique_brands_df.iterrows()
    ]
    bulk(es_client, brand_actions)
    print(f"✅ Indexed {len(brand_actions)} unique multilingual brands.")

    CATEGORY_INDEX = "categories_index"
    if es_client.indices.exists(index=CATEGORY_INDEX):
        es_client.indices.delete(index=CATEGORY_INDEX)

    category_mapping = {
        "properties": {
            "name": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
            "name_hi": {"type": "text", "analyzer": "hindi"}
        }
    }
    es_client.indices.create(index=CATEGORY_INDEX, mappings=category_mapping)

    unique_categories_df = df[['department', 'department_hi']].drop_duplicates().dropna(subset=['department'])
    category_actions = [
        {"_index": CATEGORY_INDEX, "_source": {"name": row['department'], "name_hi": row['department_hi']}}
        for _, row in unique_categories_df.iterrows()
    ]
    bulk(es_client, category_actions)
    print(f"✅ Indexed {len(category_actions)} unique multilingual categories.")

if __name__ == "__main__":
    index_brands_and_categories()