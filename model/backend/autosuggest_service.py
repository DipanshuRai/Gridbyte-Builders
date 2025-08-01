from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import os

class AutosuggestService:
    def __init__(self):
        print("Initializing Autosuggest Service...")
        self.es_client = Elasticsearch("http://localhost:9200")
        if not self.es_client.ping():
            raise ConnectionError("Could not connect to Elasticsearch")
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        print("Service Initialized.")

    def get_query_suggestions(self, prefix: str, limit: int = 4):
        """
        Fetches the most popular, matching user search queries.
        This provides the most relevant suggestions.
        """
        try:
            body = {
                "suggest": {
                    "text": prefix, 
                    "query_suggester": {
                        "completion": {
                            "field": "suggest", 
                            "size": limit,
                            "skip_duplicates": True,
                            "fuzzy": {"fuzziness": "AUTO"}
                        }
                    }
                }
            }
            response = self.es_client.search(index="queries_index", body=body)
            return [{"suggestion": opt['_source']['query_text'], "type": "query"} for opt in response['suggest']['query_suggester'][0]['options']]
        except Exception as e:
            print(f"Could not fetch query suggestions: {e}")
            return []

    def get_product_suggestions(self, prefix: str, limit: int = 3):
        """
        Fetches the most semantically relevant products.
        This is for users who are looking for a specific item.
        """
        try:
            query_embedding = self.embedding_model.encode(prefix, normalize_embeddings=True)
            body = {
                "size": limit,
                "knn": {"field": "embedding", "query_vector": query_embedding, "k": limit, "num_candidates": 50},
                "_source": ["title", "image"],
                "query": {"match": {"title": {"query": prefix, "fuzziness": "AUTO"}}}
            }
            response = self.es_client.search(index="products_index", body=body)
            return [{"suggestion": hit['_source']['title'], "image": hit['_source'].get("image"), "type": "product"} for hit in response['hits']['hits']]
        except Exception as e:
            print(f"Could not fetch product suggestions: {e}")
            return []

    def get_category_suggestions(self, prefix: str, limit: int = 2):
        """
        Fetches matching categories for navigational suggestions.
        e.g., "in Laptops"
        """
        try:
            body = {"size": limit, "query": {"match_phrase_prefix": {"name": prefix}}}
            response = self.es_client.search(index="categories_index", body=body)
            return [{"suggestion": f"in {hit['_source']['name']}", "original_name": hit['_source']['name'], "type": "category"} for hit in response['hits']['hits']]
        except Exception as e:
            print(f"Could not fetch category suggestions: {e}")
            return []
        
    def get_brand_suggestions(self, prefix: str, limit: int = 1):
        """Fetches matching brands."""
        try:
            body = {"size": limit, "query": {"match_phrase_prefix": {"name": prefix}}}
            response = self.es_client.search(index="brands_index", body=body)
            return [{"suggestion": hit['_source']['name'], "type": "brand"} for hit in response['hits']['hits']]
        except Exception as e:
            print(f"Could not fetch brand suggestions: {e}")
            return []

    def get_flipkart_style_suggestions(self, prefix: str):
        """
        Orchestrates fetching all suggestion types and blends them into a single,
        prioritized list for the best user experience.
        """
        queries = self.get_query_suggestions(prefix)
        products = self.get_product_suggestions(prefix)
        categories = self.get_category_suggestions(prefix)
        brands = self.get_brand_suggestions(prefix)
        
        final_suggestions = []
        seen_suggestions = set()

        all_sugs_in_order = queries + categories + products + brands
        
        for sug in all_sugs_in_order:
            if sug['suggestion'].lower() not in seen_suggestions:
                final_suggestions.append(sug)
                seen_suggestions.add(sug['suggestion'].lower())

        return final_suggestions[:15]

autosuggest_service = AutosuggestService()