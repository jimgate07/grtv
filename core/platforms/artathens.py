import requests
from bs4 import BeautifulSoup
import re

def update_m3u8(output_file='artathens.m3u8'):
    main_url = "https://www.arttv.info/p/art.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    print(f"[*] Fetching main page: {main_url}")
    try:
        r = requests.get(main_url, headers=headers, timeout=10)
        r.raise_for_status()
        html_content = r.text
    except Exception as e:
        print(f"[!] Failed to fetch main page: {e}")
        return

    soup = BeautifulSoup(html_content, 'html.parser')
    
    embed_id = None
    
    # 1. Ψάχνουμε σε όλα τα iframes
    for iframe in soup.find_all("iframe"):
        src = iframe.get("src", "")
        print(f"[-] Checking iframe src: {src}")
        if "rumble.com" in src:
            match = re.search(r'(?:embed/|v=)v?([a-zA-Z0-9]+)', src)
            if match:
                embed_id = match.group(1)
                break

    # 2. Αν δεν βρέθηκε, ψάχνουμε παντού στο κείμενο της σελίδας για rumble links
    if not embed_id:
        matches = re.findall(r'rumble\.com/(?:embed/|live-hls/|v/)v?([a-zA-Z0-9]+)', html_content)
        if matches:
            embed_id = matches[0]

    # 3. Τελευταία προσπάθεια: αναζήτηση για οποιοδήποτε script/url που περιέχει rumble
    if not embed_id:
        match_alt = re.search(r'rumble\.com/.*?([a-zA-Z0-9]{5,8})', html_content)
        if match_alt:
            embed_id = match_alt.group(1)

    if not embed_id:
        print("[!] Warning: Could not detect any Rumble ID on the page! Keeping previous or fallback.")
        embed_id = "7clc2e" # Βάλε εδώ προσωρινά το νεο ID αν το ξέρεις χειροκίνητα

    if embed_id.startswith('v') and embed_id[1:].isalnum():
        embed_id = embed_id[1:]

    print(f"[✓] Final detected ID: {embed_id}")

    stream_url = f"https://rumble.com/live-hls/{embed_id}/playlist.m3u8"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(stream_url)

    print(f"[✔] Successfully updated {output_file} with: {stream_url}")

if __name__ == "__main__":
    update_m3u8()
