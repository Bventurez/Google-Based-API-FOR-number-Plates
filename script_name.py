import os
import io
import json
import base64
import requests


ENDPOINT_URL = "https://vision.googleapis.com/v1/images:annotate"

def detect_text_with_api_key(api_key, image_path):
    """Uses Google Vision API to detect text from an image using an API key."""
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()

    
    encoded_image = base64.b64encode(content).decode("utf-8")

  
    request_payload = {
        "requests": [
            {
                "image": {
                    "content": encoded_image  
                },
                "features": [
                    {
                        "type": "TEXT_DETECTION",
                        "maxResults": 1
                    }
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json"
    }

    
    response = requests.post(
        ENDPOINT_URL,
        params={"key": api_key},
        headers=headers,
        json=request_payload
    )

    if response.status_code == 200:
        result = response.json()
        text = result.get("responses", [{}])[0].get("textAnnotations", [])
        if text:
            print("Detected text:")
            for annotation in text:
                print(annotation.get("description"))
        else:
            print("No text detected.")
    else:
        print(f"Error: {response.status_code}, {response.text}")

if __name__ == "__main__":
   
    api_key = input("Enter your Google Cloud Vision API key: ").strip()
    
    if not api_key:
        print("API key is required.")
        exit(1)

    
    image_path = input("Enter the path to the image file: ").strip()

    if not os.path.exists(image_path):
        print(f"Image file not found: {image_path}")
        exit(1)

   
    detect_text_with_api_key(api_key, image_path)
