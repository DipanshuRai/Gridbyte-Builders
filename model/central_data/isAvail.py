import pandas as pd
import numpy as np

# Load your CSV file
df = pd.read_csv('flipkart-products-with-hindi.csv')  # Replace with your actual file name

# Generate random True (80%) / False (20%) values
is_available = np.random.choice([True, False], size=len(df), p=[0.8, 0.2])

# Add the column
df['isAvailable'] = is_available

# Save the updated CSV
df.to_csv('flipkart-products-with-hindi.csv', index=False)

print("New file saved as 'your_file_with_availability.csv'")
