import pandas as pd
import numpy as np
import json
import os
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend for scripts
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import StandardScaler
from scipy.spatial import ConvexHull


# **Set path to the CSV file**
file_path = r"D:\OneDrive\Academic History\Research\NLP-Driven Sustainable Design_CoDesign Lab\Co-Design Lab\Databases_IDETC\Final_lemmatizedAffordances.csv"

# **Load the dataset**
df = pd.read_csv(file_path, encoding='ISO-8859-1')

# **Extract relevant categorical values from "product_affordances_lemmatized"**
df["product_affordances_lemmatized"] = df["product_affordances_lemmatized"].str.extract(r'\[(.*?)\]')[0].str.replace('"', '').str.split(', ')

# **Extract relevant categorical values from "GPT_ABSA"**
def extract_relevant_absa(json_str):
    if isinstance(json_str, str):
        try:
            absa_dict = json.loads(json_str)
            relevant_aspects = [aspect for aspect, value in absa_dict.items() if value != 0]
            return relevant_aspects
        except json.JSONDecodeError:
            return []
    return []

df["GPT_ABSA_filtered"] = df["GPT_ABSA"].apply(extract_relevant_absa)

# **Get unique values**
all_affordances = sorted(set([item for sublist in df["product_affordances_lemmatized"].dropna() for item in sublist]))
all_gpt_absa = sorted(set([item for sublist in df["GPT_ABSA_filtered"].dropna() for item in sublist]))

# **Create contingency table**
contingency_table = pd.DataFrame(0, index=all_affordances, columns=all_gpt_absa)

# **Populate the contingency table**
for _, row in df.dropna(subset=["product_affordances_lemmatized", "GPT_ABSA_filtered"]).iterrows():
    for affordance in row["product_affordances_lemmatized"]:
        for sentiment in row["GPT_ABSA_filtered"]:
            contingency_table.at[affordance, sentiment] += 1

# **Drop empty rows and columns**
contingency_table = contingency_table.loc[(contingency_table.sum(axis=1) > 0), (contingency_table.sum(axis=0) > 0)]

# **Perform Correspondence Analysis**
X = contingency_table.values
X = X / X.sum(axis=1, keepdims=True)  # Normalize row-wise

svd = TruncatedSVD(n_components=2)
X_svd = svd.fit_transform(X)

# **Standardize for better visualization**
scaler = StandardScaler()
X_standardized = scaler.fit_transform(X_svd)  # Ensures correct spread and distances

# **Select top variables**
num_top_affordances = min(20, len(contingency_table))
num_top_sentiments = min(15, len(contingency_table.columns))

top_affordances = contingency_table.sum(axis=1).nlargest(num_top_affordances).index.tolist()
top_sentiments = contingency_table.sum(axis=0).nlargest(num_top_sentiments).index.tolist()

# **Get indices for plotting**
filtered_affordance_indices = [list(contingency_table.index).index(a) for a in top_affordances]
filtered_sentiment_indices = [list(contingency_table.columns).index(s) for s in top_sentiments]

# **Extract coordinates**
affordance_points = X_standardized[filtered_affordance_indices]
sentiment_points = X_standardized[filtered_sentiment_indices]

# **Function to draw convex hulls**
def draw_hull(points, color, alpha=0.15):
    """Draws a convex hull around a cluster of points."""
    if len(points) > 2:
        hull = ConvexHull(points)
        plt.fill(points[hull.vertices, 0], points[hull.vertices, 1], color=color, alpha=alpha)

# **Create Perceptual Map**
plt.figure(figsize=(12, 8))

# Draw convex hulls (same as before)
draw_hull(affordance_points, "blue", alpha=0.15)
draw_hull(sentiment_points, "green", alpha=0.15)

# Plot points (for reference)
plt.scatter(affordance_points[:, 0], affordance_points[:, 1], c='blue', alpha=0.3)
plt.scatter(sentiment_points[:, 0], sentiment_points[:, 1], c='green', alpha=0.3)

# A small offset for text labels
offset_x = np.std(X_standardized[:, 0]) * 0.02
offset_y = np.std(X_standardized[:, 1]) * 0.02

# Annotate Product Affordances (Blue)
for i, idx in enumerate(filtered_affordance_indices):
    x, y = X_standardized[idx, 0], X_standardized[idx, 1]
    # Apply a slight stagger based on the index i
    dx = (i % 3) * offset_x
    dy = ((i + 1) % 3) * offset_y
    plt.text(
        x + dx,
        y + dy,
        top_affordances[i],
        fontsize=9,
        color="blue",
        fontweight="bold"
    )

# Annotate GPT_ABSA Sentiment Categories (Green)
for i, idx in enumerate(filtered_sentiment_indices):
    x, y = X_standardized[idx, 0], X_standardized[idx, 1]
    dx = (i % 3) * offset_x
    dy = ((i + 1) % 3) * offset_y
    plt.text(
        x + dx,
        y - dy,  # offset in the opposite direction
        top_sentiments[i],
        fontsize=9,
        color="darkgreen",
        fontweight="bold"
    )

# Final formatting (same as before)
plt.axhline(0, color='black', linewidth=0.5, linestyle="--")
plt.axvline(0, color='black', linewidth=0.5, linestyle="--")
plt.xlabel("Dimension-1 (CA Axis)")
plt.ylabel("Dimension-2 (CA Axis)")
plt.title("Final Optimized Perceptual Map: Lemmatized Product Affordances vs. GPT_ABSA Sentiment Categories")
plt.grid(True, linestyle='dotted', alpha=0.6)

# Save
output_path = os.path.join(os.path.dirname(file_path), "CA_Affordances_ABSA_PerceptualMap_Lemmatized.png")
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✅ Perceptual Map saved to: {output_path}")