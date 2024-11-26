import os
import pandas as pd
import time
from openai import OpenAI

# OpenAI client initialization
client = OpenAI(
    organization='org-P3ku0rZnfoQcLhZDOFipNeoJ',
    project='proj_NdtqWQ2yFoHGoSMlUyDzHSHJ',
    api_key='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'
)

# Directories for input and output
input_directory = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Amazon Filter\input'
output_directory = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Amazon Filter\output'

# Function to check if content is in English using the OpenAI API
def is_english_content(content):
    # Prepare the prompt to determine if content is English, considering potential noise like symbols
    prompt = f"""
    Determine if the following text is written in English. Sometimes, there may be messy code or symbols in the text, 
    so please judge based on the overall sentence structure and meaning rather than individual phrases or symbols. 
    If you are unsure, assume that the text is in English.
    Answer only with 'Yes' if the text is in English, and 'No' if it is not.

    Text: "{content}"
    """

    # Initialize response
    response = None
    attempts = 3

    # Retry mechanism for API call
    for attempt in range(attempts):
        try:
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that checks the language of the content."},
                    {"role": "user", "content": prompt}
                ]
            )
            response = completion.choices[0].message.content.strip()
            break  # Exit the retry loop if successful
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            time.sleep(2)  # Wait before retrying

    # Return True if response indicates English content, else False
    return response == "Yes"

# Function to process each CSV file
def filter_english_rows(input_file, output_file):
    print(f"Starting processing for {input_file}...")  # Logging start of processing
    # Load the input CSV file
    df = pd.read_csv(input_file)

    # Initialize list to store rows with English content
    english_rows = []

    # Iterate over each row in the CSV
    for index, row in df.iterrows():
        content = row['content']

        # Check if the content is English
        if is_english_content(content):
            english_rows.append(row)

    # Convert list of English rows back to DataFrame
    english_df = pd.DataFrame(english_rows)

    # Save the filtered DataFrame to the output CSV file
    english_df.to_csv(output_file, index=False)
    print(f"Completed processing for {input_file}. Output saved to {output_file}")  # Logging completion

# Function to process all CSV files in the input directory
def process_all_files(input_directory, output_directory):
    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)

    # Iterate over all files in the input directory
    for file_name in os.listdir(input_directory):
        # Process only CSV files
        if file_name.endswith('.csv'):
            input_file = os.path.join(input_directory, file_name)
            output_file = os.path.join(output_directory, file_name)

            # Process the file
            filter_english_rows(input_file, output_file)

# Run the processing on all files
process_all_files(input_directory, output_directory)
