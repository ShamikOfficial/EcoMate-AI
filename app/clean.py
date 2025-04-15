import pandas as pd
import os

file_path = "./data/ghg-conversion-factors-2024-full_set__for_advanced_users__v1_1.xlsx"
xls = pd.ExcelFile(file_path)

relevant_sheets = ["Fuels"]

# Canonical form of desired column names (normalized)
desired_columns = [
    "Activity", "Fuel", "Unit", "kg CO2e", "kg CO2e of CO2 per unit"
]

collected_data = []

for sheet in relevant_sheets:
    try:
        df = pd.read_excel(xls, sheet_name=sheet)
        
        # Normalize column names to remove weird characters/spaces
        df.columns = df.columns.str.strip().str.replace('\n', ' ').str.replace('\r', ' ')
        print(f"Columns in {sheet}:", df.columns.tolist())  # Debugging line
        
        # Select matching columns
        selected_cols = [col for col in desired_columns if col in df.columns]
        if not selected_cols:
            print(f"No matching columns found in sheet: {sheet}")
            continue
        
        df_filtered = df[selected_cols].copy()
        df_filtered.loc[:, "Source Sheet"] = sheet
        collected_data.append(df_filtered)
        
    except Exception as e:
        print(f"Error processing sheet {sheet}: {e}")

if collected_data:
    combined_df = pd.concat(collected_data, ignore_index=True)
    combined_df.to_csv("data/cleaned_data.csv", index=False)
    print("Saved to cleaned_data.csv")
else:
    print("No data collected. Please check column headers.")
