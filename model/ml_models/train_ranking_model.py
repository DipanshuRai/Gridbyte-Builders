import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, roc_auc_score
from sentence_transformers import SentenceTransformer, util
import joblib
import os
import numpy as np
import torch

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
LOG_PATH = os.path.join(ROOT_DIR, 'central_data', 'query_product_log.csv')
PRODUCTS_PATH = os.path.join(ROOT_DIR, 'central_data', 'flipkart-products-with-hindi.csv')
MODEL_OUTPUT_PATH = os.path.join(ROOT_DIR, 'ml_models', 'ltr_model.joblib')
VECTORIZER_OUTPUT_PATH = os.path.join(ROOT_DIR, 'ml_models', 'tfidf_vectorizer.joblib')

def train_ranking_model():
    print("--- Starting Multilingual LTR Model Training ---")

    try:
        log_df = pd.read_csv(LOG_PATH)
        products_df = pd.read_csv(PRODUCTS_PATH)
    except FileNotFoundError as e:
        print(f"Error: A required data file was not found. {e}")
        return
    
    training_data = pd.merge(log_df, products_df, left_on='clicked_asin', right_on='asin')
    if training_data.empty:
        print("Error: No matching data found between query log and products. Aborting training.")
        return
        
    print(f"Loaded and merged data, creating a training set of {len(training_data)} interactions.")
    print("Performing advanced multilingual feature engineering...")
    
    training_data.fillna({'search_query': '', 'title': '', 'title_hi': ''}, inplace=True)

    vectorizer = TfidfVectorizer()
    query_vectors_tfidf = vectorizer.fit_transform(training_data['search_query'])
    title_vectors_tfidf = vectorizer.transform(training_data['title'])
    training_data['text_similarity'] = np.asarray(query_vectors_tfidf.multiply(title_vectors_tfidf).sum(axis=1)).flatten()

    print("Calculating multilingual semantic similarity scores...")
    embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    query_embeddings = embedding_model.encode(training_data['search_query'].tolist(), convert_to_tensor=True, show_progress_bar=True)
    title_en_embeddings = embedding_model.encode(training_data['title'].tolist(), convert_to_tensor=True, show_progress_bar=True)
    title_hi_embeddings = embedding_model.encode(training_data['title_hi'].tolist(), convert_to_tensor=True, show_progress_bar=True)
    
    cosine_scores_en = util.cos_sim(query_embeddings, title_en_embeddings).diag()
    cosine_scores_hi = util.cos_sim(query_embeddings, title_hi_embeddings).diag()
    
    training_data['semantic_similarity'] = torch.max(cosine_scores_en, cosine_scores_hi).numpy()

    training_data['query_length'] = training_data['search_query'].apply(len)
    
    features = [
        'text_similarity',
        'semantic_similarity',
        'query_length', 
        'rating', 
        'rating_count', 
        'quality_score', 
        'discount_percentage', 
        'bought_past_month'
    ]
    label = 'is_purchase'

    X = training_data[features]
    y = training_data[label]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"Data split into training ({len(X_train)} rows) and testing ({len(X_test)} rows).")

    print("Training LightGBM classifier...")
    lgbm = lgb.LGBMClassifier(objective='binary', random_state=42)
    lgbm.fit(X_train, y_train)

    print("Evaluating model performance...")
    y_pred = lgbm.predict(X_test)
    y_pred_proba = lgbm.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_pred_proba)

    print(f"\n--- Model Performance ---")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"AUC Score: {auc:.4f}")
    print("-------------------------")
    
    print("Saving model and TF-IDF vectorizer...")
    joblib.dump(lgbm, MODEL_OUTPUT_PATH)
    joblib.dump(vectorizer, VECTORIZER_OUTPUT_PATH)
    print(f"✅ Model saved to {MODEL_OUTPUT_PATH}")
    print(f"✅ Vectorizer saved to {VECTORIZER_OUTPUT_PATH}")

if __name__ == "__main__":
    train_ranking_model()