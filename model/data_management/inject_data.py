import pandas as pd
import os
import ast

DB_PATH = '../central_data/cleaned-amazon-products.csv'

REQUIRED_SCHEMA = {
    'title': str,
    'brand': str,
    'description': str,
    'initial_price': int,
    'final_price': int,
    'currency': str,
    'availability': str,
    'reviews_count': int,
    'categories': list,
    'asin': str,
    'number_of_sellers': int,
    'root_bs_rank': int,
    'answered_questions': int,
    'url': str,
    'image_url': str,
    'item_weight': str,
    'rating': float,
    'product_dimensions': str,
    'seller_id': str,
    'discount': int,
    'model_number': str,
    'manufacturer': str,
    'department': str,
    'plus_content': bool,
    'top_review': str,
    'features': str,
    'ingredients': str,
    'bought_past_month': int,
    'is_available': bool,
    'badge': str
}

def inject_new_product():
    """
    Guides a user to input data for a new product, validates it,
    and injects it into the central database.
    """
    print("--- New Product Injection Module ---")

    try:
        df = pd.read_csv(DB_PATH)
    except FileNotFoundError:
        print(f"Error: Database not found at {DB_PATH}")
        print("Please run the data cleaning script first to create the database.")
        return

    new_product = {}

    print("\nPlease enter the details for the new product.")
    print("Note: For 'categories', enter a Python-style list, e.g., ['Books', 'Fiction']")
    
    for col, dtype in REQUIRED_SCHEMA.items():
        if col == 'department': continue 

        while True:
            try:
                user_input = input(f"Enter {col} ({dtype.__name__}): ")
         
                if dtype == list:
           
                    val = ast.literal_eval(user_input)
                    if not isinstance(val, list):
                        raise ValueError("Input is not a list.")
                elif dtype == bool:
                    if user_input.lower() not in ['true', 'false']:
                        raise ValueError("Please enter 'true' or 'false'.")
                    val = user_input.lower() == 'true'
                else:
                    val = dtype(user_input)
                
                new_product[col] = val
                break
            except (ValueError, SyntaxError):
                print(f"Invalid input. Please enter a valid {dtype.__name__}.")

    new_asin = new_product['asin']
    if new_asin in df['asin'].values:
        print(f"\n❌ Injection Failed: Product with asin '{new_asin}' already exists.")
        return

    print("\nValidation successful. ASIN is unique.")


    categories_list = new_product.get('categories', [])
    new_product['department'] = categories_list[0].lstrip() if categories_list else 'NA'


    new_product_df = pd.DataFrame([new_product])
    

    new_product_df = new_product_df[df.columns]
    

    updated_df = pd.concat([df, new_product_df], ignore_index=True)
    

    try:
        updated_df.to_csv(DB_PATH, index=False)
        print(f"✅ Injection Successful: Product '{new_product['title']}' has been added to the database.")
    except Exception as e:
        print(f"❌ Injection Failed: Could not write to file. Error: {e}")


if __name__ == '__main__':
    inject_new_product()