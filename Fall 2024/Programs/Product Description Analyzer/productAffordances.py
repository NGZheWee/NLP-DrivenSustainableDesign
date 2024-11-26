import os
import csv
import json
from openai import OpenAI
import pandas as pd

# OpenAI client initialization
client = OpenAI(
    organization='org-P3ku0rZnfoQcLhZDOFipNeoJ',
    project='proj_NdtqWQ2yFoHGoSMlUyDzHSHJ',
    api_key='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'
)

# Directories for input and output
input_directory = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Product Description Analyzer\input2'
output_directory = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Product Description Analyzer\output'

# Function to interact with OpenAI API for extracting product affordances
def extract_affordances(description):
    # Prepare the prompt for extracting affordances
    prompt = f"""
    Analyze the following product description: "{description}"
    Please extract the Product Affordances: An array of action verbs, nouns, and adjectives that describe how the product can be used or interacted with. Focus on action words and suffixes like "-able", "-ible", and "-ity".
    Return the result in this example format: Product Affordances: ["Affordance 1", "Affordance 2", "Affordance 3", "Affordance 4"]'.
    """

    # Interact with the GPT-4 OpenAI API
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that extracts product affordances."},
            {"role": "user", "content": prompt}
        ]
    )

    # Extract and parse the response
    response = completion.choices[0].message.content
    return response

# Function to process each CSV file
def process_csv(input_file, output_file):
    print(f"Starting processing for {input_file}...")  # Logging start of processing
    # Load the input CSV file
    df = pd.read_csv(input_file)

    # Initialize empty list to store the extracted product affordances
    affordances_list = []

    # Iterate over each row in the CSV
    for index, row in df.iterrows():
        description = row['description']

        # Extract affordances using the OpenAI API
        result = extract_affordances(description)

        # Append the result to the affordances_list
        affordances_list.append(result)

    # Add the extracted data as new columns to the dataframe
    df['product_affordances'] = affordances_list

    # Save the updated dataframe to the output CSV file
    df.to_csv(output_file, index=False)
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
            process_csv(input_file, output_file)

# Run the processing on all files
process_all_files(input_directory, output_directory)
