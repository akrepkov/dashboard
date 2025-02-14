Smart Zone Dashboard
Overview
The Smart Zone Dashboard helps city officials see how smart parking sensors are being used in their city. By analyzing parking data, it gives clear insights into how often parking spaces are being used, how long people park, and when parking activity is highest. This helps decision-makers better manage parking areas.

Features
Data Processing:
Imports and processes data about parking activity from a database.
Calculates useful insights, such as the total number of parking events, average parking time, and occupancy rates.
Dashboard:
Displays graphs showing parking activity, occupancy rates, and other important data.
Shows key numbers like the total number of parking activities, average parking time, and when parking is most popular.

1. Data Processing

Dataset Import
The parking data is stored in an SQLite database (coding_curbs.db) for easy management and querying. The database includes a table called parking_status that tracks:

Sensor ID: Identifies where the sensor is located.
Status: 1 means a vehicle is parked, and 0 means the parking spot is empty.
Timestamp: The exact time when the parking status changed.

SQL Queries & Python Processing
I use SQL to get the parking data from the database and Python to calculate useful information.

Key Insights:
Total Number of Parking Activities: Counts how many times a parking space status changes.
Average Parking Duration: Calculates how long, on average, a parking spot is occupied.
Peak hour: Calculates the most busy hour within recorded period of time.

2. Dashboard

Visualizations
Depending on chosen sensor (I gave them city names for easier interaction) we can see:
Total Number of Parking Activities
Average Parking Duration
Peak hour
Daily sensor on time: A graph created using Chart.js that shows the occupancy rate of parking spaces.

3. Requirements

Python: Required for running the data processing.
SQLite Database: The coding_curbs.db database should be available with the parking data.
Web Browser: For viewing the dashboard in HTML format.

How to Run:
- Set Up the Database: Ensure the SQLite database (coding_curbs.db) is ready and contains the relevant data.
- Run the Python script to process the data and generate the JSON files:
    python process_data.py
- Open the main.html file in any web browser to view the dashboard.