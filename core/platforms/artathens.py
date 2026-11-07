import requests
import re

def update_m3u8(output_file='artathens.m3u8'):
    target_url = "https://www.arttv.info/p/art.html"
    main_url = f"https://r.jina.ai/{target_url}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,xml"
    }

    print(f"[*] Fetching via Jina proxy: {target_url}")
    try:
        r = requests.get(main_url, headers=headers, timeout=15)
        r.raise_for_status()
        page_content = r.text
    except Exception as e:
        print(f"[!] Failed to fetch main page: {e}")
        return

    embed_id = None
    
    # 1. Αναζήτηση για rumble.com/embed/ εντός JavaScript strings ή HTML
    # Πιάνει περιπτώσεις όπως: src=\"https://rumble.com/embed/v7fteuo/...\" ή απλό URL
    match = re.search(r'rumble\.com/embed/v?([a-zA-Z0-9]+)', page_content)
    if match:
        embed_id = match.group(1)
        print(f"[+] Found Rumble ID via embed pattern: {embed_id}")

    # 2. Γενική αναζήτηση για IDs μέσα σε JavaScript variables ή URLs του Rumble
    if not embed_id:
        # Ψάχνει για patterns τυπου rumble.com/... και παίρνει το αλριθμητικό ID
        matches = re.findall(r'rumble\.com/(?:embed/|live-hls/|v/)?v?([a-zA-Z0-9]{5,8})', page_content)
        if matches:
            valid_ids = [m for m in matches if m not in ['embed', 'live', 'hls', 'pub']]
            if valid_ids:
                embed_id = valid_ids[0]
                print(f"[+] Found ID via general pattern: {embed_id}")

    if not embed_id:
        print("[!] Error: Could not detect any Rumble ID on the page!")
        return

    # Καθαρισμός αν τυχόν ξεκινάει από 'v'
    if embed_id.startswith('v') and embed_id[1:].isalnum():
        embed_id = embed_id[1:]

    print(f"[✓] Final detected ID: {embed_id}")

    stream_url = f"https://rumble.com/live-hls/{embed_id}/playlist.m3u8"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(stream_url)

    print(f"[✔] Successfully updated {output_file} with: {stream_url}")

if __name__ == "__main__":
    update_m3u8()
