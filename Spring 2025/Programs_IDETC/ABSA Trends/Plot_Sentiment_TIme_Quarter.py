import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Force a non-interactive backend
import matplotlib.pyplot as plt
import os
import re  # For filename sanitization

# Define updated file paths
input_file_path = r"D:\OneDrive\Academic History\Research\NLP-Driven Sustainable Design_CoDesign Lab\Co-Design Lab\Databases_IDETC\ABSA Trends_Quarter\ABSA_Counts_Quarter.csv"
output_dir = r"D:\OneDrive\Academic History\Research\NLP-Driven Sustainable Design_CoDesign Lab\Co-Design Lab\Databases_IDETC\ABSA Trends_Quarter"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load dataset
df = pd.read_csv(input_file_path)

# Convert "Quarter" column to proper datetime format
df["Quarter"] = pd.to_datetime(df["Quarter"])  # Assuming format is already correct

# Ensure the data is sorted by quarter
df = df.sort_values(by=["Quarter"])

# Group by aspect and process each
aspects = df["Aspect"].unique()

# **Function to sanitize filenames**
def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name)  # Replace invalid characters with "_"

### **Plot 1: Total Reviews Over Time (All Aspects)**
plt.figure(figsize=(12, 6))
for aspect in aspects:
    aspect_data = df[df["Aspect"] == aspect]
    plt.plot(aspect_data["Quarter"], aspect_data["Total_Reviews"], marker="o", label=aspect)

plt.xlabel("Quarter")
plt.ylabel("Total Reviews")
plt.title("Total Reviews Over Time for Each Aspect (Quarterly)")
plt.xticks(rotation=45)
plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "0_Total_Reviews_Over_Time_Quarterly.png"), dpi=300)
plt.close()

### **Plot 2: Rate of Change of Total Reviews Over Time as Percentage (All Aspects)**
plt.figure(figsize=(12, 6))
for aspect in aspects:
    aspect_data = df[df["Aspect"] == aspect].copy()
    aspect_data["Review_Change_Percentage"] = aspect_data["Total_Reviews"].pct_change() * 100  # Convert to percentage
    plt.plot(aspect_data["Quarter"], aspect_data["Review_Change_Percentage"], marker="o", linestyle="--", label=aspect)

plt.xlabel("Quarter")
plt.ylabel("Rate of Change of Total Reviews (%)")
plt.title("Rate of Change of Total Reviews Over Time (Quarterly)")
plt.xticks(rotation=45)
plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "0_Rate_of_Change_Over_Time_Quarterly.png"), dpi=300)
plt.close()

### **Plot 3: Positive-Negative Ratio Over Time (All Aspects)**
plt.figure(figsize=(12, 6))
for aspect in aspects:
    aspect_data = df[df["Aspect"] == aspect]
    plt.plot(aspect_data["Quarter"], aspect_data["Positive_Negative_Ratio"], marker="o", label=aspect)

plt.xlabel("Quarter")
plt.ylabel("Positive-Negative Ratio")
plt.title("Positive-Negative Ratio Over Time for Each Aspect (Quarterly)")
plt.xticks(rotation=45)
plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "0_Positive_Negative_Ratio_Over_Time_Quarterly.png"), dpi=300)
plt.close()

### **INDIVIDUAL PLOTS for EACH ASPECT**
for aspect in aspects:
    aspect_data = df[df["Aspect"] == aspect].copy()
    safe_aspect = sanitize_filename(aspect)  # Fix invalid characters

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

    # **Rate of Change of Total Reviews as Percentage (Individual)**
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

# **Confirm save location**
print(f"✅ All quarterly plots saved successfully in: {output_dir}")
