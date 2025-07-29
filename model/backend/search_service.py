from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

class SearchService:
    def __init__(self):
        """Initializes the Elasticsearch client and the sentence embedding model."""
        print("Initializing Search Service...")
        self.es_client = Elasticsearch("http://localhost:9200")
        if not self.es_client.ping():
            raise ConnectionError("Could not connect to Elasticsearch")
        
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Search Service Initialized Successfully.")

    def search_products(self, user_query: str, limit: int = 20):
        """
        Performs a hybrid search (keyword + semantic vector search) in Elasticsearch.
        """
        if not user_query:
            return []

        query_embedding = self.embedding_model.encode(user_query, normalize_embeddings=True)

        es_query = {
            "size": limit,
            "knn": {
                "field": "embedding",
                "query_vector": query_embedding,
                "k": 10,
                "num_candidates": 100
            },
            "query": {
                "multi_match": {
                    "query": user_query,
                    "fields": ["title^2", "description", "brand"],
                    "fuzziness": "AUTO"
                }
            },
            "aggs": {
                "brands": { "terms": { "field": "brand", "size": 10 } },
                "departments": { "terms": { "field": "department", "size": 10 } }
            }
        }
        
        response = self.es_client.search(index="products_index", body=es_query)
        
        MIN_RELEVANCE_SCORE = 1.0
        
        filtered_hits = [hit for hit in response['hits']['hits'] if hit['_score'] >= MIN_RELEVANCE_SCORE]
        
        results = [hit['_source'] for hit in filtered_hits]
        facets = {
            "brands": response['aggregations']['brands']['buckets'],
            "departments": response['aggregations']['departments']['buckets']
        }
        
        return {"results": results, "facets": facets}

search_service = SearchService()