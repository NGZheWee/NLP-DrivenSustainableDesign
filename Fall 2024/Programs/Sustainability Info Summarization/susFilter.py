import os
import pandas as pd
import json

# Directories
input_dir = r"D:\OneDrive\UC Berkeley\Sustainable Design Insights\Databases\V6 GPT ABSA"
output_dir = r"D:\OneDrive\UC Berkeley\Sustainable Design Insights\Databases\V7 Sustainability Info\Excels_Sustainability Reviews"
os.makedirs(output_dir, exist_ok=True)

# Aspects to check (excluding User Experience aspects)
aspects_to_check = [
    "General Sustainability", "Material: Bio Friendly", "Material: Chemical Contents",
    "Material: Recyclability", "Material: Waste", "Packaging",
    "Environment: Bioenvironment", "Environment: Climate", "Energy: Consumption",
    "Energy: Renewability", "Manufacturing Process: Production", "Manufacturing Process: Worker",
    "Manufacturing Process: Supply"
]

# Function to filter rows in a CSV file
def filter_csv(input_file, output_file):
    print(f"Processing {input_file}...")
    # Read the CSV file
    df = pd.read_csv(input_file)

    # Filter rows
    filtered_rows = []
    for index, row in df.iterrows():
        try:
            # Parse the ABSA_GPT column
            absa_gpt = json.loads(row["GPT_ABSA"])

            # Check if all specified aspects have a value of 0
            if any(absa_gpt.get(aspect, 0) != 0 for aspect in aspects_to_check):
                filtered_rows.append(row)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Skipping row {index}: Invalid JSON or missing GPT_ABSA column. Error: {e}")

    # Create a new DataFrame from the filtered rows
    filtered_df = pd.DataFrame(filtered_rows)

    # Save the filtered DataFrame to a new CSV file
    filtered_df.to_csv(output_file, index=False)
    print(f"Filtered data saved to {output_file}")

# Process all files in the input directory
def process_all_files(input_dir, output_dir):
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".csv"):
            input_file = os.path.join(input_dir, file_name)
            output_file = os.path.join(output_dir, file_name)
            filter_csv(input_file, output_file)

# Run the processing
process_all_files(input_dir, output_dir)
