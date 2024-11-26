import pandas as pd
import torch
from transformers import BertTokenizer, BertForSequenceClassification
import matplotlib.pyplot as plt
import seaborn as sns
import re
from tqdm import tqdm
import os

# Define paths for the input and output directories
input_folder = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Sentiment Analysis with BERT\input'
output_folder = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Sentiment Analysis with BERT\output'

# Ensure the output folder exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Load pre-trained BERT tokenizer and model for sentiment analysis
tokenizer = BertTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
model = BertForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')

# Check if GPU is available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

# Function to get sentiment scores using BERT
def get_sentiment_score(review):
    try:
        inputs = tokenizer(review, return_tensors='pt', truncation=True, padding=True, max_length=512)
        inputs = {key: value.to(device) for key, value in inputs.items()}
        outputs = model(**inputs)
        scores = outputs.logits.detach().cpu().numpy()
        sentiment = scores.argmax(axis=1)[0]
        return sentiment - 2  # Adjusting to range [-2, 2] to align with VADER's compound score range
    except Exception as e:
        print(f"Error processing review: {review[:30]}... Error: {e}")
        return None

# Function to clean price strings and convert to float if necessary
def clean_price(price):
    # If the price is already a float or integer, return it as is
    if isinstance(price, (int, float)):
        return price
    elif isinstance(price, str):
        try:
            # Remove currency symbols and commas before extracting the number
            price = re.sub(r'[^\d.]', '', price)
            return float(re.findall(r'\d+\.\d+', price)[0])
        except (IndexError, ValueError):
            return None
    else:
        return None


# Function to process individual files
def process_file(file_path):
    # Load the CSV file
    df = pd.read_csv(file_path)

    # Rename rating_x and rating_y
    df = df.rename(columns={
        'rating_x': 'rating_product',
        'rating_y': 'rating_customer'
    })

    # Ensure all entries in 'content' column are strings
    df['content'] = df['content'].astype(str)

    # Apply sentiment analysis on the reviews with progress bar
    tqdm.pandas()
    df['sentiment'] = df['content'].progress_apply(get_sentiment_score)

    # Apply the cleaning function to the 'price' column
    df['price'] = df['price'].apply(clean_price)

    # Ensure 'rating_product', 'rating_customer', and 'number_of_reviews' are numerical values
    df['rating_product'] = df['rating_product'].str.extract(r'(\d+\.\d+)').astype(float)

    # Modify the lambda function to handle non-string values in rating_customer
    df['rating_customer'] = df['rating_customer'].apply(
        lambda x: 1 if isinstance(x, str) and 'one' in x else (
            2 if isinstance(x, str) and 'two' in x else (
                3 if isinstance(x, str) and 'three' in x else (
                    4 if isinstance(x, str) and 'four' in x else (
                        5 if isinstance(x, str) and 'five' in x else None)))))

    # Handle NaN values in 'number_of_reviews': fill NaN with 0 or skip rows
    df['number_of_reviews'] = df['number_of_reviews'].str.extract(r'(\d+)')
    df['number_of_reviews'] = df['number_of_reviews'].fillna(0).astype(int)  # Fill NaN with 0

    # Drop rows with missing price or other important columns for the correlation matrix calculation
    correlation_df = df.dropna(subset=['price', 'sentiment', 'rating_product', 'rating_customer', 'number_of_reviews'])

    # Columns of interest for correlation
    columns_of_interest = ['sentiment', 'rating_product', 'rating_customer', 'price', 'number_of_reviews']

    # Only compute the correlation matrix if we have enough valid data
    if not correlation_df.empty:
        correlation_matrix = correlation_df[columns_of_interest].corr()

        # Plot the correlation matrix if there is valid data
        plt.figure(figsize=(12, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
        plt.title(f'Correlation Matrix for {os.path.basename(file_path)}')

        # Save the plot automatically
        plot_file = os.path.join(output_folder, os.path.basename(file_path).replace('.csv', '_correlation_matrix.png'))
        plt.savefig(plot_file)
        plt.close()  # Close the plot to avoid manual intervention
        print(f"Correlation matrix saved: {plot_file}")
    else:
        print(f"No valid data for correlation matrix in {file_path}")

    # Save the updated dataframe to a new CSV file in the output folder
    output_file = os.path.join(output_folder, os.path.basename(file_path).replace('.csv', '_with_BERT_Sentiment.csv'))
    df.to_csv(output_file, index=False)
    print(f"Processed and saved: {output_file}")


# Process all CSV files in the input folder
for file_name in os.listdir(input_folder):
    if file_name.endswith('.csv'):
        file_path = os.path.join(input_folder, file_name)
        process_file(file_path)

print("Processing complete for all files.")
