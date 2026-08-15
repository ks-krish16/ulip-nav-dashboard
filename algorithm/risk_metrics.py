import os
import numpy as np
import pandas as pd

# -----------------------------
# INPUT / OUTPUT
# -----------------------------
INPUT_FILE = "Nav table.xlsx"
OUTPUT_FOLDER = "risk_metrics"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# -----------------------------
# READ EXCEL
# -----------------------------
excel = pd.ExcelFile(INPUT_FILE)

# Ignore master sheet
sheets = [
    s for s in excel.sheet_names
    if s.lower() not in ["nav master", "lookup"]
]

# -----------------------------
# STORE SUMMARY OF ALL INSURERS
# -----------------------------
summary_results = []

# -----------------------------
# PROCESS EACH INSURERa
# -----------------------------
for sheet in sheets:

    print(f"\nProcessing {sheet}")

    df = pd.read_excel(INPUT_FILE, sheet_name=sheet)

    # Convert date column
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Sort by Fund and Date
    df = df.sort_values(["sfin", "date"])

    # Store daily returns for this insurer
    daily_returns_results = []

    # -----------------------------
    # PROCESS EACH FUND
    # -----------------------------
    for fund_id, group in df.groupby("sfin"):

        group = group.sort_values("date").copy()

        first = group.iloc[0]

        print(
            first["fund_name"],
            group["date"].min().date(),
            group["date"].max().date(),
            len(group)
        )

        # -----------------------------
        # DAILY RETURNS
        # -----------------------------
        group["Daily Return"] = group["value"].pct_change()
        # -----------------------------
        # DRAWDOWN
        # -----------------------------

        # Running maximum NAV till each date
        group["Previous Peak NAV"] = group["value"].cummax()

        # Drawdown (%)
        group["Drawdown"] = (
            (group["value"] - group["Previous Peak NAV"])
            / group["Previous Peak NAV"]
        )

        # Maximum Drawdown
        maximum_drawdown = group["Drawdown"].min()

        # Store every day's NAV and Daily Return
        for _, row in group.iterrows():

           daily_returns_results.append({

            "Insurer": first["insurer_name"],

            "Fund Name": first["fund_name"],

            "SFIN": fund_id,

            "Date": row["date"],

            "NAV": row["value"],

            "Previous Peak NAV":
                row["Previous Peak NAV"],

            "Drawdown (%)":
                round(row["Drawdown"] * 100, 2),

            "Daily Return (%)":
                round(row["Daily Return"] * 100, 2)
                if pd.notna(row["Daily Return"])
                else None

        })

        # -----------------------------
        # DAILY VOLATILITY
        # -----------------------------
        daily_volatility = group["Daily Return"].std()

        # -----------------------------
        # ANNUALIZED VOLATILITY
        # -----------------------------
        annualized_volatility = daily_volatility * np.sqrt(250)
        
        negative_returns = group.loc[group["Daily Return"] < 0, "Daily Return"]

        if len(negative_returns) >= 2:
            downside_deviation = negative_returns.std()
        else:
            downside_deviation = 0.0

        annualized_downside_deviation = downside_deviation * np.sqrt(250)
        # -----------------------------
        # DOWNSIDE DEVIATION
        # -----------------------------

        negative_returns = group.loc[
            group["Daily Return"] < 0,
            "Daily Return"
        ]

        downside_deviation = negative_returns.std()

        annualized_downside_deviation = (
            downside_deviation * np.sqrt(250)
        )

        # -----------------------------
        # STORE SUMMARY
        # -----------------------------
        summary_results.append({

            "Insurer": first["insurer_name"],

            "Fund Name": first["fund_name"],

            "SFIN": fund_id,

            "Observations": group["Daily Return"].count(),

            "Daily Volatility (%)":
                round(daily_volatility * 100, 2),

            "Annualized Volatility (%)":
                round(annualized_volatility * 100, 2),

            "Downside Deviation (%)":
                round(downside_deviation * 100, 2),

            "Annualized Downside Deviation (%)":
                round(annualized_downside_deviation * 100, 2),

            "Maximum Drawdown (%)":
                round(maximum_drawdown * 100, 2)

        })

    # -----------------------------
    # SAVE DAILY RETURNS
    # -----------------------------
    daily_df = pd.DataFrame(daily_returns_results)

    daily_output = os.path.join(
        OUTPUT_FOLDER,
        f"{sheet}_Daily_Returns.xlsx"
    )

    daily_df.to_excel(daily_output, index=False)

    print(f"Saved -> {daily_output}")

# -----------------------------
# SAVE SUMMARY OF ALL FUNDS
# -----------------------------
summary_df = pd.DataFrame(summary_results)

summary_output = os.path.join(
    OUTPUT_FOLDER,
    "RiskMetrics_Summary.xlsx"
)

summary_df.to_excel(summary_output, index=False)

print(f"Saved -> {summary_output}")

print("\nFinished!")