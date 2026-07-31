import os
import pandas as pd
from pandas.tseries.offsets import DateOffset

# -----------------------------
# INPUT / OUTPUT
# -----------------------------
INPUT_FILE = "Nav table.xlsx"
OUTPUT_FOLDER = "output_result"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# -----------------------------
# RETURN METRICS FUNCTION
# -----------------------------
from pandas.tseries.offsets import DateOffset
import pandas as pd

def calculate_return(group, months=0, years=0):

    group = group.sort_values("date").reset_index(drop=True)

    latest_date = group.iloc[-1]["date"]
    latest_nav = group.iloc[-1]["value"]

    target_date = latest_date - DateOffset(months=months, years=years)

    # Find the nearest available NAV date
    group = group.copy()
    group["diff"] = (group["date"] - target_date).abs()

    previous = group.loc[group["diff"].idxmin()]

    # Don't use data that's too far away
    if previous["diff"] > pd.Timedelta(days=10):
        return None

    previous_nav = previous["value"]

    return round(((latest_nav - previous_nav) / previous_nav) * 100, 2)

    group = group.sort_values("date").reset_index(drop=True)

    latest_date = group.iloc[-1]["date"]
    latest_nav = group.iloc[-1]["value"]

    target_date = latest_date - DateOffset(months=months, years=years)

    # Allow a 7-day tolerance
    previous = group[group["date"] >= target_date - pd.Timedelta(days=7)]
    previous = previous[previous["date"] <= target_date + pd.Timedelta(days=7)]

    if previous.empty:
        return None

    previous_nav = previous.iloc[0]["value"]

    return round(((latest_nav - previous_nav) / previous_nav) * 100, 2)

    group = group.sort_values("date").reset_index(drop=True)

    if len(group) <= periods:
        return None

    latest_nav = group.iloc[-1]["value"]
    previous_nav = group.iloc[-periods-1]["value"]

    return round(((latest_nav - previous_nav) / previous_nav) * 100, 2)

    group = group.sort_values("date")

    latest_date = group["date"].iloc[-1]
    latest_nav = group["value"].iloc[-1]

    target_date = latest_date - DateOffset(months=months, years=years)

    previous = group[group["date"] <= target_date]

    if previous.empty:
        return None

    previous_nav = previous.iloc[-1]["value"]

    return round(((latest_nav - previous_nav) / previous_nav) * 100, 2)


# -----------------------------
# READ EXCEL
# -----------------------------
excel = pd.ExcelFile(INPUT_FILE)

# Ignore master sheet
sheets = [s for s in excel.sheet_names if s.lower() != "nav master"]



# -----------------------------
# PROCESS EACH INSURER
# -----------------------------
for sheet in sheets:

    print(f"\nProcessing {sheet}")

    df = pd.read_excel(INPUT_FILE, sheet_name=sheet)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    df = df.sort_values(["sfin", "date"])

    print(df["date"].dtype)
    print(type(df["date"].iloc[0]))

    results = []

    # ---------------------------------
    # PROCESS EACH FUND
    # ---------------------------------

    for fund_id, group in df.groupby("sfin"):

        group = group.sort_values("date")

        first = group.iloc[0]
        print(
        first["fund_name"],
        group["date"].min(),
        group["date"].max(),
        len(group)
        )


        results.append({

            "insurer_name": first["insurer_name"],


            "fund_name": first["fund_name"],

            "sfin": fund_id,

            "1M Return (%)": calculate_return(group, months=1),
            "3M Return (%)": calculate_return(group, months=3),
            "6M Return (%)": calculate_return(group, months=6),
            "1Y Return (%)": calculate_return(group, years=1),

        }
        )
        

    result_df = pd.DataFrame(results)

    output_file = os.path.join(
        OUTPUT_FOLDER,
        f"{sheet}_Return_Metrics.xlsx"
    )

    result_df.to_excel(output_file, index=False)

    print(f"Saved -> {output_file}")

print("\nFinished!")