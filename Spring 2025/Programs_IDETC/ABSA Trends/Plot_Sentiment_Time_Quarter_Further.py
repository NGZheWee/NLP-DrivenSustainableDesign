import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for plotting
import matplotlib.pyplot as plt
import os
import re

# Define input and output paths
input_file_path = r"D:\OneDrive\Academic History\Research\NLP-Driven Sustainable Design_CoDesign Lab\Co-Design Lab\Databases_IDETC\ABSA Trends_Quarter\ABSA_Counts_Quarter.csv"

output_dir_without_ux = r"D:\OneDrive\Academic History\Research\NLP-Driven Sustainable Design_CoDesign Lab\Co-Design Lab\Databases_IDETC\ABSA Trends_Quarter\Without UX"
output_dir_grouped = r"D:\OneDrive\Academic History\Research\NLP-Driven Sustainable Design_CoDesign Lab\Co-Design Lab\Databases_IDETC\ABSA Trends_Quarter\Grouped"

# Ensure output directories exist
os.makedirs(output_dir_without_ux, exist_ok=True)
os.makedirs(output_dir_grouped, exist_ok=True)

# Load dataset
df = pd.read_csv(input_file_path)

# Convert "Quarter" column to proper datetime format
df["Quarter"] = pd.to_datetime(df["Quarter"], errors="coerce")

# Remove aspects related to "User Experience"
df_filtered = df[~df["Aspect"].str.contains("User Experience", case=False, na=False)]

# Define group mapping
GROUP_MAP = {
    "Manufacturing Process: Production": "Manufacturing Process",
    "Manufacturing Process: Worker": "Manufacturing Process",
    "Manufacturing Process: Supply": "Manufacturing Process",
    "General Sustainability": "General Sustainability",
    "Material: Bio Friendly": "Material",
    "Material: Chemical Contents": "Material",
    "Material: Recyclability": "Material",
    "Material: Waste": "Material",
    "Packaging": "Packaging",
    "Environment: Bioenvironment": "Environment",
    "Environment: Climate": "Environment",
    "Energy: Consumption": "Energy",
    "Energy: Renewability": "Energy",
}

# Apply group mapping
df_grouped = df_filtered.copy()
df_grouped["Aspect"] = df_grouped["Aspect"].replace(GROUP_MAP)

# Function to sanitize filenames
def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name)

# Function to create plots (both overall and individual)
def create_plots(df, output_dir, generate_individual=False):
    df = df.sort_values(by=["Quarter"])
    aspects = df["Aspect"].unique()

    ### **Plot 1: Total Reviews Over Time**
    plt.figure(figsize=(12, 6))
    for aspect in aspects:
        aspect_data = df[df["Aspect"] == aspect]
        plt.plot(aspect_data["Quarter"], aspect_data["Total_Reviews"], marker="o", label=aspect)

    plt.xlabel("Quarter")
    plt.ylabel("Total Reviews")
    plt.title("Total Reviews Over Time (Quarterly)")
    plt.xticks(rotation=45)
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "0_Total_Reviews_Over_Time_Quarterly.png"), dpi=300)
    plt.close()

    ### **Plot 2: Rate of Change of Total Reviews Over Time**
    plt.figure(figsize=(12, 6))
    for aspect in aspects:
        aspect_data = df[df["Aspect"] == aspect].copy()
        aspect_data["Review_Change_Percentage"] = aspect_data["Total_Reviews"].pct_change() * 100
        plt.plot(aspect_data["Quarter"], aspect_data["Review_Change_Percentage"], marker="o", linestyle="--", label=aspect)

    plt.xlabel("Quarter")
    plt.ylabel("Rate of Change (%)")
    plt.title("Rate of Change of Total Reviews Over Time (Quarterly)")
    plt.xticks(rotation=45)
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "0_Rate_of_Change_Over_Time_Quarterly.png"), dpi=300)
    plt.close()

    ### **Plot 3: Positive-Negative Ratio Over Time**
    plt.figure(figsize=(12, 6))
    for aspect in aspects:
        aspect_data = df[df["Aspect"] == aspect]
        plt.plot(aspect_data["Quarter"], aspect_data["Positive_Negative_Ratio"], marker="o", label=aspect)

    plt.xlabel("Quarter")
    plt.ylabel("Positive-Negative Ratio")
    plt.title("Positive-Negative Ratio Over Time (Quarterly)")
    plt.xticks(rotation=45)
    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "0_Positive_Negative_Ratio_Over_Time_Quarterly.png"), dpi=300)
    plt.close()

    # Generate individual aspect plots if requested
    if generate_individual:
        for aspect in aspects:
            aspect_data = df[df["Aspect"] == aspect].copy()
            safe_aspect = sanitize_filename(aspect)

            # **Total Reviews Over Time (Individual)**
            plt.figure(figsize=(8, 5))
            plt.plot(aspect_data["Quarter"], aspect_data["Total_Reviews"], marker="o", color="b")
            plt.xlabel("Quarter")
            plt.ylabel("Total Reviews")
            plt.title(f"Total Reviews Over Time - {aspect} (Quarterly)")
            plt.xticks(rotation=45)
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f"Total_Reviews_Over_Time_Quarterly_{safe_aspect}.png"), dpi=300)
            plt.close()

            # **Rate of Change of Total Reviews (Individual)**
            aspect_data["Review_Change_Percentage"] = aspect_data["Total_Reviews"].pct_change() * 100
            plt.figure(figsize=(8, 5))
            plt.plot(aspect_data["Quarter"], aspect_data["Review_Change_Percentage"], marker="o", linestyle="--", color="r")
            plt.xlabel("Quarter")
            plt.ylabel("Rate of Change (%)")
            plt.title(f"Rate of Change of Total Reviews - {aspect} (Quarterly)")
            plt.xticks(rotation=45)
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f"Rate_of_Change_Over_Time_Quarterly_{safe_aspect}.png"), dpi=300)
            plt.close()

            # **Positive-Negative Ratio Over Time (Individual)**
            plt.figure(figsize=(8, 5))
            plt.plot(aspect_data["Quarter"], aspect_data["Positive_Negative_Ratio"], marker="o", color="g")
            plt.xlabel("Quarter")
            plt.ylabel("Positive-Negative Ratio")
            plt.title(f"Positive-Negative Ratio Over Time - {aspect} (Quarterly)")
            plt.xticks(rotation=45)
            plt.grid(True)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f"Positive_Negative_Ratio_Over_Time_Quarterly_{safe_aspect}.png"), dpi=300)
            plt.close()

# Generate plots for "Without UX" (Overall only)
create_plots(df_filtered, output_dir_without_ux, generate_individual=False)

# Generate plots for "Grouped" (Overall + Individual)
create_plots(df_grouped, output_dir_grouped, generate_individual=True)

print(f"✅ All quarterly plots saved successfully in:\n- {output_dir_without_ux}\n- {output_dir_grouped}")
