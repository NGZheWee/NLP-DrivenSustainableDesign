import os
import pandas as pd
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer

# Define input and output directories
input_dir = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Topic Modelling with BERTopic\input'
output_dir = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Topic Modelling with BERTopic\output'
os.makedirs(output_dir, exist_ok=True)

# Load pre-trained SentenceTransformer model for generating embeddings
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize BERTopic without UMAP (for handling small files without dimensional reduction issues)
topic_model = BERTopic(umap_model=None)


# Function to process each file, handling smaller files by avoiding dimensionality reduction
def process_file(file_path, output_dir):
    # Load data
    df = pd.read_csv(file_path)

    # Ensure 'content' column exists
    if 'content' not in df.columns:
        print(f"Column 'content' not found in {file_path}")
        return

    # Preprocess text data (basic cleaning)
    df['content'] = (
        df['content'].fillna('')
            .str.lower()
            .str.replace(r'\W', ' ', regex=True)
            .str.replace(r'\s+', ' ', regex=True)
    )

    # Generate embeddings for the 'content' data
    content_texts = df['content'].tolist()
    embeddings = embedding_model.encode(content_texts, show_progress_bar=True)

    # Apply BERTopic only if there are enough samples
    if len(content_texts) > 5:  # Only apply if more than a minimal number of entries
        topics, _ = topic_model.fit_transform(content_texts, embeddings)
        topic_info = topic_model.get_topic_info()

        # Save topics to an output file
        file_name = os.path.basename(file_path).replace('.csv', '_BERTtopics.txt')
        output_path = os.path.join(output_dir, file_name)

        with open(output_path, 'w', encoding='utf-8') as f:
            for _, row in topic_info.iterrows():
                topic_num = row['Topic']
                if topic_num != -1:  # Ignore outliers
                    f.write(f"Topic {topic_num}: {row['Name']}\n")
                    top_words = topic_model.get_topic(topic_num)
                    words = ", ".join([word[0] for word in top_words])
                    f.write(f"Top Words: {words}\n\n")
        print(f"Topics for {file_name} saved to {output_path}")
    else:
        print(f"File {file_path} has too few entries for topic modeling.")


# Process each CSV file in the input directory
for file_name in os.listdir(input_dir):
    if file_name.endswith('.csv'):
        file_path = os.path.join(input_dir, file_name)
        process_file(file_path, output_dir)
