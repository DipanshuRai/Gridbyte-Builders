import pandas as pd

# Replace with your actual CSV file path and column name
csv_file_path = './model/central_data/cleaned-flipkart-products.csv'
category_column = 'department'  # change to the actual column name

# Read the CSV file
df = pd.read_csv(csv_file_path)

# Get value counts (i.e., unique categories and their frequencies)
category_counts = df[category_column].value_counts()

# Print sorted categories and their counts
print("Unique Categories and Counts (Descending):")
for category, count in category_counts.items():
    print(f"{category}: {count}")