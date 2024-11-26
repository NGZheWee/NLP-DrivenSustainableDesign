import pandas as pd
import os
import re

# Paths
input_folder = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Amazon Merger\input'
output_folder = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Amazon Merger\output'

# Ensure the output folder exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)


# Function to extract product_id from a URL or link for both XLSX and CSV
def extract_product_id(url):
    # Extract product_id from CSV format URL (after '/dp/')
    csv_match = re.search(r'/dp/(\w+)', url)
    if csv_match:
        return csv_match.group(1)

    # Extract product_id from XLSX format URL (after '/product-reviews/')
    xlsx_match = re.search(r'/product-reviews/(\w+)', url)
    if xlsx_match:
        return xlsx_match.group(1)

    # If no match, return None
    return None


# Function to merge CSV and XLSX files based on extracted product_id
def merge_files(csv_file, xlsx_file, output_file):
    # Load the CSV and XLSX files
    csv_df = pd.read_csv(csv_file)
    xlsx_df = pd.read_excel(xlsx_file)

    # Extract 'product_id' from 'product_page_url' in the CSV and 'url' in the XLSX
    csv_df['product_id'] = csv_df['product_page_url'].apply(extract_product_id)
    xlsx_df['product_id'] = xlsx_df['url'].apply(extract_product_id)

    # Check if 'product_id' column exists in both datasets
    if 'product_id' in csv_df.columns and 'product_id' in xlsx_df.columns:
        # Merge the dataframes on 'product_id'
        merged_df = pd.merge(csv_df, xlsx_df, on='product_id', how='outer')

        # Save the merged DataFrame to the output folder
        merged_df.to_csv(output_file, index=False)
        print(f"Saved merged file to {output_file}")
    else:
        print(f"Cannot merge files {csv_file} and {xlsx_file} as 'product_id' column is missing.")


# Iterate through the input folder and find corresponding CSV and XLSX files
for file_name in os.listdir(input_folder):
    if file_name.endswith('.csv'):
        # Generate the matching XLSX filename
        base_name = file_name.replace('.csv', '')
        xlsx_file = os.path.join(input_folder, f"{base_name}.xlsx")
        csv_file = os.path.join(input_folder, file_name)

        # Check if the matching XLSX file exists
        if os.path.exists(xlsx_file):
            # Generate output file path
            output_file = os.path.join(output_folder, f"{base_name}_merged.csv")

            # Merge the files
            merge_files(csv_file, xlsx_file, output_file)
        else:
            print(f"Matching XLSX file for {file_name} not found.")

print("Merging complete.")
