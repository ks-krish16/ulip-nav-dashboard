import pandas as pd
from pathlib import Path

# =====================================
# CHANGE THIS TO YOUR CSV FOLDER
# =====================================
folder = Path(r"D:\work\A POP project\tata_nav_data")

all_data = []

# Read every CSV in the folder
for csv_file in folder.glob("*.csv"):
    print(f"Processing: {csv_file.name}")

    try:
        # Read CSV
        df = pd.read_csv(csv_file)

        # Rename Tata AIA columns
        df = df.rename(columns={
            "FDT": "date",
            "FPR": "value"
        })

        # Add insurer name
        df["insurer name"] = "TATA AIA"

        # Fund name from filename
        fund_name = csv_file.stem.replace("_", " ").title() + " Fund"
        df["fund name"] = fund_name

        # Keep only required columns
        df = df[["insurer name", "fund name", "value", "date"]]

        # Append
        all_data.append(df)

    except Exception as e:
        print(f"Error processing {csv_file.name}: {e}")

# Check if anything was read
if not all_data:
    raise Exception("No CSV files were successfully processed.")

# Combine all data
final_df = pd.concat(all_data, ignore_index=True)

# Convert date to proper Excel date (optional)
final_df["date"] = pd.to_datetime(
    final_df["date"],
    format="%d-%m-%Y",
    errors="coerce"
)

# Sort by fund and date
final_df = final_df.sort_values(
    by=["fund name", "date"]
)

# Save to Excel
output_file = folder / "TATA_AIA_NAV_MASTER.xlsx"
final_df.to_excel(output_file, index=False)

print("\n===================================")
print(f"Done! Total records: {len(final_df):,}")
print(f"Excel saved to:\n{output_file}")
print("===================================")