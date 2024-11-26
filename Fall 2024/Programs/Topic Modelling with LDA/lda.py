import os
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

# Define input and output directories
input_dir = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Topic Modelling with LDA\input'
output_dir = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Topic Modelling with LDA\output'
os.makedirs(output_dir, exist_ok=True)


# Function to apply LDA topic modeling to each file
def lda_topic_modeling(file_path, output_dir):
    # Load data
    df = pd.read_csv(file_path)

    # Ensure 'content' column exists
    if 'content' not in df.columns:
        print(f"Column 'content' not found in {file_path}")
        return

    # Preprocess text data (basic cleaning)
    df['content'] = df['content'].fillna('').str.lower().str.replace(r'\W', ' ', regex=True).str.replace(r'\s+', ' ',
                                                                                                         regex=True)

    # Vectorize the text data
    vectorizer = CountVectorizer(max_df=0.95, min_df=2, stop_words='english')
    X = vectorizer.fit_transform(df['content'])

    # Apply LDA
    lda = LatentDirichletAllocation(n_components=10, random_state=42)
    lda.fit(X)

    # Extract and display topics
    def display_topics(model, feature_names, no_top_words):
        topics = []
        for topic_idx, topic in enumerate(model.components_):
            topics.append(" ".join([feature_names[i] for i in topic.argsort()[:-no_top_words - 1:-1]]))
        return topics

    topics = display_topics(lda, vectorizer.get_feature_names_out(), 10)

    # Save topics to an output file
    file_name = os.path.basename(file_path).replace('.csv', '_LDAtopics.txt')
    output_path = os.path.join(output_dir, file_name)

    with open(output_path, 'w', encoding='utf-8') as f:
        for idx, topic in enumerate(topics):
            f.write(f"Topic {idx + 1}: {topic}\n")

    print(f"Topics for {file_name} saved to {output_path}")


# Loop over files in the input directory and process each
for file_name in os.listdir(input_dir):
    if file_name.endswith('.csv'):
        file_path = os.path.join(input_dir, file_name)
        lda_topic_modeling(file_path, output_dir)
