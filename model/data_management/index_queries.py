import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import os
import regex as re

ES_HOST = "http://localhost:9200"
INDEX_NAME = "queries_index"
QUERY_LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'central_data', 'query_product_log.csv')

def create_es_client():
    return Elasticsearch(ES_HOST)

def detect_language(text: str) -> str:
    """Detects if text contains Hindi characters using Unicode properties."""
    hindi_pattern = re.compile(r'[\p{Devanagari}]')
    if isinstance(text, str) and hindi_pattern.search(text):
        return 'hi'
    return 'en'

def create_queries_index(client: Elasticsearch):
    """Creates the Elasticsearch index with multilingual completion mappings."""
    if client.indices.exists(index=INDEX_NAME):
        client.indices.delete(index=INDEX_NAME)

    mapping = {
        "properties": {
            "query_text": {"type": "keyword"}, # Store the original query text
            "suggest": {"type": "completion"},    # For English suggestions
            "suggest_hi": {"type": "completion"}   # For Hindi suggestions
        }
    }
    client.indices.create(index=INDEX_NAME, mappings=mapping)
    print(f"Index '{INDEX_NAME}' created successfully with multilingual support.")

def index_user_queries():
    """Reads a mixed-language query log and indexes queries into the correct language field."""
    es_client = create_es_client()
    try:
        log_df = pd.read_csv(QUERY_LOG_PATH)
        log_df.dropna(subset=['search_query'], inplace=True)
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
        
        lang = detect_language(query_text)

        doc = {
            "query_text": query_text,
            "suggest": {
                "input": query_text if lang == 'en' else [],
                "weight": weight
            },
            "suggest_hi": {
                "input": query_text if lang == 'hi' else [], 
                "weight": weight
            }
        }
        actions.append({"_index": INDEX_NAME, "_source": doc})

    bulk(es_client, actions)
    print(f"✅ Indexed {len(actions)} unique multilingual user queries.")

if __name__ == "__main__":
    index_user_queries()