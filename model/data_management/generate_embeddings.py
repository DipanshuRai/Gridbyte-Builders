import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
import os
import json

DB_PATH = '../central_data/cleaned-flipkart-products.csv'
OUTPUT_PATH = '../central_data/product_embeddings.csv'

def generate_embeddings():
    """
    Generates text embeddings for each product using title and description.
    """
    print("--- Starting Text Embedding Generation ---")


    print("Loading the embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Model loaded successfully.")

    try:
        df = pd.read_csv(DB_PATH)
        df.dropna(subset=['title'], inplace=True)
    except FileNotFoundError:
        print(f"Error: Database not found at {DB_PATH}")
        print("Please run the data cleaning script first.")
        return

    df['description'] = df['description'].fillna('')
    
    texts_to_embed = (df['title'] + ". " + df['description']).tolist()
    
    print(f"Preparing to generate embeddings for {len(texts_to_embed)} products...")

    embeddings = model.encode(texts_to_embed, show_progress_bar=True, normalize_embeddings=True)
    print(f"Embeddings generated successfully. Vector dimension: {embeddings.shape[1]}")

    embeddings_df = pd.DataFrame({
        'asin': df['asin'],
        'embedding': [json.dumps(emb.tolist()) for emb in embeddings]
    })
    
    try:
        embeddings_df.to_csv(OUTPUT_PATH, index=False)
        print(f"✅ Success! Embeddings saved to {OUTPUT_PATH}")
    except Exception as e:
        print(f"❌ Error saving file: {e}")

if __name__ == '__main__':
    generate_embeddings()