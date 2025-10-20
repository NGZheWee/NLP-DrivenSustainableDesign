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

# **Fix misspellings manually (e.g., "Applicanes" -> "Appliances")**
df["product_category"] = df["product_category"].replace({
    "Applicanes": "Appliances",
    "Applicane": "Appliances"
})

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

# **Get unique values (including all sentiments and categories)**
all_categories = df["product_category"].dropna().unique().tolist()
all_gpt_absa = sorted(set([item for sublist in df["GPT_ABSA_filtered"].dropna() for item in sublist]))

# **Create contingency table including all sentiments and categories**
contingency_table = pd.DataFrame(0, index=all_categories, columns=all_gpt_absa)

# **Populate the contingency table**
for _, row in df.dropna(subset=["product_category", "GPT_ABSA_filtered"]).iterrows():
    for sentiment in row["GPT_ABSA_filtered"]:
        contingency_table.at[row["product_category"], sentiment] += 1

# **Drop empty rows and columns (if any)**
contingency_table = contingency_table.loc[(contingency_table.sum(axis=1) > 0), (contingency_table.sum(axis=0) > 0)]

# **Perform Correspondence Analysis (CA)**
X = contingency_table.values
X = X / X.sum(axis=1, keepdims=True)  # Normalize row-wise

svd = TruncatedSVD(n_components=2)
X_svd = svd.fit_transform(X)

# **Standardize to ensure proper spread and visibility**
scaler = StandardScaler()
X_standardized = scaler.fit_transform(X_svd)

# **Get indices for plotting (includes all categories and sentiments)**
filtered_category_indices = list(range(len(contingency_table.index)))
filtered_sentiment_indices = list(range(len(contingency_table.columns)))

# **Ensure safe indexing**
filtered_category_indices = [idx for idx in filtered_category_indices if idx < X_standardized.shape[0]]
filtered_sentiment_indices = [idx for idx in filtered_sentiment_indices if idx < X_standardized.shape[0]]

# **Extract coordinates**
category_points = X_standardized[filtered_category_indices]
sentiment_points = X_standardized[filtered_sentiment_indices]

# **Function to draw convex hulls**
def draw_hull(points, color, alpha=0.2):
    """Draws a convex hull around a cluster of points."""
    if len(points) > 2:
        hull = ConvexHull(points)
        plt.fill(points[hull.vertices, 0], points[hull.vertices, 1], color=color, alpha=alpha)

# **Create Perceptual Map**
plt.figure(figsize=(14, 10))

# **Draw convex hulls for better visualization**
draw_hull(category_points, "blue", alpha=0.15)
draw_hull(sentiment_points, "green", alpha=0.15)

# **Define offsets dynamically for improved text readability**
offset_x, offset_y = np.std(X_standardized[:, 0]) * 0.05, np.std(X_standardized[:, 1]) * 0.05

# **Improve label placement to reduce overlap**
left_threshold = np.percentile(X_standardized[:, 0], 25)  # Detect left-clustered points
extra_offset_x = offset_x * 3  # More spacing for left-side categories
extra_offset_y = offset_y * 2  # More spacing vertically

# **Annotate Product Categories (Blue)**
for i, idx in enumerate(filtered_category_indices):
    x, y = X_standardized[idx, 0], X_standardized[idx, 1]

    # Apply extra spacing **only** if point is in the left cluster
    if x < left_threshold:
        adjusted_x = x - extra_offset_x - ((i % 2) * offset_x)
        adjusted_y = y + ((i % 5) * extra_offset_y)
    else:
        adjusted_x = x - ((i % 3) * offset_x)
        adjusted_y = y + ((i % 4) * offset_y)

    plt.text(adjusted_x, adjusted_y, contingency_table.index[i], fontsize=9, ha='right', va='bottom',
             color="blue", fontweight="bold", alpha=0.8)

# **Annotate GPT_ABSA Sentiment Categories (Green)**
for i, idx in enumerate(filtered_sentiment_indices):
    x, y = X_standardized[idx, 0], X_standardized[idx, 1]
    adjusted_x = x + ((i % 3) * offset_x)
    adjusted_y = y - ((i % 4) * offset_y)
    plt.text(adjusted_x, adjusted_y, contingency_table.columns[i], fontsize=9, ha='left', va='top',
             color="darkgreen", fontweight="bold", alpha=0.8)

# **Final Formatting**
plt.axhline(0, color='black', linewidth=0.5, linestyle="--")
plt.axvline(0, color='black', linewidth=0.5, linestyle="--")
plt.xlabel("Dimension-1 (CA Axis)")
plt.ylabel("Dimension-2 (CA Axis)")
plt.title("Final Perceptual Map: Product Categories vs. GPT_ABSA Sentiments (Lemmatized)")
plt.grid(True, linestyle='dotted', alpha=0.6)

# **Save the plot**
output_path = os.path.join(os.path.dirname(file_path), "CA_ProductCategory_ABSA_PerceptualMap_Lemmatized.png")
plt.savefig(output_path, dpi=300, bbox_inches='tight')

# **Confirm Save Location**
print(f"✅ Perceptual Map saved to: {output_path}")
