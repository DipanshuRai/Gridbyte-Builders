import pandas as pd
import os
from collections import defaultdict
import random
import ast

DB_PATH = '../central_data/flipkart-products-with-hindi.csv'
OUTPUT_DIR = '../central_data/'

def create_categories_dataset(df):
    """
    Creates a dataset mapping each unique category to a list of product ASINs.
    """
    print("Creating Categories Dataset...")
    category_map = defaultdict(list)
    
    for _, row in df.iterrows():
        asin = row['asin']
        categories = row['categories']
        if isinstance(categories, list):
            for category in categories:
                category_map[category.strip()].append(asin)
                
    categories_df = pd.DataFrame(list(category_map.items()), columns=['category_name', 'asin_list'])
    
    output_path = os.path.join(OUTPUT_DIR, 'categories_dataset.csv')
    categories_df.to_csv(output_path, index=False)
    print(f"Categories Dataset saved to {output_path}")


def create_hot_selling_dataset(df):
    """
    Creates a dataset of the top 5 best-selling products for each department
    based on the 'bought_past_month' metric.
    """
    print("\nCreating Hot-Selling/Trending Products Dataset...")
    
    df['bought_past_month'] = pd.to_numeric(df['bought_past_month'], errors='coerce').fillna(0)
    
    hot_selling = (df.sort_values('bought_past_month', ascending=False)
                     .groupby('department')
                     .head(5))
                     
    hot_selling_summary = hot_selling.groupby('department')['asin'].apply(list).reset_index()
    hot_selling_summary.rename(columns={'asin': 'top_5_asins'}, inplace=True)

    output_path = os.path.join(OUTPUT_DIR, 'hot_selling_dataset.csv')
    hot_selling_summary.to_csv(output_path, index=False)
    print(f"Hot-Selling Dataset saved to {output_path}")


def create_user_preference_dataset(df):
    """
    Generates a simulated search history for 5 users to model user preferences.
    """
    print("\nCreating User Preference History Dataset...")
    
    # Get a list of unique departments to search from
    unique_departments = df['department'].unique().tolist()
    if not unique_departments:
        print("Cannot generate user data, no departments found.")
        return

    user_ids = [f'user_{101 + i}' for i in range(5)]
    history = []

    for user_id in user_ids:
        num_searches = random.randint(60, 70)
        for _ in range(num_searches):
            search_data = {
                'user_id': user_id,
                'searched_category': random.choice(unique_departments),
                'interested_rating_above': round(random.uniform(3.5, 4.8), 1)
            }
            history.append(search_data)
            
    user_pref_df = pd.DataFrame(history)
    
    output_path = os.path.join(OUTPUT_DIR, 'user_preference_history.csv')
    user_pref_df.to_csv(output_path, index=False)
    print(f"✅ User Preference History saved to {output_path}")


if __name__ == '__main__':
    print("--- Starting Specialized Dataset Generation ---")
    try:
        main_df = pd.read_csv(DB_PATH)
        main_df['categories'] = main_df['categories'].apply(ast.literal_eval)
    except FileNotFoundError:
        print(f"Error: Main database not found at {DB_PATH}")
        print("Please run the data cleaning script first.")
    except Exception as e:
        print(f"An error occurred while loading the main dataframe: {e}")
    else:
        create_categories_dataset(main_df.copy())
        create_hot_selling_dataset(main_df.copy())
        create_user_preference_dataset(main_df.copy())
        print("\n--- All specialized datasets have been generated successfully! ---")