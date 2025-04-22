import csv
import sqlite3
from datetime import datetime
from collections import defaultdict
import json

def load_sensor_data_from_csv(csv_file_path):
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file, delimiter=';')  # use ; because your CSV is semicolon-delimited
        data = list(reader)

    for entry in data:
        entry['status'] = int(entry['status'])
        entry['sensor_id'] = entry['sensor_id'].strip()  # clean whitespace if needed
        entry['timestamp'] = entry['timestamp'].strip()
    return data


# Core logic to calculate total 'on' hours per day, average duration, and peak hour
def calculate_hours_on(data):
    amount_of_days = 0
    total_duration = 0
    hours_per_day = {}
    hour_frequency = defaultdict(int)

    current_period_start = None
    previous_date = None
    previous_status = None
    status_changes = 0

    for entry in data:
        status = entry['status']
        timestamp = entry['timestamp']
        current_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        current_date = current_time.date()

        if previous_status is not None and previous_status != status:
            status_changes += 1

        if previous_date is not None and previous_date != current_date:
            amount_of_days += 1

        if status == 1 and current_period_start is None:
            current_period_start = current_time

        elif status == 0 and current_period_start is not None:
            time_diff = (current_time - current_period_start).total_seconds() / 3600
            hours_per_day[current_date] = hours_per_day.get(current_date, 0) + time_diff
            total_duration += time_diff

            hour_frequency[current_time.hour] += 1
            current_period_start = None

        previous_date = current_date
        previous_status = status

    peak_hour = max(hour_frequency, key=hour_frequency.get) if hour_frequency else None
    average_duration = round(total_duration / max(amount_of_days, 1), 2)

    return hours_per_day, average_duration, peak_hour, status_changes
