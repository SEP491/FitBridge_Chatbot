"""
FitBridge Chatbot Test Cases
Test various scenarios for gym search functionality
"""

import requests
import json
from typing import Dict, Any

# Base URL for your FastAPI server
BASE_URL = "http://localhost:8002"

class FitBridgeTestCase:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url

    def send_chat_request(self, prompt: str, longitude: float = None, latitude: float = None, conversation_history: list = None) -> Dict[str, Any]:
        """Send a chat request to the FitBridge API"""
        url = f"{self.base_url}/chat"

        payload = {
            "prompt": prompt,
            "longitude": longitude,
            "latitude": latitude,
            "conversation_history": conversation_history or []
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def print_test_result(self, test_name: str, request_data: dict, response: dict):
        """Print formatted test results"""
        print(f"\n{'='*60}")
        print(f"TEST: {test_name}")
        print(f"{'='*60}")
        print(f"REQUEST: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
        print(f"\nRESPONSE:")
        if "error" in response:
            print(f"❌ ERROR: {response['error']}")
        else:
            print(f"✅ SUCCESS")
            print(f"Response: {response.get('promptResponse', 'N/A')}")
            if response.get('gyms'):
                print(f"Found {len(response['gyms'])} gyms:")
                for i, gym in enumerate(response['gyms'][:3], 1):  # Show first 3 gyms
                    print(f"  {i}. {gym.get('gymName', 'Unknown')} - {gym.get('address', 'No address')}")
        print(f"{'='*60}")

def run_test_cases():
    """Run comprehensive test cases for FitBridge chatbot"""

    test_client = FitBridgeTestCase()

    # Test Case 1: General Gym Search
    print("🏋️ Running FitBridge Chatbot Test Cases...")

    # Test 1: Simple gym search
    test_data = {
        "prompt": "Tìm gym gần đây",
        "longitude": None,
        "latitude": None,
        "conversation_history": []
    }
    response = test_client.send_chat_request(**test_data)
    test_client.print_test_result("Simple Gym Search", test_data, response)

    # Test 2: Location-based search with coordinates
    test_data = {
        "prompt": "Tìm gym gần tôi",
        "longitude": 106.6297,  # Ho Chi Minh City coordinates
        "latitude": 10.8231,
        "conversation_history": []
    }
    response = test_client.send_chat_request(**test_data)
    test_client.print_test_result("Location-based Search with Coordinates", test_data, response)

    # Test 3: Search for hot/popular gyms
    test_data = {
        "prompt": "Gym nào hot nhất?",
        "longitude": None,
        "latitude": None,
        "conversation_history": []
    }
    response = test_client.send_chat_request(**test_data)
    test_client.print_test_result("Hot/Popular Gym Search", test_data, response)

    # Test 4: Search with specific location name
    test_data = {
        "prompt": "Tìm gym ở Quận 1",
        "longitude": None,
        "latitude": None,
        "conversation_history": []
    }
    response = test_client.send_chat_request(**test_data)
    test_client.print_test_result("Search by District Name", test_data, response)

    # Test 5: Search with distance preference
    test_data = {
        "prompt": "Gym gần đây trong bán kính 5km",
        "longitude": 106.6297,
        "latitude": 10.8231,
        "conversation_history": []
    }
    response = test_client.send_chat_request(**test_data)
    test_client.print_test_result("Distance-based Search (5km)", test_data, response)

    # Test 6: Conversational context - follow up question
    conversation_history = [
        {
            "role": "user",
            "content": "Tìm gym gần đây",
            "timestamp": "2024-01-15T10:00:00"
        },
        {
            "role": "assistant",
            "content": "🏋️ **Tìm thấy 3 phòng gym:** 1. **FitZone Gym** 2. **PowerHouse Fitness** 3. **Elite Gym**",
            "timestamp": "2024-01-15T10:00:01"
        }
    ]

    test_data = {
        "prompt": "Gym nào có thiết bị tốt nhất?",
        "longitude": None,
        "latitude": None,
        "conversation_history": conversation_history
    }
    response = test_client.send_chat_request(**test_data)
    test_client.print_test_result("Conversational Follow-up", test_data, response)

    # Test 7: Non-gym related question (should use Gemini AI)
    test_data = {
        "prompt": "Làm sao để tăng cân?",
        "longitude": None,
        "latitude": None,
        "conversation_history": []
    }
    response = test_client.send_chat_request(**test_data)
    test_client.print_test_result("General Fitness Advice (Non-gym)", test_data, response)

    # Test 8: Greeting (should use Gemini AI)
    test_data = {
        "prompt": "Xin chào!",
        "longitude": None,
        "latitude": None,
        "conversation_history": []
    }
    response = test_client.send_chat_request(**test_data)
    test_client.print_test_result("Greeting Message", test_data, response)

    # Test 9: List all gyms
    test_data = {
        "prompt": "Danh sách tất cả gym",
        "longitude": None,
        "latitude": None,
        "conversation_history": []
    }
    response = test_client.send_chat_request(**test_data)
    test_client.print_test_result("List All Gyms", test_data, response)

    # Test 10: Specific gym name search
    test_data = {
        "prompt": "Tìm California Fitness",
        "longitude": None,
        "latitude": None,
        "conversation_history": []
    }
    response = test_client.send_chat_request(**test_data)
    test_client.print_test_result("Specific Gym Name Search", test_data, response)

    # Test 11: Walking distance search
    test_data = {
        "prompt": "Gym đi bộ được từ đây",
        "longitude": 106.6297,
        "latitude": 10.8231,
        "conversation_history": []
    }
    response = test_client.send_chat_request(**test_data)
    test_client.print_test_result("Walking Distance Search", test_data, response)

    # Test 12: Budget-friendly gym search
    test_data = {
        "prompt": "Gym rẻ gần đây",
        "longitude": None,
        "latitude": None,
        "conversation_history": []
    }
    response = test_client.send_chat_request(**test_data)
    test_client.print_test_result("Budget-friendly Gym Search", test_data, response)

def run_single_test(prompt: str, longitude: float = None, latitude: float = None):
    """Run a single test case quickly"""
    test_client = FitBridgeTestCase()

    test_data = {
        "prompt": prompt,
        "longitude": longitude,
        "latitude": latitude,
        "conversation_history": []
    }

    response = test_client.send_chat_request(**test_data)
    test_client.print_test_result("Single Test", test_data, response)

    return response

if __name__ == "__main__":
    print("🚀 Starting FitBridge Chatbot Tests...")
    print("Make sure your FastAPI server is running on http://localhost:8002")
    print("Press Enter to continue or Ctrl+C to cancel...")

    try:
        input()
        run_test_cases()
        print("\n✅ All test cases completed!")

        # Interactive test mode
        print("\n🔧 Interactive Test Mode")
        print("Type your questions (or 'quit' to exit):")

        while True:
            user_input = input("\nYour question: ")
            if user_input.lower() in ['quit', 'exit', 'q']:
                break

            # Ask for coordinates if needed
            coords_input = input("Add coordinates? (lat,lng or press Enter to skip): ")
            longitude, latitude = None, None

            if coords_input.strip():
                try:
                    parts = coords_input.split(',')
                    if len(parts) == 2:
                        latitude = float(parts[0].strip())
                        longitude = float(parts[1].strip())
                except ValueError:
                    print("Invalid coordinates format. Skipping coordinates.")

            run_single_test(user_input, longitude, latitude)

    except KeyboardInterrupt:
        print("\n\n👋 Test cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
