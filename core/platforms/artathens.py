import requests
from urllib.parse import urljoin

def update_m3u8(embed_id="v7clc2e", output_file='artathens.m3u8'):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": f"https://rumble.com/embed/{embed_id}/"
    }
    
    # Δοκιμάζουμε να πάρουμε το m3u8 μέσω ενός εναλλακτικού public endpoint του Rumble player
    api_urls = [
        f"https://rumble.com/embedJS/u3/?request=video&v={embed_id}",
        f"https://rumble.com/embed/{embed_id}/"
    ]
    
    hls_url = None
    
    for url in api_urls:
        try:
            print(f"[*] Trying to fetch from: {url}")
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                import re
                matches = re.findall(r'(https?://[^\s\'"]+\.m3u8[^\s\'"]*)', r.text)
                if matches:
                    hls_url = matches[0].replace('\\/', '/')
                    break
        except Exception as e:
            print(f"    [!] Attempt failed: {e}")

    # Αν εξακολουθεί να το μπλοκάρει, χρησιμοποιούμε το γνωστό δομικό pattern του Rumble CDN για το συγκεκριμένο ID
    if not hls_url:
        print("[*] Using direct CDN pattern fallback...")
        # Fallback master link pattern για τα live streams του Rumble
        hls_url = f"https://hugh.cdn.rumble.cloud/live/{embed_id}/index.m3u8"

    print(f"[✓] Using stream URL: {hls_url}")

    try:
        r_m3u = requests.get(hls_url, headers=headers, timeout=10)
        r_m3u.raise_for_status()
        content = r_m3u.text

        # Αν είναι Master Playlist, παίρνουμε το chunklist για να παίζει άμεσα
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
                    base_path = hls_url.rsplit("/", 1)[0]
                    sub_url = urljoin(base_path + "/", sub_url)
                
                print(f"[*] Fetching chunklist: {sub_url}")
                r_sub = requests.get(sub_url, headers=headers, timeout=10)
                r_sub.raise_for_status()
                content = r_sub.text
                base_path = sub_url.rsplit("/", 1)[0]
            else:
                base_path = hls_url.rsplit("/", 1)[0]
        else:
            base_path = hls_url.rsplit("/", 1)[0]

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

        print(f"[✔] Successfully updated {output_file}!")

    except Exception as e:
        print(f"[!] Error downloading m3u8 stream: {e}")

if __name__ == "__main__":
    update_m3u8(embed_id="v7clc2e")
