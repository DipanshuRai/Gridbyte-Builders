import pandas as pd
import os
import pickle
import sys


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.trie_data_structure import Trie


def build_and_save_trie():
    """
    Builds the autosuggest Trie from the query log and saves it to a file.
    """
    print("--- Starting Autosuggest Index (Trie) Generation ---")
    
    query_log_path = '../central_data/query_product_log.csv'
    output_path = '../central_data/autosuggest_trie.pkl'

    try:
        log_df = pd.read_csv(query_log_path)
    except FileNotFoundError:
        print(f"Error: Query log not found at {query_log_path}")
        print("Please run 'generate_query_log.py' first.")
        return

    print("Calculating frequencies of each search query...")
    query_counts = log_df['search_query'].value_counts()
    
    print("Building the Trie with query data...")
    trie = Trie()
    for query, count in query_counts.items():
        trie.insert(str(query), int(count))

    print(f"Saving the Trie to {output_path}...")
    try:
        with open(output_path, 'wb') as f:
            pickle.dump(trie, f)
        print(f"✅ Success! Autosuggest Trie has been built and saved.")
    except Exception as e:
        print(f"❌ Error saving Trie file: {e}")

if __name__ == '__main__':
    build_and_save_trie()