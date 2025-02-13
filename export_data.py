import sqlite3
import json
from datetime import datetime

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
from datetime import datetime

def calculate_hours_on(data):
	hours_per_day = {}
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

		if status == 1 and current_period_start is None:
			current_period_start = current_time  # Start a new "on" period
		
		# If the sensor goes "off" (0), calculate the time difference
		elif status == 0 and current_period_start is not None:
			time_diff = (current_time - current_period_start).total_seconds() / 3600  # Convert to hours
			# print(f"Time difference in hours: {time_diff} for current_time {current_time} and current_period_start {current_period_start}")
			if current_date not in hours_per_day:
				hours_per_day[current_date] = 0
			hours_per_day[current_date] += time_diff

			current_period_start = None
		
		# Update previous_date for the next iteration
		previous_date = current_date

	return hours_per_day


hours_on = calculate_hours_on(data_as_dicts)

for entry in data_as_dicts:
    timestamp = entry['timestamp']
    current_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    current_date = current_time.date()

    entry['hours_on'] = hours_on.get(current_date, 0)

output_data = {
    "sensor_data": data_as_dicts,
    "hours_per_day": [{"date": str(date), "hours_on": hours} for date, hours in hours_on.items()]
}

json_data = json.dumps(output_data, indent=4)
with open("data.json", "w") as json_file:
    json_file.write(json_data)


cursor.close()
connection.close()

# To run it: python3 export_data.py