import pandas as pd
import random
import os

DB_PATH = '../central_data/cleaned-flipkart-products.csv'
USER_PREF_PATH = '../central_data/user_preference_history.csv'
OUTPUT_PATH = '../central_data/query_product_log.csv'

def generate_realistic_queries(product_title, product_brand, product_department):
    """Generates a list of potential search queries for a single product."""
    queries = set()
    
    if isinstance(product_brand, str) and product_brand != 'NA':
        queries.add(product_brand.lower())
    if isinstance(product_department, str) and product_department != 'NA':
        queries.add(product_department.lower())
    if isinstance(product_brand, str) and isinstance(product_department, str) and product_brand != 'NA' and product_department != 'NA':
        queries.add(f"{product_brand.lower()} {product_department.lower()}")

    if isinstance(product_title, str):
        words = product_title.lower().split()
        if len(words) > 1:
            queries.add(" ".join(words[:2])) # First two words
        if len(words) > 2 and product_department != 'NA' and isinstance(product_department, str):
             queries.add(f"{words[0]} {product_department.lower()}") # First word + department

    return [q for q in queries if q]


def generate_interaction_log():
    """
    Generates a simulated log of user searches, clicks, and purchases.
    """
    print("--- Starting Query-Product Interaction Log Generation ---")

    try:
        products_df = pd.read_csv(DB_PATH)
        users_df = pd.read_csv(USER_PREF_PATH)
        user_ids = users_df['user_id'].unique().tolist()
    except FileNotFoundError as e:
        print(f"Error: Could not find a required file. {e}")
        print("Please ensure 'cleaned-flipkart-products.csv' and 'user_preference_history.csv' exist.")
        return

    print(f"Loaded {len(products_df)} products and {len(user_ids)} users.")
    
    interaction_log = []
    
    print("Simulating user search sessions...")
    for user_id in user_ids:
        num_searches = random.randint(10, 25)
        
        for _ in range(num_searches):
            target_product = products_df.sample(1).iloc[0]
            
            queries = generate_realistic_queries(
                target_product['title'], 
                target_product['brand'], 
                target_product['department']
            )
            
            if not queries:
                continue 

           
            search_query = random.choice(queries)
            

            clicked_asin = target_product['asin']
            
            is_purchase = random.random() < 0.20
            
            interaction_log.append({
                'user_id': user_id,
                'search_query': search_query,
                'clicked_asin': clicked_asin,
                'is_purchase': is_purchase
            })

    if not interaction_log:
        print("Could not generate any interactions. Please check your source data.")
        return

    
    log_df = pd.DataFrame(interaction_log)
    
    try:
        log_df.to_csv(OUTPUT_PATH, index=False)
        print(f"✅ Success! Query log with {len(log_df)} interactions saved to {OUTPUT_PATH}")
    except Exception as e:
        print(f"❌ Error saving file: {e}")


if __name__ == '__main__':
    generate_interaction_log()