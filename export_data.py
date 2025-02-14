import sqlite3
import json
from datetime import datetime
from collections import defaultdict
connection = sqlite3.connect('coding_curbs.db')
# cursor - pointer that helps to interact with db
cursor = connection.cursor() 

cursor.execute("""
SELECT * FROM parking_status
WHERE sensor_id = '863213040206349'
ORDER BY timestamp
""")

# Once a query is executed, I use the cursor to fetch the results.
# cursor.fetchall(): Fetches all the rows from the query.
# cursor.fetchone(): Fetches the next row from the query.
# cursor.fetchmany(n): Fetches n rows from the query.

rows = cursor.fetchall()

# Convert rows to a list of dictionaries (use column names as keys)
columns = [column[0] for column in cursor.description] 
data_as_dicts = [dict(zip(columns, row)) for row in rows] 
# columns - keys (names of the columns)
# row - values
# zip - creates iterator , and makes the key-value pairs: ("status": 0), ("timestamp": "2024-10-10 07:05:01"), 
# dict - creates the dictionary 

def calculate_hours_on(data):
	amount_of_days = 0
	total_duration = 0
	hours_per_day = {}
	hour_frequency = defaultdict(int)
	current_period_start = None
	previous_date = None  # Initialize previous_date to None

	for entry in data:
		status = entry['status']
		timestamp = entry['timestamp']
		current_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
		current_date = current_time.date()
		if previous_date is not None and previous_date != current_date:
			# If the date has changed, reset the start time for the new day
			current_period_start = datetime.combine(current_date, datetime.min.time())
			amount_of_days += 1

		if status == 1 and current_period_start is None:
			current_period_start = current_time  # Start a new "on" period
		
		# If the sensor goes "off" (0), calculate the time difference
		elif status == 0 and current_period_start is not None:
			time_diff = (current_time - current_period_start).total_seconds() / 3600  # Convert to hours
			# print(f"Time difference in hours: {time_diff} for current_time {current_time} and current_period_start {current_period_start}")
			if current_date not in hours_per_day:
				hours_per_day[current_date] = 0
			hours_per_day[current_date] += time_diff
			total_duration +=time_diff

			#calculating peak hour
			hour_of_day = current_time.hour
			hour_frequency[hour_of_day] += 1
			
			
			current_period_start = None
		
		# Update previous_date for the next iteration
		previous_date = current_date
	peak_hour = max(hour_frequency, key=hour_frequency.get)
	average_duration = round(total_duration / amount_of_days, 1)
	return hours_per_day, average_duration, peak_hour


hours_on, average_duration, peak_hour = calculate_hours_on(data_as_dicts)

total_parking_activities = len(rows)

# print(f"average {average_duration}")

for entry in data_as_dicts:
    timestamp = entry['timestamp']
    current_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    current_date = current_time.date()

    entry['hours_on'] = hours_on.get(current_date, 0)

output_data = {
    "sensor_data": data_as_dicts,
    "hours_per_day": [{"date": str(date), "hours_on": hours} for date, hours in hours_on.items()],
	"total_parking_activities": total_parking_activities,
	"average_duration": average_duration,
	"peak_hour": peak_hour
}

json_data = json.dumps(output_data, indent=4)
with open("data.json", "w") as json_file:
    json_file.write(json_data)


cursor.close()
connection.close()

# To run it: python export_data.py