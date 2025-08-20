"""
Run manually once inside Docker to populate DB from CSVs.
"""

import pandas as pd
from app import create_app
from app.db import db
from app.models import StoreStatusPing, BusinessHour, StoreTimezone

app = create_app()
ctx = app.app_context()
ctx.push()

def load():
    status_df = pd.read_csv("store_status.csv")
    bh_df = pd.read_csv("business_hours.csv")
    tz_df = pd.read_csv("store_timezones.csv")

    for _, r in status_df.iterrows():
        db.session.add(StoreStatusPing(
            store_id=r['store_id'],
            timestamp_utc=pd.to_datetime(r['timestamp_utc']),
            status=r['status']
        ))

    for _, r in bh_df.iterrows():
        db.session.add(BusinessHour(
            store_id=r['store_id'],
            day_of_week=r['dayOfWeek'],
            start_time_local=pd.to_datetime(r['start_time_local']).time(),
            end_time_local=pd.to_datetime(r['end_time_local']).time()
        ))

    for _, r in tz_df.iterrows():
        db.session.add(StoreTimezone(
            store_id=r['store_id'],
            timezone_str=r['timezone_str']
        ))

    db.session.commit()

if __name__ == "__main__":
    load()
    print("Loaded data!")
