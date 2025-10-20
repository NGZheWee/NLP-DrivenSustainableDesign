import pandas as pd
import numpy as np
import os
import re
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

########################################
# 1. LOAD CSV
########################################
file_path = r"D:\OneDrive\Academic History\Research\NLP-Driven Sustainable Design_CoDesign Lab\Co-Design Lab\Databases_IDETC\V2 Lemmatized\Final_lemmatizedAffordances.csv"
df = pd.read_csv(file_path, encoding='ISO-8859-1')

########################################
# 2. CLEAN & PARSE AFFORDANCES
########################################
df["product_affordances_lemmatized"] = (
    df["product_affordances_lemmatized"]
        .str.extract(r'\[(.*?)\]')[0]  # capture text inside [ ... ]
        .str.replace('"', '', regex=False)  # remove double quotes
        .str.split(r',\s*')  # split on comma + optional spaces
)

# Ensure each row is a list (instead of NaN or float)
df["product_affordances_lemmatized"] = df["product_affordances_lemmatized"].apply(
    lambda x: x if isinstance(x, list) else []
)

########################################
# 3. LEMMATIZE THE 'description' COLUMN
########################################
def simple_lemmatize(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)  # remove punctuation
    tokens = text.split()
    # naive suffix stripping (NOT real lemmatization!)
    lemmas = []
    for t in tokens:
        if len(t) > 2 and t.endswith('es'):
            t = t[:-2]
        elif len(t) > 1 and t.endswith('s'):
            t = t[:-1]
        lemmas.append(t)
    return lemmas

df["description"] = df["description"].astype(str)
df["description_lemmatized"] = df["description"].apply(simple_lemmatize)

########################################
# 4. EXTRACT TOP-N MOST FREQUENT AFFORDANCE WORDS
########################################
all_aff_words = []
for aff_list in df["product_affordances_lemmatized"]:
    all_aff_words.extend(aff_list)

aff_word_counts = pd.Series(all_aff_words).value_counts()
top_n = 20
top_aff_words = aff_word_counts.head(top_n).index.tolist()
print(f"\nTop {top_n} affordances:\n{top_aff_words}\n")

########################################
# 5. CREATE BINARY COLUMNS FOR PRESENCE
########################################
for w in top_aff_words:
    df[f"aff_{w}"] = 0
    df[f"desc_{w}"] = 0

for i, row in df.iterrows():
    aff_set = set(row["product_affordances_lemmatized"])
    desc_set = set(row["description_lemmatized"])

    for w in top_aff_words:
        if w in aff_set:
            df.at[i, f"aff_{w}"] = 1
        if w in desc_set:
            df.at[i, f"desc_{w}"] = 1

########################################
# 6. CORRELATION PER WORD
########################################
# For each word w, we find corr(aff_w, desc_w).

results = []
for w in top_aff_words:
    aff_series = df[f"aff_{w}"]
    desc_series = df[f"desc_{w}"]

    # Pearson correlation
    corr_value = aff_series.corr(desc_series)  # can be NaN if no variation
    # Co-occurrence metrics
    both = ((aff_series == 1) & (desc_series == 1)).sum()
    either = ((aff_series == 1) | (desc_series == 1)).sum()
    jaccard = both / either if either > 0 else 0

    results.append((w, corr_value, both, either, jaccard))

df_results = pd.DataFrame(
    results, columns=["Word", "Correlation", "Count_Both", "Count_Either", "Jaccard"]
)
# Sort by correlation descending
df_results = df_results.sort_values("Correlation", ascending=False)

print("\nIndividual Word Correlation:\n", df_results)

########################################
# 7. BAR CHART OF CORRELATION
########################################
plt.figure(figsize=(10, 6))
sns.barplot(x="Correlation", y="Word", data=df_results, palette="viridis")
plt.title("Correlation of Each Affordance Word vs. Its Presence in Description")
plt.xlim(-1, 1)
plt.tight_layout()

# Save the bar chart
output_folder = os.path.dirname(file_path)
output_image = os.path.join(output_folder, "AffordanceWord_Correlation_Bar.png")
plt.savefig(output_image, dpi=300)
plt.close()

print(f"✅ Bar chart saved at: {output_image}")

########################################
# 8. SAVE CORRELATION DATA TO CSV
########################################
output_csv = os.path.join(output_folder, "AffordanceWord_Correlation_Data.csv")
df_results.to_csv(output_csv, index=False, encoding='ISO-8859-1')

print(f"✅ Correlation data saved at: {output_csv}")

########################################
# 9. OPTIONAL: PRINT HIGHEST JACCARD
########################################
df_jaccard = df_results.sort_values("Jaccard", ascending=False)
print("\nWords with highest Jaccard (co-occurrence ratio):\n", df_jaccard.head(10))
print("\nDone.")
