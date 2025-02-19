import pandas as pd
from bs4 import BeautifulSoup
import glob
import os
import re

# Function to extract and clean table data step by step
def extract_table_data(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
        table = soup.find("table")

        if not table:
            return None

        # Extract table title
        title = table.find_previous("h2")
        table_title = title.text.strip() if title else os.path.basename(file_path)

        # Extract headers
        headers = [th.text.strip() for th in table.find_all("th")]

        # Extract rows
        data = []
        rows = table.find_all("tr")

        for row in rows:
            cols = row.find_all("td")
            # **Step 1: Remove Dollar Signs ($)**
            cols = [col.text.strip().replace("$", "") for col in cols]

            # **Step 2: Remove Parentheses and Percentage Signs (%, ())**
            cols = [re.sub(r"[\(\)%]", "", col) for col in cols]

            if any(cols):  # Keep only non-empty rows
                data.append(cols)

        # **Step 3: Ensure consistent column count**
        max_columns = max(len(row) for row in data) if data else 0
        if headers and len(headers) != max_columns:
            headers = ["Column_" + str(i) for i in range(max_columns)]  # Generic column names if misaligned

        # **Step 4: Create DataFrame**
        df = pd.DataFrame(data, columns=headers if headers else None)

        # **Step 5: Remove Empty Columns**
        df.dropna(axis=1, how="all", inplace=True)  # Drop columns that are entirely empty

        # **Step 6: Insert metadata (Filename, Table Title)**
        df.insert(0, "Filename", os.path.basename(file_path))
        df.insert(1, "Table Title", table_title)

        return df if not df.empty else None  # Return None if the table is empty

# **Process all HTML files in the current directory**
html_files = glob.glob("*.html")
all_data = []

for file in html_files:
    df = extract_table_data(file)
    if df is not None:
        all_data.append(df)

# **Save to an Excel file**
if all_data:
    final_df = pd.concat(all_data, ignore_index=True)

    # **Step 7: Remove Empty Rows**
    final_df.dropna(how="all", inplace=True)

    output_file = "cleaned_tablesthrough9.xlsx"
    final_df.to_excel(output_file, index=False)
    print(f"Excel file created: {output_file}")
else:
    print("No tables found in the provided HTML files.")
