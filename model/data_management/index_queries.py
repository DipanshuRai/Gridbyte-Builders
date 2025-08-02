import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import os

ES_HOST = "http://localhost:9200"
INDEX_NAME = "queries_index"
QUERY_LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'central_data', 'query_product_log.csv')

def create_es_client():
    return Elasticsearch(ES_HOST)

def create_queries_index(client: Elasticsearch):
    if client.indices.exists(index=INDEX_NAME):
        client.indices.delete(index=INDEX_NAME)

    mapping = {
        "properties": {
            "query_text": {"type": "text", "analyzer": "standard"},
            "suggest": {"type": "completion"}
        }
    }
    client.indices.create(index=INDEX_NAME, mappings=mapping)
    print(f"Index '{INDEX_NAME}' created successfully.")

def index_user_queries():
    es_client = create_es_client()
    try:
        log_df = pd.read_csv(QUERY_LOG_PATH)
    except FileNotFoundError:
        print(f"Error: Query log not found at {QUERY_LOG_PATH}")
        return

    create_queries_index(es_client)

    query_counts = log_df['search_query'].value_counts().reset_index()
    query_counts.columns = ['query', 'count']

    actions = []
    for _, row in query_counts.iterrows():
        query_text = str(row['query'])
        weight = int(row['count'])
        doc = {
            "query_text": query_text,
            "suggest": {"input": query_text, "weight": weight}
        }
        actions.append({"_index": INDEX_NAME, "_source": doc})

    bulk(es_client, actions)
    print(f"✅ Indexed {len(actions)} unique user queries.")

if __name__ == "__main__":
    index_user_queries()