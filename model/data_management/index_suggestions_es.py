import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import os
import json

ES_HOST = "http://localhost:9200"
INDEX_NAME = "products_index"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
PRODUCTS_PATH = os.path.join(ROOT_DIR, 'central_data', 'cleaned-flipkart-products.csv')
EMBEDDINGS_PATH = os.path.join(ROOT_DIR, 'central_data', 'product_embeddings.csv')

def create_es_client():
    return Elasticsearch(ES_HOST)

def create_index(client: Elasticsearch, embedding_dim: int):
    if client.indices.exists(index=INDEX_NAME):
        print(f"Index '{INDEX_NAME}' already exists. Deleting it for re-indexing.")
        client.indices.delete(index=INDEX_NAME)

    mapping = {
        "properties": {
            "title": {"type": "text", "analyzer": "english"},
            "brand": {"type": "keyword"},
            "image": {"type": "keyword"},
            "description": {"type": "text", "analyzer": "english"},
            "department": {"type": "keyword"},
            "embedding": {"type": "dense_vector", "dims": embedding_dim},
            "rating": {"type": "float"},
            "reviews_count": {"type": "integer"},
            "final_price": {"type": "integer"},
            "discount_percentage": {"type": "float"},
            "quality_score": {"type": "float"},
            "bought_past_month": {"type": "integer"},
            "product_specifications": {
                "type": "nested",
                "properties": {
                    "key": {"type": "text"},
                    "value": {"type": "text"}
                }
            }
        }
    }
    client.indices.create(index=INDEX_NAME, mappings=mapping)
    print(f"Index '{INDEX_NAME}' created with nested mapping for specifications.")

def index_products():
    es_client = create_es_client()

    try:
        products_df = pd.read_csv(PRODUCTS_PATH)
        products_df['image_url'] = products_df['image_url'].fillna('')
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
        try:
            spec_list = json.loads(row['product_specifications'])
        except (TypeError, json.JSONDecodeError):
            spec_list = []

        doc = {
            "title": row['title'],
            "brand": row['brand'],
            "image": row['image_url'],
            "description": row['description'],
            "department": row['department'],
            "embedding": json.loads(row['embedding']),
            "rating": row['rating'],
            "reviews_count": row['reviews_count'],
            "final_price": row['final_price'],
            "discount_percentage": row['discount_percentage'],
            "quality_score": row['quality_score'],
            "bought_past_month": row['bought_past_month'],
            "product_specifications": spec_list
        }
        actions.append({"_index": INDEX_NAME, "_id": row['asin'], "_source": doc})

    print(f"Indexing {len(actions)} products into Elasticsearch...")
    bulk(es_client, actions)
    print("✅ Product indexing complete.")

if __name__ == "__main__":
    index_products()

# import pandas as pd
# from elasticsearch import Elasticsearch
# from elasticsearch.helpers import bulk
# import os
# import json

# ES_HOST = "http://localhost:9200"
# INDEX_NAME = "products_index"

# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# ROOT_DIR = os.path.dirname(SCRIPT_DIR)
# PRODUCTS_PATH = os.path.join(ROOT_DIR, 'central_data', 'cleaned-amazon-products.csv')
# EMBEDDINGS_PATH = os.path.join(ROOT_DIR, 'central_data', 'product_embeddings.csv')


# def create_es_client():
#     return Elasticsearch(ES_HOST)

# def create_index(client: Elasticsearch, embedding_dim: int):
#     """Creates the Elasticsearch index with mappings for keyword and vector search."""
#     if client.indices.exists(index=INDEX_NAME):
#         print(f"Index '{INDEX_NAME}' already exists. Deleting it for re-indexing.")
#         client.indices.delete(index=INDEX_NAME)

#     mapping = {
#         "properties": {
#             "title": {"type": "text", "analyzer": "english"},
#             "brand": {"type": "keyword"},
#             "image": {"type": "keyword"},
#             "description": {"type": "text", "analyzer": "english"},
#             "department": {"type": "keyword"},
#             "embedding": {"type": "dense_vector", "dims": embedding_dim},
#             "rating": {"type": "float"},
#             "reviews_count": {"type": "integer"},
#             "final_price": {"type": "integer"},
#             "discount_percentage": {"type": "float"},
#             "quality_score": {"type": "float"},
#             "bought_past_month": {"type": "integer"}
#         }
#     }
#     client.indices.create(index=INDEX_NAME, mappings=mapping)
#     print(f"Index '{INDEX_NAME}' created with dense_vector mapping for embeddings.")

# def index_products():
#     """Reads product data and embeddings, and bulk-indexes them into Elasticsearch."""
#     es_client = create_es_client()

#     try:
#         products_df = pd.read_csv(PRODUCTS_PATH)
#         embeddings_df = pd.read_csv(EMBEDDINGS_PATH)
#         products_df['image_url'] = products_df['image_url'].fillna('')
#     except FileNotFoundError as e:
#         print(f"Error: A required data file was not found. {e}")
#         return

#     data_df = pd.merge(products_df, embeddings_df, on='asin')
#     data_df.fillna(0, inplace=True)

#     first_embedding = json.loads(data_df['embedding'].iloc[0])
#     embedding_dimension = len(first_embedding)
    
#     create_index(es_client, embedding_dimension)

#     actions = []
#     print(f"Generating documents for {len(data_df)} products...")
#     for _, row in data_df.iterrows():
#         doc = {
#             "title": row['title'],
#             "brand": row['brand'],
#             "image": row['image_url'],
#             "description": row['description'],
#             "department": row['department'],
#             "embedding": json.loads(row['embedding']),
#             "rating": row['rating'],
#             "reviews_count": row['reviews_count'],
#             "final_price": row['final_price'],
#             "discount_percentage": row['discount_percentage'],
#             "quality_score": row['quality_score'],
#             "bought_past_month": row['bought_past_month']
#         }
#         actions.append({"_index": INDEX_NAME, "_id": row['asin'], "_source": doc})

#     print(f"Indexing {len(actions)} products into Elasticsearch...")
#     bulk(es_client, actions)
#     print("✅ Product indexing complete.")

# if __name__ == "__main__":
#     index_products()



# import pandas as pd
# from elasticsearch import Elasticsearch
# from elasticsearch.helpers import bulk
# import os
# import json

# ES_HOST = "http://localhost:9200"
# INDEX_NAME = "products_index"

# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# ROOT_DIR = os.path.dirname(SCRIPT_DIR)
# PRODUCTS_PATH = os.path.join(ROOT_DIR, 'central_data', 'cleaned-amazon-products.csv')
# EMBEDDINGS_PATH = os.path.join(ROOT_DIR, 'central_data', 'product_embeddings.csv')


# def create_es_client():
#     return Elasticsearch(ES_HOST)


# def create_index(client: Elasticsearch, embedding_dim: int):
#     if client.indices.exists(index=INDEX_NAME):
#         print(f"Index '{INDEX_NAME}' already exists. Deleting it for re-indexing.")
#         client.indices.delete(index=INDEX_NAME)

#     index_config = {
#         "settings": {
#             "number_of_shards": 1,
#             "number_of_replicas": 0
#         },
#         "mappings": {
#             "properties": {
#                 "title": {"type": "text", "analyzer": "english"},
#                 "brand": {"type": "keyword"},
#                 "description": {"type": "text", "analyzer": "english"},
#                 "department": {"type": "keyword"},
#                 "embedding": {
#                     "type": "dense_vector",
#                     "dims": embedding_dim,
#                     "index": True,                   # ✅ Required for search
#                     "similarity": "cosine"           # ✅ Required for similarity search
#                 },
#                 "rating": {"type": "float"},
#                 "reviews_count": {"type": "integer"},
#                 "final_price": {"type": "integer"},
#                 "discount_percentage": {"type": "float"},
#                 "quality_score": {"type": "float"},
#                 "bought_past_month": {"type": "integer"}
#             }
#         }
#     }

#     client.indices.create(index=INDEX_NAME, body=index_config)
#     print(f"✅ Index '{INDEX_NAME}' created with dense_vector config.")


# def index_products():
#     """Reads product data and embeddings, and bulk-indexes them into Elasticsearch."""
#     es_client = create_es_client()

#     try:
#         products_df = pd.read_csv(PRODUCTS_PATH)
#         embeddings_df = pd.read_csv(EMBEDDINGS_PATH)
#     except FileNotFoundError as e:
#         print(f"Error: A required data file was not found. {e}")
#         return

#     data_df = pd.merge(products_df, embeddings_df, on='asin')
#     data_df.fillna(0, inplace=True)

#     first_embedding = json.loads(data_df['embedding'].iloc[0])
#     embedding_dimension = len(first_embedding)
    
#     create_index(es_client, embedding_dimension)

#     actions = []
#     print(f"Generating documents for {len(data_df)} products...")
#     for _, row in data_df.iterrows():
#         doc = {
#             "title": row['title'],
#             "brand": row['brand'],
#             "description": row['description'],
#             "department": row['department'],
#             "embedding": json.loads(row['embedding']),
#             "rating": row['rating'],
#             "reviews_count": row['reviews_count'],
#             "final_price": row['final_price'],
#             "discount_percentage": row['discount_percentage'],
#             "quality_score": row['quality_score'],
#             "bought_past_month": row['bought_past_month']
#         }
#         actions.append({"_index": INDEX_NAME, "_id": row['asin'], "_source": doc})

#     print(f"Indexing {len(actions)} products into Elasticsearch...")
#     bulk(es_client, actions)
#     print("✅ Product indexing complete.")

# if __name__ == "__main__":
#     index_products()




    # import pandas as pd
# from elasticsearch import Elasticsearch
# from elasticsearch.helpers import bulk
# import os
# import json
# import math

# ES_HOST = "http://localhost:9200"
# INDEX_NAME = "products_index"

# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# ROOT_DIR = os.path.dirname(SCRIPT_DIR)
# PRODUCTS_PATH = os.path.join(ROOT_DIR, 'central_data', 'cleaned-amazon-products.csv')
# EMBEDDINGS_PATH = os.path.join(ROOT_DIR, 'central_data', 'product_embeddings.csv')


# # def create_es_client():
# #     return Elasticsearch(ES_HOST)

# def create_es_client():
#     return Elasticsearch(
#         ES_HOST,
#         headers={"Content-Type": "application/json", "Accept": "application/json"},
#         request_timeout=30,
#         verify_certs=False  # Only if you're not using https, remove if unnecessary
#     )


# def create_index(client: Elasticsearch, embedding_dim: int):
#     if client.indices.exists(index=INDEX_NAME):
#         print(f"Index '{INDEX_NAME}' already exists. Deleting it for re-indexing.")
#         client.indices.delete(index=INDEX_NAME)

#     index_config = {
#         "settings": {
#             "number_of_shards": 1,
#             "number_of_replicas": 0
#         },
#         "mappings": {
#             "properties": {
#                 "title": {"type": "text", "analyzer": "english"},
#                 "brand": {"type": "keyword"},
#                 "description": {"type": "text", "analyzer": "english"},
#                 "department": {"type": "keyword"},
#                 "embedding": {
#                     "type": "dense_vector",
#                     "dims": embedding_dim,
#                     "index": True,
#                     "similarity": "cosine"
#                 },
#                 "rating": {"type": "float"},
#                 "reviews_count": {"type": "integer"},
#                 "final_price": {"type": "integer"},
#                 "discount_percentage": {"type": "float"},
#                 "quality_score": {"type": "float"},
#                 "bought_past_month": {"type": "integer"}
#             }
#         }
#     }

#     client.indices.create(index=INDEX_NAME, body=index_config)
#     print(f"✅ Index '{INDEX_NAME}' created with dense_vector config.")


# def is_valid_vector(vector, expected_dim):
#     return (
#         isinstance(vector, list)
#         and len(vector) == expected_dim
#         and all(isinstance(x, (float, int)) for x in vector)
#         and all(math.isfinite(x) for x in vector)
#     )


# def index_products():
#     """Reads product data and embeddings, and bulk-indexes them into Elasticsearch."""
#     es_client = create_es_client()

#     try:
#         products_df = pd.read_csv(PRODUCTS_PATH)
#         embeddings_df = pd.read_csv(EMBEDDINGS_PATH)
#     except FileNotFoundError as e:
#         print(f"❌ Error: A required data file was not found. {e}")
#         return

#     data_df = pd.merge(products_df, embeddings_df, on='asin')
#     data_df.fillna(0, inplace=True)

#     try:
#         first_embedding = json.loads(data_df['embedding'].iloc[0])
#         embedding_dimension = len(first_embedding)
#     except Exception as e:
#         print(f"❌ Error reading first embedding: {e}")
#         return

#     create_index(es_client, embedding_dimension)

#     actions = []
#     print(f"🔄 Validating and indexing {len(data_df)} products...")
#     error_count = 0

#     for i, row in data_df.iterrows():
#         try:
#             vector = json.loads(row['embedding'])
#         except Exception as e:
#             print(f"❌ JSON error at row {i}, ASIN {row['asin']}: {e}")
#             error_count += 1
#             continue

#         if not is_valid_vector(vector, embedding_dimension):
#             print(f"❌ Invalid vector at row {i}, ASIN {row['asin']}")
#             error_count += 1
#             continue

#         doc = {
#             "title": row['title'],
#             "brand": row['brand'],
#             "description": row['description'],
#             "department": row['department'],
#             "embedding": vector,
#             "rating": row['rating'],
#             "reviews_count": row['reviews_count'],
#             "final_price": row['final_price'],
#             "discount_percentage": row['discount_percentage'],
#             "quality_score": row['quality_score'],
#             "bought_past_month": row['bought_past_month']
#         }
#         actions.append({"_index": INDEX_NAME, "_id": row['asin'], "_source": doc})

#     print(f"✅ {len(actions)} valid products prepared. Skipped {error_count} invalid entries.")

#     if actions:
#         print("📤 Indexing to Elasticsearch...")
#         bulk(es_client, actions)
#         print("✅ Product indexing complete.")
#     else:
#         print("⚠️ No valid documents to index. Aborting.")

# if __name__ == "__main__":
#     index_products()




