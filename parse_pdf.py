import re
import pdfplumber
import pandas as pd

PDF_PATH = "data/2019"
PDF_FILENAME = "ThreeFamily_CY2019_Sales (2).pdf"

def clean_lines(raw_lines):
    cleaned_lines = []
    for line in raw_lines:
        if "Calendar Year" in line or "Ward & Parcel No" in line or "Sources:" in line:
            continue
        if re.match(r"\d+ of \d+", line):  # Skip pagination
            continue
        cleaned_lines.append(line.strip())
    return cleaned_lines

def merge_rows(lines):
    rows = []
    current_row = ""
    for line in lines:
        if re.match(r"\d{2}[‐-]\d{5}[‐-]\d{3}", line):  # New record starts
            if current_row:
                rows.append(current_row.strip())
            current_row = line
        else:
            current_row += " " + line
    if current_row:
        rows.append(current_row.strip())
    return rows

def parse_row(row):
    # Handle dash variants: normalize all dashes to ASCII '-'
    row = row.replace("‐", "-")

    pattern = re.compile(
        r"(?P<parcel>\d{2}-\d{5}-\d{3})\s+"
        r"(?P<street_no>\d+)\s+"
        r"(?P<street_name>.+?)\s+"
        r"(?P<unit>\S+)\s+"  # Added Unit field
        r"(?P<sale_date>\d{1,2}/\d{1,2}/\d{4})\s+\$\s*"
        r"(?P<sale_price>[\d,]+)\s+"
        r"(?P<living_area>[\d,]+)\s+"
        r"(?P<price_per_sf>[\d.,]+)"
    )
    match = pattern.search(row)
    if match:
        return match.groupdict()
    return None

def to_dataframe(parsed_rows):
    return pd.DataFrame([row for row in parsed_rows if row])

# Step-by-step processing
if __name__ == "__main__":
    all_text_lines = []
    with pdfplumber.open(PDF_PATH + "/" + PDF_FILENAME) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split("\n")
                all_text_lines.extend(lines)

    cleaned_lines = clean_lines(all_text_lines)
    merged_rows = merge_rows(cleaned_lines)
    parsed_rows = [parse_row(row) for row in merged_rows]
    df = to_dataframe(parsed_rows)

    # Show and save
    print(df.head())
    new_filename = PDF_FILENAME.replace(".pdf", ".csv")
    df.to_csv(new_filename, index=False)