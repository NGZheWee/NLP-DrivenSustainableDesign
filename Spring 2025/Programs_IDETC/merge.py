import pandas as pd
import os

# Directory containing the CSV files
directory = 'D:/OneDrive/Academic History/Research/NLP-Driven Sustainable Design_CoDesign Lab/(2) Fall 2024/Databases/V6 GPT ABSA'
# Change this to your directory

# List to store DataFrames
dataframes = []

# Iterate over all files in the directory
for filename in os.listdir(directory):
    if filename.endswith('.csv'):
        # Extracting certifications and product_category from filename
        parts = filename.replace('_Final.csv', '').split('_')
        certification = parts[0]
        product_category = '_'.join(parts[1:-1])

        # Construct full file path
        filepath = os.path.join(directory, filename)

        # Read CSV file
        df = pd.read_csv(filepath)

        # Insert new columns
        df.insert(0, 'certifications', certification)
        df.insert(1, 'product_category', product_category)

        # Append DataFrame to the list
        dataframes.append(df)

# Concatenate all DataFrames
combined_df = pd.concat(dataframes, ignore_index=True)

# Save to a new CSV file
combined_df.to_csv('combined_output.csv', index=False)
