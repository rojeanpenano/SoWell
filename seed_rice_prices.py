from firebase_init import db
import pandas as pd
from datetime import datetime

# Load Excel file
excel_path = "weekly-rice_price.xlsx"
xls = pd.ExcelFile(excel_path)

# Filter only the weekly sheets
weekly_sheets = [s for s in xls.sheet_names if s.startswith("2025-W")]

# Loop through each sheet
for sheet_name in weekly_sheets:
    df = xls.parse(sheet_name)

    # Extract raw date range from cell A1
    raw_range = df.iloc[0, 0]  # example: "03/24/2025 - 03/29/2025"

    try:
        start_str, end_str = raw_range.split(" - ")
        start_date = datetime.strptime(start_str.strip(), "%m/%d/%Y")
        end_date = datetime.strptime(end_str.strip(), "%m/%d/%Y")
        # Format: April 7–12, 2025
        if start_date.month == end_date.month:
            readable_range = f"{start_date.strftime('%B')} {start_date.day}–{end_date.day}, {end_date.year}"
        else:
            readable_range = f"{start_date.strftime('%B %d')} – {end_date.strftime('%B %d, %Y')}"
    except:
        readable_range = raw_range.strip()  # fallback in case of error

    # Get price table
    price_data = df.iloc[3:, [0, 3, 4]]
    price_data.columns = ["quality", "imported", "local"]
    price_data.dropna(subset=["quality"], inplace=True)

    imported = []
    local = []

    for _, row in price_data.iterrows():
        if pd.notna(row["imported"]):
            imported.append({
                "quality": str(row["quality"]).strip(),
                "price_per_kg": float(row["imported"])
            })
        if pd.notna(row["local"]):
            local.append({
                "quality": str(row["quality"]).strip(),
                "price_per_kg": float(row["local"])
            })

    doc_data = {
        "recorded_range": readable_range,
        "imported": imported,
        "local": local,
        "updated_at": datetime.utcnow()
    }

    db.collection("rice_prices").document(sheet_name).set(doc_data)

print("Weekly rice prices uploaded successfully to Firestore.")