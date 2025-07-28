import pandas as pd
import os
import random

CATEGORIES_SOURCE_PATH = '../central_data/hot_selling_dataset.csv'
OUTPUT_DIR = '../central_data/'
AD_OUTPUT_PATH = os.path.join(OUTPUT_DIR, 'advertisement_dataset.csv')

def generate_ad_dataset():
    """
    Generates a dataset of advertisements, one for each category.
    """
    print("--- Starting Ad Dataset Generation ---")
    try:
        df = pd.read_csv(CATEGORIES_SOURCE_PATH)
        categories = df['department'].unique().tolist()
    except FileNotFoundError:
        print(f"Error: Source file not found at {CATEGORIES_SOURCE_PATH}")
        print("Please run 'create_specialized_datasets.py' first.")
        return
    
    ad_name_templates = [
        "Mega Deals on {}!",
        "Explore The Best {}",
        "Fresh Arrivals: {} Collection",
        "Unlock Savings on {}",
        "{}: Up to 50% Off",
        "Exclusive Offers on {}"
    ]
    
    description_templates = [
        "Don't miss out on our exclusive offers for {}. Shop now for the best quality and prices.",
        "Discover the latest trends in {}. Perfect for every occasion. Limited time offer!",
        "Upgrade your lifestyle with our premium selection of {}. Fast delivery available.",
        "Find exactly what you're looking for in our extensive {} range. Click to see more.",
        "Top-rated {} just for you. Quality guaranteed. Explore our collection today!"
    ]
    
    ads_data = []

    for category in categories:
        ad = {
            'ad_name': random.choice(ad_name_templates).format(category),
            'category': category,
            'description': random.choice(description_templates).format(category),
            'link': '#'
        }
        ads_data.append(ad)

    if not ads_data:
        print("No categories found to generate ads for. Aborting.")
        return

    ads_df = pd.DataFrame(ads_data)
    
    try:
        ads_df.to_csv(AD_OUTPUT_PATH, index=False)
        print(f"Success! Advertisement dataset with {len(ads_df)} ads saved to {AD_OUTPUT_PATH}")
    except Exception as e:
        print(f"❌ Error saving file: {e}")


if __name__ == '__main__':
    generate_ad_dataset()