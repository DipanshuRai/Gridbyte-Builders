from elasticsearch import Elasticsearch

ES_HOST = "http://localhost:9200"
INDEX_NAME = "autosuggest_index"
SUGGESTER_NAME = "product-suggester"

class AutosuggestService:
    def __init__(self):
        print("Initializing Autosuggest Service with Elasticsearch backend...")
        self.es_client = Elasticsearch(ES_HOST)
        if not self.es_client.ping():
            raise ConnectionError("Could not connect to Elasticsearch")
        print("Service Initialized Successfully.")

    def get_suggestions(self, prefix: str, user_context: str = None, limit: int = 10):
        if not prefix:
            return []

        completion_config = {
            "field": "suggest",
            "size": limit,
            "skip_duplicates": True,
            "fuzzy": { "fuzziness": "AUTO" }
        }

        if user_context:
            completion_config["contexts"] = {
                "category_context": user_context
            }
        
        suggest_query = {
            "suggest": {
                SUGGESTER_NAME: {
                    "prefix": prefix.lower(),
                    "completion": completion_config
                }
            }
        }

        response = self.es_client.search(index=INDEX_NAME, body=suggest_query)
        
        suggestions = []
        if SUGGESTER_NAME in response.get('suggest', {}) and response['suggest'][SUGGESTER_NAME][0]['options']:
            for option in response['suggest'][SUGGESTER_NAME][0]['options']:
                suggestions.append({
                    "suggestion": option['_source']['title'],
                    "type": "product",
                    "score": option['_score']
                })
                
        return suggestions

autosuggest_service = AutosuggestService()

# from elasticsearch import Elasticsearch

# ES_HOST = "http://localhost:9200"
# INDEX_NAME = "autosuggest_index"
# SUGGESTER_NAME = "product-suggester"

# class AutosuggestService:
#     def __init__(self):
#         print("Initializing Autosuggest Service with Elasticsearch backend...")
#         self.es_client = Elasticsearch(ES_HOST)
#         if not self.es_client.ping():
#             raise ConnectionError("Could not connect to Elasticsearch")
#         print("Service Initialized Successfully.")

#     def get_suggestions(self, prefix: str, limit: int = 10):
#         print(f"🚀 Autosuggest called with prefix: {prefix}")  

#         if not prefix:
#             return []

#         suggest_query = {
#             "suggest": {
#                 SUGGESTER_NAME: {
#                     "prefix": prefix.lower(),
#                     "completion": {
#                         "field": "suggest", 
#                         "size": limit,
#                         "skip_duplicates": True,
#                         "fuzzy": {
#                             "fuzziness": "AUTO"
#                         }
#                     }
#                 }
#             }
#         }

#         response = self.es_client.search(index=INDEX_NAME, body=suggest_query)
        
#         suggestions = []
#         for option in response['suggest'][SUGGESTER_NAME][0]['options']:
#             suggestions.append({
#                 "suggestion": option['_source']['title'], 
#                 "type": "product",
#                 "score": option['_score']
#             })
            
#         return suggestions

# autosuggest_service = AutosuggestService()



# from elasticsearch import Elasticsearch

# ES_HOST = "http://localhost:9200"
# INDEX_NAME = "autosuggest_index"
# SUGGESTER_NAME = "product-suggester"

# class AutosuggestService:
#     def __init__(self):
#         print("Initializing Autosuggest Service with Elasticsearch backend...")
#         self.es_client = Elasticsearch(ES_HOST)
#         if not self.es_client.ping():
#             raise ConnectionError("Could not connect to Elasticsearch")
#         print("Service Initialized Successfully.")

#     def get_suggestions(self, prefix: str, limit: int = 10):
#     print(f"🚀 Autosuggest called with prefix: {prefix}")

#         if not prefix:
#             return []

#         suggest_query = {
#             "suggest": {
#                 SUGGESTER_NAME: {
#                     "prefix": prefix.lower(),
#                     "completion": {
#                         "field": "suggest", 
#                         "size": limit,
#                         "skip_duplicates": True,
#                         "fuzzy": {
#                             "fuzziness": "AUTO"
#                         }
#                     }
#                 }
#             }
#         }

#         response = self.es_client.search(index=INDEX_NAME, body=suggest_query)
        
#         suggestions = []
#         for option in response['suggest'][SUGGESTER_NAME][0]['options']:
#             suggestions.append({
#                 "suggestion": option['_source']['title'], 
#                 "type": "product",
#                 "score": option['_score']
#             })
            
#         return suggestions

# autosuggest_service = AutosuggestService()
