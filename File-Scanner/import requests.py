import requests
import json

api_key="AIzaSyD1cqy7So8NCXwVfpHtCdcn6X3MLURpekU"

def Ai_scan(prompt,api_key):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=GEMINI_API_KEY"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
    }
    # Replace GEMINI_API_KEY with your actual API key
    url = url.replace("GEMINI_API_KEY", api_key)
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text}
    
def extract_gemini_response(response):
    try:
        return response['candidates'][0]['content']['parts'][0]['text']
    except (KeyError, IndexError, TypeError):
        return "No response found"
    
