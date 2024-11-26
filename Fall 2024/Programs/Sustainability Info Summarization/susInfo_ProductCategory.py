import os
import pandas as pd
import re
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend for matplotlib
import matplotlib.pyplot as plt

# Directories
input_dir = r"D:\OneDrive\Academic History\Researches\Sustainable Design Insights\Databases\V7 Sustainability Info_ProductCategory\Bar Charts_Sustainability Aspects\Raw"
output_dir = r"D:\OneDrive\Academic History\Researches\Sustainable Design Insights\Databases\V7 Sustainability Info_ProductCategory\Bar Charts_Sustainability Aspects"
os.makedirs(output_dir, exist_ok=True)

# Function to extract product category and number from the file name
def extract_category_and_number(file_name):
    match = re.match(r"(.+?)_(\d+)_sustainability_counts", file_name)
    if match:
        category = match.group(1).strip()
        number = int(match.group(2))
        return category, number
    return None, 0

# Function to sum counts while maintaining structure
def combine_files(input_dir, output_dir):
    files_grouped_by_category = {}

    # Group files by their product category
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".xlsx"):
            category, number = extract_category_and_number(file_name)
            if category:
                if category not in files_grouped_by_category:
                    files_grouped_by_category[category] = []
                files_grouped_by_category[category].append((file_name, number))

    # Combine files for each product category
    for category, files_info in files_grouped_by_category.items():
        combined_data = None
        total_count = 0

        for file_name, number in files_info:
            file_path = os.path.join(input_dir, file_name)
            df = pd.read_excel(file_path)

            # Ensure required columns exist
            if not {"Aspect", "Sentiment", "Count"}.issubset(df.columns):
                print(f"Skipping file {file_name}: Missing required columns.")
                continue

            # Sum counts while maintaining structure
            if combined_data is None:
                combined_data = df.copy()
            else:
                combined_data["Count"] += df["Count"]

            # Add the numeric part of the file name to the total count
            total_count += number

        if combined_data is not None:
            # Ensure original structure with sentiments -1 and 1 for all aspects
            unique_aspects = combined_data["Aspect"].unique()
            included_sentiments = [-1, 1]  # Only include -1 and 1 sentiments

            # Create a complete DataFrame with all combinations
            complete_data = pd.DataFrame(
                [(aspect, sentiment) for aspect in unique_aspects for sentiment in included_sentiments],
                columns=["Aspect", "Sentiment"]
            )
            # Merge with combined_data to retain structure
            combined_data = pd.merge(complete_data, combined_data, on=["Aspect", "Sentiment"], how="left").fillna(0)

            # Convert 'Count' to integers
            combined_data["Count"] = combined_data["Count"].astype(int)

            # Save to output directory
            output_file_name = f"{category}_{total_count}_sustainability_counts_Combined.xlsx"
            output_file_path = os.path.join(output_dir, output_file_name)
            combined_data.to_excel(output_file_path, index=False)
            print(f"Combined file saved: {output_file_path}")

            # Generate bar chart for the combined file
            generate_bar_chart(combined_data, category, total_count, output_dir)

# Function to generate bar charts
def generate_bar_chart(df, category, total_count, output_dir):
    # Filter out rows with `Count == 0`
    filtered_df = df[df["Count"] != 0].copy()

    # Add a combined column for Aspect and Sentiment
    filtered_df["Aspect_Sentiment"] = filtered_df["Aspect"] + "_" + filtered_df["Sentiment"].astype(str)

    # Plot the bar chart
    plt.figure(figsize=(12, 6))
    bars = plt.bar(filtered_df["Aspect_Sentiment"], filtered_df["Count"], color=['red' if x == -1 else 'green' for x in filtered_df["Sentiment"]])

    # Add counts at the top of each bar
    for bar, count in zip(bars, filtered_df["Count"]):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height, f"{int(count)}", ha='center', va='bottom')

    plt.title(f"Sustainability Aspect Counts for {category}_{total_count}")
    plt.xlabel("Aspect and Sentiment")
    plt.ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    # Save the chart
    chart_file_name = f"{category}_{total_count}_sustainability_counts_Combined_chart.png"
    chart_output_path = os.path.join(output_dir, chart_file_name)
    plt.savefig(chart_output_path)
    plt.close()
    print(f"Bar chart saved to {chart_output_path}")

# Run the process
combine_files(input_dir, output_dir)
