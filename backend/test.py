import requests
import json

url = "http://127.0.0.1:5000/predict"  # Correct the Flask backend port


# Define your test data
data = {
    "required_species": "Oryzias latipes",
    "required_stages": [18, 20, 25],
    "available_temperatures": [24, 26, 28],
    "start_datetime": "2024-09-17T10:00:00",
    "desired_time": "2024-09-20T10:00:00",
    "lab_days": [1, 2, 3, 4],
    "lab_start_time": "08:00:00",
    "lab_end_time": "18:00:00"
}

# Send the POST request
response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(data))

# Check the response status and content
print(response.status_code)
if response.status_code == 200:
    print(response.json())
else:
    print(response.text)  # Print error message if it's not a 200 status