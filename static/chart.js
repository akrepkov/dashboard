let chartInstances = {};

function loadCityData(cityName) {
    const sensorMap = {
        "Utrecht": "1001",
        "Groningen": "1002",
        "Amersfoort": "1003",
        "Rotterdam": "1004"
    };
    const sensor_id = sensorMap[cityName];
    console.log(sensor_id);

    fetch(`/sensor/${sensor_id}`)
        .then(response => response.json())
        .then(data => {
            const chartId = `chart-${cityName}`;
            const pieId = `pie-${cityName}`;

            // Destroy previous chart instances if they exist
            if (chartInstances[chartId]) {
                chartInstances[chartId].destroy();
            }
            if (chartInstances[pieId]) {
                chartInstances[pieId].destroy();
            }
            const hoursPerDay = data.hours_per_day;
            const days = hoursPerDay.map(entry => entry.date);
            const hours = hoursPerDay.map(entry => entry.hours_on);

            chartInstances[chartId] = new Chart(document.getElementById(chartId), {
                type: "bar",
                data: {
                    labels: days,
                    datasets: [{
                        label: "Time when the sensors were on",
                        data: hours,
                        backgroundColor: "#a686da",
                        borderColor: "rgba(75,192,192,1)",
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,  
                    scales: {
                        x: { title: { display: true, text: "Days" } },
                        y: { title: { display: true, text: "Hours per day" } }
                    }
                }
            });

            const weekdayHours = data.weekday_hours;
            const weekdays = Object.keys(weekdayHours);
            const hoursPerWeekday = Object.values(weekdayHours);

            chartInstances[pieId] = new Chart(document.getElementById(pieId), {
                type: "pie",
                data: {
                    labels: weekdays,
                    datasets: [{
                        label: 'Weekday hours',
                        data: hoursPerWeekday,
                        backgroundColor: [
                            '#575A9C', '#353786', '#3b1942',
                            '#2e2e4d', '#76c0f1', '#8F8F8F', '#6233ad'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,  
                    plugins: {
                        legend: { position: 'right' ,
                            labels: {
                                boxWidth: 20,
                                padding: 15,
                                font: { size: 18 }
                            }
                        },
                        title: { display: true }
                    },
                    radius: '90%',
                }
            });

            const peakHour = data.peak_hour;
            const peakTimeRange = `${peakHour}:00-${peakHour + 1}:00`;

            // document.getElementById("total_parking_activities").textContent = data.total_parking_activities;
            // document.getElementById("average_duration").textContent = data.average_duration;
            // document.getElementById("peak_hour").textContent = peakTimeRange;
        })
        .catch(error => console.error('Error loading JSON:', error));
}
