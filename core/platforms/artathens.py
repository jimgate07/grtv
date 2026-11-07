import requests
import re

def update_m3u8(output_file='artathens.m3u8'):
    # Χρήση του επίσημου JSON Feed του Blogspot (γρήγορο, χωρίς proxy και χωρίς 429 errors)
    feed_url = "https://www.arttv.info/feeds/posts/default?max-results=3&alt=json"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    print(f"[*] Fetching Blogspot JSON feed: {feed_url}")
    try:
        r = requests.get(feed_url, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[!] Failed to fetch feed: {e}")
        return

    embed_id = None
    
    # Ψάχνουμε στις τελευταίες αναρτήσεις του feed για το Rumble ID
    entries = data.get('feed', {}).get('entry', [])
    for entry in entries:
        content_html = entry.get('content', {}).get('$t', '')
        
        # Αναζήτηση για το iframe ή το embed link του Rumble μέσα στο περιεχόμενο της ανάρτησης
        match = re.search(r'rumble\.com/embed/v?([a-zA-Z0-9]+)', content_html)
        if match:
            embed_id = match.group(1)
            print(f"[+] Found Rumble ID in feed entry: {embed_id}")
            break

    if not embed_id:
        print("[!] Error: Could not detect any Rumble ID in the blog feed!")
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
