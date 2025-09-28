#!/usr/bin/env python3
"""
Test script to demonstrate rate limiting functionality
"""
import requests
import json
import time
from datetime import datetime

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

def test_rate_limiting():
    print("🚦 Testing Rate Limiting Functionality")
    print("Rate limit: 5 orders per vendor per minute")
    print()
    
    vendor_id = 1
    successful_orders = 0
    rate_limited_orders = 0
    
    print(f"Creating orders for vendor {vendor_id}...")
    print()
    
    for i in range(7):
        order_id = f"RATE_TEST_{i+1:03d}"
        print(f"Creating order {i+1}/7: {order_id}")
        
        response = create_test_order(vendor_id, order_id)
        
        if response is None:
            print("Connection failed. Exiting test.")
            return
        
        if response.status_code == 200:
            successful_orders += 1
            print(f"Order {i+1} created successfully")
        elif response.status_code == 429:
            rate_limited_orders += 1
            print(f"Order {i+1} rate limited (429)")
            try:
                error_data = response.json()
                print(f" Error: {error_data.get('detail', 'Rate limit exceeded')}")
            except:
                print(f" Error: {response.text}")
        else:
            print(f"Order {i+1} failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f" Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f" Error: {response.text}")
        
        time.sleep(0.5)
    
    print()
    print("Test Results:")
    print(f"  Successful orders: {successful_orders}")
    print(f"  Rate limited orders: {rate_limited_orders}")
    print(f"  Total attempts: {successful_orders + rate_limited_orders}")
    
    if successful_orders == 5 and rate_limited_orders >= 1:
        print("Rate limiting is working correctly!")
    else:
        print(" Rate limiting may not be working as expected")

if __name__ == "__main__":
    print("FastAPI Rate Limiting Test")
    print("This script tests the rate limiting functionality.")
    print()
    
    test_rate_limiting()