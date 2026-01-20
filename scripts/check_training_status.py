#!/usr/bin/env python3
import requests
import json
import time

SPACE_URL = "https://ainativestudio-kwanzaa-training.hf.space"

# Call the get_logs function
response = requests.post(
    f"{SPACE_URL}/gradio_api/call/get_logs",
    json={"data": []},
    headers={"Content-Type": "application/json"}
)

if response.status_code == 200:
    data = response.json()
    event_id = data.get("event_id")

    if event_id:
        # Get the result
        time.sleep(1)
        result_response = requests.get(
            f"{SPACE_URL}/gradio_api/call/get_logs/{event_id}",
            stream=True
        )

        for line in result_response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    try:
                        result_data = json.loads(line_str[6:])
                        if result_data:
                            print("Training Status:")
                            print("="*60)
                            print(result_data[0] if isinstance(result_data, list) else result_data)
                            print("="*60)
                            break
                    except:
                        pass
else:
    print(f"Error: {response.status_code}")
    print(response.text)
