import os
import json
import pandas as pd
import re
from openai import OpenAI

# **Corrected File Path**
file_path = r"D:\OneDrive\Academic History\Research\NLP-Driven Sustainable Design_CoDesign Lab\Co-Design Lab\Databases_IDETC\Mini Database\V1 Merged.xlsx"
output_path = r"D:\OneDrive\Academic History\Research\NLP-Driven Sustainable Design_CoDesign Lab\Co-Design Lab\Databases_IDETC\Mini Database\V1 Merged_Processed.xlsx"

# **Check if the file exists before reading**
if not os.path.exists(file_path):
    raise FileNotFoundError(f"❌ Error: File not found at {file_path}. Please check the filename and directory.")

# **OpenAI API Initialization**
client = OpenAI(
    organization='org-P3ku0rZnfoQcLhZDOFipNeoJ',
    project='proj_NdtqWQ2yFoHGoSMlUyDzHSHJ',
)

# **Load the Excel file**
df = pd.read_excel(file_path)
print("✅ File successfully loaded!")

# **ABSA Expected JSON Structure**
expected_absa_structure = {
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


# **Function to Interact with OpenAI for Product Features Extraction**
def extract_features(description):
    prompt = f"""
    Analyze the following product description: "{description}"
    Please extract the Product Features: An array of nouns that describe the product's components or attributes, and any relevant linking verbs.
    Return the result in this example format: Product Features: ["Feature 1", "Feature 2", "Feature 3", "Feature 4"]'.
    """
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that extracts product features."},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content.strip()


# **Function to Interact with OpenAI for Product Affordances Extraction**
def extract_affordances(description):
    prompt = f"""
    Analyze the following product description: "{description}"
    Please extract the Product Affordances: An array of action verbs, nouns, and adjectives that describe how the product can be used or interacted with. Focus on action words and suffixes like "-able", "-ible", and "-ity".
    Return the result in this example format: Product Affordances: ["Affordance 1", "Affordance 2", "Affordance 3", "Affordance 4"]'.
    """
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that extracts product affordances."},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content.strip()


# **Function to Generate ABSA Prompt**
def generate_absa_prompt(product_name, comment):
    return f"""
    Task Description: Aspect-Based Sentiment Analysis for Sustainability Evaluation.

    Input:
    Given the customer comment "{comment}" about the product "{product_name}", analyze the sentiment of the comment across the following sustainability dimensions and update the corresponding rating in the provided JSON format. Use the following guidelines for assigning sentiment ratings:

    Positive Sentiment: Assign a value of 1 if the comment expresses positive sentiment about the aspect.
    Negative Sentiment: Assign a value of -1 if the comment expresses negative sentiment about the aspect.
    Neutral or No Mention: Assign a value of 0 if the comment is neutral about the aspect or does not mention it.

    Definitions of Dimensions:
    {json.dumps(expected_absa_structure, indent=2)}

    Output:
    Using chain-of-thought reasoning, analyze the sentiment step-by-step for each dimension and ensure consistency in ratings. After your analysis, output only the JSON in the following format with nothing else:
    {json.dumps(expected_absa_structure, indent=2)}
    """


# **Function to Extract and Validate ABSA JSON**
def perform_absa(product_name, comment):
    prompt = generate_absa_prompt(product_name, comment)
    while True:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for Aspect-Based Sentiment Analysis."},
                {"role": "user", "content": prompt}
            ]
        )
        response = completion.choices[0].message.content.strip()

        try:
            # Remove non-JSON text
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                response = match.group(0)
            absa_json = json.loads(response)
            if set(absa_json.keys()) == set(expected_absa_structure.keys()):
                return absa_json
            else:
                raise ValueError("Incorrect JSON format.")
        except Exception as e:
            print(f"❌ Error parsing JSON: {response}. Retrying...")


# **Processing Data**
features_list, affordances_list, absa_list = [], [], []

for index, row in df.iterrows():
    description = row['description']
    product_name = row['name']
    comment = row['content']

    # **Extract Features**
    features = extract_features(description)
    features_list.append(features)

    # **Extract Affordances**
    affordances = extract_affordances(description)
    affordances_list.append(affordances)

    # **Perform ABSA**
    absa = perform_absa(product_name, comment)
    absa_list.append(json.dumps(absa))

# **Store Results in DataFrame**
df['product_features'] = features_list
df['product_affordances'] = affordances_list
df['GPT_ABSA'] = absa_list

# **Save Processed Data**
df.to_excel(output_path, index=False)
print(f"✅ Processing Complete! Output saved to: {output_path}")
