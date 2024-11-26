import os
import pandas as pd
import json
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF

# Directories for filtering
input_dir = r"D:\OneDrive\UC Berkeley\Sustainable Design Insights\Databases\V6 GPT ABSA"
output_filtered_dir = r"D:\OneDrive\UC Berkeley\Sustainable Design Insights\Databases\V7 Sustainability Info\Excels_Sustainability Reviews"
os.makedirs(output_filtered_dir, exist_ok=True)

# Directories for topic modeling
lda_output_dir = r"D:\OneDrive\UC Berkeley\Sustainable Design Insights\Databases\V7 Sustainability Info\Modelled Topics_LDA"
nmf_output_dir = r"D:\OneDrive\UC Berkeley\Sustainable Design Insights\Databases\V7 Sustainability Info\Modelled Topics_NMF"
os.makedirs(lda_output_dir, exist_ok=True)
os.makedirs(nmf_output_dir, exist_ok=True)

# Aspects to check (excluding User Experience aspects)
aspects_to_check = [
    "General Sustainability", "Material: Bio Friendly", "Material: Chemical Contents",
    "Material: Recyclability", "Material: Waste", "Packaging",
    "Environment: Bioenvironment", "Environment: Climate", "Energy: Consumption",
    "Energy: Renewability", "Manufacturing Process: Production", "Manufacturing Process: Worker",
    "Manufacturing Process: Supply"
]

# Parameters for topic modeling
n_topics = 10  # Number of topics
n_top_words = 10  # Number of top words to display per topic

# Initialize vectorizers
lda_vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
nmf_vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)


# Function to filter rows in a CSV file
def filter_csv(input_file, output_file):
    print(f"Processing {input_file}...")
    # Read the CSV file
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Error reading {input_file}: {e}")
        return None

    if df.empty:
        print(f"{input_file} is empty. Skipping.")
        return None

    # Filter rows
    filtered_rows = []
    for index, row in df.iterrows():
        try:
            # Parse the ABSA_GPT column
            absa_gpt = json.loads(row["GPT_ABSA"])

            # Check if any specified aspects have a value other than 0
            if any(absa_gpt.get(aspect, 0) != 0 for aspect in aspects_to_check):
                filtered_rows.append(row)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Skipping row {index}: Invalid JSON or missing GPT_ABSA column. Error: {e}")

    # Create a new DataFrame from the filtered rows
    filtered_df = pd.DataFrame(filtered_rows)

    if filtered_df.empty:
        print(f"No valid rows after filtering in {input_file}.")
        return None

    # Save the filtered DataFrame to a new CSV file
    filtered_df.to_csv(output_file, index=False)
    print(f"Filtered data saved to {output_file}")
    return output_file


# Function to display topics
def display_topics(model, feature_names, no_top_words):
    topics = []
    for topic_idx, topic in enumerate(model.components_):
        topics.append(" ".join([feature_names[i] for i in topic.argsort()[:-no_top_words - 1:-1]]))
    return topics


# Function to apply LDA topic modeling
def lda_topic_modeling(file_path, output_dir):
    try:
        df = pd.read_csv(file_path)
        if 'content' not in df.columns or df['content'].dropna().empty:
            print(f"No valid 'content' column in {file_path}. Skipping LDA.")
            return
    except Exception as e:
        print(f"Error reading {file_path} for LDA: {e}")
        return

    # Preprocess text data
    df['content'] = df['content'].fillna('').str.lower().str.replace(r'\W', ' ', regex=True).str.replace(r'\s+', ' ', regex=True)

    # Check if the number of rows is sufficient for LDA
    if len(df) < 2:
        print(f"Not enough documents for LDA in {file_path}. Producing empty output.")
        file_name = os.path.basename(file_path).replace('.csv', '_LDAtopics.txt')
        output_path = os.path.join(output_dir, file_name)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("No valid topics: Not enough data.\n")
        print(f"Empty LDA output saved to {output_path}")
        return

    # Vectorize the text data
    X = lda_vectorizer.fit_transform(df['content'])

    # Apply LDA
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    lda.fit(X)

    # Extract topics
    topics = display_topics(lda, lda_vectorizer.get_feature_names_out(), n_top_words)

    # Save topics to an output file
    file_name = os.path.basename(file_path).replace('.csv', '_LDAtopics.txt')
    output_path = os.path.join(output_dir, file_name)

    with open(output_path, 'w', encoding='utf-8') as f:
        for idx, topic in enumerate(topics):
            f.write(f"Topic {idx + 1}: {topic}\n")

    print(f"LDA topics for {file_name} saved to {output_path}")


# Function to apply NMF topic modeling
def nmf_topic_modeling(file_path, output_dir):
    try:
        df = pd.read_csv(file_path)
        if 'content' not in df.columns or df['content'].dropna().empty:
            print(f"No valid 'content' column in {file_path}. Skipping NMF.")
            return
    except Exception as e:
        print(f"Error reading {file_path} for NMF: {e}")
        return

    # Preprocess text data
    df['content'] = df['content'].fillna('').str.lower().str.replace(r'\W', ' ', regex=True).str.replace(r'\s+', ' ', regex=True)

    # Check if the number of rows is sufficient for NMF
    if len(df) < 2:
        print(f"Not enough documents for NMF in {file_path}. Producing empty output.")
        file_name = os.path.basename(file_path).replace('.csv', '_NMFtopics.txt')
        output_path = os.path.join(output_dir, file_name)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("No valid topics: Not enough data.\n")
        print(f"Empty NMF output saved to {output_path}")
        return

    # Vectorize the text data
    term_matrix = nmf_vectorizer.fit_transform(df['content'])

    # Apply NMF
    nmf_model = NMF(n_components=n_topics, random_state=42, max_iter=400)  # Increased iterations for convergence
    nmf_model.fit(term_matrix)

    # Extract topics
    topics = display_topics(nmf_model, nmf_vectorizer.get_feature_names_out(), n_top_words)

    # Save topics to an output file
    file_name = os.path.basename(file_path).replace('.csv', '_NMFtopics.txt')
    output_path = os.path.join(output_dir, file_name)

    with open(output_path, 'w', encoding='utf-8') as f:
        for idx, topic in enumerate(topics):
            f.write(f"Topic {idx + 1}: {topic}\n")

    print(f"NMF topics for {file_name} saved to {output_path}")


# Process all files in the input directory
def process_all_files(input_dir, filtered_dir, lda_output_dir, nmf_output_dir):
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".csv"):
            input_file = os.path.join(input_dir, file_name)
            filtered_file = os.path.join(filtered_dir, file_name)

            # Filter rows
            filtered_file = filter_csv(input_file, filtered_file)
            if filtered_file is None:
                continue

            # Apply topic modeling on filtered data
            lda_topic_modeling(filtered_file, lda_output_dir)
            nmf_topic_modeling(filtered_file, nmf_output_dir)


# Run the processing
process_all_files(input_dir, output_filtered_dir, lda_output_dir, nmf_output_dir)
