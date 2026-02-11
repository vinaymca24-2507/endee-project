import requests
import time

API_URL = "http://127.0.0.1:8000"

def test_index():
    print("Testing /index...")
    # Index the sample repo
    response = requests.post(f"{API_URL}/index", json={"repo_path": "./requests-demo"})
    print(response.json())
    
def test_search():
    print("\nTesting /search...")
    # Search for "database"
    response = requests.post(f"{API_URL}/search", json={"query": "database", "limit": 2})
    print(response.json())

def test_explain():
    print("\nTesting /explain...")
    # Ask what the project does
    response = requests.post(f"{API_URL}/explain", json={"question": "What does the Indexer class do?"})
    print(response.json())

if __name__ == "__main__":
    try:
        test_index()
        print("Waiting 5 seconds for indexing (mocked)...")
        time.sleep(5) 
        test_search()
        test_explain() # Testing explain to see if it causes 500
    except Exception as e:
        print(f"Error: {e}")
