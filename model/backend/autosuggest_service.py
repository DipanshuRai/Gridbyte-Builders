from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

ES_HOST = "http://localhost:9200"
INDEX_NAME = "products_index"
SUGGESTER_INDEX = "autosuggest_index"
SUGGESTER_NAME = "product-suggester"

class AutosuggestService:
    def __init__(self):
        print("Initializing Autosuggest Service...")
        self.es_client = Elasticsearch(ES_HOST)
        if not self.es_client.ping():
            raise ConnectionError("Could not connect to Elasticsearch")
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        print("Service Initialized.")

    def prefix_suggestions(self, prefix: str, limit: int = 5):
        suggest_query = {
            "suggest": {
                SUGGESTER_NAME: {
                    "prefix": prefix.lower(),
                    "completion": {
                        "field": "suggest",
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
                "suggestion": option['_source']['title'],
                "type": "product",
                "score": option['_score'],
                "image": option['_source'].get('image')
            })

        return suggestions

    def vector_suggestions(self, prefix: str, limit: int = 5):
        query_embedding = self.embedding_model.encode(prefix, normalize_embeddings=True)

        es_query = {
            "size": limit,
            "knn": {
                "field": "embedding",
                "query_vector": query_embedding,
                "k": limit,
                "num_candidates": 50
            },
            "_source": ["title", "image"],  # include image if available
            "query": {
                "match": {
                    "title": {
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
            title = hit['_source']['title']
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
        prefix_sugs = self.prefix_suggestions(prefix, limit=limit//2)
        vector_sugs = self.vector_suggestions(prefix, limit=limit)

        seen = set(s['suggestion'] for s in prefix_sugs)
        for s in vector_sugs:
            if s['suggestion'] not in seen:
                prefix_sugs.append(s)
                seen.add(s['suggestion'])

        return prefix_sugs

autosuggest_service = AutosuggestService()