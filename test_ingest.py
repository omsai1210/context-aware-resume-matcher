import requests
import json
import os

API_URL = "http://127.0.0.1:8000/api/v1/ingest"

def test_ingest_file(file_path: str):
    """
    Sends a file to the ingest API and prints the response.
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return

    print(f"\n--- Testing file: {os.path.basename(file_path)} ---")
    
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
        try:
            response = requests.post(API_URL, files=files)
            
            print(f"Status Code: {response.status_code}")
            try:
                # Try parsing JSON response
                json_resp = response.json()
                print("Response JSON:")
                print(json.dumps(json_resp, indent=2))
            except ValueError:
                # Fallback purely for safety
                print("Raw Response:", response.text)
                
        except requests.exceptions.ConnectionError:
            print("Error: Could not connect to the API. Is the server running?")

if __name__ == "__main__":
    # Create some dummy files for testing if they don't exist
    os.makedirs("test_files", exist_ok=True)
    
    txt_path = "test_files/sample_resume.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("""
John Doe
Software Engineer
Email: john.doe@example.com
Phone: (555) 123-4567
Location: San Francisco, CA
https://linkedin.com/in/johndoe
        
I am a senior developer with 10 years of experience.
""")
        
    print("Testing the `/ingest` endpoint.")
    print("Make sure your FastAPI server is running (uvicorn main:app --reload)")
    
    test_ingest_file(txt_path)
