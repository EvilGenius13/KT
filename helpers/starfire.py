import json
import requests

class Starfire:
  def log(data):
    url = 'http://localhost:8010/ingest/event'
    headers = {'Content-Type': 'application/json'}
    try:
        payload = json.dumps(data)
        response = requests.post(url, data=payload, headers=headers)
        return response.status_code
    except Exception as e:
        print(f"Error sending event to Starfire: {e}")