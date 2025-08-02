import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
import os
import json

DB_PATH = '../central_data/flipkart-products-with-hindi.csv'
OUTPUT_PATH = '../central_data/product_embeddings.csv'

def create_semantic_text(row):
    """
    Combines English and Hindi titles, descriptions, and key specifications
    into a single rich, multilingual text string for embedding.
    """
    title_en = str(row.get('title', ''))
    desc_en = str(row.get('description', ''))
    
    title_hi = str(row.get('title_hi', ''))
    desc_hi = str(row.get('description_hi', ''))

    spec_values = []
    try:
        specs_data = row.get('product_specifications', '[]')
        spec_list = json.loads(specs_data) if isinstance(specs_data, str) else specs_data
        
        if isinstance(spec_list, list):
            for spec in spec_list:
                if isinstance(spec, dict) and 'value' in spec:
                    spec_values.append(str(spec['value']))
    except (TypeError, json.JSONDecodeError):
        pass
    
    specs_text = ' '.join(spec_values)

    # Combine everything into a single, powerful string.
    # The repetition of titles gives them more weight in the embedding.
    # Including both languages makes the embedding bilingual.
    combined_text = f"{title_en}. {title_hi}. {title_en}. {title_hi}. {specs_text}. {desc_en}. {desc_hi}"
    
    return combined_text

def generate_embeddings():
    """
    Generates rich, multilingual text embeddings for each product.
    """
    print("--- Starting Multilingual Text Embedding Generation ---")

    print("Loading the multilingual embedding model...")
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    print("Model loaded successfully.")

    try:
        df = pd.read_csv(DB_PATH)
        df.dropna(subset=['title'], inplace=True)
    except FileNotFoundError:
        print(f"Error: Database not found at {DB_PATH}")
        print("Please run the 'prepare_data.py' script first.")
        return

    print("Creating rich multilingual semantic text for each product...")
    texts_to_embed = df.apply(create_semantic_text, axis=1).tolist()
    
    print(f"Preparing to generate embeddings for {len(texts_to_embed)} products...")
    embeddings = model.encode(texts_to_embed, show_progress_bar=True, normalize_embeddings=True)
    print(f"Embeddings generated successfully. Vector dimension: {embeddings.shape[1]}")

    embeddings_df = pd.DataFrame({
        'asin': df['asin'],
        'embedding': [json.dumps(emb.tolist()) for emb in embeddings]
    })
    
    try:
        embeddings_df.to_csv(OUTPUT_PATH, index=False)
        print(f"✅ Success! Rich multilingual embeddings saved to {OUTPUT_PATH}")
    except Exception as e:
        print(f"❌ Error saving file: {e}")

if __name__ == '__main__':
    generate_embeddings()