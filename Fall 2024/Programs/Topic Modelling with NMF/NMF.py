import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF

# Define input and output directories
input_dir = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Topic Modelling with NMF\input'
output_dir = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Topic Modelling with NMF\output'
os.makedirs(output_dir, exist_ok=True)

# Parameters for chunking the data and topic modeling
chunk_size = 5000  # Adjust based on available memory
n_topics = 10  # Set the number of topics for NMF
n_top_words = 10  # Number of top words to display per topic

# Initialize TF-IDF Vectorizer
vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)  # Adjust `max_features` based on data size


# Function to display topics
def display_topics(model, feature_names, no_top_words):
    topics = []
    for topic_idx, topic in enumerate(model.components_):
        topic_terms = " ".join([feature_names[i] for i in topic.argsort()[:-no_top_words - 1:-1]])
        topics.append(f"Topic {topic_idx + 1}: {topic_terms}")
    return topics


# Function to process each file with NMF
def process_file(file_path, output_dir):
    # Load data
    df = pd.read_csv(file_path)

    # Ensure 'content' column exists
    if 'content' not in df.columns:
        print(f"Column 'content' not found in {file_path}")
        return

    # Preprocess text data
    df['content'] = (
        df['content'].fillna('')
            .str.lower()
            .str.replace(r'\W', ' ', regex=True)
            .str.replace(r'\s+', ' ', regex=True)
    )

    # Fit the vectorizer to transform the data into a term-document matrix
    term_matrix = vectorizer.fit_transform(df['content'])

    # Apply NMF model to find topics
    nmf_model = NMF(n_components=n_topics, random_state=42)
    nmf_model.fit(term_matrix)

    # Get topic terms and save them
    feature_names = vectorizer.get_feature_names_out()
    topics = display_topics(nmf_model, feature_names, n_top_words)

    # Save topics to an output file
    file_name = os.path.basename(file_path).replace('.csv', '_NMFtopics.txt')
    output_path = os.path.join(output_dir, file_name)

    with open(output_path, 'w', encoding='utf-8') as f:
        for topic in topics:
            f.write(f"{topic}\n\n")

    print(f"Topics for {file_name} saved to {output_path}")


# Process each CSV file in the input directory
for file_name in os.listdir(input_dir):
    if file_name.endswith('.csv'):
        file_path = os.path.join(input_dir, file_name)
        process_file(file_path, output_dir)
