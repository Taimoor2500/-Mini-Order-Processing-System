import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def create_test_order(vendor_id: int, order_id: str, priority="LOW", items=None):
    if items is None:
        items = [{"item_name": "Test Item", "quantity": 1}]
    
    order_data = {
        "order_id": order_id,
        "vendor_id": vendor_id,
        "priority": priority,
        "items": items,
        "address": "123 Test Street",
        "city": "Test City", 
        "state": "Test State",
        "postal_code": "12345"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/orders/", json=order_data)
        return response
    except requests.exceptions.ConnectionError:
        print("Connection failed. Start server: uvicorn app.main:app --reload")
        return None

def test_basic_order_creation():
    order_id = f"BASIC_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    response = create_test_order(1, order_id)
    
    if response is None:
        return False
    
    if response.status_code == 200:
        return True
    elif response.status_code == 429:
        return test_basic_order_creation()
    else:
        return False

def test_different_priorities():
    priorities = ["LOW", "MEDIUM", "HIGH"]
    results = []
    
    for priority in priorities:
        order_id = f"PRIORITY_{priority}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        response = create_test_order(1, order_id, priority=priority)
        
        if response is None:
            results.append(False)
            continue
            
        if response.status_code == 200:
            results.append(True)
        elif response.status_code == 429:
            results.append(False)
        else:
            results.append(False)
        
        time.sleep(1)
    
    return any(results)

def test_multiple_items():
    items = [
        {"item_name": "Item 1", "quantity": 2},
        {"item_name": "Item 2", "quantity": 3},
        {"item_name": "Item 3", "quantity": 1}
    ]
    
    order_id = f"MULTI_ITEMS_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    response = create_test_order(1, order_id, items=items)
    
    if response is None:
        return False
    
    if response.status_code == 200:
        return True
    elif response.status_code == 429:
        return False
    else:
        return False

def test_vendor_independence():
    order_id_2 = f"VENDOR2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    response2 = create_test_order(2, order_id_2)
    
    if response2 is None:
        return False
    
    if response2.status_code == 200:
        return True
    else:
        return False

def test_duplicate_order():
    order_id = f"DUPLICATE_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    response1 = create_test_order(2, order_id)
    if response1 is None:
        return False
    
    response2 = create_test_order(2, order_id)
    if response2 is None:
        return False
    
    if response1.status_code == 200 and response2.status_code == 409:
        return True
    elif response1.status_code == 429:
        return False
    else:
        return False

def test_invalid_data():
    order_id = f"INVALID_QTY_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    response = create_test_order(2, order_id, items=[{"item_name": "Test", "quantity": 0}])
    
    if response is None:
        return False
    
    if response.status_code in [400, 422]:
        return True
    elif response.status_code == 429:
        return False
    else:
        return False

def test_order_status_retrieval():
    order_id = f"STATUS_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    create_response = create_test_order(2, order_id)
    
    if create_response is None:
        return False
    
    if create_response.status_code != 200:
        return False
    
    try:
        status_response = requests.get(f"{BASE_URL}/orders/status/{order_id}")
        if status_response.status_code == 200:
            return True
        else:
            return False
    except:
        return False

def main():
    tests = [
        ("Basic Order Creation", test_basic_order_creation),
        ("Different Priorities", test_different_priorities),
        ("Multiple Items", test_multiple_items),
        ("Vendor Independence", test_vendor_independence),
        ("Duplicate Order Rejection", test_duplicate_order),
        ("Invalid Data Handling", test_invalid_data),
        ("Order Status Retrieval", test_order_status_retrieval),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            results.append((test_name, False))
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"Results: {passed}/{len(results)} tests passed")

if __name__ == "__main__":
    main()
