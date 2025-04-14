from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime

# Scopes for steps and sleep data
SCOPES = [
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/fitness.sleep.read'
]

# 1. Authenticate
flow = InstalledAppFlow.from_client_secrets_file('C:/Users/arora/Desktop/hackathon/google_fit_api/client_secret.json' , SCOPES)
creds = flow.run_local_server(port=8080)

service = build('fitness', 'v1', credentials=creds)

# 2. Define time range (last 24 hours)
end_time = int(datetime.datetime.now().timestamp() * 1e9)
start_time = int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp() * 1e9)

# 3. Get step count from appropriate data source
def get_steps():
    data_sources = service.users().dataSources().list(userId='me').execute()
    for source in data_sources['dataSource']:
        if 'step_count' in source['dataStreamName'].lower():
            dataset_id = f"{start_time}-{end_time}"
            data = service.users().dataSources().datasets().get(
                userId='me',
                dataSourceId=source['dataStreamId'],
                datasetId=dataset_id
            ).execute()
            total_steps = 0
            for point in data.get("point", []):
                for val in point["value"]:
                    total_steps += val.get("intVal", 0)
            return total_steps
    return 0

# 4. Get sleep duration
def get_sleep_hours():
    dataset_id = f"{start_time}-{end_time}"
    sleep_ds = service.users().sessions().list(userId='me').execute()
    total_sleep_sec = 0
    for session in sleep_ds.get("session", []):
        if session["activityType"] == 72:  # Sleep
            start = int(session["startTimeMillis"])
            end = int(session["endTimeMillis"])
            total_sleep_sec += (end - start) / 1000
    return total_sleep_sec / 3600  # Convert seconds to hours

steps = get_steps()
sleep_hours = get_sleep_hours()

print(f"Steps: {steps}")
print(f"Sleep Hours: {sleep_hours:.2f}")

import json
with open("player_stats.json", "w") as f:
    json.dump({"steps": steps, "sleepHours": sleep_hours, "workoutDuration": 0.0}, f)
