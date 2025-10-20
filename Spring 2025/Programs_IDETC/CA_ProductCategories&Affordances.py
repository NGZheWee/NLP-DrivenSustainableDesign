import pandas as pd
import numpy as np
import os
import json
import matplotlib

matplotlib.use('Agg')  # non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

from scipy.spatial import ConvexHull

########################################
# 1. LOAD YOUR DATA
########################################

file_path = r"D:\OneDrive\Academic History\Research\NLP-Driven Sustainable Design_CoDesign Lab\Co-Design Lab\Databases_IDETC\Final_lemmatizedAffordances.csv"
df = pd.read_csv(file_path, encoding='ISO-8859-1')

# Fix known misspellings
df["product_category"] = df["product_category"].replace({
    "Applicanes": "Appliances",
    "Applicane": "Appliances"
})

# Extract affordances
df["product_affordances_lemmatized"] = (
    df["product_affordances_lemmatized"]
    .str.extract(r'\[(.*?)\]')[0]
    .str.replace('"', '')
    .str.split(', ')
)

########################################
# 2. BUILD THE CONTINGENCY TABLE
########################################

# Create an initial table of categories vs. affordances
all_categories = df["product_category"].dropna().unique().tolist()

# Flatten all affordances into a single list
all_affordances = [
    afford for aff_list in df["product_affordances_lemmatized"].dropna()
    for afford in aff_list
]

contingency_table = pd.crosstab(
    df["product_category"].dropna(),
    pd.Series(all_affordances, name="affordance")
)

# Remove any rows/cols of all zeros if present
contingency_table = contingency_table.loc[
    (contingency_table.sum(axis=1) > 0),
    (contingency_table.sum(axis=0) > 0)
]

########################################
# 3. (OPTIONAL) FILTER FOR TOP CATEGORIES/AFFORDANCES
########################################

top_n_categories = 15
top_n_affordances = 20

cat_sums = contingency_table.sum(axis=1).sort_values(ascending=False)
aff_sums = contingency_table.sum(axis=0).sort_values(ascending=False)

keep_categories = cat_sums.index[:top_n_categories]
keep_affordances = aff_sums.index[:top_n_affordances]

filtered_table = contingency_table.loc[
    contingency_table.index.intersection(keep_categories),
    contingency_table.columns.intersection(keep_affordances)
]

# Drop any empty rows/cols after filtering
filtered_table = filtered_table.loc[
    (filtered_table.sum(axis=1) > 0),
    (filtered_table.sum(axis=0) > 0)
]

########################################
# 4. CORRESPONDENCE ANALYSIS (CA)
########################################

def correspondence_analysis(df_contingency, n_components=2):
    """
    Perform CA on a contingency DataFrame.
    Returns (row_coords, col_coords, explained_inertia).
    """
    T = df_contingency.values
    total = T.sum()

    # Relative frequencies
    P = T / total
    r = P.sum(axis=1)  # row sums
    c = P.sum(axis=0)  # col sums

    # Center by subtracting row x col marginals
    S = P - np.outer(r, c)

    # Weighted by sqrt of marginals
    Dr_inv_sqrt = np.diag(1.0 / np.sqrt(r))
    Dc_inv_sqrt = np.diag(1.0 / np.sqrt(c))

    # SVD
    M = Dr_inv_sqrt @ S @ Dc_inv_sqrt
    U, singular_values, Vt = np.linalg.svd(M, full_matrices=False)

    # Eigenvalues and inertia
    eigenvalues = singular_values**2
    total_inertia = eigenvalues.sum()
    explained_inertia = eigenvalues[:n_components] / total_inertia

    # Row/column principal coordinates
    row_coords = Dr_inv_sqrt @ U[:, :n_components] @ np.diag(singular_values[:n_components])
    col_coords = Dc_inv_sqrt @ Vt[:n_components, :].T @ np.diag(singular_values[:n_components])

    return row_coords, col_coords, explained_inertia

row_coords, col_coords, explained_inertia = correspondence_analysis(filtered_table, n_components=2)

# Convert to DataFrames for easier plotting
row_coords_df = pd.DataFrame(row_coords,
                             index=filtered_table.index,
                             columns=['Dim1', 'Dim2'])
col_coords_df = pd.DataFrame(col_coords,
                             index=filtered_table.columns,
                             columns=['Dim1', 'Dim2'])

########################################
# 5. PLOTTING THE BIPLOT (NO 'adjustText')
########################################

plt.figure(figsize=(12, 9))

# Extract coordinates
cat_points = row_coords_df[['Dim1', 'Dim2']].values
aff_points = col_coords_df[['Dim1', 'Dim2']].values

# Convex hull function
def draw_hull(points, color='blue', alpha=0.15):
    if len(points) > 2:
        hull = ConvexHull(points)
        plt.fill(points[hull.vertices, 0], points[hull.vertices, 1],
                 color=color, alpha=alpha)

# Draw hulls
draw_hull(cat_points, 'blue', alpha=0.2)
draw_hull(aff_points, 'green', alpha=0.2)

# Plot points
plt.scatter(cat_points[:, 0], cat_points[:, 1], color='blue', alpha=0.6, label='Product Categories')
plt.scatter(aff_points[:, 0], aff_points[:, 1], color='green', alpha=0.6, label='Affordances')

# Small offsets to reduce label collisions
offset_x = (cat_points[:, 0].max() - cat_points[:, 0].min()) * 0.01
offset_y = (cat_points[:, 1].max() - cat_points[:, 1].min()) * 0.01

# Annotate row coords (Categories)
for i, (idx, (x, y)) in enumerate(row_coords_df.iterrows()):
    dx = ((i % 3) - 1) * offset_x
    dy = ((i % 4) - 2) * offset_y
    plt.text(x+dx, y+dy, str(idx), color='blue', weight='bold', fontsize=9)

# Annotate column coords (Affordances)
for i, (idx, (x, y)) in enumerate(col_coords_df.iterrows()):
    dx = ((i % 3) - 1) * offset_x
    dy = ((i % 4) - 2) * offset_y
    plt.text(x+dx, y+dy, str(idx), color='darkgreen', weight='bold', fontsize=9)

# Axis lines at origin
plt.axhline(0, color='gray', lw=0.5, ls='--')
plt.axvline(0, color='gray', lw=0.5, ls='--')

plt.xlabel(f"Dimension 1 ({(explained_inertia[0]*100):.2f}% inertia)")
plt.ylabel(f"Dimension 2 ({(explained_inertia[1]*100):.2f}% inertia)")
plt.title("Perceptual Map: Categories vs. Affordances (Correspondence Analysis)")

plt.legend()
plt.grid(True, ls='dotted', alpha=0.7)

# Save
output_path = os.path.join(os.path.dirname(file_path),
                           "CA_ProductCategory_Affordances_PerceptualMap_Lemmatized.png")
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✅ Map saved to: {output_path}")
