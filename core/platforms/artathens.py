import requests
from bs4 import BeautifulSoup
import re

def update_m3u8(output_file='artathens.m3u8'):
    target_url = "https://www.arttv.info/p/art.html"
    
    # Χρησιμοποιούμε πλήρη headers κανονικού browser για να μην τρώμε 429 / bot block
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "el-GR,el;q=0.9,en;q=0.8",
        "Referer": "https://www.arttv.info/"
    }

    print(f"[*] Fetching directly: {target_url}")
    try:
        r = requests.get(target_url, headers=headers, timeout=15)
        r.raise_for_status()
        html_content = r.text
    except Exception as e:
        print(f"[!] Failed to fetch main page directly: {e}")
        return

    embed_id = None
    
    # 1. Αναζήτηση με BeautifulSoup μέσα στα iframes (αφού έχουμε πλέον καθαρό HTML)
    soup = BeautifulSoup(html_content, 'html.parser')
    for iframe in soup.find_all("iframe"):
        src = iframe.get("src", "")
        print(f"[-] Checking iframe src: {src}")
        if "rumble.com" in src:
            match = re.search(r'embed/v?([a-zA-Z0-9]+)', src)
            if match:
                embed_id = match.group(1)
                print(f"[+] Found ID via iframe src: {embed_id}")
                break

    # 2. Εναλλακτικό: Αναζήτηση με Regex απευθείας στο HTML αν δεν βρεθεί στα iframes
    if not embed_id:
        match = re.search(r'rumble\.com/embed/v?([a-zA-Z0-9]+)', html_content)
        if match:
            embed_id = match.group(1)
            print(f"[+] Found ID via regex in HTML: {embed_id}")

    if not embed_id:
        print("[!] Error: Could not detect any Rumble ID on the page!")
        return

    # Καθαρισμός: αν ξεκινάει από 'v' (π.χ. v7fteuo), το αφαιρούμε για να μείνει το καθαρό 7fteuo
    if embed_id.startswith('v') and embed_id[1:].isalnum():
        embed_id = embed_id[1:]

    print(f"[✓] Final detected ID: {embed_id}")

    stream_url = f"https://rumble.com/live-hls/{embed_id}/playlist.m3u8"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(stream_url)

    print(f"[✔] Successfully updated {output_file} with: {stream_url}")

if __name__ == "__main__":
    update_m3u8()
