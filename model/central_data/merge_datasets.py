import pandas as pd

d1 = pd.read_csv('cleaned-flipkart-products.csv')
d2 = pd.read_csv('flipkart-cleaned-dataset-hi.csv')

d2_subset = d2[['asin', 'title_hi', 'description_hi']]

merged_df = pd.merge(d1, d2_subset, on='asin', how='left')  # 'left' keeps all rows from d1

merged_df.to_csv('flipkart-products-with-hindi.csv', index=False)

print("Merged file saved as 'flipkart-products-with-hindi.csv'")
