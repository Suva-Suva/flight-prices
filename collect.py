import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
TOKEN = os.getenv("TP_TOKEN")
URL = "https://api.travelpayouts.com/v2/prices/month-matrix"

ROUTES = [
    ("MOW", "LED"), ("MOW", "AER"), ("MOW", "KZN"), ("MOW", "SVX"),
    ("MOW", "KGD"), ("MOW", "OVB"), ("MOW", "KRR"), ("MOW", "MRV"),
    ("LED", "MOW"), ("LED", "AER"),
]
MONTHS = ["2026-11-01", "2026-12-01", "2027-01-01", "2027-02-01"]

rows = []
for origin, dest in ROUTES:
    for month in MONTHS:
        r = requests.get(URL, params={
            "origin": origin,
            "destination": dest,
            "month": month,
            "currency": "rub",
            "show_to_affiliates": "true",
            "token": TOKEN,
        }, timeout=30)
        if r.status_code != 200:
            print("Ошибка", origin, dest, month, r.status_code)
            continue
        for item in r.json().get("data", []):
            rows.append({"origin": origin, "destination": dest, **item})
        print("OK", origin, dest, month)
        time.sleep(0.5)

df = pd.DataFrame(rows)
print(df.shape)
print(df.head())

engine = create_engine(os.getenv("DATABASE_URL"))
df.to_sql("prices", engine, if_exists="replace", index=False)
print("Записано в PostgreSQL:", len(df), "строк")