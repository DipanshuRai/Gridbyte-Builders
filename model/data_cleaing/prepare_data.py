import pandas as pd
import numpy as np
import ast
import os
import random
import json

def generate_synthetic_engagement_data(df):
    def assign_rating(row):
        if pd.notna(row['rating']) and row['rating'] > 0:
            return row['rating']
        
        price = row['final_price']
        if price > 5000:
            return round(random.uniform(3.5, 5.0), 1)
        elif price > 1000:
            return round(random.uniform(3.0, 4.8), 1)
        else:
            return round(random.uniform(2.5, 4.5), 1)

    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df['rating'] = df.apply(assign_rating, axis=1)

    def assign_rating_count(row):
        price = row['final_price']
        if price > 10000:
            base_count = random.randint(50, 5000)
        elif price > 2000:
            base_count = random.randint(10, 1000)
        else:
            base_count = random.randint(1, 200)
        
        rating_multiplier = max(1, (row['rating'] - 2.5))
        return int(base_count * rating_multiplier)

    df['rating_count'] = df.apply(assign_rating_count, axis=1)

    def assign_reviews(row):
        price = row['final_price']
        if price > 10000:
            base_reviews = random.randint(50, 5000)
        elif price > 2000:
            base_reviews = random.randint(10, 1000)
        else:
            base_reviews = random.randint(1, 200)
        
        rating_multiplier = max(1, (row['rating'] - 2.5))
        return int(base_reviews * rating_multiplier)

    df['reviews_count'] = df.apply(assign_reviews, axis=1)
    
    def assign_sales(row):
        rating_count = row['rating_count']
        if rating_count > 1000:
            base_sales = random.randint(200, 10000)
        elif rating_count > 200:
            base_sales = random.randint(50, 1000)
        else:
            base_sales = random.randint(0, 200)
            
        rating_multiplier = max(0.5, (row['rating'] - 3.0))
        return int(base_sales * rating_multiplier)

    df['bought_past_month'] = df.apply(assign_sales, axis=1)
    
    return df

def clean_new_dataset(input_path, output_path, departments_output_path):
    print("--- Starting Data Preparation with Top Department Calculation ---")

    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"Error: The file {input_path} was not found.")
        return

    columns_to_keep = {
        'pid': 'asin',
        'product_name': 'title',
        'description': 'description',
        'brand': 'brand',
        'retail_price': 'initial_price',
        'discounted_price': 'final_price',
        'product_rating': 'rating',
        'image': 'images',
        'product_category_tree': 'category_tree',
        'product_specifications': 'product_specifications'
    }
    existing_cols_to_keep = {k: v for k, v in columns_to_keep.items() if k in df.columns}
    df = df[list(existing_cols_to_keep.keys())].rename(columns=existing_cols_to_keep)

    df.dropna(subset=['asin', 'title'], inplace=True)
    df['brand'] = df['brand'].fillna('NA')
    df['description'] = df['description'].fillna('No Info available')

    for col in ['initial_price', 'final_price']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(subset=['initial_price', 'final_price'], inplace=True)
    
    df = generate_synthetic_engagement_data(df)

    availability = [True, False]
    probabilities = [0.8, 0.2]
    df['isAvailable'] = np.random.choice(availability, size=len(df), p=probabilities)

    def parse_specifications(spec_string):
        if not isinstance(spec_string, str):
            return []
        try:
            json_compatible_string = spec_string.replace('=>', ':').replace('\\"', '"')
            data = ast.literal_eval(json_compatible_string)
            if isinstance(data, dict):
                spec_list = data.get("product_specification")
            
            if isinstance(spec_list, list) and all(isinstance(item, dict) for item in spec_list):
                return spec_list
                
            return []
        except (ValueError, SyntaxError, KeyError):
            return []
        
    if 'product_specifications' in df.columns:
        df['product_specifications'] = df['product_specifications'].apply(parse_specifications)
        df['product_specifications'] = df['product_specifications'].apply(json.dumps)
    else:
        df['product_specifications'] = '[]'
        print("Warning: 'product_specifications' column not found. Creating empty column.")

    def parse_all_images(url_string):
        if not isinstance(url_string, str):
            return []
        try:
            url_list = ast.literal_eval(url_string)
            if isinstance(url_list, list) and len(url_list) > 0:
                return url_list
            return []
        except (ValueError, SyntaxError):
            return []
            
    df['images'] = df['images'].apply(parse_all_images)
    df['image_url'] = df['images'].apply(lambda x: x[0] if x else '')
    df['images'] = df['images'].apply(json.dumps)

    def parse_category_tree(tree_string):
        try:
            categories = tree_string.split(' >> ')
            cleaned_cats = [cat.strip().replace('["', '').replace('"]', '') for cat in categories]
            return cleaned_cats
        except:
            return ['NA']
            
    df['categories'] = df['category_tree'].apply(parse_category_tree)
    df['department'] = df['categories'].apply(lambda cats: cats[0] if cats else 'NA')
    df.drop(columns=['category_tree'], inplace=True)
    
    print("Calculating and saving top 15 departments by product count...")
    top_departments = df['department'].value_counts().head(15)
    top_departments_list = top_departments.index.tolist()
    
    try:
        with open(departments_output_path, 'w') as f:
            json.dump(top_departments_list, f)
        print(f"✅ Top 15 departments saved to {departments_output_path}")
    except Exception as e:
        print(f"❌ Error saving top departments file: {e}")
        
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"✅ Success! Cleaned data saved to {output_path}.")
    except Exception as e:
        print(f"❌ Error saving file: {e}")

if __name__ == '__main__':
    INPUT_FILE_PATH = '../central_data/flipkart-products.csv'
    OUTPUT_FILE_PATH = '../central_data/cleaned-flipkart-products.csv'
    DEPARTMENTS_JSON_PATH = '../central_data/top_departments.json'
    
    clean_new_dataset(
        input_path=INPUT_FILE_PATH, 
        output_path=OUTPUT_FILE_PATH,
        departments_output_path=DEPARTMENTS_JSON_PATH
    )

# import pandas as pd
# import numpy as np
# import ast
# import os
# import re

# def clean_amazon_data(input_path, output_path):
#     """
#     Cleans and standardizes the Amazon products dataset.
#     - Converts prices to INR.
#     - Standardizes weights to KG.
#     - Performs all previously defined cleaning steps.
#     """
#     print("Starting data preparation process...")

#     try:
#         df = pd.read_csv(input_path)
#         print(f"Successfully loaded {input_path}. Initial shape: {df.shape}")
#     except FileNotFoundError:
#         print(f"Error: The file {input_path} was not found.")
#         return

#     currency_to_inr = {
#         'USD': 86.73,
#         'EUR': 100.63,
#         'GBP': 116.06,
#         'INR': 1.0
#     }
#     df['initial_price'] = pd.to_numeric(df['initial_price'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce')
#     df['final_price'] = pd.to_numeric(df['final_price'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce')
#     df.dropna(subset=['initial_price', 'final_price'], inplace=True)

#     rate = df['currency'].map(currency_to_inr).fillna(1.0)
#     df['initial_price'] = df['initial_price'] * rate
#     df['final_price'] = df['final_price'] * rate
#     df['currency'] = 'INR'
#     print("Step 1 Complete: Prices converted to INR.")


#     def convert_weight_to_kg(weight_str):
#         if pd.isna(weight_str) or 'No Info available' in str(weight_str):
#             return 'No Info available'
        
#         weight_str = str(weight_str).lower()
#         numbers = re.findall(r'(\d+\.?\d*)', weight_str)
#         if not numbers:
#             return 'No Info available'

#         value = float(numbers[0])
        
#         if 'pounds' in weight_str or 'lb' in weight_str:
#             return f"{value * 0.453592:.3f} kg"
#         if 'ounces' in weight_str or 'oz' in weight_str:
#             return f"{value * 0.028350:.3f} kg"
#         if 'grams' in weight_str or 'g' in weight_str:
#             return f"{value / 1000:.3f} kg"
#         if 'kilograms' in weight_str or 'kg' in weight_str:
#             return f"{value:.3f} kg"
        
#         return 'No Info available'

#     df['item_weight'] = df['item_weight'].apply(convert_weight_to_kg)
#     print("Step 2 Complete: Weights standardized to KG.")


#     columns_to_drop = [
#         'Timestamp', 'seller_name', 'buybox_seller', 'domain', 'images_count',
#         'video_count', 'date_first_available', 'upc', 'video', 'variations',
#         'delivery', 'format', 'buybox_prices', 'parent_asin', 'input_asin',
#         'origin_url', 'root_bs_category', 'bs_category', 'bs_rank',
#         'subcategory_rank', 'amazon_choice', 'images', 'product_details',
#         'prices_breakdown', 'country_of_origin'
#     ]
#     df.drop(columns=columns_to_drop, inplace=True, errors='ignore')
#     print(f"Step 3 Complete: Pruned columns. Shape after pruning: {df.shape}")

#     columns_to_dropna = ['title', 'brand', 'availability', 'number_of_sellers', 'root_bs_rank', 'rating']
#     df.dropna(subset=columns_to_dropna, inplace=True)
#     print(f"Step 4 Complete: Filtered rows with missing critical values. Shape after filtering: {df.shape}")

#     df['answered_questions'] = df['answered_questions'].fillna(0)
#     df['bought_past_month'] = df['bought_past_month'].fillna(0)
#     df['is_available'] = df['is_available'].fillna(False)

#     string_impute_cols = ['product_dimensions', 'model_number', 'manufacturer', 'top_review', 'features', 'ingredients']
#     for col in string_impute_cols:
#         df[col] = df[col].fillna('No Info available')

#     df['reviews_count'] = pd.to_numeric(df['reviews_count'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
#     df['discount'] = df['discount'].astype(str).str.extract(r'(\d+)').fillna(0)

#     df = df.astype({
#         'answered_questions': 'int', 'discount': 'int', 'bought_past_month': 'int',
#         'reviews_count': 'int', 'initial_price': 'int', 'final_price': 'int',
#         'is_available': 'bool'
#     })

#     df['badge'] = df['badge'].apply(lambda x: "Amazon's Choice" if x == "Amazon's Choice" else "NA")

#     def safe_literal_eval(val):
#         try:
#             return ast.literal_eval(val)
#         except (ValueError, SyntaxError):
#             return []
            
#     df['categories'] = df['categories'].apply(safe_literal_eval)
#     print("Step 5 Complete: Imputed missing values and standardized formats.")

#     df['department'] = df['categories'].apply(lambda cats: cats[0].lstrip() if cats else 'NA')
#     print("Step 6 Complete: 'department' column populated from categories.")

#     try:
#         os.makedirs(os.path.dirname(output_path), exist_ok=True)
#         df.to_csv(output_path, index=False)
#         print(f"Success! Cleaned data saved to {output_path}. Final shape: {df.shape}")
#     except Exception as e:
#         print(f"Error saving file: {e}")


# if __name__ == '__main__':
#     INPUT_FILE_PATH = '../central_data/amazon-products.csv'
#     OUTPUT_FILE_PATH = '../central_data/cleaned-amazon-products.csv'
    
#     clean_amazon_data(input_path=INPUT_FILE_PATH, output_path=OUTPUT_FILE_PATH)