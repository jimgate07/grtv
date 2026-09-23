import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

def update_m3u8(output_file='artathens.m3u8'):
    main_url = "https://www.arttv.info/p/art.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://www.arttv.info/"
    }

    print(f"[*] Fetching main page: {main_url}")
    try:
        r = requests.get(main_url, headers=headers, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print(f"[!] Failed to fetch main page: {e}")
        return

    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Εντοπισμός του Rumble ID
    embed_id = None
    for iframe in soup.find_all("iframe"):
        src = iframe.get("src", "")
        if "rumble.com" in src:
            match = re.search(r'(?:embed/|v=)v?([a-zA-Z0-9]+)', src)
            if match:
                embed_id = match.group(1)
                break

    if not embed_id:
        match = re.search(r'rumble\.com/(?:embed/|live-hls/)v?([a-zA-Z0-9]+)', r.text)
        if match:
            embed_id = match.group(1)

    if not embed_id:
        print("[!] Could not find any active Rumble ID on the page.")
        return

    # Αφαίρεση τυχόν 'v' στην αρχή
    if embed_id.startswith('v') and embed_id[1:].isalnum():
        embed_id = embed_id[1:]

    print(f"[✓] Found active clean Rumble ID: {embed_id}")

    hls_url = f"https://rumble.com/live-hls/{embed_id}/playlist.m3u8"
    print(f"[✓] Using stream URL: {hls_url}")

    # Πλήρη headers browser για να παρακάμψουμε το 403 Forbidden
    player_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "el-GR,el;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://rumble.com",
        "Referer": f"https://rumble.com/embed/{embed_id}/",
        "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="8", "Google Chrome";v="122"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }

    try:
        r_m3u = requests.get(hls_url, headers=player_headers, timeout=10)
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
                r_sub = requests.get(sub_url, headers=player_headers, timeout=10)
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
