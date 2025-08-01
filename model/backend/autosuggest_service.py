from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import regex as re
import time

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

    def prefix_suggestions(self, prefix: str, limit: int = 5):
        # Detect input language
        lang = self.detect_language(prefix)
        
        # Choose suggestion field based on language
        suggest_field = "suggest_hi" if lang == "hi" else "suggest"
        suggest_query = {
            "suggest": {
                SUGGESTER_NAME: {
                    "prefix": prefix.lower(),
                    "completion": {
                        "field": suggest_field,
                        "size": limit,
                        "skip_duplicates": True,
                        "fuzzy": {"fuzziness": "AUTO"}
                    }
                }
            }
        }

        response = self.es_client.search(index=SUGGESTER_INDEX, body=suggest_query)

        suggestions = []
        for option in response['suggest'][SUGGESTER_NAME][0]['options']:
            suggestions.append({
                "suggestion": option['_source']['title_hi'] if lang=='hi' else option['_source']['title'],
                "type": "product",
                "score": option['_score'],
                "image": option['_source'].get('image')
            })

        return suggestions

    def vector_suggestions(self, prefix: str, limit: int = 5):
        # Detect query language
        lang = self.detect_language(prefix)
        print(f"Detected language {lang}")

        query_embedding = self.embedding_model.encode(prefix, normalize_embeddings=True)

        es_query = {
            "size": limit,
            "knn": {
                "field": "embedding",
                "query_vector": query_embedding,
                "k": limit,
                "num_candidates": 50
            },
            "_source": ["title","title_hi", "image"],  # include image if available
            "query": {
                "match": {
                    "title_hi" if lang == "hi" else "title": {
                        "query": prefix,
                        "fuzziness": "AUTO"
                    }
                }
            }
        }

        response = self.es_client.search(index=INDEX_NAME, body=es_query)

        suggestions = []
        seen_titles = set()
        for hit in response['hits']['hits']:
            title = hit['_source']['title_hi'] if lang=='hi' else hit['_source']['title']
            if title in seen_titles:
                continue
            seen_titles.add(title)
            suggestions.append({
                "suggestion": title,
                "type": "product",
                "score": hit['_score'],
                "image": hit['_source'].get("image")  # optional
            })

        return suggestions

    def get_hybrid_suggestions(self, prefix: str, limit: int = 10):
        start_time=time.time()
        prefix_sugs = self.prefix_suggestions(prefix, limit=limit//2)
        vector_sugs = self.vector_suggestions(prefix, limit=limit)

        seen = set(s['suggestion'] for s in prefix_sugs)
        for s in vector_sugs:
            if s['suggestion'] not in seen:
                prefix_sugs.append(s)
                seen.add(s['suggestion'])
        end_time=time.time()
        print(f"Time taken for the autosuggest query: {(end_time-start_time)*1000}ms")
        return prefix_sugs

autosuggest_service = AutosuggestService()