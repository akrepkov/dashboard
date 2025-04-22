from flask import Flask, render_template, jsonify
from utils import load_sensor_data_from_csv, calculate_hours_on
from datetime import datetime

app = Flask(__name__)

all_sensor_data = load_sensor_data_from_csv('data.csv')

#Filter by sensors 
def get_sensor_data(sensor_id):
    return [entry for entry in all_sensor_data if entry['sensor_id'] == sensor_id]

## API Endpoint:
# Flask route decorator defines a URL path that app will listen to
@app.route('/favicon.ico')
def favicon():
    return '', 204  # No Content

@app.route("/")
def home():
    return render_template("main.html") 

@app.route('/sensor/<sensor_id>') 
def sensor_report(sensor_id): #Passes 'sensor_id' from the URL into here
    sensor_data = get_sensor_data(sensor_id)

    if not sensor_data:
        return jsonify({"error": "Sensor not found"}), 404

    hours_on, avg_duration, peak_hour, status_changes = calculate_hours_on(sensor_data)

    # Add 'hours_on' to each entry for frontend
    for entry in sensor_data:
        current_time = datetime.strptime(entry['timestamp'], '%Y-%m-%d %H:%M:%S')
        entry['hours_on'] = hours_on.get(current_time.date(), 0)

    # Day of week summary
    weekday_hours = {day: 0 for day in ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]}
    for date, hours in hours_on.items():
        day_name = datetime.strptime(str(date), "%Y-%m-%d").strftime("%A")
        weekday_hours[day_name] += hours

    total_hours = sum(weekday_hours.values())
    weekday_percentages = {
        day: (hours / total_hours) * 100 if total_hours else 0
        for day, hours in weekday_hours.items()
    }

    result = {
        "sensor_data": sensor_data,
        "hours_per_day": [{"date": str(date), "hours_on": hours} for date, hours in hours_on.items()],
        "total_parking_activities": status_changes,
        "average_duration": avg_duration,
        "peak_hour": peak_hour,
        "weekday_hours": weekday_hours,
        "weekday_percentages": weekday_percentages
    }

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True) #Enables auto-reload when code changes (only on development stage!)