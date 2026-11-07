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
        print(f"[DEBUG] Total content length received: {len(page_content)} characters")
    except Exception as e:
        print(f"[!] Failed to fetch via Jina proxy: {e}")
        return

    embed_id = None
    
    # 1. Βρίσκουμε ΟΠΟΙΟΔΗΠΟΤΕ URL περιέχει το rumble.com στο κείμενο
    matches = re.findall(r'rumble\.com/[^\s"\'<>)]+', page_content, re.IGNORECASE)
    print(f"[DEBUG] Found rumble links: {matches}")

    for link in matches:
        # Εξάγουμε το ID από οποιοδήποτε μοτίβο (embed/, v/, live-hls/)
        id_match = re.search(r'(?:embed|v|live-hls)/v?([a-zA-Z0-9]+)', link, re.IGNORECASE)
        if id_match:
            candidate = id_match.group(1)
            if candidate.lower() not in ['embed', 'live', 'hls', 'playlist', 'pub']:
                embed_id = candidate
                print(f"[+] Successfully extracted ID from link '{link}': {embed_id}")
                break

    # 2. Fallback: Γενική αναζήτηση με regex στο κείμενο αν δεν βρέθηκε από τα links
    if not embed_id:
        fallback_match = re.search(r'rumble\.com/(?:embed|v|live-hls)/v?([a-zA-Z0-9]+)', page_content, re.IGNORECASE)
        if fallback_match:
            embed_id = fallback_match.group(1)
            print(f"[+] Found ID via fallback regex: {embed_id}")

    if not embed_id:
        print("[!] Error: Could not detect any Rumble ID on the page! Dumping first 1000 chars for debugging:")
        print("--------------------------------------------------")
        print(page_content[:1000])
        print("--------------------------------------------------")
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
