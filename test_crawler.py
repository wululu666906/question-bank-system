import requests
import json

def test_jina_search():
    query = "老师 明朝是如何灭亡的 最新案例"
    url = f"https://s.jina.ai/{query}"
    
    headers = {
        "Accept": "text/plain",
        "X-Return-Format": "markdown"
    }
    
    try:
        print(f"Requesting URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            print("Content Preview:")
            print(content[:500])
        else:
            print(f"Error Content: {response.text}")
            
    except Exception as e:
        print(f"Network Error: {e}")

if __name__ == "__main__":
    test_jina_search()
