"""Quick test to call the race endpoint with curl-like syntax"""
import subprocess
import json

# Test payload
payload = {
    "discipline": "SINGLE_SEATER",
    "track_id": 1,
    "num_laps": 50
}

# Convert to JSON string
json_payload = json.dumps(payload)

# Use Invoke-RestMethod in PowerShell
ps_command = f"""
$body = '{json_payload}'
try {{
    $response = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/simulate/race' -Method Post -Body $body -ContentType 'application/json' -TimeoutSec 30
    $response | ConvertTo-Json -Depth 10
}} catch {{
    Write-Host "Error: $_"
    $_.Exception.Response
}}
"""

print("Testing race simulation endpoint...")
print(f"Payload: {json_payload}\n")

result = subprocess.run(
    ["powershell", "-Command", ps_command],
    capture_output=True,
    text=True
)

print("STDOUT:")
print(result.stdout)
if result.stderr:
    print("\nSTDERR:")
    print(result.stderr)
print(f"\nExit code: {result.returncode}")
