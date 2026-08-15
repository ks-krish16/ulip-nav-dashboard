from pathlib import Path
import pandas as pd

input_folder = Path(__file__).parent
output_folder = input_folder / "nav_excel"
output_folder.mkdir(exist_ok=True)

funds = {
    "BSE_500_Enhanced_Value_50": {
        "fund_name": "BSE 500 Enhanced Value 50 Index Fund",
        "sfin": "ULIF 161 091025 EnhancedVF 105",
        "inception_date": "2025-11-10"
    },
    "Bluechip_fund": {
        "fund_name": "Bluechip Fund",
        "sfin": "ULIF 087 24/11/09 LBluChip 105",
        "inception_date": "2009-11-24"
    },
    "Dividend_leaders_50": {
        "fund_name": "Dividend Leaders 50 Index Fund",
        "sfin": "ULIF 163 300126 DivLeaders 105",
        "inception_date": "2026-03-02"
    },
    "focus50": {
        "fund_name": "Focus 50 Fund",
        "sfin": "ULIF 142 04/02/19 FocusFifty 105",
        "inception_date": "2019-03-20"
    },
    "India_consumption": {
        "fund_name": "India Consumption Fund",
        "sfin": "ULIF 158 170425 IndConsump 105",
        "inception_date": "2025-05-19"
    },
    "india_growth_fund": {
        "fund_name": "India Growth Fund",
        "sfin": "ULIF 141 04/02/19 IndiaGrwth 105",
        "inception_date": "2019-06-17"
    },
    "large_n_midcap": {
        "fund_name": "Large N Mid Cap Advantage Fund",
        "sfin": "ULIF 166 020626 LMidcapAdv 105",
        "inception_date": "2026-07-02"
    },
    "maximise_india": {
        "fund_name": "Maximise India Fund",
        "sfin": "ULIF 136 11/20/14 MIF 105",
        "inception_date": "2015-02-23"
    },
    "maximiserV": {
        "fund_name": "Maximiser Fund V",
        "sfin": "ULIF 114 15/03/11 LMaximis5 105",
        "inception_date": "2011-08-29"
    },
    "midcap_150_momentum_50": {
        "fund_name": "Mid Cap 150 Momentum 50 Index Fund",
        "sfin": "ULIF 151 180124 McMomentum 105",
        "inception_date": "2024-02-19"
    },
    "midcap_index": {
        "fund_name": "Mid Cap Index Fund",
        "sfin": "ULIF 149 050723 McIndxFund 105",
        "inception_date": "2023-09-25"
    },
    "midcap": {
        "fund_name": "Mid Cap Fund",
        "sfin": "ULIF 146 28/06/22 MidCapFund 105",
        "inception_date": "2022-09-23"
    },
    "midsmall_cap400": {
        "fund_name": "MidSmall Cap 400 Index Fund",
        "sfin": "ULIF 153 150424 MidSmal400 105",
        "inception_date": "2024-05-15"
    },
    "midsmall_cap_400_momentum_quality100": {
        "fund_name": "MidSmallCap 400 Momentum Quality 100 Index Fund",
        "sfin": "ULIF 156 251024 MscMomQual 105",
        "inception_date": "2024-12-02"
    },
    "multicap_growth": {
        "fund_name": "Multi Cap Growth Fund",
        "sfin": "ULIF 085 24/11/09 LMCapGro 105",
        "inception_date": "2009-11-24"
    },
    "multicap_50_25_25": {
        "fund_name": "Multicap 50 25 25 Index Fund",
        "sfin": "ULIF 152 220224 MultiCapIF 105",
        "inception_date": "2024-03-20"
    },
    "nifty_alpha_50": {
        "fund_name": "Nifty Alpha 50 Index Fund",
        "sfin": "ULIF 160 290725 AlphaIndIF 105",
        "inception_date": "2025-09-08"
    },
    "oppurtunities_fund": {
        "fund_name": "Opportunities Fund",
        "sfin": "ULIF 086 24/11/09 LOpport 105",
        "inception_date": "2009-11-24"
    },
    "sector_leader": {
        "fund_name": "Sector Leaders Index Fund",
        "sfin": "ULIF 162 251125 SecLeaders 105",
        "inception_date": "2025-12-29"
    },
    "smallcap_250": {
        "fund_name": "Smallcap 250 Index Fund",
        "sfin": "ULIF 164 270226 Smallcp250 105",
        "inception_date": "2026-03-30"
    },
    "Smallcap250_Momentum_quality100": {
        "fund_name": "Smallcap250 Momentum Quality 100 Index Fund",
        "sfin": "ULIF 157 301224 SmcMomQual 105",
        "inception_date": "2025-01-31"
    },
    "sustainable_equity": {
        "fund_name": "Sustainable Equity Fund",
        "sfin": "ULIF 145 03/06/21 SustainEqu 105",
        "inception_date": "2021-10-29"
    },
    "value_enhancer": {
        "fund_name": "Value Enhancer Fund",
        "sfin": "ULIF 139 24/11/17 VEF 105",
        "inception_date": "2018-07-23"
    },
    "pension_bluechip": {
        "fund_name": "Pension Bluechip Fund",
        "sfin": "ULIF 093 11/01/10 PBluChip 105",
        "inception_date": "2010-01-11"
    },
    "pension_india_consumption": {
        "fund_name": "Pension India Consumption Fund",
        "sfin": "ULIF 159 190625 PenIndCons 105",
        "inception_date": "2025-07-31"
    },
    "pension_india_growth": {
        "fund_name": "Pension India Growth Fund",
        "sfin": "ULIF 154 260624 PenIndGrwt 105",
        "inception_date": "2024-08-30"
    },
    "pension_multicap_growth": {
        "fund_name": "Pension Multi Cap Growth Fund",
        "sfin": "ULIF 091 11/01/10 PMCapGro 105",
        "inception_date": "2010-01-11"
    },
    "pension_oppurtunities": {
        "fund_name": "Pension Opportunities Fund",
        "sfin": "ULIF 092 11/01/10 POpport 105",
        "inception_date": "2010-01-11"
    }
}

filename_map = {
    "ICICI Nav Table - BSE 500 Enhanced Value 50 Index Fund": "BSE_500_Enhanced_Value_50",
    "ICICI Nav Table - Bluechip Fund": "Bluechip_fund",
    "ICICI Nav Table - Dividend Leaders 50 Index Fund": "Dividend_leaders_50",
    "ICICI Nav Table - Focus 50 Fund": "focus50",
    "ICICI Nav Table - India Consumption Fund": "India_consumption",
    "ICICI Nav Table - India Growth Fund": "india_growth_fund",
    "ICICI Nav Table - Maximise India Fund": "maximise_india",
    "ICICI Nav Table - Maximiser Fund V": "maximiserV",
    "ICICI Nav Table - Mid Cap 150 Momentum 50 Index Fund": "midcap_150_momentum_50",
    "ICICI Nav Table - Mid Cap Fund": "midcap",
    "ICICI Nav Table - MidSmall Cap 400 Index Fund": "midsmall_cap400",
    "ICICI Nav Table - MidSmallCap 400 Momentum Quality 100 Index Fund": "midsmall_cap_400_momentum_quality100",
    "ICICI Nav Table - Multi Cap Growth Fund": "multicap_growth",
    "ICICI Nav Table - Multicap 50 25 25 Index Fund": "multicap_50_25_25",
    "ICICI Nav Table - Opportunities Fund": "oppurtunities_fund",
    "ICICI Nav Table - Pension Bluechip Fund": "pension_bluechip",
    "ICICI Nav Table - Pension India Consumption Fund": "pension_india_consumption",
    "ICICI Nav Table - Pension India Growth Fund": "pension_india_growth",
    "ICICI Nav Table - Pension Multi Cap Growth Fund": "pension_multicap_growth",
    "ICICI Nav Table - Pension Opportunities Fund (1)": "pension_oppurtunities",
    "ICICI Nav Table - Sector Leaders Index Fund": "sector_leader",
    "ICICI Nav Table - Smallcap 250 Index Fund": "smallcap_250",
    "ICICI Nav Table - Smallcap250 Momentum Quality 100 Index Fund": "Smallcap250_Momentum_quality100",
    "ICICI Nav Table - Sustainable Equity Fund": "sustainable_equity",
    "ICICI Nav Table - Value Enhancer Fund": "value_enhancer",
}

all_data = []

for csv_file in input_folder.glob("*.csv"):
    print(f"Reading: {csv_file.name}")

    df = pd.read_csv(csv_file, header=None, names=["temp"])

    df[["date", "value"]] = df["temp"].str.split(",", expand=True)
    df.drop(columns="temp", inplace=True)

    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    df["value"] = df["value"].astype(float)

    key = filename_map.get(csv_file.stem)
    meta = funds.get(key)

    if meta:
        df.insert(0, "insurer_name", "ICICI Prudential")
        df.insert(1, "fund_name", meta["fund_name"])
        df.insert(2, "sfin", meta["sfin"])
       

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")

    all_data.append(df)

combined_df = pd.concat(all_data, ignore_index=True)

output_file = output_folder / "ICICI_Prudential_NAV_Data.xlsx"
combined_df.to_excel(output_file, index=False)

print(f"\nCreated: {output_file}")
print("\nDone!")