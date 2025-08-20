import csv
from datetime import datetime, timedelta
import os
from .models import StoreStatusPing, BusinessHour, StoreTimezone, Report
from .db import db
from .utils import convert_local_to_utc, linear_interpolate

def generate_report(report_id):
    # choose current time
    max_ping = db.session.query(db.func.max(StoreStatusPing.timestamp_utc)).scalar()
    curr_time = max_ping

    results = []

    store_ids = [
        r[0]
        for r in db.session.query(StoreStatusPing.store_id).distinct()
    ]

    for store in store_ids:
        tz = StoreTimezone.query.filter_by(store_id=store).first()
        tz_str = tz.timezone_str if tz else "America/Chicago"

        # time windows
        one_hour_ago = curr_time - timedelta(hours=1)
        one_day_ago = curr_time - timedelta(days=1)
        one_week_ago = curr_time - timedelta(days=7)

        ping_data = (
            StoreStatusPing.query.filter_by(store_id=store)
            .filter(StoreStatusPing.timestamp_utc >= one_week_ago)
            .order_by(StoreStatusPing.timestamp_utc.asc())
            .all()
        )

        pings = [(p.timestamp_utc, 1 if p.status == "active" else 0) for p in ping_data]

        # get business hours for last 7 days
        hours = BusinessHour.query.filter_by(store_id=store).all()

        def compute_uptime(start, end):
            total_up, total_down = 0, 0
            # if missing business hours → assume 24*7
            if not hours:
                timeline = linear_interpolate(pings, start, end)
                for t, st in timeline:
                    if st == 1:
                        total_up += 1
                    else:
                        total_down += 1
                return total_up, total_down

            dt = start
            while dt < end:
                day_hrs = [h for h in hours if h.day_of_week == dt.weekday()]
                # if missing specific day → open 24h
                if not day_hrs:
                    slot_start = dt
                    slot_end = dt + timedelta(days=1)
                    sub_end = min(slot_end, end)
                    timeline = linear_interpolate(pings, slot_start, sub_end)
                    for t, st in timeline:
                        if st == 1:
                            total_up += 1
                        else:
                            total_down += 1
                    dt = slot_end
                    continue

                for h in day_hrs:
                    s_utc = convert_local_to_utc(h.start_time_local, dt.date(), tz_str)
                    e_utc = convert_local_to_utc(h.end_time_local, dt.date(), tz_str)
                    slot_start = max(start, s_utc)
                    slot_end = min(end, e_utc)
                    if slot_start < slot_end:
                        timeline = linear_interpolate(pings, slot_start, slot_end)
                        for t, st in timeline:
                            if st == 1:
                                total_up += 1
                            else:
                                total_down += 1
                dt += timedelta(days=1)
            return total_up, total_down

        up1, down1 = compute_uptime(one_hour_ago, curr_time)
        up24, down24 = compute_uptime(one_day_ago, curr_time)
        up7, down7 = compute_uptime(one_week_ago, curr_time)

        results.append(
            {
                "store_id": store,
                "uptime_last_hour(min)": up1,
                "uptime_last_day(hrs)": round(up24/60, 2),
                "uptime_last_week(hrs)": round(up7/60, 2),
                "downtime_last_hour(min)": down1,
                "downtime_last_day(hrs)": round(down24/60, 2),
                "downtime_last_week(hrs)": round(down7/60, 2),
            }
        )

    # save csv
    filename = f"report_{report_id}.csv"
    filepath = os.path.join("/app", filename)
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)

    # update DB
    rep = Report.query.get(report_id)
    rep.status = 'Complete'
    rep.csv_path = filepath
    db.session.commit()
