import sqlite3
import json
from datetime import datetime
from collections import defaultdict


def calculate_hours_on(data):
	amount_of_days = 0
	total_duration = 0
	hours_per_day = {}
	hour_frequency = defaultdict(int)
	# The main difference between a dict and a defaultdict is that in defaultdict, 
	# if you access or try to retrieve a key that doesn't exist, it automatically creates an entry for that key 
	# with a default value. A regular dict would raise a KeyError
	current_period_start = None
	previous_date = None  # Initialize previous_date to None
	previous_status = None
	status_changes = 0  # Initialize previous_date to None
	for entry in data:
		status = entry['status']
		timestamp = entry['timestamp']
		current_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
		current_date = current_time.date()
		if previous_status is not None and previous_status != status:
			status_changes += 1
		# Counting all days:
		if previous_date is not None and previous_date != current_date:
			current_period_start = datetime.combine(current_date, datetime.min.time())
			amount_of_days += 1
		# Start a new "on" period
		if status == 1 and current_period_start is None:
			current_period_start = current_time
		
		# If the sensor goes "off" (0), calculate the time difference
		elif status == 0 and current_period_start is not None:
			time_diff = (current_time - current_period_start).total_seconds() / 3600  # Convert to hours
			# print(f"Time difference in hours: {time_diff} for current_time {current_time} and current_period_start {current_period_start}")
			if current_date not in hours_per_day:
				hours_per_day[current_date] = 0
			hours_per_day[current_date] += time_diff
			total_duration +=time_diff

			#Calculating peak hour
			hour_of_day = current_time.hour
			hour_frequency[hour_of_day] += 1
			
			current_period_start = None
			previous_status = status
		
		# Update previous_date for the next iteration
		previous_date = current_date
	peak_hour = max(hour_frequency, key=hour_frequency.get)
	average_duration = round(total_duration / amount_of_days, 2)
	return hours_per_day, average_duration, peak_hour, status_changes

def process_sensor_data(sensor_id, sensor_filename):
	connection = sqlite3.connect('data.db')
	# cursor - pointer that helps to interact with db
	cursor = connection.cursor() 

	cursor.execute("""
	SELECT * FROM parking_status
	WHERE sensor_id = ?
	ORDER BY timestamp
	""", (sensor_id,))
	#The ? is a placeholder (also called a parameter marker) in the query. 
	# It indicates that a value will be provided later, and it allows for parameterized queries. 

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


	hours_on, average_duration, peak_hour, status_changes = calculate_hours_on(data_as_dicts)
	total_parking_activities = status_changes

	# print(f"average {average_duration}")

	for entry in data_as_dicts:
		timestamp = entry['timestamp']
		current_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
		current_date = current_time.date()
		entry['hours_on'] = hours_on.get(current_date, 0)

	weekday_hours = {
		"Sunday": 0,
		"Monday": 0,
		"Tuesday": 0,
		"Wednesday": 0,
		"Thursday": 0,
		"Friday": 0,
		"Saturday": 0
	}

	for date, hours in hours_on.items():
    # Convert date to day of the week
		day_of_week = datetime.strptime(str(date), "%Y-%m-%d").strftime("%A")
		weekday_hours[day_of_week] += hours

	total_hours = sum(weekday_hours.values())

	# Calculate percentage for each day
	weekday_percentages = {
		day: (hours / total_hours) * 100 for day, hours in weekday_hours.items()
	}
	output_data = {
		"sensor_data": data_as_dicts,
		"hours_per_day": [{"date": str(date), "hours_on": hours} for date, hours in hours_on.items()],
		"total_parking_activities": total_parking_activities,
		"average_duration": average_duration,
		"peak_hour": peak_hour,
		"weekday_hours": weekday_hours,
		"weekday_percentages": weekday_percentages
	} 

	json_data = json.dumps(output_data, indent=4)
	with open(sensor_filename, "w") as json_file:
		json_file.write(json_data)


	cursor.close()
	connection.close()


process_sensor_data('863213040206349', '863213040206349.json')
process_sensor_data('863213040200508', '863213040200508.json')
process_sensor_data('863213040198520', '863213040198520.json')
process_sensor_data('863213040212347', '863213040212347.json')
# To run it: python export_data.py