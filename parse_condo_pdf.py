"""
Parse Boston condo‑sales PDF (CY‑2023), audit, list failures.

pip install pdfplumber pandas
"""

import re, pathlib, pdfplumber, pandas as pd

# ───────────────────────── CONFIG ─────────────────────────
PDF_DIR      = pathlib.Path("data/2023")
PDF_FILENAME = "FY2025 CDSalesReport_0.pdf"
PDF_PATH     = PDF_DIR / PDF_FILENAME
OUT_CSV      = PDF_PATH.with_suffix(".csv")

# ────────────────── HEADER / FOOTER CLEANERS ─────────────
def clean_lines(raw):
    keep = []
    for ln in raw:
        if ("Calendar Year" in ln or "Ward & Parcel No" in ln or "Sources:" in ln
            or re.match(r"\d+\s+of\s+\d+", ln)):          # pagination
            continue
        keep.append(ln.strip())
    return keep

# ───────────────────────── MERGER ────────────────────────
PARCEL_RE = re.compile(r"\d{2}[‐-]\d{5}[‐-]\d{3}")

def merge_rows(lines):
    rows, cur = [], ""
    for ln in lines:
        if PARCEL_RE.match(ln):
            if cur:
                rows.append(cur.strip())
            cur = ln
        else:
            cur += " " + ln
    if cur:
        rows.append(cur.strip())
    return rows

# ───────────────────────── REGEX (tweaked) ───────────────
CONDO_REGEX = re.compile(
    r"^(?P<parcel>\d{2}-\d{5}-\d{3})\s+"
    r"(?P<street_no>\d+[A-Z]?)\s+"              # 20  |  20A
    r"(?P<street_name>.+?)\s+"
    r"(?P<unit>[A-Za-z0-9\-\/]+)\s+"
    r"(?P<sale_date>\d{1,2}/\d{1,2}/\d{4})\s+"
    # ── 1️⃣ NEW: soak up “$ 4 80,000” (digits/commas/spaces) ──
    r"\$?\s*(?P<sale_price>\d[\d ,]*\d)\s+"     # allow internal spaces
    r"(?P<living_area>[\d ,]+)\s+"              # 2️⃣ allow spaces here too
    r"(?P<price_per_sf>[\d,.]+)\s*$"
)

def parse_row(row: str):
    row = row.replace("‐", "-")                 # normalize dashes
    m = CONDO_REGEX.match(row)
    if not m:
        return None
    d = m.groupdict()

    # strip commas *and* stray spaces before casting
    for col in ("sale_price", "living_area", "price_per_sf"):
        d[col] = float(d[col].replace(",", "").replace(" ", ""))

    return d

# ───────────────────────── PIPELINE ──────────────────────
def main():
    raw = []
    with pdfplumber.open(PDF_PATH) as pdf:
        for pg in pdf.pages:
            if txt := pg.extract_text():
                raw.extend(txt.splitlines())

    merged = merge_rows(clean_lines(raw))
    parsed, failed = [], []
    for r in merged:
        out = parse_row(r)
        (parsed if out else failed).append(out or r)

    df = pd.DataFrame(parsed)

    # ───── audit ─────
    print("\n——  Parse audit  ——")
    print(f"Rows detected  : {len(merged):,}")
    print(f"Rows parsed    : {len(df):,}")
    print(f"Rows failed    : {len(failed):,}")
    dup = len(df) - df['parcel'].nunique() if not df.empty else 0
    print(f"Duplicate parcels: {dup:,}")

    if failed:
        print(f"\n——  Unparsed rows ({len(failed)}) ——")
        for bad in failed[:20]:                 # show only first 20
            print(f"• {bad.split()[0]}  |  {bad}")

    df.to_csv(OUT_CSV, index=False)
    print(f"\nSaved {len(df):,} rows ➜ {OUT_CSV}")

    if failed:
        raise ValueError("Some condo rows did not parse — see list above.")
    if dup:
        raise ValueError("Duplicate parcel IDs found — verify PDF integrity.")

if __name__ == "__main__":
    main()
