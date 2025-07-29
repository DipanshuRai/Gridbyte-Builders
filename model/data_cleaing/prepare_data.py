import pandas as pd
import numpy as np
import ast
import os
import re

def clean_amazon_data(input_path, output_path):
    """
    Cleans and standardizes the Amazon products dataset.
    - Converts prices to INR.
    - Standardizes weights to KG.
    - Performs all previously defined cleaning steps.
    """
    print("Starting data preparation process...")

    try:
        df = pd.read_csv(input_path)
        print(f"Successfully loaded {input_path}. Initial shape: {df.shape}")
    except FileNotFoundError:
        print(f"Error: The file {input_path} was not found.")
        return

    currency_to_inr = {
        'USD': 86.73,
        'EUR': 100.63,
        'GBP': 116.06,
        'INR': 1.0
    }
    df['initial_price'] = pd.to_numeric(df['initial_price'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce')
    df['final_price'] = pd.to_numeric(df['final_price'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce')
    df.dropna(subset=['initial_price', 'final_price'], inplace=True)

    rate = df['currency'].map(currency_to_inr).fillna(1.0)
    df['initial_price'] = df['initial_price'] * rate
    df['final_price'] = df['final_price'] * rate
    df['currency'] = 'INR'
    print("Step 1 Complete: Prices converted to INR.")


    def convert_weight_to_kg(weight_str):
        if pd.isna(weight_str) or 'No Info available' in str(weight_str):
            return 'No Info available'
        
        weight_str = str(weight_str).lower()
        numbers = re.findall(r'(\d+\.?\d*)', weight_str)
        if not numbers:
            return 'No Info available'

        value = float(numbers[0])
        
        if 'pounds' in weight_str or 'lb' in weight_str:
            return f"{value * 0.453592:.3f} kg"
        if 'ounces' in weight_str or 'oz' in weight_str:
            return f"{value * 0.028350:.3f} kg"
        if 'grams' in weight_str or 'g' in weight_str:
            return f"{value / 1000:.3f} kg"
        if 'kilograms' in weight_str or 'kg' in weight_str:
            return f"{value:.3f} kg"
        
        return 'No Info available'

    df['item_weight'] = df['item_weight'].apply(convert_weight_to_kg)
    print("Step 2 Complete: Weights standardized to KG.")


    columns_to_drop = [
        'Timestamp', 'seller_name', 'buybox_seller', 'domain', 'images_count',
        'video_count', 'date_first_available', 'upc', 'video', 'variations',
        'delivery', 'format', 'buybox_prices', 'parent_asin', 'input_asin',
        'origin_url', 'root_bs_category', 'bs_category', 'bs_rank',
        'subcategory_rank', 'amazon_choice', 'images', 'product_details',
        'prices_breakdown', 'country_of_origin'
    ]
    df.drop(columns=columns_to_drop, inplace=True, errors='ignore')
    print(f"Step 3 Complete: Pruned columns. Shape after pruning: {df.shape}")

    columns_to_dropna = ['title', 'brand', 'availability', 'number_of_sellers', 'root_bs_rank', 'rating']
    df.dropna(subset=columns_to_dropna, inplace=True)
    print(f"Step 4 Complete: Filtered rows with missing critical values. Shape after filtering: {df.shape}")

    df['answered_questions'] = df['answered_questions'].fillna(0)
    df['bought_past_month'] = df['bought_past_month'].fillna(0)
    df['is_available'] = df['is_available'].fillna(False)

    string_impute_cols = ['product_dimensions', 'model_number', 'manufacturer', 'top_review', 'features', 'ingredients']
    for col in string_impute_cols:
        df[col] = df[col].fillna('No Info available')

    df['reviews_count'] = pd.to_numeric(df['reviews_count'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
    df['discount'] = df['discount'].astype(str).str.extract(r'(\d+)').fillna(0)

    df = df.astype({
        'answered_questions': 'int', 'discount': 'int', 'bought_past_month': 'int',
        'reviews_count': 'int', 'initial_price': 'int', 'final_price': 'int',
        'is_available': 'bool'
    })

    df['badge'] = df['badge'].apply(lambda x: "Amazon's Choice" if x == "Amazon's Choice" else "NA")

    def safe_literal_eval(val):
        try:
            return ast.literal_eval(val)
        except (ValueError, SyntaxError):
            return []
            
    df['categories'] = df['categories'].apply(safe_literal_eval)
    print("Step 5 Complete: Imputed missing values and standardized formats.")

    df['department'] = df['categories'].apply(lambda cats: cats[0].lstrip() if cats else 'NA')
    print("Step 6 Complete: 'department' column populated from categories.")

    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Success! Cleaned data saved to {output_path}. Final shape: {df.shape}")
    except Exception as e:
        print(f"Error saving file: {e}")


if __name__ == '__main__':
    INPUT_FILE_PATH = '../central_data/amazon-products.csv'
    OUTPUT_FILE_PATH = '../central_data/cleaned-amazon-products.csv'
    
    clean_amazon_data(input_path=INPUT_FILE_PATH, output_path=OUTPUT_FILE_PATH)