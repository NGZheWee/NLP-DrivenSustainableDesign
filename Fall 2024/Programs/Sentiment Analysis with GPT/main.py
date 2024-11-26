import os
import pandas as pd
from openai import OpenAI

# OpenAI client initialization
client = OpenAI(
    organization='org-P3ku0rZnfoQcLhZDOFipNeoJ',
    project='proj_NdtqWQ2yFoHGoSMlUyDzHSHJ',
    api_key='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'
)

# Directories for input and output
input_folder = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Sentiment Analysis with GPT\input2'
output_folder = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Sentiment Analysis with GPT\output'


# Function to interact with OpenAI API for sentiment analysis
def analyze_sentiment(review):
    prompt = f"""
    Analyze the sentiment of the provided review text and, using chain-of-thought reasoning, assign a single sentiment score.

    Instructions:
    1. Input: "{review}"
    2. Task: 
       - Analyze the text to determine the sentiment expressed by the customer.
       - Apply chain-of-thought reasoning to break down the sentiment step-by-step, carefully balancing different aspects of the review to reach a conclusion.
       - Ensure the final sentiment score aligns consistently with this reasoning.
    3. Sentiment Score:
       - Assign a sentiment score on a scale from -2 to 2:
         - -2: Most negative sentiment
         - -1: Slightly negative sentiment
         - 0: Neutral sentiment
         - 1: Slightly positive sentiment
         - 2: Most positive sentiment
       - The score must accurately reflect the sentiment conveyed through your reasoning.
    4. Output: Provide only the final sentiment score as a single whole number, with no additional text.
    """

    while True:
        # Send prompt to OpenAI API
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for sentiment analysis."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract and parse the response
        response = completion.choices[0].message.content.strip()

        try:
            # Attempt to convert response to an integer
            return int(response)
        except ValueError:
            # If response is not an integer, re-prompt with clarification
            print(f"Invalid response received: {response}. Retrying with clarification...")
            prompt = f"""
            Please provide only the final sentiment score as a single whole number between -2 and 2 based on the analysis of this review:
            "{review}"
            """


# Function to process each CSV file
def process_csv(input_file, output_file):
    print(f"Starting processing for {input_file}...")

    # Load the input CSV file
    df = pd.read_csv(input_file)

    # Initialize list to store the sentiment scores
    sentiment_scores = []

    # Process each row in the CSV
    for index, row in df.iterrows():
        review_content = row['content']

        # Analyze sentiment using the OpenAI API
        score = analyze_sentiment(review_content)

        # Append the score to the list
        sentiment_scores.append(score)

    # Add the new column 'sentiment' with scores to the DataFrame
    df['sentiment'] = sentiment_scores

    # Save the updated DataFrame to the output CSV file
    df.to_csv(output_file, index=False)
    print(f"Completed processing for {input_file}. Output saved to {output_file}")


# Function to process all CSV files in the input directory
def process_all_files(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    # Iterate over all files in the input directory
    for file_name in os.listdir(input_folder):
        # Process only CSV files
        if file_name.endswith('.csv'):
            input_file = os.path.join(input_folder, file_name)
            output_file = os.path.join(output_folder, file_name)

            # Process the file
            process_csv(input_file, output_file)


# Run the processing on all files
process_all_files(input_folder, output_folder)
