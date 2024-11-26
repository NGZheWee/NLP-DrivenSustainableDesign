import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os

# Define paths for the input and output directories
input_folder = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Sentiment Analysis with GPT\output'
output_folder = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Sentiment Analysis with GPT\output_CM'

# Ensure the output folder exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Function to clean price strings and convert to float if necessary
def clean_price(price):
    if isinstance(price, (int, float)):
        return price
    elif isinstance(price, str):
        try:
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

    # Locate the sentiment column
    sentiment_column = next((col for col in df.columns if col.strip().lower() in ['sentiment', 'sentiment_score']), None)
    if sentiment_column is None:
        print(f"Skipping {file_path}: 'sentiment' column not found.")
        return
    
    # Rename the found sentiment column to standardize it
    df = df.rename(columns={sentiment_column: 'sentiment'})

    # Scale sentiment to 0-5 range
    df['sentiment_scaled'] = (df['sentiment'] + 2) * 5 / 4

    # Apply the cleaning function to the 'price' column
    df['price'] = df['price'].apply(clean_price)

    # Ensure 'rating_product', 'rating_customer', and 'number_of_reviews' are numerical values
    df['rating_product'] = df['rating_product'].str.extract(r'(\d+\.\d+)').astype(float)
    df['rating_customer'] = df['rating_customer'].apply(
        lambda x: 1 if isinstance(x, str) and 'one' in x else (
            2 if isinstance(x, str) and 'two' in x else (
                3 if isinstance(x, str) and 'three' in x else (
                    4 if isinstance(x, str) and 'four' in x else (
                        5 if isinstance(x, str) and 'five' in x else None)))))

    df['number_of_reviews'] = df['number_of_reviews'].str.extract(r'(\d+)').fillna(0).astype(int)

    # Drop rows with missing price or other important columns for the correlation matrix calculation
    correlation_df = df.dropna(subset=['price', 'sentiment_scaled', 'rating_product', 'rating_customer', 'number_of_reviews'])

    # Columns of interest for correlation
    columns_of_interest = ['sentiment_scaled', 'rating_product', 'rating_customer', 'price', 'number_of_reviews']

    # Only compute the correlation matrix if we have enough valid data
    if not correlation_df.empty:
        correlation_matrix = correlation_df[columns_of_interest].corr()

        # Plot the correlation matrix
        plt.figure(figsize=(12, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
        plt.title(f'Correlation Matrix for {os.path.basename(file_path)}')

        # Save the plot as an image
        plot_file = os.path.join(output_folder, os.path.basename(file_path).replace('.csv', '_correlation_matrix.png'))
        plt.savefig(plot_file)
        plt.close()  # Close the plot to avoid memory issues
        print(f"Correlation matrix saved as an image: {plot_file}")
    else:
        print(f"No valid data for correlation matrix in {file_path}")

# Process all CSV files in the input folder
for file_name in os.listdir(input_folder):
    if file_name.endswith('.csv'):
        file_path = os.path.join(input_folder, file_name)
        process_file(file_path)

print("Processing complete for all files.")
