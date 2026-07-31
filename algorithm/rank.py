import pandas as pd
import os

# ==========================================================
# Paths
# ==========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RISK_FOLDER = os.path.join(BASE_DIR, "output_result", "risk_metrics")

SUMMARY_FILE = os.path.join(RISK_FOLDER, "RiskMetrics_Summary.xlsx")

print("Current Working Directory:", os.getcwd())

DAILY_FILES = [
    "icici nav_Daily_Returns.xlsx",
    "HDFC_nav_Daily_Returns.xlsx",
    "TATA AIA nav_Daily_Returns.xlsx"
]

# ==========================================================
# Read Summary
# ==========================================================
summary = pd.read_excel(SUMMARY_FILE)

# Clean summary text
summary["Insurer"] = (
    summary["Insurer"]
    .astype(str)
    .str.strip()
)

summary["Fund Name"] = (
    summary["Fund Name"]
    .astype(str)
    .str.strip()
    .str.replace(r"\s+", " ", regex=True)
)

# ==========================================================
# Read Categories
# ==========================================================
category_frames = []

for file in DAILY_FILES:

    path = os.path.join(RISK_FOLDER, file)

    df = pd.read_excel(path)

    # Clean text
    df["Insurer"] = (
        df["Insurer"]
        .astype(str)
        .str.strip()
    )

    df["Fund Name"] = (
        df["Fund Name"]
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    temp = (
        df[["Insurer", "Fund Name", "category"]]
        .drop_duplicates()
    )

    temp = temp.rename(columns={"category": "Category"})

    category_frames.append(temp)

category_df = pd.concat(category_frames, ignore_index=True)

category_df = category_df.drop_duplicates(
    subset=["Insurer", "Fund Name"]
)

# ==========================================================
# Merge
# ==========================================================
summary = summary.merge(
    category_df,
    on=["Insurer", "Fund Name"],
    how="left"
)


# ==========================================================
# Rank
# ==========================================================
summary["Volatility Rank"] = (
    summary.groupby("Category")["Annualized Volatility (%)"]
    .rank(method="min", ascending=True)
)

# ==========================================================
# Funds in each Category
# ==========================================================
summary["Funds in Category"] = (
    summary.groupby("Category")["Category"]
    .transform("count")
)

# ==========================================================
# Risk Score
# ==========================================================
def calculate_score(rank, total):

    if pd.isna(rank):
        return None

    if total <= 1:
        return 100

    return round(((total - rank) / (total - 1)) * 100)

summary["Risk Score"] = summary.apply(
    lambda x: calculate_score(
        x["Volatility Rank"],
        x["Funds in Category"]
    ),
    axis=1
)

# Convert rank to nullable integer
summary["Volatility Rank"] = summary["Volatility Rank"].astype("Int64")

summary["Risk Score"] = summary["Risk Score"].astype("Int64")

# ==========================================================
# Sort
# ==========================================================
summary = summary.sort_values(
    ["Category", "Volatility Rank"],
    na_position="last"
)

# ==========================================================
# Save
# ==========================================================
OUTPUT_FILE = os.path.join(
    RISK_FOLDER,
    "RiskMetrics_Summary_With_RiskScore.xlsx"
)

summary.to_excel(OUTPUT_FILE, index=False)

print("\nDone!")
print("Saved to:", OUTPUT_FILE)