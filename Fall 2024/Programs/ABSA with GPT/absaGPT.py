import os
import pandas as pd
import json
import re
from openai import OpenAI

# OpenAI client initialization
client = OpenAI(
    organization='org-P3ku0rZnfoQcLhZDOFipNeoJ',
    project='proj_NdtqWQ2yFoHGoSMlUyDzHSHJ',
    api_key='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'
)

# Directories for input and output
input_directory = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\ABSA with GPT\input'
output_directory = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\ABSA with GPT\output'
os.makedirs(output_directory, exist_ok=True)

# Template for expected JSON structure
expected_structure = {
    "General Sustainability": 0,
    "Material: Bio Friendly": 0,
    "Material: Chemical Contents": 0,
    "Material: Recyclability": 0,
    "Material: Waste": 0,
    "Packaging": 0,
    "Environment: Bioenvironment": 0,
    "Environment: Climate": 0,
    "Energy: Consumption": 0,
    "Energy: Renewability": 0,
    "Manufacturing Process: Production": 0,
    "Manufacturing Process: Worker": 0,
    "Manufacturing Process: Supply": 0,
    "User Experience: Price": 0,
    "User Experience: Quality/Performance": 0,
    "User Experience: Safety": 0
}

# Task prompt for ABSA
def generate_absa_prompt(product_name, comment):
    return f"""
    Task Description: Aspect-Based Sentiment Analysis for Sustainability Evaluation.

    Input:
    Given the customer comment "{comment}" about the product "{product_name}", analyze the sentiment of the comment across the following sustainability dimensions and update the corresponding rating in the provided JSON format. Use the following guidelines for assigning sentiment ratings:

    Positive Sentiment: Assign a value of 1 if the comment expresses positive sentiment about the aspect.
    Negative Sentiment: Assign a value of -1 if the comment expresses negative sentiment about the aspect.
    Neutral or No Mention: Assign a value of 0 if the comment is neutral about the aspect or does not mention it.

    Definitions of Dimensions:
    - General Sustainability: The overall impression of the product's commitment to sustainability.
    - Material: Bio Friendly: Whether the materials used in the product are environmentally friendly, such as biodegradable or naturally sourced materials.
    - Material: Chemical Contents: Comments on the presence or absence of harmful chemicals in the product materials.
    - Material: Recyclability: The ease with which the product materials can be recycled.
    - Material: Waste: Whether the product reduces waste during its lifecycle or promotes waste reduction.
    - Packaging: Sentiment about the sustainability of the product packaging, including its eco-friendliness or minimal use of non-recyclable materials.
    - Environment: Bioenvironment: Impact of the product on the natural environment, including wildlife and ecosystems.
    - Environment: Climate: Comments on how the product affects the climate, such as reducing carbon footprint.
    - Energy: Consumption: Sentiment about the product’s energy usage or efficiency.
    - Energy: Renewability: Whether the product uses or promotes renewable energy sources.
    - Manufacturing Process: Production: The sustainability of the production process, including energy efficiency and material usage.
    - Manufacturing Process: Worker: Comments on ethical labor practices in the product’s manufacturing process.
    - Manufacturing Process: Supply: Sentiment about the sustainability of the supply chain, including transportation and sourcing of materials.
    - User Experience: Price: Sentiment about the affordability or value-for-money of the product.
    - User Experience: Quality/Performance: The perceived quality, durability, and performance of the product.
    - User Experience: Safety: Comments about the safety of the product during its use.

    Output:
    Using chain-of-thought reasoning, analyze the sentiment step-by-step for each dimension and ensure consistency in ratings. After your analysis, output only the JSON in the following format with nothing else:
    {json.dumps(expected_structure, indent=2)}
    """

# Function to clean and validate JSON response
def clean_and_validate_json(response):
    # Remove backticks and any surrounding text that isn't JSON
    match = re.search(r'\{.*\}', response, re.DOTALL)
    if match:
        response = match.group(0)
    else:
        raise ValueError("No valid JSON found in response.")

    # Try parsing the cleaned response
    try:
        response_json = json.loads(response)
        # Check if the keys match the expected structure
        if set(response_json.keys()) == set(expected_structure.keys()):
            return response_json
        else:
            raise ValueError("JSON keys do not match the expected structure.")
    except json.JSONDecodeError:
        raise ValueError("Failed to parse JSON.")

# Function to interact with OpenAI API for ABSA
def perform_absa(product_name, comment):
    prompt = generate_absa_prompt(product_name, comment)

    while True:
        # Interact with the GPT-4 OpenAI API
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for Aspect-Based Sentiment Analysis."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract the response
        response = completion.choices[0].message.content.strip()

        try:
            # Validate and clean the response
            return clean_and_validate_json(response)
        except ValueError as e:
            print(f"Invalid JSON: {response}. {e} Reprompting...")
            prompt = f"""
            Your previous response did not match the required JSON structure or format. Please strictly follow this format:
            {json.dumps(expected_structure, indent=2)}
            """

# Function to process each CSV file
def process_csv(input_file, output_file):
    print(f"Starting processing for {input_file}...")

    # Load the input CSV file
    df = pd.read_csv(input_file)

    # Initialize empty list to store the ABSA results
    absa_results = []

    # Iterate over each row in the CSV
    for index, row in df.iterrows():
        product_name = row['name']
        comment = row['content']

        # Perform ABSA using the OpenAI API
        absa_json = perform_absa(product_name, comment)

        # Append the JSON string as the result
        absa_results.append(json.dumps(absa_json))

    # Add the extracted data as a new column to the dataframe
    df['GPT_ABSA'] = absa_results

    # Save the updated dataframe to the output CSV file
    df.to_csv(output_file, index=False)
    print(f"Completed processing for {input_file}. Output saved to {output_file}")

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
