import os
import pandas as pd
import glob

# ==========================================================
# FILE PATHS
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

NAV_FILE = os.path.join(
    BASE_DIR,
    "..",
    "Nav table.xlsx"
)

RETURN_FILE = os.path.join(
    BASE_DIR,
    "output_result",
    "return_metrics"
)
files = glob.glob(os.path.join(RETURN_FILE, "*.xlsx"))

return_list = []

for file in files:

    df = pd.read_excel(file)

    return_list.append(df)

returns = pd.concat(return_list, ignore_index=True)

# --------------------------------------------------
# Rename columns
# --------------------------------------------------

returns.rename(
    columns={
        "insurer_name": "Insurer",
        "fund_name": "Fund Name"
    },
    inplace=True
)

# --------------------------------------------------
# Create Return Score
# --------------------------------------------------

returns["Return Score"] = returns[
    [
        "1M Return (%)",
        "3M Return (%)",
        "6M Return (%)",
        "1Y Return (%)"
    ]
].mean(axis=1)
print(returns.head())

RISK_FILE = os.path.join(
    BASE_DIR,
    "output_result",
    "risk_metrics",
    "RiskMetrics_Summary_With_RiskScore.xlsx"
)

CONSISTENCY_FILE = os.path.join(
    BASE_DIR,
    "output_result",
    "consistency_metrics",
    "Consistency_Metrics.xlsx"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "output_result",
    "Category_Comparison.xlsx"
)

# ==========================================================
# WEIGHTS
# ==========================================================

RETURN_WEIGHT = 0.40
RISK_WEIGHT = 0.30
CONSISTENCY_WEIGHT = 0.30

# ==========================================================
# LOAD FILES
# ==========================================================

print("Loading files...")


risk = pd.read_excel(RISK_FILE)

consistency = pd.read_excel(
    CONSISTENCY_FILE,
    sheet_name="Fund Summary"
)

lookup = pd.read_excel(
    NAV_FILE,
    sheet_name="Lookup"
)

# ==========================================================
# KEEP REQUIRED COLUMNS
# ==========================================================

returns = returns[
    [
        "Insurer",
        "Fund Name",
        "Return Score"
    ]
]

risk = risk[
    [
        "Insurer",
        "Fund Name",
        "Risk Score"
    ]
]

consistency = consistency[
    [
        "Insurer",
        "Fund",
        "Consistency Score"
    ]
]

lookup = lookup[
    [
        "Insurer",
        "Fund Name",
        "Category"
    ]
]
# Standardize insurer names
returns["Insurer"] = returns["Insurer"].str.strip()
risk["Insurer"] = risk["Insurer"].str.strip()
consistency["Insurer"] = consistency["Insurer"].str.strip()
lookup["Insurer"] = lookup["Insurer"].str.strip()

# Make Tata insurer name consistent
returns["Insurer"] = returns["Insurer"].replace({
    "TATA AIA": "Tata AIA"
})

risk["Insurer"] = risk["Insurer"].replace({
    "TATA AIA": "Tata AIA"
})

consistency["Insurer"] = consistency["Insurer"].replace({
    "TATA AIA": "Tata AIA"
})

def get_broad_category(category):
    category = str(category).lower()

    if "equity" in category:
        return "Equity"

    elif "balanced" in category or "hybrid" in category:
        return "Hybrid"

    elif "debt" in category:
        return "Debt"

    elif "liquid" in category:
        return "Liquid"

    else:
        return "Others"

lookup["Broad Category"] = lookup["Category"].apply(get_broad_category)
# ==========================================================
# MERGE EVERYTHING
# ==========================================================

print("Merging data...")

master = returns.merge(

    risk,

    on=["Insurer", "Fund Name"],

    how="left"

)

master = master.merge(

    consistency,

    left_on=["Insurer", "Fund Name"],

    right_on=["Insurer", "Fund"],

    how="left"

)

master.drop(columns=["Fund"], inplace=True)

master = master.merge(

    lookup,

    on=["Insurer", "Fund Name"],

    how="left"

)

# ==========================================================
# FINAL SCORE
# ==========================================================

print("Calculating Final Score...")

master["Final Score"] = (

    master["Return Score"] * RETURN_WEIGHT +

    master["Risk Score"] * RISK_WEIGHT +

    master["Consistency Score"] * CONSISTENCY_WEIGHT

).round(2)

# ==========================================================
# CATEGORY RANK
# ==========================================================

master["Category Rank"] = (

    master.groupby(

        ["Insurer", "Broad Category"]

    )["Final Score"]

    .rank(

        ascending=False,

        method="dense"

    )

)

# ==========================================================
# SORT
# ==========================================================

master = master.sort_values(

    [

        "Insurer",

        "Broad Category",

        "Category Rank"

    ]

)
# ==========================================================
# REORDER COLUMNS
# ==========================================================

master = master[
    [
        "Insurer",
        "Broad Category",
        "Category",
        "Category Rank",
        "Fund Name",
        "Return Score",
        "Risk Score",
        "Consistency Score",
        "Final Score"
    ]
]
# ==========================================================
# EXPORT
# ==========================================================

with pd.ExcelWriter(

    OUTPUT_FILE,

    engine="openpyxl"

) as writer:

    master.to_excel(

        writer,

        sheet_name="Category Comparison",

        index=False

    )

print("\nDone!")
print("Output saved to:")
print(OUTPUT_FILE)