from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import os
import regex as re

ES_HOST = "http://localhost:9200"
INDEX_NAME = "products_index"
SUGGESTER_INDEX = "autosuggest_index"
SUGGESTER_NAME = "product-suggester"

class AutosuggestService:
    def __init__(self):
        print("Initializing Autosuggest Service...")
        self.hindi_pattern = re.compile(r'[\p{Devanagari}]')
        self.es_client = Elasticsearch(ES_HOST)
        if not self.es_client.ping():
            raise ConnectionError("Could not connect to Elasticsearch")
        self.embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        print("Service Initialized.")

    def detect_language(self, text: str) -> str:
        """Detects if text contains Hindi characters"""
        if self.hindi_pattern.search(text):
            return 'hi'
        return 'en'

#     def prefix_suggestions(self, prefix: str, limit: int = 5):
#         # Detect input language
#         lang = self.detect_language(prefix)
        
#         # Choose suggestion field based on language
#         suggest_field = "suggest_hi" if lang == "hi" else "suggest"
#         suggest_query = {
#             "suggest": {
#                 SUGGESTER_NAME: {
#                     "prefix": prefix.lower(),
#                     "completion": {
#                         "field": suggest_field,
#                         "size": limit,
#                         "skip_duplicates": True,
#                         "fuzzy": {"fuzziness": "AUTO"}
#                     }
#                 }
#             }
#         }

#         response = self.es_client.search(index=SUGGESTER_INDEX, body=suggest_query)

#         suggestions = []
#         for option in response['suggest'][SUGGESTER_NAME][0]['options']:
#             suggestions.append({
#                 "suggestion": option['_source']['title_hi'] if lang=='hi' else option['_source']['title'],
#                 "type": "product",
#                 "score": option['_score'],
#                 "image": option['_source'].get('image')
#             })

#         return suggestions

#     def vector_suggestions(self, prefix: str, limit: int = 5):
#         # Detect query language
#         lang = self.detect_language(prefix)
#         print(f"Detected language {lang}")

#         query_embedding = self.embedding_model.encode(prefix, normalize_embeddings=True)

#         es_query = {
#             "size": limit,
#             "knn": {
#                 "field": "embedding",
#                 "query_vector": query_embedding,
#                 "k": limit,
#                 "num_candidates": 50
#             },
#             "_source": ["title","title_hi", "image"],  # include image if available
#             "query": {
#                 "match": {
#                     "title_hi" if lang == "hi" else "title": {
#                         "query": prefix,
#                         "fuzziness": "AUTO"
#                     }
#                 }
#             }
#         }

#         response = self.es_client.search(index=INDEX_NAME, body=es_query)

#         suggestions = []
#         seen_titles = set()
#         for hit in response['hits']['hits']:
#             title = hit['_source']['title_hi'] if lang=='hi' else hit['_source']['title']
#             if title in seen_titles:
#                 continue
#             seen_titles.add(title)
#             suggestions.append({
#                 "suggestion": title,
#                 "type": "product",
#                 "score": hit['_score'],
#                 "image": hit['_source'].get("image")  # optional
#             })
            
    def get_query_suggestions(self, prefix: str, limit: int = 4):
        """Fetches popular user search queries, now with language support."""
        try:
            lang = self.detect_language(prefix)
            suggest_field = "suggest_hi" if lang == "hi" else "suggest"
            
            body = {
                "suggest": {
                    "text": prefix, 
                    "query_suggester": {
                        "completion": {
                            "field": suggest_field, 
                            "size": limit,
                            "skip_duplicates": True,
                            "fuzzy": {"fuzziness": "AUTO"}
                        }
                    }
                }
            }
            response = self.es_client.search(index="queries_index", body=body)
            query_field = "query_text_hi" if lang == "hi" else "query_text"
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
            lang = self.detect_language(prefix)
            query_embedding = self.embedding_model.encode(prefix, normalize_embeddings=True)
            title_field = "title_hi" if lang == "hi" else "title"
            body = {
                "size": limit,
                "knn": {"field": "embedding", "query_vector": query_embedding, "k": limit, "num_candidates": 50},
                "_source": ["title", "title_hi", "image"],
                "query": {"match": {"title": {"query": prefix, "fuzziness": "AUTO"}}}
            }
            response = self.es_client.search(index="products_index", body=body)
            return [{"suggestion": hit['_source'][title_field], "image": hit['_source'].get("image"), "type": "product"} for hit in response['hits']['hits']]
        except Exception as e:
            print(f"Could not fetch product suggestions: {e}")
            return []

    def get_category_suggestions(self, prefix: str, limit: int = 2):
        try:
            lang = self.detect_language(prefix)
            name_field = "name_hi" if lang == "hi" else "name"
            
            body = {"size": limit, "query": {"match_phrase_prefix": {name_field: prefix}}}
            response = self.es_client.search(index="categories_index", body=body)
            return [{"suggestion": f"in {hit['_source'][name_field]}", "original_name": hit['_source'][name_field], "type": "category"} for hit in response['hits']['hits']]
        except Exception as e:
            print(f"Could not fetch category suggestions: {e}")
            return []
        
    def get_brand_suggestions(self, prefix: str, limit: int = 1):
        try:
            lang = self.detect_language(prefix)
            name_field = "name_hi" if lang == "hi" else "name"
            
            body = {"size": limit, "query": {"match_phrase_prefix": {name_field: prefix}}}
            response = self.es_client.search(index="brands_index", body=body)
            return [{"suggestion": hit['_source'][name_field], "type": "brand"} for hit in response['hits']['hits']]
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