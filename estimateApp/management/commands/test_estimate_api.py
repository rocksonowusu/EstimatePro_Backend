import requests
import json

# Configuration
BASE_URL = "https://estimatepro.pythonanywhere.com/api"  # Change to your actual URL
ESTIMATE_ID = 1  # Change to an existing estimate ID

# Test data for creating a new estimate
CREATE_DATA = {
    "user_email": "test@example.com",  # Use an existing user email
    "client_name": "Test Client",
    "estimate_title": "Test Estimate",
    "notes": "Test notes",
    "workmanship": 500.00,
    "total_materials": 1000.00,
    "grand_total": 1500.00,
    "items": [
        {
            "description": "Test Item 1",
            "quantity": 10,
            "unit": "pcs",
            "unit_price": 50.00,
            "amount": 500.00
        },
        {
            "description": "Test Item 2",
            "quantity": 5,
            "unit": "boxes",
            "unit_price": 100.00,
            "amount": 500.00
        }
    ]
}

# Test data for updating an existing estimate
UPDATE_DATA = {
    "client_name": "Updated Client Name",
    "estimate_title": "Updated Estimate Title",
    "notes": "Updated notes",
    "workmanship": 600.00,
    "total_materials": 1200.00,
    "grand_total": 1800.00,
    "items": [
        {
            "id": 1,  # Existing item ID - will update
            "description": "Updated Item 1",
            "quantity": 15,
            "unit": "pcs",
            "unit_price": 60.00,
            "amount": 900.00
        },
        {
            # No ID - will create new item
            "description": "New Item 3",
            "quantity": 3,
            "unit": "sets",
            "unit_price": 100.00,
            "amount": 300.00
        }
    ]
}


def test_create_estimate():
    """Test creating a new estimate"""
    print("\n=== Testing CREATE Estimate ===")
    url = f"{BASE_URL}/estimates/"
    
    try:
        response = requests.post(url, json=CREATE_DATA)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("✓ Estimate created successfully!")
            return response.json().get('id')
        else:
            print("✗ Failed to create estimate")
            return None
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return None


def test_get_estimate(estimate_id):
    """Test getting a single estimate"""
    print(f"\n=== Testing GET Estimate (ID: {estimate_id}) ===")
    url = f"{BASE_URL}/estimates/{estimate_id}/preview/"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✓ Estimate retrieved successfully!")
            return response.json()
        else:
            print("✗ Failed to retrieve estimate")
            return None
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return None


def test_update_estimate(estimate_id):
    """Test updating an existing estimate"""
    print(f"\n=== Testing UPDATE Estimate (ID: {estimate_id}) ===")
    url = f"{BASE_URL}/estimates/{estimate_id}/edit/"
    
    try:
        response = requests.put(url, json=UPDATE_DATA)
        print(f"Status Code: {response.status_code}")
        
        # Try to parse JSON response
        try:
            response_data = response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            print("✓ Estimate updated successfully!")
            return True
        else:
            print("✗ Failed to update estimate")
            return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def test_update_without_items(estimate_id):
    """Test updating estimate without modifying items"""
    print(f"\n=== Testing UPDATE Estimate Without Items (ID: {estimate_id}) ===")
    url = f"{BASE_URL}/estimates/{estimate_id}/edit/"
    
    data = {
        "client_name": "Client Without Item Changes",
        "workmanship": 700.00
    }
    
    try:
        response = requests.put(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✓ Estimate updated successfully without items!")
            return True
        else:
            print("✗ Failed to update estimate")
            return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def run_all_tests():
    """Run all tests in sequence"""
    print("=" * 50)
    print("ESTIMATE API TEST SUITE")
    print("=" * 50)
    
    # Test 1: Create a new estimate
    new_estimate_id = test_create_estimate()
    
    if new_estimate_id:
        # Test 2: Get the created estimate
        estimate_data = test_get_estimate(new_estimate_id)
        
        # Test 3: Update the estimate with items
        if estimate_data:
            # Update UPDATE_DATA with actual item IDs from created estimate
            if estimate_data.get('items'):
                UPDATE_DATA['items'][0]['id'] = estimate_data['items'][0]['id']
            test_update_estimate(new_estimate_id)
        
        # Test 4: Update without items
        test_update_without_items(new_estimate_id)
    else:
        print("\nSkipping update tests due to creation failure")
    
    # Test 5: Try updating an existing estimate (use your own ID)
    print("\n" + "=" * 50)
    print("Testing with existing estimate ID...")
    test_update_estimate(ESTIMATE_ID)
    
    print("\n" + "=" * 50)
    print("TEST SUITE COMPLETED")
    print("=" * 50)


if __name__ == "__main__":
    run_all_tests()