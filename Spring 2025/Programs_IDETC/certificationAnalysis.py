import os
import pandas as pd
import ast

# Define file paths
input_file_path = r"D:\OneDrive\Academic History\Research\NLP-Driven Sustainable Design_CoDesign Lab\Co-Design Lab\Databases_IDETC\V1 Merged\Final_withFFL.csv"
output_dir = r"D:\OneDrive\Academic History\Research\NLP-Driven Sustainable Design_CoDesign Lab\Co-Design Lab\Databases_IDETC\Certification Analysis"
os.makedirs(output_dir, exist_ok=True)

# Load dataset
df = pd.read_csv(input_file_path, encoding="ISO-8859-1")

# Ensure the necessary columns exist
if "certifications" not in df.columns or "GPT_ABSA" not in df.columns:
    raise ValueError("Required columns 'certifications' or 'GPT_ABSA' are missing from the dataset.")

# **Fixed Column Order**
aspects = [
    "Material: Bio Friendly", "Material: Chemical Contents", "Material: Recyclability",
    "Material: Waste", "Packaging", "Environment: Bioenvironment", "Environment: Climate",
    "Energy: Consumption", "Energy: Renewability", "Manufacturing Process: Production",
    "Manufacturing Process: Worker", "Manufacturing Process: Supply", "User Experience: Price",
    "User Experience: Quality/Performance", "User Experience: Safety", "General Sustainability"
]

# **STEP 1: STANDARDIZE CERTIFICATIONS**
df["certifications"] = df["certifications"].astype(str).str.strip().str.upper()  # Convert to uppercase & remove spaces

# **STEP 2: HANDLE MULTIPLE CERTIFICATIONS IN ONE ROW**
df = df.assign(certifications=df["certifications"].str.split(",")).explode("certifications")
df["certifications"] = df["certifications"].str.strip()  # Ensure clean formatting

# **STEP 3: COMBINE "BIFMA" and "BIMFA" INTO ONE CATEGORY**
df["certifications"] = df["certifications"].replace({"BIMFA": "BIFMA"})  # Treat BIMFA as BIFMA

# Extract unique certifications after cleaning
certifications = df["certifications"].dropna().unique()

# Initialize dictionaries for counts
positive_counts = {cert: {aspect: 0 for aspect in aspects} for cert in certifications}
negative_counts = {cert: {aspect: 0 for aspect in aspects} for cert in certifications}
total_counts = {cert: {aspect: 0 for aspect in aspects} for cert in certifications}

# Iterate through rows and count positive/negative aspects for each certification
for _, row in df.iterrows():
    cert = row["certifications"]
    gpt_absa_data = row["GPT_ABSA"]

    # Parse JSON from the column
    try:
        absa_dict = ast.literal_eval(gpt_absa_data)
    except (SyntaxError, ValueError):
        continue  # Skip invalid JSON entries

    # Ensure the row's certification exists in our extracted certifications list
    if cert not in certifications:
        continue

    # Count positive, negative, and total sentiment occurrences per aspect
    for aspect, sentiment in absa_dict.items():
        if aspect in aspects:
            if sentiment == 1:
                positive_counts[cert][aspect] += 1
            elif sentiment == -1:
                negative_counts[cert][aspect] += 1
            total_counts[cert][aspect] += abs(sentiment)  # Count total occurrences

# Convert dictionaries to DataFrames
df_positive = pd.DataFrame.from_dict(positive_counts, orient="index").reset_index().rename(columns={"index": "Certification"})
df_negative = pd.DataFrame.from_dict(negative_counts, orient="index").reset_index().rename(columns={"index": "Certification"})
df_total = pd.DataFrame.from_dict(total_counts, orient="index").reset_index().rename(columns={"index": "Certification"})

# **STEP 4: MERGE BIFMA + BIMFA COUNTS INTO ONE FINAL "BIFMA" ROW**
for df_counts in [df_positive, df_negative, df_total]:
    if "BIFMA" in df_counts["Certification"].values and "BIMFA" in df_counts["Certification"].values:
        bimfa_row = df_counts[df_counts["Certification"] == "BIMFA"]
        bifma_index = df_counts[df_counts["Certification"] == "BIFMA"].index[0]

        # Sum the BIMFA row into the BIFMA row
        df_counts.loc[bifma_index, aspects] += bimfa_row[aspects].values[0]

        # Drop the now-redundant "BIMFA" row
        df_counts.drop(df_counts[df_counts["Certification"] == "BIMFA"].index, inplace=True)

# **STEP 5: SORT, REORDER COLUMNS, AND SAVE OUTPUT FILES**
df_positive = df_positive[["Certification"] + aspects].sort_values("Certification")
df_negative = df_negative[["Certification"] + aspects].sort_values("Certification")
df_total = df_total[["Certification"] + aspects].sort_values("Certification")

positive_output_path = os.path.join(output_dir, "ABSA_Positive_Counts.csv")
negative_output_path = os.path.join(output_dir, "ABSA_Negative_Counts.csv")
total_output_path = os.path.join(output_dir, "ABSA_Total_Counts.csv")

df_positive.to_csv(positive_output_path, index=False)
df_negative.to_csv(negative_output_path, index=False)
df_total.to_csv(total_output_path, index=False)

# Print confirmation messages
print(f"✅ Positive Counts saved at: {positive_output_path}")
print(f"✅ Negative Counts saved at: {negative_output_path}")
print(f"✅ Total Counts saved at: {total_output_path}")
