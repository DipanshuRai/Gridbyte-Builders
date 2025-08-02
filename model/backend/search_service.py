from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer, util
import pandas as pd
import numpy as np
import os
import json
from collections import Counter
import regex as re

AD_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'central_data', 'advertisement_dataset.csv')
BANNER_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'central_data', 'banners.json')

class SearchService:
    def __init__(self):
        print("Initializing Search Service...")
        self.es_client = Elasticsearch("http://localhost:9200")
        if not self.es_client.ping():
            raise ConnectionError("Could not connect to Elasticsearch")
        
        self.hindi_pattern = re.compile(r'[\p{Devanagari}]')
        self.embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

        self.category_view_map = {
            "Clothing": "grid", "Jewellery": "grid", "Footwear": "grid",
            "Home Decor & Festive Needs": "grid", "Beauty and Personal Care": "grid",
            "Home Furnishing": "grid", "Kitchen & Dining": "grid", "Watches": "grid",
            "Baby Care": "grid", "Toys & School Supplies": "grid", "Pens & Stationery": "grid",
            "Bags, Wallets & Belts": "grid", "Furniture": "grid", "Sports & Fitness": "grid",
            "Sunglasses": "grid", "Pet Supplies": "grid", "Home & Kitchen": "grid",
            "Eyewear": "grid", "Mobiles & Accessories": "grid",
            "Automotive": "list", "Computers": "list", "Tools & Hardware": "list",
            "Home Improvement": "list", "Cameras & Accessories": "list",
            "Health & Personal Care Appliances": "list", "Gaming": "list",
            "Home Entertainment": "list", "eBooks": "list"
        }

        try:
            self.ads_df = pd.read_csv(AD_DATA_PATH)
            print("Advertisement dataset loaded successfully.")
        except FileNotFoundError:
            self.ads_df = None
            print("Warning: Advertisement dataset not found. No ads will be shown.")
        try:
            with open(BANNER_DATA_PATH, 'r') as f:
                self.banners = json.load(f)
            print("Banners loaded successfully.")
        except FileNotFoundError:
            self.banners = []
            print("Warning: Banners not found.")
        print("Search Service Initialized Successfully.")

    def detect_language(self, text: str) -> str:
        if self.hindi_pattern.search(text):
            return 'hi'
        return 'en'

    def get_relevant_ads(self, dominant_category, num_ads=2):
        if self.ads_df is None or self.ads_df.empty or not dominant_category: return []
        relevant_ads = self.ads_df[self.ads_df['category'].str.contains(dominant_category, case=False, na=False)]
        return relevant_ads.sample(min(num_ads, len(relevant_ads))).to_dict(orient='records')

    def get_relevant_banner(self, dominant_category):
        if not self.banners or not dominant_category: return None
        for banner in self.banners:
            if banner.get('category') == dominant_category: return banner
        return None

    def blend_results(self, products, ads, banner):
        final_page, product_idx, ad_idx = [], 0, 0
        total_slots = len(products) + (1 if banner else 0) + len(ads)
        for i in range(total_slots):
            if i == 0 and banner: final_page.append({"type": "banner", "data": banner})
            elif i == 3 and ad_idx < len(ads): final_page.append({"type": "ad", "data": ads[ad_idx]}); ad_idx += 1
            elif i == 9 and ad_idx < len(ads): final_page.append({"type": "ad", "data": ads[ad_idx]}); ad_idx += 1
            else:
                if product_idx < len(products): final_page.append({"type": "product", "data": products[product_idx]}); product_idx += 1
        return final_page
    
    def get_product_by_asin(self, asin: str):
        """
        Retrieves a single product document from Elasticsearch by its ASIN (ID).
        """
        try:
            response = self.es_client.get(index="products_index", id=asin)
            
            product_data = response['_source']
            
            product_data['asin'] = response['_id']
            
            return product_data
        except NotFoundError:
            return None
        except Exception as e:
            print(f"An error occurred while fetching product by ASIN: {e}")
            return None

    def search_products(self, user_query: str, limit: int = 40, discount: int = 0, price_range=None, ratings: int = 0):
        if not user_query:
            return {"page_content": [], "facets": {}, "view_preference": "grid"}

        query_embedding = self.embedding_model.encode(user_query, normalize_embeddings=True)
        
        lang = self.detect_language(user_query)

        filters = []
        if discount > 0: filters.append({"range": {"discount_percentage": {"gte": discount}}})
        if price_range: filters.append({"range": {"final_price": {"gte": price_range[0], "lte": price_range[1]}}})
        if ratings > 0: filters.append({"range": {"rating": {"gte": ratings}}})

        title_field = "title_hi" if lang == 'hi' else "title"
        description_field = "description_hi" if lang == 'hi' else "description"
        
        es_query = {
            "size": 100,
            "query": {"bool": {"must": {"multi_match": {"query": user_query, "fields": [f"{title_field}^3", f"{description_field}^2", "brand", "product_specifications.value"], "fuzziness": "AUTO"}}, "filter": filters}},
            "knn": {"field": "embedding", "query_vector": query_embedding, "k": 100, "num_candidates": 200},
            "aggs": {"brands": {"terms": {"field": "brand", "size": 10}}, "departments": {"terms": {"field": "department", "size": 10}}}
        }
        
        response = self.es_client.search(index="products_index", body=es_query)
        
        candidates = []
        for hit in response['hits']['hits']:
            product_data = hit['_source']
            product_data['asin'] = hit['_id']
            product_data['title'] = product_data.get(title_field, product_data.get('title'))
            product_data['description'] = product_data.get(description_field, product_data.get('description'))
            candidates.append(product_data)

        facets = {"brands": response['aggregations']['brands']['buckets'], "departments": response['aggregations']['departments']['buckets']}

        if not candidates:
            return {"page_content": [], "facets": facets, "view_preference": "grid"}

        results_df = pd.DataFrame(candidates)
        product_embeddings = np.array([p['embedding'] for p in candidates]).astype(np.float32)
        cosine_scores = util.cos_sim(query_embedding, product_embeddings)
        results_df['semantic_similarity'] = cosine_scores.flatten()

        semantically_ranked_products = results_df.sort_values(
            by='semantic_similarity', ascending=False
        ).to_dict(orient='records')
        
        dominant_category = None
        if semantically_ranked_products:
            top_departments = [p.get('department') for p in semantically_ranked_products[:10] if p.get('department')]
            if top_departments:
                dominant_category = Counter(top_departments).most_common(1)[0][0]
        
        relevant_ads = self.get_relevant_ads(dominant_category)
        relevant_banner = self.get_relevant_banner(dominant_category)

        final_page_content = self.blend_results(semantically_ranked_products, relevant_ads, relevant_banner)

        view_preference = self.category_view_map.get(dominant_category, 'grid')

        return {
            "page_content": final_page_content[:limit],
            "facets": facets, 
            "view_preference": view_preference
        }

search_service = SearchService()