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
        r = requests.get(main_url, headers=headers, timeout=20)
        r.raise_for_status()
        page_content = r.text
    except Exception as e:
        print(f"[!] Failed to fetch page: {e}")
        return

    embed_id = None
    
    # Αναζήτηση για οποιοδήποτε pattern rumble.com/embed/ ή παρόμοιο στο κείμενο του Jina
    match = re.search(r'rumble\.com/(?:embed|v|live-hls)/v?([a-zA-Z0-9]+)', page_content)
    if match:
        embed_id = match.group(1)
        print(f"[+] Found Rumble ID: {embed_id}")

    # Αν δεν το βρει έτσι, ψάχνουμε για οποιοδήποτε string ακολουθεί το rumble.com/
    if not embed_id:
        matches = re.findall(r'rumble\.com/[^\s"\'<>)]+', page_content)
        for m in matches:
            sub_match = re.search(r'([a-zA-Z0-9]{5,8})', m)
            if sub_match and sub_match.group(1) not in ['embed', 'live', 'hls', 'html']:
                embed_id = sub_match.group(1)
                print(f"[+] Found ID via generic link scan: {embed_id}")
                break

    if not embed_id:
        print("[!] Error: Could not detect any Rumble ID on the page!")
        return

    # Καθαρισμός: αν ξεκινάει από 'v' (π.χ. v7fteuo), το αφαιρούμε για να μείνει το καθαρό 7fteuo
    if embed_id.lower().startswith('v') and embed_id[1:].isalnum():
        embed_id = embed_id[1:]

    print(f"[✓] Final detected ID: {embed_id}")

    stream_url = f"https://rumble.com/live-hls/{embed_id}/playlist.m3u8"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(stream_url)

    print(f"[✔] Successfully updated {output_file} with: {stream_url}")

if __name__ == "__main__":
    update_m3u8()
