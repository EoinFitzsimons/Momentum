"""Simple test for the updated race simulation endpoint"""
import time
import json

# Wait for server to be ready
print("Waiting for server to start...")
time.sleep(3)

# Use PowerShell to make the request
import subprocess

payload = {
    "discipline": "SINGLE_SEATER",
    "track_id": 1,
    "num_laps": 50,
    "weather_conditions": "dry"
}

json_payload = json.dumps(payload).replace('"', '\\"')

ps_command = f"""
$body = '{json.dumps(payload)}'
$headers = @{{"Content-Type" = "application/json"}}
try {{
    $response = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/simulate/race' -Method Post -Body $body -Headers $headers -TimeoutSec 30
    Write-Output "SUCCESS!"
    $response | ConvertTo-Json -Depth 10
}} catch {{
    Write-Output "ERROR:"
    Write-Output $_.Exception.Message
    if ($_.ErrorDetails) {{
        Write-Output $_.ErrorDetails.Message
    }}
}}
"""

print("=" * 80)
print("TESTING UPDATED RACE SIMULATION ENDPOINT")
print("=" * 80)
print(f"Request: POST /simulate/race")
print(f"Payload: {json.dumps(payload, indent=2)}\n")

result = subprocess.run(
    ["powershell", "-Command", ps_command],
    capture_output=True,
    text=True,
    timeout=60
)

print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

print("\n" + "=" * 80)
