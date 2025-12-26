import urllib.request
import sys

def check_url(url):
    print(f"Checking {url}...")
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            print(f"Status: {response.status}")
            print(f"MIME Type: {response.getheader('Content-Type')}")
            content = response.read(200).decode('utf-8')
            print(f"Start of content:\n{content}")
            print("-" * 20)
    except Exception as e:
        print(f"Error checking {url}: {e}")

urls = [
    "http://127.0.0.1:5185/",
    "http://127.0.0.1:5185/src/main.jsx",
    "http://127.0.0.1:5185/@vite/client"
]

for url in urls:
    check_url(url)
