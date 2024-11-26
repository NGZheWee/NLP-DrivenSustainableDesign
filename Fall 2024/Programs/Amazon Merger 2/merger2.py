import pandas as pd
import os
import glob

# Define paths
input_folder_bert = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Amazon Merger 2\input_BERT'
input_folder_gpt = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Amazon Merger 2\input_GPT'
output_folder = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Amazon Merger 2\output1'

# Ensure the output folder exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Define columns for final output in required order
output_columns = [
    'name', 'price', 'description', 'sustainability_features', 'rating_product',
    'product_page_url', 'product_id', 'review_url', 'author', 'date',
    'rating_customer', 'content', 'BERT_sentiment', 'GPT_sentiment'
]


# Helper function to extract base filename without directory or extension
def extract_base_filename(file_path):
    return os.path.basename(file_path).replace('_merged_with_BERT_Sentiment.csv', '')


# Process each BERT file and its corresponding GPT file
for bert_file in glob.glob(os.path.join(input_folder_bert, '*.csv')):
    base_filename = extract_base_filename(bert_file)
    gpt_file = os.path.join(input_folder_gpt, f"{base_filename}_merged.csv")

    # Check if the corresponding GPT file exists
    if os.path.exists(gpt_file):
        try:
            # Load both dataframes
            df_bert = pd.read_csv(bert_file)
            df_gpt = pd.read_csv(gpt_file)

            # Rename columns to standardize names across files
            df_bert = df_bert.rename(columns={
                'rating_product': 'rating_product',
                'rating_customer': 'rating_customer',
                'sentiment': 'BERT_sentiment',
                'url': 'review_url'
            })
            df_gpt = df_gpt.rename(columns={
                'rating_x': 'rating_product',
                'rating_y': 'rating_customer',
                'sentiment': 'GPT_sentiment',
                'url': 'review_url'
            })

            # Merge on 'product_id' and 'author' to avoid inconsistencies
            merged_df = pd.merge(
                df_bert, df_gpt[['product_id', 'author', 'GPT_sentiment']],
                on=['product_id', 'author'], how='left'
            )

            # Select and reorder columns according to the specified output format
            merged_df = merged_df[output_columns]

            # Output file path
            output_file = os.path.join(output_folder, f"{base_filename}_Final.csv")

            # Save the merged DataFrame
            merged_df.to_csv(output_file, index=False)
            print(f"Successfully merged: {base_filename}_Final.csv")

        except Exception as e:
            print(f"Error merging {base_filename}: {e}")
    else:
        print(f"Matching GPT file for {base_filename} not found.")

print("Merging process complete.")
