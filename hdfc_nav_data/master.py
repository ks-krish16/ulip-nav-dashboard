import requests
import pandas as pd
from datetime import datetime

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ5b3VyLXNlcnZpY2UiLCJleHAiOjE3ODY3ODMzOTUsInNjb3BlIjoicmVhZDphcGkifQ.PPz4eHiwcdbc7WNlMuVhVAogbeA0PZQ0DYiLd961r8Y"
DEVICE_ID = "c7096699-4688-40cf-a4ac-6b381f67486f"

HEADERS = {
    "Authorization": TOKEN,
    "Content-Type": "application/json",
    "Origin": "https://www.hdfclife.com",
    "Referer": "https://www.hdfclife.com/",
    "User-Agent": "Mozilla/5.0",
    "x-device-id": DEVICE_ID,
}

BASE = "https://apiretooling-prod.hdfclife.com/api/funds"

PRODUCTS = {
    56: "Click2Wealth",
    94: "Click2Invest",
    93: "SampoornNiveshPlus",
    96: "SmartProtectPlus",
}

FROM_DATE = "2025-07-31"
TO_DATE   = "2026-07-31"

all_data = []

for product_id, product_name in PRODUCTS.items():

    print(f"Fetching funds for {product_name}...")

    r = requests.post(
        f"{BASE}/get-product-funds-data/",
        headers=HEADERS,
        json={"product_id": str(product_id)},
    )
    r.raise_for_status()

    funds = r.json()["response"]["funds_data"]

    for fund in funds:

        fund_id = int(fund["fund_id"])
        fund_name = fund["fund_name"]

        print(f"   {fund_name}")

        payload = {
            "product_id": product_id,
            "fund_id": fund_id,
            "from_date": FROM_DATE,
            "to_date": TO_DATE,
            "max_min": True
        }

        nav = requests.post(
            f"{BASE}/get-fund-nav/",
            headers=HEADERS,
            json=payload,
        )

        nav.raise_for_status()

        history = nav.json()["response"]["nav_data"]

        df = pd.DataFrame(history)

        if len(df) == 0:
            continue

        df["product"] = product_name
        df["fund_name"] = fund_name
        df["fund_id"] = fund_id

        all_data.append(df)

final = pd.concat(all_data, ignore_index=True)

final = final[
    [
        "product",
        "fund_name",
        "fund_id",
        "nav_date",
        "bid_price",
    ]
]

final.to_excel("HDFC_Life_NAV_2025_2026(1).xlsx", index=False)

print(final.head())
print(f"\nRows downloaded: {len(final)}")