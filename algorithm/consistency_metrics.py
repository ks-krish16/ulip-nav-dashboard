import pandas as pd
import numpy as np

# ==========================================================
# CONFIGURATION
# ==========================================================

INPUT_FILE = "Nav table.xlsx"

# ==========================================================
# LOAD ONE INSURER SHEET
# ==========================================================

def load_sheet(excel_file, sheet_name, column_mapping):
    """
    Reads one insurer sheet and converts it into a common format.

    Output Columns:
        insurer
        fund
        sfin
        date
        nav
    """

    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    print(f"\n{sheet_name}")
    print(df.columns.tolist())

    # Remove completely empty columns
    df = df.dropna(axis=1, how="all")

    # Rename columns to common names
    df = df.rename(columns=column_mapping)

    # Keep only required columns
    df = df.rename(columns=column_mapping)

    required_cols = ["insurer", "fund", "sfin", "date", "nav"]

    missing = [col for col in required_cols if col not in df.columns]

    if missing:
        raise ValueError(
            f"{sheet_name}: Missing columns {missing}\n"
            f"Available columns: {list(df.columns)}"
        )

    df = df[required_cols].copy()

    # Convert datatypes
    df["date"] = pd.to_datetime(df["date"])
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")

    # Remove invalid rows
    df = df.dropna(subset=["date", "nav"])

    # Sort by fund and date
    df = df.sort_values(
        ["fund", "date"]
    ).reset_index(drop=True)

    return df


# ==========================================================
# LOAD ALL INSURERS
# ==========================================================

def load_data():

    excel = pd.ExcelFile(INPUT_FILE)

    data = {}

    # ---------------- ICICI ----------------

    data["ICICI Prudential"] = load_sheet(
        excel,
        "icici nav",
        {
            "insurer_name": "insurer",
            "fund_name": "fund",
            "sfin": "sfin",
            "date": "date",
            "value": "nav"
        }
    )
    # ---------------- HDFC ----------------

    data["HDFC Life"] = load_sheet(
        excel,
        "HDFC_nav",
        {
            "insurer_name": "insurer",
            "fund_name": "fund",
            "sfin": "sfin",
            "date": "date",
            "value": "nav"
        }
    )

    # ---------------- TATA ----------------

    data["TATA AIA"] = load_sheet(

        excel,

        "TATA AIA nav",

        {
            "insurer_name": "insurer",
            "fund_name": "fund",
            "sfin": "sfin",
            "date": "date",
            "value": "nav"
        }

    )

    return data


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    data = load_data()

    for insurer, df in data.items():

        print(f"\n{insurer}")

        print(df.head())

        print(df.shape)

# ==========================================================
# MONTH-END NAV
# ==========================================================

def prepare_monthly_nav(df):
    """
    Converts daily NAVs into month-end NAVs.

    Output:
        Index   -> Month End
        Columns -> Fund Names
        Values  -> Month-end NAV
    """

    monthly_nav = (
        df.pivot_table(
            index="date",
            columns="fund",
            values="nav"
        )
        .resample("ME")
        .last()
    )

    return monthly_nav


# ==========================================================
# MONTHLY RETURNS
# ==========================================================

def calculate_monthly_returns(monthly_nav):
    """
    Monthly Return = NAV(t)/NAV(t-1)-1
    """

    return monthly_nav.pct_change()


# ==========================================================
# ROLLING 3-MONTH RETURNS
# ==========================================================

def calculate_rolling_returns(monthly_nav):
    """
    Rolling 3 Month Return

    NAV(t)
    -------
    NAV(t-3)
      -1
    """

    return monthly_nav.pct_change(periods=3)


# ==========================================================
# MONTHLY RANKS
# ==========================================================

def calculate_monthly_ranks(monthly_returns):
    """
    Highest monthly return gets Rank 1.
    """

    return monthly_returns.rank(
        axis=1,
        ascending=False,
        method="min"
    )


# ==========================================================
# PREPARE ALL MONTHLY DATA
# ==========================================================

def prepare_monthly_data(df):
    """
    Runs all monthly calculations.

    Returns
    -------
    monthly_nav
    monthly_returns
    rolling_returns
    monthly_ranks
    """

    monthly_nav = prepare_monthly_nav(df)

    monthly_returns = calculate_monthly_returns(monthly_nav)

    rolling_returns = calculate_rolling_returns(monthly_nav)

    monthly_ranks = calculate_monthly_ranks(monthly_returns)

    return (
        monthly_nav,
        monthly_returns,
        rolling_returns,
        monthly_ranks
    )



# ==========================================================
# SETTINGS
# ==========================================================

MIN_MONTHS_REQUIRED = 6

WEIGHT_POSITIVE = 0.40
WEIGHT_ROLLING = 0.40
WEIGHT_TOP_HALF = 0.20


# ==========================================================
# COMMON PERIOD
# ==========================================================

def restrict_common_period(monthly_nav):
    return monthly_nav


# ==========================================================
# CONSISTENCY SCORE
# ==========================================================

def calculate_consistency_score(
        positive_ratio,
        rolling_ratio,
        top_half_ratio):

    return round(

        positive_ratio * WEIGHT_POSITIVE +

        rolling_ratio * WEIGHT_ROLLING +

        top_half_ratio * WEIGHT_TOP_HALF,

        2
    )


# ==========================================================
# FUND METRICS
# ==========================================================

def calculate_fund_metrics(

        insurer,

        monthly_nav,

        monthly_returns,

        rolling_returns,

        monthly_ranks):

    summary = []

    monthly_details = []

    total_funds = len(monthly_nav.columns)

    top_half_limit = total_funds // 2

    for fund in monthly_nav.columns:

        nav = monthly_nav[fund].dropna()

        returns = monthly_returns[fund].dropna()

        rolling = rolling_returns[fund].dropna()

        ranks = monthly_ranks[fund].dropna()

        # -----------------------------------------
        # Data Quality
        # -----------------------------------------

        if len(returns) < MIN_MONTHS_REQUIRED:

            summary.append({
                "Insurer": insurer,
                "Fund": fund,
                "Status": "Insufficient History",
                "Positive Months": 0,
                "Total Months": len(returns),
                "Positive Month Ratio (%)": 0,
                "Positive Rolling Windows": 0,
                "Rolling Windows": len(rolling),
                "Rolling Consistency (%)": 0,
                "Average Rank": None,
                "Top Half Months": 0,
                "Top Half Ratio (%)": 0,
                "Consistency Score": 0
            })

            continue

        # -----------------------------------------
        # Positive Months
        # -----------------------------------------

        positive_months = (returns > 0).sum()

        total_months = len(returns)

        positive_ratio = round(

            positive_months /

            total_months *

            100,

            2

        )

        # -----------------------------------------
        # Rolling Returns
        # -----------------------------------------

        positive_rolling = (rolling > 0).sum()

        total_rolling = len(rolling)

        rolling_ratio = round(

            positive_rolling /

            total_rolling *

            100,

            2

        )

        # -----------------------------------------
        # Rank Stability
        # -----------------------------------------

        average_rank = round(

            ranks.mean(),

            2

        )

        top_half_months = (

            ranks <= top_half_limit

        ).sum()

        top_half_ratio = round(

            top_half_months /

            len(ranks) *

            100,

            2

        )

        # -----------------------------------------
        # Final Score
        # -----------------------------------------

        score = calculate_consistency_score(

            positive_ratio,

            rolling_ratio,

            top_half_ratio

        )

        # -----------------------------------------
        # Summary Row
        # -----------------------------------------

        summary.append({

            "Insurer": insurer,

            "Fund": fund,

            "Status": "Calculated",

            "Positive Months": positive_months,

            "Total Months": total_months,

            "Positive Month Ratio (%)": positive_ratio,

            "Positive Rolling Windows": positive_rolling,

            "Rolling Windows": total_rolling,

            "Rolling Consistency (%)": rolling_ratio,

            "Average Rank": average_rank,

            "Top Half Months": top_half_months,

            "Top Half Ratio (%)": top_half_ratio,

            "Consistency Score": score

        })

        # -----------------------------------------
        # Monthly Details
        # -----------------------------------------

        for month in monthly_nav.index:

            monthly_details.append({

                "Insurer": insurer,

                "Fund": fund,

                "Month": month,

                "NAV": monthly_nav.loc[month, fund],

                "Monthly Return":

                    monthly_returns.loc[month, fund],

                "Rolling 3M Return":

                    rolling_returns.loc[month, fund],

                "Rank":

                    monthly_ranks.loc[month, fund]

            })

    summary = pd.DataFrame(summary)

    monthly_details = pd.DataFrame(monthly_details)

    return summary, monthly_details        

# ==========================================================
# EXPORT RESULTS
# ==========================================================

def export_excel(summary_df, monthly_df):
    """
    Exports the final results into one Excel workbook.
    """

    # Sort funds by Consistency Score
    summary_df = summary_df.sort_values(
        by="Consistency Score",
        ascending=False,
        na_position="last"
    )

    with pd.ExcelWriter(
        "Consistency_Metrics.xlsx",
        engine="openpyxl"
    ) as writer:

        summary_df.to_excel(
            writer,
            sheet_name="Fund Summary",
            index=False
        )

        monthly_df.to_excel(
            writer,
            sheet_name="Monthly Calculations",
            index=False
        )

    print("\nConsistency_Metrics.xlsx created successfully!")


# ==========================================================
# MAIN
# ==========================================================

def main():

    print("=" * 60)
    print("Consistency Metrics Calculation Started")
    print("=" * 60)

    # Load all insurer data
    data = load_data()

    all_summary = []
    all_monthly = []

    # Process insurer-wise
    for insurer, df in data.items():

        print(f"\nProcessing {insurer}...")

        # Prepare monthly data
        (
            monthly_nav,
            monthly_returns,
            rolling_returns,
            monthly_ranks
        ) = prepare_monthly_data(df)

        # Restrict to common history
        monthly_nav = restrict_common_period(monthly_nav)
        print(f"\n{insurer}")
        print("Monthly NAV shape:", monthly_nav.shape)

        # Recalculate after restriction
        monthly_returns = calculate_monthly_returns(monthly_nav)

        rolling_returns = calculate_rolling_returns(monthly_nav)

        monthly_ranks = calculate_monthly_ranks(monthly_returns)

        # Calculate consistency metrics
        summary, monthly = calculate_fund_metrics(

            insurer,

            monthly_nav,

            monthly_returns,

            rolling_returns,

            monthly_ranks

        )

        all_summary.append(summary)
        all_monthly.append(monthly)

        print(f"✓ {insurer} completed.")

    # Combine insurers
    final_summary = pd.concat(
        all_summary,
        ignore_index=True
    )

    final_monthly = pd.concat(
        all_monthly,
        ignore_index=True
    )

    # Export
    export_excel(
        final_summary,
        final_monthly
    )

    print("\nDone!")


# ==========================================================
# RUN
# ==========================================================

if __name__ == "__main__":
    main()