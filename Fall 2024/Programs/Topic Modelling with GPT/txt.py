import os
import pandas as pd

# Define input and output directories
input_folder = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Topic Modelling with GPT\input'
output_folder = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Topic Modelling with GPT\input2'
os.makedirs(output_folder, exist_ok=True)


# Function to process each CSV file and save 'content' column to a txt file
def extract_content_to_txt(input_file, output_file):
    print(f"Processing file: {input_file}")

    # Load the CSV file
    df = pd.read_csv(input_file)

    # Extract 'content' column, drop NaNs, and join rows with two newlines as separators
    content_text = "\n\n".join(df['content'].dropna().astype(str).tolist())

    # Write the content to the output text file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content_text)

    print(f"Extracted content saved to {output_file}")


# Process all CSV files in the input directory
for file_name in os.listdir(input_folder):
    if file_name.endswith('.csv'):
        # Define input and output file paths
        input_file = os.path.join(input_folder, file_name)
        output_file = os.path.join(output_folder, file_name.replace('.csv', '.txt'))

        # Extract content and save to txt
        extract_content_to_txt(input_file, output_file)
