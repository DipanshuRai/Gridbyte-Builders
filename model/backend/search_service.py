from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import joblib
import pandas as pd
import numpy as np
import os

class SearchService:
    def __init__(self):
        print("Initializing Search Service...")
        self.es_client = Elasticsearch("http://localhost:9200")
        if not self.es_client.ping():
            raise ConnectionError("Could not connect to Elasticsearch")
        
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        self.category_view_map = {
            # Visual Categories -> Grid View
            "Clothing": "grid",
            "Jewellery": "grid",
            "Footwear": "grid",
            "Home Decor & Festive Needs": "grid",
            "Beauty and Personal Care": "grid",
            "Home Furnishing": "grid",
            "Kitchen & Dining": "grid",
            "Watches": "grid",
            "Baby Care": "grid",
            "Toys & School Supplies": "grid",
            "Pens & Stationery": "grid",
            "Bags, Wallets & Belts": "grid",
            "Furniture": "grid",
            "Sports & Fitness": "grid",
            "Sunglasses": "grid",
            "Pet Supplies": "grid",
            "Home & Kitchen": "grid",
            "Eyewear": "grid",
            "Mobiles & Accessories": "grid",

            # Informational Categories -> List View
            "Automotive": "list",
            "Computers": "list",
            "Tools & Hardware": "list",
            "Home Improvement": "list",
            "Cameras & Accessories": "list",
            "Health & Personal Care Appliances": "list",
            "Gaming": "list",
            "Home Entertainment": "list",
            "eBooks": "list"
        }

        model_path = os.path.join(os.path.dirname(__file__), '..', 'ml_models', 'ltr_model.joblib')
        vectorizer_path = os.path.join(os.path.dirname(__file__), '..', 'ml_models', 'tfidf_vectorizer.joblib')
        try:
            self.ltr_model = joblib.load(model_path)
            self.tfidf_vectorizer = joblib.load(vectorizer_path)
            print("Loaded LTR model and TF-IDF vectorizer successfully.")
        except FileNotFoundError:
            print("Warning: LTR model or vectorizer not found. Search will fallback to basic ES ranking.")
            self.ltr_model = None
            self.tfidf_vectorizer = None

        print("Search Service Initialized Successfully.")

    def search_products(self, user_query: str, limit: int = 20, discount: int = 0, price_range=None, ratings: int = 0):
        if not user_query:
            return {"results": [], "facets": {}, "view_preference": "grid"}

        query_embedding = self.embedding_model.encode(user_query, normalize_embeddings=True)

        filters = []
        if discount > 0:
            filters.append({
                "range": {
                    "discount_percentage": {
                        "gte": discount 
                    }
                }
            })
        if price_range:
            filters.append({"range": {"final_price": {"gte": price_range[0], "lte": price_range[1]}}})
        if ratings > 0:
            filters.append({"range": {"rating": {"gte": ratings}}})

        es_query = {
            "size": 100, 
            "query": {
                "bool": {
                    "must": {
                        "multi_match": {
                            "query": user_query,
                            "fields": ["title^3", "description^2", "brand", "product_specifications.value"],
                            "fuzziness": "AUTO"
                        }
                    },
                    "filter": filters  # Apply the list of filters here
                }
            },
            "knn": {
                "field": "embedding",
                "query_vector": query_embedding,
                "k": 50,
                "num_candidates": 100
            },
            "aggs": {
                "brands": { "terms": { "field": "brand", "size": 10 } },
                "departments": { "terms": { "field": "department", "size": 10 } }
            }
        }
        
        response = self.es_client.search(index="products_index", body=es_query)
        candidates = [hit['_source'] for hit in response['hits']['hits']]
        facets = {"brands": response['aggregations']['brands']['buckets'], "departments": response['aggregations']['departments']['buckets']}

        if not candidates or not self.ltr_model:
            return {"results": candidates[:limit], "facets": facets, "view_preference": "grid"}

        rerank_df = pd.DataFrame(candidates)
        rerank_df['search_query'] = user_query
        
        query_vec = self.tfidf_vectorizer.transform(rerank_df['search_query'])
        title_vec = self.tfidf_vectorizer.transform(rerank_df['title'])
        rerank_df['text_similarity'] = np.asarray(query_vec.multiply(title_vec).sum(axis=1)).flatten()
        
        rerank_df['query_length'] = rerank_df['search_query'].apply(len)
        
        features_to_predict = [
            'text_similarity', 'query_length', 'rating', 'reviews_count', 
            'quality_score', 'discount_percentage', 'bought_past_month'
        ]
        X_predict = rerank_df[features_to_predict]

        relevance_scores = self.ltr_model.predict_proba(X_predict)[:, 1]
        rerank_df['relevance_score'] = relevance_scores

        reranked_results = rerank_df.sort_values(by='relevance_score', ascending=False).to_dict(orient='records')

        view_preference = "grid"
        if reranked_results:
            top_product_department = reranked_results[0].get('department')
            view_preference = self.category_view_map.get(top_product_department, 'grid')

        return {"results": reranked_results[:limit], "facets": facets, "view_preference": view_preference}

search_service = SearchService()

# from elasticsearch import Elasticsearch
# from sentence_transformers import SentenceTransformer
# import joblib
# import pandas as pd
# import numpy as np
# import os

# class SearchService:
#     def __init__(self):
#         """
#         Initializes the service by loading the ES client, embedding model,
#         and the trained LTR model and vectorizer.
#         """
#         print("Initializing Search Service...")
#         self.es_client = Elasticsearch("http://localhost:9200")
#         if not self.es_client.ping():
#             raise ConnectionError("Could not connect to Elasticsearch")
        
#         self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

#         model_path = os.path.join(os.path.dirname(__file__), '..', 'ml_models', 'ltr_model.joblib')
#         vectorizer_path = os.path.join(os.path.dirname(__file__), '..', 'ml_models', 'tfidf_vectorizer.joblib')
#         try:
#             self.ltr_model = joblib.load(model_path)
#             self.tfidf_vectorizer = joblib.load(vectorizer_path)
#             print("Loaded LTR model and TF-IDF vectorizer successfully.")
#         except FileNotFoundError:
#             print("Warning: LTR model or vectorizer not found. Search will fallback to basic ES ranking.")
#             self.ltr_model = None
#             self.tfidf_vectorizer = None

#         print("Search Service Initialized Successfully.")

#     def search_products(self, user_query: str, limit: int = 20):
#         """
#         Performs a two-stage search:
#         1. Retrieval from Elasticsearch (keyword + semantic).
#         2. Re-ranking with a trained LightGBM model.
#         """
#         if not user_query:
#             return {"results": [], "facets": {}}

#         query_embedding = self.embedding_model.encode(user_query, normalize_embeddings=True)
#         es_query = {
#             "size": 100, 
#             "knn": {
#                 "field": "embedding",
#                 "query_vector": query_embedding,
#                 "k": 50,
#                 "num_candidates": 100
#             },
#             "query": {
#                 "multi_match": {
#                     "query": user_query,
#                     "fields": ["title^2", "description", "brand"],
#                     "fuzziness": "AUTO"
#                 }
#             },
#             "aggs": {
#                 "brands": { "terms": { "field": "brand", "size": 10 } },
#                 "departments": { "terms": { "field": "department", "size": 10 } }
#             }
#         }
        
#         response = self.es_client.search(index="products_index", body=es_query)
#         candidates = [hit['_source'] for hit in response['hits']['hits']]
        
#         if not candidates or not self.ltr_model:
#             facets = {"brands": response['aggregations']['brands']['buckets'], "departments": response['aggregations']['departments']['buckets']}
#             return {"results": candidates[:limit], "facets": facets}

#         rerank_df = pd.DataFrame(candidates)
#         rerank_df['search_query'] = user_query
        
#         query_vec = self.tfidf_vectorizer.transform(rerank_df['search_query'])
#         title_vec = self.tfidf_vectorizer.transform(rerank_df['title'])
#         rerank_df['text_similarity'] = np.asarray(query_vec.multiply(title_vec).sum(axis=1)).flatten()
        
#         rerank_df['query_length'] = rerank_df['search_query'].apply(len)
        
#         features_to_predict = [
#             'text_similarity', 'query_length', 'rating', 'reviews_count', 
#             'quality_score', 'discount_percentage', 'bought_past_month'
#         ]
#         X_predict = rerank_df[features_to_predict]

#         relevance_scores = self.ltr_model.predict_proba(X_predict)[:, 1]
#         rerank_df['relevance_score'] = relevance_scores

#         reranked_results = rerank_df.sort_values(by='relevance_score', ascending=False).to_dict(orient='records')

#         facets = {"brands": response['aggregations']['brands']['buckets'], "departments": response['aggregations']['departments']['buckets']}
#         return {"results": reranked_results[:limit], "facets": facets}

# search_service = SearchService()

# from elasticsearch import Elasticsearch
# from sentence_transformers import SentenceTransformer

# class SearchService:
#     def __init__(self):
#         """Initializes the Elasticsearch client and the sentence embedding model."""
#         print("Initializing Search Service...")
#         self.es_client = Elasticsearch("http://localhost:9200")
#         if not self.es_client.ping():
#             raise ConnectionError("Could not connect to Elasticsearch")
        
#         self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
#         print("Search Service Initialized Successfully.")

#     def search_products(self, user_query: str, limit: int = 20):
#         """
#         Performs a hybrid search (keyword + semantic vector search) in Elasticsearch.
#         """
#         if not user_query:
#             return []

#         query_embedding = self.embedding_model.encode(user_query, normalize_embeddings=True)

#         es_query = {
#             "size": limit,
#             "knn": {
#                 "field": "embedding",
#                 "query_vector": query_embedding,
#                 "k": 10,
#                 "num_candidates": 100
#             },
#             "query": {
#                 "multi_match": {
#                     "query": user_query,
#                     "fields": ["title^2", "description", "brand"],
#                     "fuzziness": "AUTO"
#                 }
#             },
#             "aggs": {
#                 "brands": { "terms": { "field": "brand", "size": 10 } },
#                 "departments": { "terms": { "field": "department", "size": 10 } }
#             }
#         }
        
#         response = self.es_client.search(index="products_index", body=es_query)
        
#         MIN_RELEVANCE_SCORE = 1.0
        
#         filtered_hits = [hit for hit in response['hits']['hits'] if hit['_score'] >= MIN_RELEVANCE_SCORE]
        
#         results = [hit['_source'] for hit in filtered_hits]
#         facets = {
#             "brands": response['aggregations']['brands']['buckets'],
#             "departments": response['aggregations']['departments']['buckets']
#         }
        
#         return {"results": results, "facets": facets}

# search_service = SearchService()
