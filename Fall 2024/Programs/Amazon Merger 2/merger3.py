import pandas as pd
import os
import glob
import re

# Define paths
output1_folder = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Amazon Merger 2\output1'
input_products_folder = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Amazon Merger 2\input_products'
output2_folder = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Amazon Merger 2\output2'

# Ensure the output folder exists
if not os.path.exists(output2_folder):
    os.makedirs(output2_folder)

# Define final column order
final_columns = [
    'name', 'price', 'description', 'sustainability_features', 'product_features',
    'product_affordances', 'rating_product', 'product_page_url', 'product_id',
    'review_url', 'author', 'date', 'rating_customer', 'content',
    'BERT_sentiment', 'GPT_sentiment'
]


# Function to extract product_id from a URL
def extract_product_id(url):
    csv_match = re.search(r'/dp/(\w+)', url)  # Extract product_id from '/dp/' pattern
    if csv_match:
        return csv_match.group(1)

    xlsx_match = re.search(r'/product-reviews/(\w+)', url)  # Extract from '/product-reviews/' pattern
    if xlsx_match:
        return xlsx_match.group(1)

    return None  # If no match, return None


# Process each file in the output1 folder
for output1_file in glob.glob(os.path.join(output1_folder, '*.csv')):
    base_filename = os.path.basename(output1_file)
    input_products_file = os.path.join(input_products_folder, base_filename.replace('_Final.csv', '.csv'))

    # Check if the corresponding input_products file exists
    if os.path.exists(input_products_file):
        try:
            # Load both dataframes
            df_output1 = pd.read_csv(output1_file)
            df_input_products = pd.read_csv(input_products_file)

            # Extract product_id from product_page_url in input_products
            df_input_products['product_id'] = df_input_products['product_page_url'].apply(extract_product_id)

            # Select necessary columns (product_id, product_features, product_affordances)
            df_input_products = df_input_products[['product_id', 'product_features', 'product_affordances']]

            # Perform a left join to ensure all rows in output1 retain product features and affordances
            merged_df = pd.merge(df_output1, df_input_products, on='product_id', how='left')

            # Use the recommended method to fill missing values without triggering warnings
            merged_df = merged_df.assign(
                product_features=merged_df['product_features'].fillna("No Features Available"),
                product_affordances=merged_df['product_affordances'].fillna("No Affordances Available")
            )

            # Remove duplicates based on 'product_id', 'author', and 'content'
            merged_df = merged_df.drop_duplicates(subset=['product_id', 'author', 'content'], keep='first')

            # Reorder columns as specified
            merged_df = merged_df[final_columns]

            # Output file path
            output2_file = os.path.join(output2_folder, base_filename)

            # Save the merged DataFrame
            merged_df.to_csv(output2_file, index=False)
            print(f"Successfully merged and deduplicated: {output2_file}")

        except Exception as e:
            print(f"Error merging {base_filename}: {e}")
    else:
        print(f"Matching input_products file for {base_filename} not found.")

print("Merging and deduplication process complete.")
