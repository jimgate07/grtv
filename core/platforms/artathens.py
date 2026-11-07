import requests
from bs4 import BeautifulSoup
import re

def update_m3u8(output_file='artathens.m3u8'):
    target_url = "https://www.arttv.info/p/art.html"
    # Χρήση του AllOrigins proxy για να πάρουμε το raw HTML με όλα τα iframes
    proxy_url = f"https://api.allorigins.win/raw?url={target_url}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    print(f"[*] Fetching via AllOrigins proxy: {target_url}")
    try:
        r = requests.get(proxy_url, headers=headers, timeout=15)
        r.raise_for_status()
        html_content = r.text
        print(f"[DEBUG] HTML content length: {len(html_content)} characters")
    except Exception as e:
        print(f"[!] Failed to fetch page: {e}")
        return

    embed_id = None
    
    # 1. Αναζήτηση στα iframes της σελίδας
    soup = BeautifulSoup(html_content, 'html.parser')
    for iframe in soup.find_all("iframe"):
        src = iframe.get("src", "")
        print(f"[-] Found iframe src: {src}")
        if "rumble.com" in src:
            match = re.search(r'embed/v?([a-zA-Z0-9]+)', src)
            if match:
                embed_id = match.group(1)
                print(f"[+] Found ID via iframe: {embed_id}")
                break

    # 2. Εναλλακτικό: Regex απευθείας στο raw HTML
    if not embed_id:
        match = re.search(r'rumble\.com/embed/v?([a-zA-Z0-9]+)', html_content)
        if match:
            embed_id = match.group(1)
            print(f"[+] Found ID via regex: {embed_id}")

    if not embed_id:
        print("[!] Error: Could not detect any Rumble ID on the page!")
        return

    # Καθαρισμός: αν ξεκινάει από 'v' (π.χ. v7fteuo), το αφαιρούμε για να μείνει το καθαρό ID
    if embed_id.startswith('v') and embed_id[1:].isalnum():
        embed_id = embed_id[1:]

    print(f"[✓] Final detected ID: {embed_id}")

    stream_url = f"https://rumble.com/live-hls/{embed_id}/playlist.m3u8"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(stream_url)

    print(f"[✔] Successfully updated {output_file} with: {stream_url}")

if __name__ == "__main__":
    update_m3u8()
