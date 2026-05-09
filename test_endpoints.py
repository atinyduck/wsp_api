import requests
import json

API_BASE = "http://localhost:8000"

print("=" * 60)
print("Testing WSP API Endpoints")
print("=" * 60)

# Test 1: Login
print("\n[TEST 1] Login with Officer Credentials")
login_payload = {
    "username": "12345",
    "password": "johndoe"
}
response = requests.post(f"{API_BASE}/token", data=login_payload)
print(f"Status: {response.status_code}")
if response.status_code == 201:
    token_data = response.json()
    token = token_data['access_token']
    print(f"/ Login successful!")
    print(f"Token: {token[:50]}...")
else:
    print(f"X Login failed: {response.json()}")
    token = None

if token:
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 2: Get Officer's Citations
    print("\n[TEST 2] Get Officer's Citations")
    response = requests.get(
        f"{API_BASE}/notices/officer/12345",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        citations = response.json()
        print(f"/ Got {len(citations)} citations")
        for citation in citations:
            print(f"  - Notice ID: {citation['Notice_ID']}, "
                  f"Driver: {citation['Driver_ID']}, "
                  f"Violations: {citation['Violations']}")
    else:
        print(f"X Failed: {response.json()}")
    
    # Test 3: Get All Drivers
    print("\n[TEST 3] Get All Drivers")
    response = requests.get(f"{API_BASE}/drivers/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        drivers = response.json()
        print(f"✅ Got {len(drivers)} drivers")
        for driver in drivers:
            print(f"  - ID: {driver['Driver_ID']}, "
                  f"Name: {driver['First_Name']} {driver['Last_Name']}")
    else:
        print(f"X Failed: {response.json()}")

print("\n" + "=" * 60)
print("Testing Complete")
print("=" * 60)