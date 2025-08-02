import pandas as pd
import numpy as np
import os

def add_precalculated_features():
    print("--- Starting Pre-calculation of Ranking Features (with synthetic data) ---")
    db_path = '../central_data/flipkart-products-with-hindi.csv'

    try:
        df = pd.read_csv(db_path)
    except FileNotFoundError:
        print(f"Error: Cleaned database not found at {db_path}")
        print("Please ensure 'cleaned-amazon-products.csv' exists.")
        return

    initial_price_safe = df['initial_price'].replace(0, np.nan)
    discount = ((initial_price_safe - df['final_price']) / initial_price_safe) * 100
    df['discount_percentage'] = discount.clip(lower=0, upper=100).fillna(0)
    print("Added 'discount_percentage' feature.")

    df['quality_score'] = df['rating'] * np.log1p(df['rating_count'])
    
    max_score = df['quality_score'].max()
    if max_score > 0:
        df['quality_score'] = (df['quality_score'] / max_score).clip(lower=0, upper=1)
    print("Added 'quality_score' feature using rating and synthetic reviews.")

    try:
        df.to_csv(db_path, index=False)
        print(f"✅ Success! Master database has been updated with new features.")
    except Exception as e:
        print(f"❌ Error saving updated file: {e}")

if __name__ == '__main__':
    add_precalculated_features()

# import pandas as pd
# import numpy as np
# import os

# def add_precalculated_features():
#     """
#     Adds pre-calculated ranking features to the main cleaned dataset.
#     """
#     print("--- Starting Pre-calculation of Ranking Features ---")
    
#     db_path = '../central_data/cleaned-amazon-products.csv'

#     try:
#         df = pd.read_csv(db_path)
#     except FileNotFoundError:
#         print(f"Error: Cleaned database not found at {db_path}")
#         print("Please ensure 'cleaned-amazon-products.csv' exists.")
#         return

#     print(f"Loaded dataset with {df.shape[1]} columns.")


#     initial_price_safe = df['initial_price'].replace(0, np.nan)
#     discount = ((initial_price_safe - df['final_price']) / initial_price_safe) * 100
    
#     df['discount_percentage'] = discount.clip(lower=0, upper=100).fillna(0)
    
#     print("Added 'discount_percentage' feature.")

#     df['quality_score'] = df['rating'] * np.log1p(df['reviews_count'])
    
#     max_score = df['quality_score'].max()
#     if max_score > 0:
#         df['quality_score'] = df['quality_score'] / max_score
        
#     print("Added 'quality_score' feature.")

#     try:
#         df.to_csv(db_path, index=False)
#         print(f"✅ Success! {df.shape[1]} columns now in the dataset.")
#         print(f"Master database at '{db_path}' has been updated with new features.")
#     except Exception as e:
#         print(f"❌ Error saving updated file: {e}")


# if __name__ == '__main__':
#     add_precalculated_features()