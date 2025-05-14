import re

def clean_lines(raw_lines):
    cleaned_lines = []
    for line in raw_lines:
        # Skip repeating headers or footers
        if "Calendar Year 2023" in line or "Ward & Parcel No" in line or "Sources:" in line:
            continue
        if re.match(r"\d+ of \d+", line): # this filters out x+ of y+ lines
            continue
        cleaned_lines.append(line.strip())
    return cleaned_lines

def merge_rows(lines):
    rows = []
    current_row = ""
    for line in lines:
        if re.match(r"\d{2}‐\d{5}‐\d{3}", line):  # Detect start of a new record
            if current_row:
                rows.append(current_row.strip())
            current_row = line
        else:
            current_row += " " + line
    if current_row:
        rows.append(current_row.strip())
    return rows

def parse_row(row):
    pattern = re.compile(
        r"(?P<parcel>\d{2}[‐-]\d{5}[‐-]\d{3})\s+"
        r"(?P<street_no>\d+)\s+"
        r"(?P<street_name>.+?)\s+"
        r"(?P<sale_date>\d{1,2}/\d{1,2}/\d{4})\s+"
        r"(?P<sale_price>[\d,]+)\s*\$\s+"
        r"(?P<living_area>[\d,]+)\s+"
        r"(?P<price_per_sf>[\d.]+)\s+"
        r"(?P<building_style>.+)"
    )

    match = pattern.match(row)
    
    if match:
        return match.groupdict()
    return None

import pandas as pd

def to_dataframe(parsed_rows):
    return pd.DataFrame([row for row in parsed_rows if row])

FILE_NAME = "data/condo_sales.txt"

with open(FILE_NAME, "r") as file:
    raw_lines = file.readlines()
    cleaned_lines = clean_lines(raw_lines)
    # print(cleaned_lines)
    merged_rows = merge_rows(cleaned_lines)
    parsed_rows = [parse_row(row) for row in merged_rows]
    df = to_dataframe(parsed_rows)
    print(df)
    # save to csv
    csv_file_name = FILE_NAME.replace(".txt", ".csv")
    df.to_csv(csv_file_name, index=False)