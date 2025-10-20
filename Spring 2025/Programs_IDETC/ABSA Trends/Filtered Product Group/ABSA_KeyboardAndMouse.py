import os
import re
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # For non-interactive environments
import matplotlib.pyplot as plt

# -----------------------------------------------------------------------
# 1. INPUT & OUTPUT PATHS
# -----------------------------------------------------------------------
filtered_data_path = r"D:\OneDrive\Academic History\Research\NLP-Driven Sustainable Design_CoDesign Lab\Co-Design Lab\Databases_IDETC\V1 Merged with Product Group\filtered_data.csv"

annual_folder = r"D:\OneDrive\Academic History\Research\NLP-Driven Sustainable Design_CoDesign Lab\Co-Design Lab\Databases_IDETC\V1 Merged with Product Group\ABSA Trends\ABSA Trends_Annual"
annual_csv_path = os.path.join(annual_folder, "ABSA Trends_Annual.csv")

quarter_folder = r"D:\OneDrive\Academic History\Research\NLP-Driven Sustainable Design_CoDesign Lab\Co-Design Lab\Databases_IDETC\V1 Merged with Product Group\ABSA Trends\ABSA Trends_Quarter"
quarter_csv_path = os.path.join(quarter_folder, "ABSA Trends_Quarter.csv")

os.makedirs(annual_folder, exist_ok=True)
os.makedirs(quarter_folder, exist_ok=True)

# -----------------------------------------------------------------------
# 2. HELPER FUNCTIONS
# -----------------------------------------------------------------------
def parse_review_date(date_str):
    """
    Extracts the date portion from a string like:
      'Reviewed in the United Kingdom on February 5, 2018'.
    Returns pd.NaT if it fails to parse.
    """
    if not isinstance(date_str, str) or not date_str.strip():
        return pd.NaT

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
    Simple ratio of positive to negative:
      - If both zero -> 0
      - If neg=0 but pos>0 -> pos_count
      - Else -> pos_count/neg_count
    """
    if pos_count == 0 and neg_count == 0:
        return 0
    elif neg_count == 0:
        return float(pos_count)
    else:
        return float(pos_count) / float(neg_count)

def sanitize_filename(name):
    """Remove characters not allowed in Windows filenames."""
    return re.sub(r'[<>:"/\\|?*]', '_', name)

# -----------------------------------------------------------------------
# 3. READ THE FILTERED DATA
# -----------------------------------------------------------------------
df = pd.read_csv(filtered_data_path, encoding='latin-1')

# (Optional) parse date column if needed:
df['ParsedDate'] = df['date'].apply(parse_review_date)
df = df.dropna(subset=['ParsedDate'])

# -----------------------------------------------------------------------
# 4. FILTER FOR KEYBOARD / KEYBOARD+MOUSE
# -----------------------------------------------------------------------
# Make sure your CSV has a column named "product_type"
valid_types = ["Keyboard", "Keyboard and mouse"]
df = df[df["product_type"].isin(valid_types)]

# If no rows remain after filtering, the script will create empty outputs.
# You can decide how to handle that case if you like.

# -----------------------------------------------------------------------
# 5. DEFINE THE 16 ASPECT COLUMNS
# -----------------------------------------------------------------------
aspects = [
    "General Sustainability",
    "Material: Bio Friendly",
    "Material: Chemical Contents",
    "Material: Recyclability",
    "Material: Waste",
    "Packaging",
    "Environment: Bioenvironment",
    "Environment: Climate",
    "Energy: Consumption",
    "Energy: Renewability",
    "Manufacturing Process: Production",
    "Manufacturing Process: Worker",
    "Manufacturing Process: Supply",
    "User Experience: Price",
    "User Experience: Quality/Performance",
    "User Experience: Safety"
]

# -----------------------------------------------------------------------
# 6. MELT (UNPIVOT) THE ASPECTS
# -----------------------------------------------------------------------
melted = df.melt(
    id_vars=["ParsedDate"],
    value_vars=aspects,
    var_name="Aspect",
    value_name="Sentiment"
)

# If you only want to keep non-zero sentiments, uncomment:
# melted = melted[melted["Sentiment"] != 0]

# -----------------------------------------------------------------------
# 7. CREATE YEAR AND QUARTER COLUMNS
# -----------------------------------------------------------------------
melted["Year"] = melted["ParsedDate"].dt.year
melted["Quarter"] = (
    melted["ParsedDate"].dt.year.astype(str)
    + "-Q"
    + ((melted["ParsedDate"].dt.month - 1) // 3 + 1).astype(str)
)

# -----------------------------------------------------------------------
# 8. AGGREGATE ANNUALLY
# -----------------------------------------------------------------------
group_year = melted.groupby(["Year", "Aspect"])["Sentiment"].agg(
    Positive_Count=lambda x: (x > 0).sum(),
    Negative_Count=lambda x: (x < 0).sum()
).reset_index()

# Ensure every (Year, Aspect) combo is represented
all_years = sorted(melted["Year"].dropna().unique())
mi_year_aspect = pd.MultiIndex.from_product([all_years, aspects], names=["Year", "Aspect"])

df_yearly = group_year.set_index(["Year", "Aspect"]).reindex(mi_year_aspect, fill_value=0).reset_index()

df_yearly["Sum_Count"] = df_yearly["Positive_Count"] + df_yearly["Negative_Count"]

# Total reviews by year
df["Year"] = df["ParsedDate"].dt.year
reviews_by_year = df.groupby("Year").size()
df_yearly["Total_Reviews"] = df_yearly["Year"].map(reviews_by_year).fillna(0).astype(int)

df_yearly["Positive_Negative_Ratio"] = df_yearly.apply(
    lambda row: positive_negative_ratio(row["Positive_Count"], row["Negative_Count"]),
    axis=1
)

# Reorder
df_yearly = df_yearly[
    [
        "Year",
        "Aspect",
        "Positive_Count",
        "Negative_Count",
        "Sum_Count",
        "Total_Reviews",
        "Positive_Negative_Ratio"
    ]
]

# Save to CSV
os.makedirs(annual_folder, exist_ok=True)
df_yearly.to_csv(annual_csv_path, index=False)
print(f"✅ Annual (Keyboard) results saved to {annual_csv_path}")

# -----------------------------------------------------------------------
# 9. AGGREGATE QUARTERLY
# -----------------------------------------------------------------------
group_quarter = melted.groupby(["Quarter", "Aspect"])["Sentiment"].agg(
    Positive_Count=lambda x: (x > 0).sum(),
    Negative_Count=lambda x: (x < 0).sum()
).reset_index()

all_quarters = sorted(melted["Quarter"].dropna().unique())
mi_quarter_aspect = pd.MultiIndex.from_product([all_quarters, aspects], names=["Quarter", "Aspect"])
df_quarterly = group_quarter.set_index(["Quarter", "Aspect"]).reindex(mi_quarter_aspect, fill_value=0).reset_index()

df_quarterly["Sum_Count"] = df_quarterly["Positive_Count"] + df_quarterly["Negative_Count"]

# Total reviews by quarter
df["Quarter"] = (
    df["ParsedDate"].dt.year.astype(str)
    + "-Q"
    + ((df["ParsedDate"].dt.month - 1) // 3 + 1).astype(str)
)
reviews_by_quarter = df.groupby("Quarter").size()
df_quarterly["Total_Reviews"] = df_quarterly["Quarter"].map(reviews_by_quarter).fillna(0).astype(int)

df_quarterly["Positive_Negative_Ratio"] = df_quarterly.apply(
    lambda row: positive_negative_ratio(row["Positive_Count"], row["Negative_Count"]),
    axis=1
)

df_quarterly = df_quarterly[
    [
        "Quarter",
        "Aspect",
        "Positive_Count",
        "Negative_Count",
        "Sum_Count",
        "Total_Reviews",
        "Positive_Negative_Ratio"
    ]
]

os.makedirs(quarter_folder, exist_ok=True)
df_quarterly.to_csv(quarter_csv_path, index=False)
print(f"✅ Quarterly (Keyboard) results saved to {quarter_csv_path}")

# -----------------------------------------------------------------------
# 10. GENERATE ANNUAL PLOTS
# -----------------------------------------------------------------------
# We'll plot directly from df_yearly in memory
aspects_annual = df_yearly["Aspect"].unique()
df_yearly = df_yearly.sort_values(by=["Year"])  # Sort by year

# --- Plot 1: Total Reviews Over Time (All Aspects)
plt.figure(figsize=(10, 6))
for aspect in aspects_annual:
    subset = df_yearly[df_yearly["Aspect"] == aspect]
    plt.plot(subset["Year"], subset["Total_Reviews"], marker="o", label=aspect)

plt.xlabel("Year")
plt.ylabel("Total Reviews")
plt.title("Total Reviews Over Time (Annual) - KEYBOARDS")
plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(annual_folder, "0_Total_Reviews_Over_Time_Annual.png"), dpi=300)
plt.close()

# --- Plot 2: Rate of Change of Total Reviews (All Aspects)
plt.figure(figsize=(10, 6))
for aspect in aspects_annual:
    subset = df_yearly[df_yearly["Aspect"] == aspect].copy()
    subset["Review_Change_Percentage"] = subset["Total_Reviews"].pct_change() * 100
    plt.plot(subset["Year"], subset["Review_Change_Percentage"], marker="o", linestyle="--", label=aspect)

plt.xlabel("Year")
plt.ylabel("Rate of Change of Total Reviews (%)")
plt.title("Rate of Change of Total Reviews (Annual) - KEYBOARDS")
plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(annual_folder, "0_Rate_of_Change_of_Reviews_Annual.png"), dpi=300)
plt.close()

# --- Plot 3: Positive-Negative Ratio Over Time (All Aspects)
plt.figure(figsize=(10, 6))
for aspect in aspects_annual:
    subset = df_yearly[df_yearly["Aspect"] == aspect]
    plt.plot(subset["Year"], subset["Positive_Negative_Ratio"], marker="o", label=aspect)

plt.xlabel("Year")
plt.ylabel("Positive-Negative Ratio")
plt.title("Positive-Negative Ratio Over Time (Annual) - KEYBOARDS")
plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(annual_folder, "0_Positive_Negative_Ratio_Annual.png"), dpi=300)
plt.close()

# --- Individual Aspect Plots (Annual)
for aspect in aspects_annual:
    subset = df_yearly[df_yearly["Aspect"] == aspect].copy()
    safe_aspect = sanitize_filename(aspect)

    # 1) Total Reviews
    plt.figure(figsize=(8, 5))
    plt.plot(subset["Year"], subset["Total_Reviews"], marker="o")
    plt.xlabel("Year")
    plt.ylabel("Total Reviews")
    plt.title(f"Total Reviews Over Time - {aspect} (Annual, KEYBOARDS)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(annual_folder, f"Total_Reviews_Annual_{safe_aspect}.png"), dpi=300)
    plt.close()

    # 2) Rate of Change
    subset["Review_Change_Percentage"] = subset["Total_Reviews"].pct_change() * 100
    plt.figure(figsize=(8, 5))
    plt.plot(subset["Year"], subset["Review_Change_Percentage"], marker="o", linestyle="--")
    plt.xlabel("Year")
    plt.ylabel("Rate of Change (%)")
    plt.title(f"Rate of Change of Total Reviews - {aspect} (Annual, KEYBOARDS)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(annual_folder, f"Rate_of_Change_Annual_{safe_aspect}.png"), dpi=300)
    plt.close()

    # 3) Positive-Negative Ratio
    plt.figure(figsize=(8, 5))
    plt.plot(subset["Year"], subset["Positive_Negative_Ratio"], marker="o")
    plt.xlabel("Year")
    plt.ylabel("Positive-Negative Ratio")
    plt.title(f"Positive-Negative Ratio - {aspect} (Annual, KEYBOARDS)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(annual_folder, f"Positive_Negative_Ratio_Annual_{safe_aspect}.png"), dpi=300)
    plt.close()

print(f"✅ All annual plots saved in: {annual_folder}")

# -----------------------------------------------------------------------
# 11. GENERATE QUARTERLY PLOTS
# -----------------------------------------------------------------------
aspects_quarterly = df_quarterly["Aspect"].unique()

# Sort df_quarterly by Quarter for correct x-axis ordering
def quarter_sort_key(q_str):
    # "YYYY-Qn" -> (YYYY, n)
    parts = q_str.split("-Q")
    return (int(parts[0]), int(parts[1]))

df_quarterly["SortKey"] = df_quarterly["Quarter"].apply(quarter_sort_key)
df_quarterly = df_quarterly.sort_values(by="SortKey")

# --- Plot 1: Total Reviews Over Time (All Aspects)
plt.figure(figsize=(10, 6))
for aspect in aspects_quarterly:
    subset = df_quarterly[df_quarterly["Aspect"] == aspect]
    plt.plot(subset["Quarter"], subset["Total_Reviews"], marker="o", label=aspect)

plt.xlabel("Quarter")
plt.ylabel("Total Reviews")
plt.title("Total Reviews Over Time (Quarterly) - KEYBOARDS")
plt.xticks(rotation=45)
plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(quarter_folder, "0_Total_Reviews_Over_Time_Quarterly.png"), dpi=300)
plt.close()

# --- Plot 2: Rate of Change of Total Reviews (All Aspects)
plt.figure(figsize=(10, 6))
for aspect in aspects_quarterly:
    subset = df_quarterly[df_quarterly["Aspect"] == aspect].copy()
    subset["Review_Change_Percentage"] = subset["Total_Reviews"].pct_change() * 100
    plt.plot(subset["Quarter"], subset["Review_Change_Percentage"], marker="o", linestyle="--", label=aspect)

plt.xlabel("Quarter")
plt.ylabel("Rate of Change of Total Reviews (%)")
plt.title("Rate of Change of Total Reviews (Quarterly) - KEYBOARDS")
plt.xticks(rotation=45)
plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(quarter_folder, "0_Rate_of_Change_Over_Time_Quarterly.png"), dpi=300)
plt.close()

# --- Plot 3: Positive-Negative Ratio Over Time (All Aspects)
plt.figure(figsize=(10, 6))
for aspect in aspects_quarterly:
    subset = df_quarterly[df_quarterly["Aspect"] == aspect]
    plt.plot(subset["Quarter"], subset["Positive_Negative_Ratio"], marker="o", label=aspect)

plt.xlabel("Quarter")
plt.ylabel("Positive-Negative Ratio")
plt.title("Positive-Negative Ratio Over Time (Quarterly) - KEYBOARDS")
plt.xticks(rotation=45)
plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(quarter_folder, "0_Positive_Negative_Ratio_Quarterly.png"), dpi=300)
plt.close()

# --- Individual Aspect Plots (Quarterly)
for aspect in aspects_quarterly:
    subset = df_quarterly[df_quarterly["Aspect"] == aspect].copy()
    safe_aspect = sanitize_filename(aspect)

    # Sort subset by Quarter again, just to be sure
    subset["SortKey"] = subset["Quarter"].apply(quarter_sort_key)
    subset = subset.sort_values(by="SortKey")

    # 1) Total Reviews
    plt.figure(figsize=(8, 5))
    plt.plot(subset["Quarter"], subset["Total_Reviews"], marker="o", color="b")
    plt.xlabel("Quarter")
    plt.ylabel("Total Reviews")
    plt.title(f"Total Reviews Over Time - {aspect} (Quarterly, KEYBOARDS)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(quarter_folder, f"Total_Reviews_Over_Time_Quarterly_{safe_aspect}.png"), dpi=300)
    plt.close()

    # 2) Rate of Change
    subset["Review_Change_Percentage"] = subset["Total_Reviews"].pct_change() * 100
    plt.figure(figsize=(8, 5))
    plt.plot(subset["Quarter"], subset["Review_Change_Percentage"], marker="o", linestyle="--", color="r")
    plt.xlabel("Quarter")
    plt.ylabel("Rate of Change (%)")
    plt.title(f"Rate of Change of Total Reviews - {aspect} (Quarterly, KEYBOARDS)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(quarter_folder, f"Rate_of_Change_Over_Time_Quarterly_{safe_aspect}.png"), dpi=300)
    plt.close()

    # 3) Positive-Negative Ratio
    plt.figure(figsize=(8, 5))
    plt.plot(subset["Quarter"], subset["Positive_Negative_Ratio"], marker="o", color="g")
    plt.xlabel("Quarter")
    plt.ylabel("Positive-Negative Ratio")
    plt.title(f"Positive-Negative Ratio Over Time - {aspect} (Quarterly, KEYBOARDS)")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(quarter_folder, f"Positive_Negative_Ratio_Over_Time_Quarterly_{safe_aspect}.png"), dpi=300)
    plt.close()

print(f"✅ All quarterly plots saved in: {quarter_folder}")

print("\nAll done!")
