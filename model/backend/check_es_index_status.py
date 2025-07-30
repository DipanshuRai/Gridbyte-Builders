from elasticsearch import Elasticsearch
import json

ES_HOST = "http://localhost:9200"
INDEX_NAME = "products_index"
TARGET_ASIN = "B07V5LK5J3"  # Replace with any valid product ID

es = Elasticsearch(ES_HOST)

def get_embedding(asin):
    """Fetches the embedding vector of a given product by ASIN."""
    res = es.get(index=INDEX_NAME, id=asin, _source_includes=["embedding"])
    return res["_source"]["embedding"]

def search_similar_products(query_vector, top_k=5):
    """Performs a vector similarity search using cosine similarity."""
    query = {
        "size": top_k,
        "query": {
            "script_score": {
                "query": {
                    "match_all": {}
                },
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {
                        "query_vector": query_vector
                    }
                }
            }
        }
    }

    response = es.search(index=INDEX_NAME, body=query, _source=["title", "brand", "final_price", "rating"])

    print(f"\n🔍 Top {top_k} similar products:\n")
    for hit in response["hits"]["hits"]:
        doc = hit["_source"]
        print(f"🆔 {hit['_id']}")
        print(f"📦 Title: {doc['title']}")
        print(f"🏷️ Brand: {doc['brand']}")
        print(f"⭐ Rating: {doc['rating']} | 🛒 Price: ₹{doc['final_price']}")
        print(f"📈 Score: {hit['_score']:.4f}")
        print("-" * 60)

if __name__ == "__main__":
    try:
        emb = get_embedding(TARGET_ASIN)
        search_similar_products(emb)
    except Exception as e:
        print("❌ Error:", e)



# from elasticsearch import Elasticsearch

# ES_HOST = "http://localhost:9200"
# INDEX_NAME = "products_index"

# def main():
#     es = Elasticsearch(ES_HOST)

#     # 1. Check if index exists
#     if not es.indices.exists(index=INDEX_NAME):
#         print(f"❌ Index '{INDEX_NAME}' does not exist.")
#         return
#     print(f"✅ Index '{INDEX_NAME}' exists.")

#     # 2. Get document count
#     count = es.count(index=INDEX_NAME)['count']
#     print(f"📊 Total documents in '{INDEX_NAME}': {count}")

#     # 3. Fetch first 3 documents
#     response = es.search(index=INDEX_NAME, size=3, query={"match_all": {}})
#     print(f"\n🔍 Sample Documents:")
#     for doc in response['hits']['hits']:
#         print(f"\n🆔 ID: {doc['_id']}")
#         print(f"📦 Title: {doc['_source']['title']}")
#         print(f"🏷️ Brand: {doc['_source']['brand']}")
#         print(f"⭐ Rating: {doc['_source']['rating']}")
#         print(f"🛒 Price: {doc['_source']['final_price']}")

# if __name__ == "__main__":
#     main()
