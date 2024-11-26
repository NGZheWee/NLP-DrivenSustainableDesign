import os
import re
from openai import OpenAI

# OpenAI client initialization
client = OpenAI(
    organization='org-P3ku0rZnfoQcLhZDOFipNeoJ',
    project='proj_NdtqWQ2yFoHGoSMlUyDzHSHJ',
    api_key='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'
)

# Directories for input and output
input_folder = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Topic Modelling with GPT\input2'
output_folder = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Topic Modelling with GPT\output'
os.makedirs(output_folder, exist_ok=True)


# Function to extract product category from file name
def extract_product_category(file_name):
    match = re.search(r'_(.*?)_', file_name)
    return match.group(1).replace('_', ' ') if match else 'Product'


# Function to interact with OpenAI API for topic modeling on each chunk
def generate_topics(text, category):
    prompt = f"""
    Please perform topic modeling on the following snippets of {category} product reviews, separated by empty lines. Topic modeling is a method that identifies key themes or subjects discussed in text data by grouping similar phrases or words together. For each review snippet, identify the main topics being discussed and output them in simple, full sentences, one per line. Please summarize each topic to capture the core idea or common themes within the review snippets.

    Reviews:
    {text}
    """

    # Send prompt to OpenAI API
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for topic modeling."},
            {"role": "user", "content": prompt}
        ]
    )

    # Extract and return the response
    response = completion.choices[0].message.content.strip()
    return response


# Function to split text into chunks to fit model’s token limit
def split_text_into_chunks(text, max_tokens=120000):
    words = text.split()
    chunks = []
    current_chunk = []

    # Iterate over words and build chunks
    for word in words:
        current_chunk.append(word)
        if len(" ".join(current_chunk)) >= max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


# Function to process each txt file and save topic modeling output
def process_txt(input_file, output_file):
    print(f"Processing file: {input_file}...")

    # Read the content of the txt file
    with open(input_file, 'r', encoding='utf-8') as f:
        text_content = f.read()

    # Extract product category from file name
    file_name = os.path.basename(input_file)
    product_category = extract_product_category(file_name)

    # Split the text into manageable chunks
    text_chunks = split_text_into_chunks(text_content, max_tokens=120000)

    # Generate topics for each chunk and combine the results
    combined_summary = ""
    for idx, chunk in enumerate(text_chunks):
        print(f"Processing chunk {idx + 1} of {len(text_chunks)} for file: {input_file}")
        chunk_summary = generate_topics(chunk, product_category)
        combined_summary += f"Chunk {idx + 1}:\n{chunk_summary}\n\n"

    # Save the combined summary to a .txt file in the output folder
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(combined_summary)

    print(f"Completed processing for {input_file}. Output saved to {output_file}")


# Function to process all txt files in the input directory
def process_all_files(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    # Iterate over all files in the input directory
    for file_name in os.listdir(input_folder):
        # Process only .txt files
        if file_name.endswith('.txt'):
            input_file = os.path.join(input_folder, file_name)
            output_file = os.path.join(output_folder, file_name.replace('.txt', '_topics.txt'))

            # Process the file
            process_txt(input_file, output_file)


# Run the processing on all files
process_all_files(input_folder, output_folder)
