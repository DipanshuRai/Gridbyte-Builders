import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
import os
import json

DB_PATH = '../central_data/flipkart-cleaned-dataset-hi.csv'
OUTPUT_PATH = '../central_data/product_embeddings.csv'

def create_semantic_text(row):
    """
    Combines title, description, and key specifications into a single
    rich text string for embedding.
    """
    title = str(row.get('title', ''))
    
    description = str(row.get('description', ''))

    spec_values = []
    try:
        spec_list = json.loads(row.get('product_specifications', '[]'))
        if isinstance(spec_list, list):
            for spec in spec_list:
                if isinstance(spec, dict) and 'value' in spec:
                    spec_values.append(str(spec['value']))
    except (TypeError, json.JSONDecodeError):
        pass

    # Combine everything into a single string.
    # The format "title. title. specs. description" is a common and effective pattern.
    combined_text = f"{title}. {title}. {' '.join(spec_values)}. {description}"
    
    return combined_text

def generate_embeddings():
    """
    Generates text embeddings for each product using title and description.
    """
    print("--- Starting Text Embedding Generation ---")


    print("Loading the embedding model...")
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    print("Model loaded successfully.")

    try:
        df = pd.read_csv(DB_PATH)
        print(df.columns)
        df.dropna(subset=['title'], inplace=True)
    except FileNotFoundError:
        print(f"Error: Database not found at {DB_PATH}")
        print("Please run the data cleaning script first.")
        return

    df['description'] = df['description'].fillna('')
    
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
        print(f"✅ Success! Embeddings saved to {OUTPUT_PATH}")
    except Exception as e:
        print(f"❌ Error saving file: {e}")

if __name__ == '__main__':
    generate_embeddings()