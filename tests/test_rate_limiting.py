import requests
import time

BASE_URL = "http://localhost:8000"

def create_test_order(vendor_id: int, order_id: str):

    order_data = {
        "order_id": order_id,
        "vendor_id": vendor_id,
        "priority": "LOW",
        "items": [
            {
                "item_name": "Test Item",
                "quantity": 1
            }
        ],
        "address": "123 Test St",
        "city": "Test City",
        "state": "Test State",
        "postal_code": "12345"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/orders/", json=order_data)
        return response
    except requests.exceptions.ConnectionError:
        print("Connection failed. Make sure the server is running:")
        return None

def test_rate_limiting(vendor_id: int, test_name: str):
    print(f"Testing {test_name} rate limiting...")
    
    successful_orders = 0
    rate_limited_orders = 0
    
    for i in range(7):
        order_id = f"{test_name.upper()}_TEST_{i+1:03d}"
        response = create_test_order(vendor_id, order_id)
        
        if response is None:
            print("Connection failed. Exiting test.")
            return False
        
        if response.status_code == 200:
            successful_orders += 1
        elif response.status_code == 429:
            rate_limited_orders += 1
        else:
            print(f"Unexpected status: {response.status_code}")
        
        time.sleep(0.5)
    
    print(f"Results: {successful_orders} successful, {rate_limited_orders} rate limited")
    
    if successful_orders == 5 and rate_limited_orders >= 1:
        print("PASS")
        return True
    else:
        print("FAIL")
        return False

def test_vendor_independence():
    print("Testing vendor independence...")
    
    response1 = create_test_order(1, "VENDOR1_INDEPENDENCE_TEST")
    vendor1_limited = response1 and response1.status_code == 429
    
    response2 = create_test_order(2, "VENDOR2_INDEPENDENCE_TEST")
    vendor2_success = response2 and response2.status_code == 200
    
    if vendor1_limited and vendor2_success:
        print("PASS - Vendors have independent rate limits")
        return True
    else:
        print("FAIL - Vendor independence not working")
        return False

if __name__ == "__main__":
    print("FastAPI Rate Limiting Test")
    print("Make sure your server is running: uvicorn app.main:app --reload")
    print()
    
    vendor1_success = test_rate_limiting(1, "Vendor1")
    independence_success = test_vendor_independence()
    vendor2_success = test_rate_limiting(2, "Vendor2")
    print("\nSUMMARY:")
    print(f"Vendor 1: {'PASS' if vendor1_success else 'FAIL'}")
    print(f"Independence: {'PASS' if independence_success else 'FAIL'}")
    print(f"Vendor 2: {'PASS' if vendor2_success else 'FAIL'}")
    
    if vendor1_success and independence_success and vendor2_success:
        print("\nALL TESTS PASSED!")
    else:
        print("\nSOME TESTS FAILED!")