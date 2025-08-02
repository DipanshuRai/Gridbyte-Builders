import pandas as pd
import os
import random
import ast 

CLEANED_PRODUCTS_PATH = '../central_data/flipkart-products-with-hindi.csv'
CATEGORIES_SOURCE_PATH = '../central_data/hot_selling_dataset.csv'
OUTPUT_DIR = '../central_data/'
AD_OUTPUT_PATH = os.path.join(OUTPUT_DIR, 'advertisement_dataset.csv')

def generate_ad_dataset():
    """
    Generates a dataset of advertisements, one for each category,
    including a relevant image of the top-selling product in that category.
    """
    print("--- Starting Ad Dataset Generation (with Images) ---")

    try:
        hot_selling_df = pd.read_csv(CATEGORIES_SOURCE_PATH)
        products_df = pd.read_csv(CLEANED_PRODUCTS_PATH)
    except FileNotFoundError as e:
        print(f"Error: A required data file was not found. {e}")
        print("Please run 'prepare_data.py' and 'create_specialized_datasets.py' first.")
        return
    
    product_image_lookup = products_df.set_index('asin')['image_url'].to_dict()
    
    ad_name_templates = [
        "Mega Deals on {}!", "Explore The Best {}", "Fresh Arrivals: {} Collection",
        "Unlock Savings on {}", "{}: Up to 50% Off", "Exclusive Offers on {}"
    ]
    
    description_templates = [
        "Don't miss out on our exclusive offers for {}. Shop now for the best quality and prices.",
        "Discover the latest trends in {}. Perfect for every occasion. Limited time offer!",
        "Upgrade your lifestyle with our premium selection of {}. Fast delivery available.",
        "Find exactly what you're looking for in our extensive {} range. Click to see more.",
        "Top-rated {} just for you. Quality guaranteed. Explore our collection today!"
    ]
    
    ads_data = []

    for _, row in hot_selling_df.iterrows():
        category = row['department']
        
        try:
            top_asins = ast.literal_eval(row['top_5_asins'])
        except (ValueError, SyntaxError):
            top_asins = []
            
        image_url = ''
        if top_asins:
            top_product_asin = top_asins[0]
            image_url = product_image_lookup.get(top_product_asin, '')

        ad = {
            'ad_name': random.choice(ad_name_templates).format(category),
            'category': category,
            'description': random.choice(description_templates).format(category),
            'link': '#',
            'image_url': image_url 
        }
        ads_data.append(ad)

    if not ads_data:
        print("No categories found to generate ads for. Aborting.")
        return

    ads_df = pd.DataFrame(ads_data)
    
    try:
        ads_df.to_csv(AD_OUTPUT_PATH, index=False)
        print(f"✅ Success! Advertisement dataset with {len(ads_df)} ads (including images) saved to {AD_OUTPUT_PATH}")
    except Exception as e:
        print(f"❌ Error saving file: {e}")


if __name__ == '__main__':
    generate_ad_dataset()