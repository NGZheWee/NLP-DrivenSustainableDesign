import pandas as pd
import json
import ast
import re
import nltk

from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet, stopwords

# Make sure you have downloaded these once
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('stopwords')

file_path = r"D:\OneDrive\Academic History\Research\NLP-Driven Sustainable Design_CoDesign Lab\Co-Design Lab\Databases_IDETC\Final.csv"

df = pd.read_csv(file_path, encoding="ISO-8859-1")

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Example synonym map for expansions (customize to your domain)
synonym_map = {
    "auto": "automatic",
    "runtime": "run time",
    "24h": "24 hours",
    # Add more domain-specific expansions here
}


def get_wordnet_pos(treebank_tag):
    """
    Convert Treebank POS tags to WordNet's format:
    JJ -> a, VB -> v, RB -> r, NN -> n
    """
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    else:
        return wordnet.NOUN  # fallback if none of the above


def clean_affordance_phrase(phrase):
    """
    Cleans a single affordance phrase:
      1. Lowercase
      2. Remove punctuation (except spaces)
      3. Tokenize
      4. Remove stopwords
      5. Synonym expansion
      6. POS Tag + Lemmatize
      7. Rejoin tokens => single string
    """

    # 1. Lowercase
    phrase = phrase.lower()

    # 2. Remove punctuation.
    #    Replace hyphens with spaces so that "run-time" -> "run time"
    phrase = re.sub(r"[-]", " ", phrase)        # convert hyphens to space
    phrase = re.sub(r"[^\w\s]", "", phrase)     # remove other non-word chars, keep spaces

    # 3. Tokenize
    tokens = nltk.word_tokenize(phrase)

    # 4. Remove stopwords
    tokens = [t for t in tokens if t not in stop_words]

    # 5. Synonym expansion
    expanded_tokens = []
    for token in tokens:
        if token in synonym_map:
            # e.g., "runtime" => "run time" => ["run", "time"]
            expanded_tokens.extend(synonym_map[token].split())
        else:
            expanded_tokens.append(token)

    # 6. POS Tag + Lemmatize
    tagged_tokens = nltk.pos_tag(expanded_tokens)
    final_tokens = []
    for (word, tag) in tagged_tokens:
        wn_pos = get_wordnet_pos(tag)
        lemma = lemmatizer.lemmatize(word, pos=wn_pos)
        final_tokens.append(lemma)

    # 7. Rejoin tokens to keep the entire phrase as single string
    cleaned_phrase = " ".join(final_tokens)

    return cleaned_phrase


def lemmatize_affordances(affordances):
    """
    Extract bracketed list, apply the extended cleaning pipeline to each phrase,
    and deduplicate results before returning.
    """
    if isinstance(affordances, str):
        try:
            # Extract bracketed portion
            match = re.search(r"\[(.*?)\]", affordances)
            if match:
                affordance_list_str = "[" + match.group(1) + "]"
                affordance_list = ast.literal_eval(affordance_list_str)  # Convert to list

                if isinstance(affordance_list, list):
                    cleaned_list = []
                    for phrase in affordance_list:
                        if isinstance(phrase, str):
                            cleaned_phrase = clean_affordance_phrase(phrase)
                            if cleaned_phrase:
                                cleaned_list.append(clean_affordance_phrase(phrase))

                    # Deduplicate (preserve order)
                    cleaned_deduped_list = list(dict.fromkeys(cleaned_list))

                    return f'Product Affordances: {json.dumps(cleaned_deduped_list)}'
            # If no valid bracket found
            return "Product Affordances: []"
        except (ValueError, SyntaxError):
            return "Product Affordances: []"
    return "Product Affordances: []"


df["product_affordances_lemmatized"] = df["product_affordances"].apply(lemmatize_affordances)

output_file_path = r"D:\OneDrive\Academic History\Research\NLP-Driven Sustainable Design_CoDesign Lab\Co-Design Lab\Databases_IDETC\Final_lemmatizedAffordances.csv"
df.to_csv(output_file_path, index=False, encoding="ISO-8859-1")

print(f"✅ Cleaned dataset saved to: {output_file_path}")
