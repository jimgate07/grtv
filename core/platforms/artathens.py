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
    
    # Ψάχνουμε για διάφορα μοτίβα του Rumble στο κείμενο (π.χ. embed/, v/, live-hls/)
    patterns = [
        r'rumble\.com/embed/([a-zA-Z0-9]+)',
        r'rumble\.com/v/([a-zA-Z0-9]+)',
        r'rumble\.com/live-hls/([a-zA-Z0-9]+)',
        r'rumble\.com/.*?/([a-zA-Z0-9]{5,8})'
    ]

    for pattern in patterns:
        matches = re.findall(pattern, page_content)
        if matches:
            # Φιλτράρουμε τυχόν άσχετα matches (κρατάμε αλριθμητικά IDs συνήθως 5-8 χαρακτήρων)
            valid_ids = [m for m in matches if len(m) >= 4]
            if valid_ids:
                embed_id = valid_ids[0]
                print(f"[+] Found match with pattern '{pattern}': {embed_id}")
                break

    if not embed_id:
        print("[!] Warning: Could not detect any Rumble ID on the page! Keeping fallback.")
        embed_id = "7clc2e" # Fallback ID

    if embed_id.startswith('v') and embed_id[1:].isalnum():
        embed_id = embed_id[1:]

    print(f"[✓] Final detected ID: {embed_id}")

    stream_url = f"https://rumble.com/live-hls/{embed_id}/playlist.m3u8"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(stream_url)

    print(f"[✔] Successfully updated {output_file} with: {stream_url}")

if __name__ == "__main__":
    update_m3u8()
