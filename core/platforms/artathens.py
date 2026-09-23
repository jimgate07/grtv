import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

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
    
    # Εντοπισμός του Rumble ID από τη σελίδα
    embed_id = None
    for iframe in soup.find_all("iframe"):
        src = iframe.get("src", "")
        if "rumble.com" in src:
            match = re.search(r'(?:embed/|v=)v?([a-zA-Z0-9]+)', src)
            if match:
                embed_id = match.group(1)
                break

    if not embed_id:
        match = re.search(r'rumble\.com/(?:embed/|live-hls/)v?([a-zA-Z0-9]+)', html_content)
        if match:
            embed_id = match.group(1)

    # Fallback αν δεν το βρει δυναμικά, βάζουμε το τελευταίο γνωστό ενεργό ID για να μη σταματάει ποτέ
    if not embed_id:
        embed_id = "7clc2e"
        print("[!] Using fallback Rumble ID.")

    if embed_id.startswith('v') and embed_id[1:].isalnum():
        embed_id = embed_id[1:]

    print(f"[✓] Using clean Rumble ID: {embed_id}")

    # Δοκιμάζουμε το live-hls URL με headers που μιμούνται browser
    hls_url = f"https://rumble.com/live-hls/{embed_id}/playlist.m3u8"
    print(f"[✓] Using stream URL: {hls_url}")

    stream_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Origin": "https://rumble.com",
        "Referer": f"https://rumble.com/embed/{embed_id}/"
    }

    try:
        r_m3u = requests.get(hls_url, headers=stream_headers, timeout=15)
        r_m3u.raise_for_status()
        content = r_m3u.text
        base_path = hls_url.rsplit("/", 1)[0]

        # Αν είναι Master Playlist, διαβάζουμε το chunklist εσωτερικά
        if "#EXT-X-STREAM-INF" in content:
            print("[*] Master playlist detected. Resolving chunklist...")
            lines = content.splitlines()
            sub_url = None
            for i, line in enumerate(lines):
                if "#EXT-X-STREAM-INF" in line and i + 1 < len(lines):
                    sub_url = lines[i + 1].strip()
                    break
            
            if sub_url:
                if not sub_url.startswith("http"):
                    sub_url = urljoin(base_path + "/", sub_url)
                
                print(f"[*] Fetching chunklist: {sub_url}")
                r_sub = requests.get(sub_url, headers=stream_headers, timeout=15)
                r_sub.raise_for_status()
                content = r_sub.text
                base_path = sub_url.rsplit("/", 1)[0]

        # Μετατροπή σχετικών paths σε απόλυτα URLs
        lines = content.splitlines()
        modified_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                if not line.startswith("http"):
                    full_url = urljoin(base_path + "/", line)
                    modified_lines.append(full_url)
                else:
                    modified_lines.append(line)
            else:
                modified_lines.append(line)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(modified_lines))

        print(f"[✔] Successfully updated {output_file} using ID: {embed_id}!")

    except Exception as e:
        print(f"[!] Error downloading m3u8 stream: {e}")

if __name__ == "__main__":
    update_m3u8()
