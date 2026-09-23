import requests
import json
from urllib.parse import urljoin, quote

def get_rumble_live_m3u8(embed_id="v7clc2e", output_file='artathens.m3u8'):
    target_url = f"https://rumble.com/embedJS/u3/?request=video&v={embed_id}"
    
    # Χρησιμοποιούμε έναν ελεύθερο proxy για να παρακάμψουμε το IP block του GitHub
    proxy_url = f"https://api.allorigins.win/get?url={quote(target_url)}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    print(f"[*] Requesting via proxy for video: {embed_id}")
    try:
        response = requests.get(proxy_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        data_json = response.json()
        raw_html_or_json = data_json.get("contents", "")
        
        data = json.loads(raw_html_or_json)
        
        plex_data = data.get("ua", {})
        hls_url = None
        
        if "hls" in plex_data:
            hls_data = plex_data["hls"]
            if isinstance(hls_data, dict):
                for key, val in hls_data.items():
                    if isinstance(val, dict) and "url" in val:
                        hls_url = val["url"]
                        break
                    elif isinstance(val, str) and val.endswith(".m3u8"):
                        hls_url = val
                        break
            elif isinstance(hls_data, str):
                hls_url = hls_data

        if not hls_url:
            import re
            m3u8_matches = re.findall(r'(https?://[^\s\'"]+\.m3u8[^\s\'"]*)', raw_html_or_json)
            if m3u8_matches:
                hls_url = m3u8_matches[0]

        if not hls_url:
            print("[!] Could not extract HLS url.")
            return

        print(f"[✓] Found Master/Stream URL: {hls_url}")

        # Κατεβάζουμε το m3u8 (δοκιμάζουμε απευθείας ή μέσω proxy αν χρειαστεί)
        r_m3u = requests.get(hls_url, headers=headers, timeout=10)
        r_m3u.raise_for_status()
        content = r_m3u.text

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
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    get_rumble_live_m3u8(embed_id="v7clc2e")
