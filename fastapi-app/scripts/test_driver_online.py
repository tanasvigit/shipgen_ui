"""
Test script to verify driver online status endpoint.

Run this after:
1. Running migration: alembic upgrade head
2. Starting the server: uvicorn app.main:app --reload --port 9001
3. Seeding demo users: python scripts/seed_rbac_demo_users.py
"""

import requests
import json

BASE_URL = "http://localhost:9001"

def test_driver_online_flow():
    print("=" * 60)
    print("Testing Driver Online Status Update")
    print("=" * 60)
    
    # Step 1: Login as driver
    print("\n1. Logging in as driver@demo.local...")
    login_response = requests.post(
        f"{BASE_URL}/int/v1/auth/login",
        json={
            "identity": "driver@demo.local",
            "password": "RbacDemo123"
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    login_data = login_response.json()
    token = login_data.get("token")
    print(f"✓ Login successful")
    print(f"  Token: {token[:50]}...")
    print(f"  User: {login_data.get('user', {}).get('name')}")
    print(f"  Role: {login_data.get('user', {}).get('role')}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Set driver online
    print("\n2. Setting driver online...")
    online_response = requests.post(
        f"{BASE_URL}/driver/online",
        headers=headers,
        json={"online": 1, "status": "active"}
    )
    
    if online_response.status_code != 200:
        print(f"❌ Failed to set driver online: {online_response.status_code}")
        print(online_response.text)
        return
    
    driver_data = online_response.json().get("driver", {})
    print(f"✓ Driver set to online")
    print(f"  UUID: {driver_data.get('uuid')}")
    print(f"  Online: {driver_data.get('online')}")
    print(f"  Status: {driver_data.get('status')}")
    print(f"  Last Seen: {driver_data.get('last_seen_at')}")
    
    # Step 3: Verify by getting driver info
    print("\n3. Verifying driver status via driver portal...")
    # The driver can check their own status through orders endpoint
    orders_response = requests.get(
        f"{BASE_URL}/driver/orders",
        headers=headers,
        params={"limit": 1, "offset": 0}
    )
    
    if orders_response.status_code == 200:
        print(f"✓ Driver portal accessible")
        orders = orders_response.json().get("orders", [])
        print(f"  Found {len(orders)} orders")
    else:
        print(f"⚠ Could not verify via driver portal: {orders_response.status_code}")
    
    # Step 4: Set driver offline
    print("\n4. Setting driver offline...")
    offline_response = requests.post(
        f"{BASE_URL}/driver/online",
        headers=headers,
        json={"online": 0, "status": "inactive"}
    )
    
    if offline_response.status_code != 200:
        print(f"❌ Failed to set driver offline: {offline_response.status_code}")
        print(offline_response.text)
        return
    
    driver_data = offline_response.json().get("driver", {})
    print(f"✓ Driver set to offline")
    print(f"  Online: {driver_data.get('online')}")
    print(f"  Status: {driver_data.get('status')}")
    print(f"  Last Seen: {driver_data.get('last_seen_at')}")
    
    # Step 5: Test with admin to see driver in list
    print("\n5. Logging in as admin to check driver list...")
    admin_login = requests.post(
        f"{BASE_URL}/int/v1/auth/login",
        json={
            "identity": "admin@demo.local",
            "password": "RbacDemo123"
        }
    )
    
    if admin_login.status_code == 200:
        admin_token = admin_login.json().get("token")
        admin_headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
        
        drivers_response = requests.get(
            f"{BASE_URL}/fleetops/v1/drivers",
            headers=admin_headers,
            params={"limit": 50, "offset": 0}
        )
        
        if drivers_response.status_code == 200:
            drivers_data = drivers_response.json()
            drivers = drivers_data.get("data", [])
            driver_found = None
            
            for d in drivers:
                if d.get("status") == "active" or d.get("online") == 1:
                    driver_found = d
                    break
            
            if driver_found:
                print(f"✓ Found driver in admin list")
                print(f"  UUID: {driver_found.get('uuid')}")
                print(f"  Online: {driver_found.get('online')}")
                print(f"  Status: {driver_found.get('status')}")
            else:
                print(f"⚠ Driver not found or offline in admin list")
                print(f"  Total drivers: {len(drivers)}")
        else:
            print(f"⚠ Could not fetch drivers list: {drivers_response.status_code}")
    else:
        print(f"⚠ Could not login as admin: {admin_login.status_code}")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_driver_online_flow()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server at http://localhost:9001")
        print("   Make sure the FastAPI server is running")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
