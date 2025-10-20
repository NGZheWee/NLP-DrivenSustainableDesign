import os
import pandas as pd
import ast
import re


def parse_review_date(date_str):
    """
    Extracts the date portion from a string like:
      'Reviewed in the United Kingdom on February 5, 2018'.
    Returns pd.NaT if:
      - It's not a string,
      - It's empty,
      - It doesn't match the pattern,
      - Or it can't be parsed into a datetime.
    """
    # 1. Guard for non-strings or empty strings
    if not isinstance(date_str, str) or not date_str.strip():
        return pd.NaT

    # 2. Regex to capture e.g. "February 5, 2018" after "on "
    pattern = r'on\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})'
    match = re.search(pattern, date_str)
    if match:
        date_part = match.group(1)
        try:
            return pd.to_datetime(date_part)
        except ValueError:
            return pd.NaT
    return pd.NaT


def positive_negative_ratio(pos_count, neg_count):
    """
    Simple ratio of positive to negative.
      - If both are zero -> 0
      - If neg_count=0 but pos_count>0 -> pos_count (or any fallback)
      - Else -> pos_count / neg_count
    """
    if pos_count == 0 and neg_count == 0:
        return 0
    elif neg_count == 0:
        return float(pos_count)
    else:
        return float(pos_count) / float(neg_count)


# -----------------------------------------------------------------------
# Main script
# -----------------------------------------------------------------------

# Update this path to your actual CSV. Example:
csv_path = r"D:\OneDrive\Academic History\Research\NLP-Driven Sustainable Design_CoDesign Lab\Co-Design Lab\Databases_IDETC\Final.csv"

# Determine the same folder as the input CSV
input_dir = os.path.dirname(csv_path)
annual_output_path = os.path.join(input_dir, "ABSA_Counts_Annual.csv")
quarter_output_path = os.path.join(input_dir, "ABSA_Counts_Quarter.csv")

# 1. Read CSV with specified encoding:
df = pd.read_csv(
    csv_path,
    encoding='latin-1'  # or 'cp1252', 'ISO-8859-1', etc. if needed
)

# 2. Parse the 'date' column (review date) into a datetime
df['ParsedDate'] = df['date'].apply(parse_review_date)

# Optionally drop rows missing valid dates
df = df.dropna(subset=['ParsedDate'])

# 3. Parse the GPT_ABSA column (JSON-like), extracting each non-zero aspect sentiment
rows_aspects = []
for idx, row in df.iterrows():
    raw_absa = row['GPT_ABSA']  # e.g. '{"General Sustainability":0, "User Experience: Price": -1, ...}'
    try:
        absa_dict = ast.literal_eval(raw_absa)
    except (SyntaxError, ValueError):
        # If we can't parse it, skip
        continue

    review_date = row['ParsedDate']
    year = review_date.year
    quarter_label = f"{year}-Q{(review_date.month - 1) // 3 + 1}"

    for aspect, sentiment in absa_dict.items():
        # Only keep aspects with a non-zero sentiment
        if sentiment != 0:
            rows_aspects.append({
                'ParsedDate': review_date,
                'Year': year,
                'Quarter': quarter_label,
                'Aspect': aspect.strip(),
                'Sentiment': sentiment
            })

df_aspects = pd.DataFrame(rows_aspects)
if df_aspects.empty:
    print("No aspect data found (all zero or invalid). Exiting.")
    exit()

# -----------------------------------------------------------------------
# YEARLY AGGREGATIONS
# -----------------------------------------------------------------------
# Group by (Year, Aspect), counting positives/negatives
group_year = df_aspects.groupby(['Year', 'Aspect'])

df_yearly = group_year['Sentiment'].agg(
    Positive_Count=lambda x: (x > 0).sum(),
    Negative_Count=lambda x: (x < 0).sum()
).reset_index()

df_yearly['Sum_Count'] = df_yearly['Positive_Count'] + df_yearly['Negative_Count']

# If needed, get total number of reviews per year from the main df
df['Year'] = df['ParsedDate'].dt.year
reviews_by_year = df.groupby('Year').size().to_dict()
df_yearly['Total_Reviews'] = df_yearly['Year'].map(reviews_by_year)

df_yearly['Positive_Negative_Ratio'] = df_yearly.apply(
    lambda row: positive_negative_ratio(row['Positive_Count'], row['Negative_Count']), axis=1
)

# Reorder columns
df_yearly = df_yearly[
    ['Year', 'Aspect', 'Positive_Count', 'Negative_Count',
     'Sum_Count', 'Total_Reviews', 'Positive_Negative_Ratio']
]

df_yearly.to_csv(annual_output_path, index=False)
print(f"Saved yearly results to {annual_output_path}")

# -----------------------------------------------------------------------
# QUARTERLY AGGREGATIONS
# -----------------------------------------------------------------------
# Group by (Quarter, Aspect)
group_quarter = df_aspects.groupby(['Quarter', 'Aspect'])

df_quarterly = group_quarter['Sentiment'].agg(
    Positive_Count=lambda x: (x > 0).sum(),
    Negative_Count=lambda x: (x < 0).sum()
).reset_index()

df_quarterly['Sum_Count'] = df_quarterly['Positive_Count'] + df_quarterly['Negative_Count']

# Map total reviews per quarter
df['Quarter'] = df['ParsedDate'].apply(lambda d: f"{d.year}-Q{(d.month - 1) // 3 + 1}")
reviews_by_quarter = df.groupby('Quarter').size().to_dict()
df_quarterly['Total_Reviews'] = df_quarterly['Quarter'].map(reviews_by_quarter)

df_quarterly['Positive_Negative_Ratio'] = df_quarterly.apply(
    lambda row: positive_negative_ratio(row['Positive_Count'], row['Negative_Count']), axis=1
)

# Reorder columns
df_quarterly = df_quarterly[
    ['Quarter', 'Aspect', 'Positive_Count', 'Negative_Count',
     'Sum_Count', 'Total_Reviews', 'Positive_Negative_Ratio']
]

df_quarterly.to_csv(quarter_output_path, index=False)
print(f"Saved quarterly results to {quarter_output_path}")
