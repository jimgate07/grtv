import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

def get_live_m3u8(output_file='artathens.m3u8'):
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
    
    # 1. Ψάχνουμε για iframe του Rumble στη σελίδα
    embed_id = None
    for iframe in soup.find_all("iframe"):
        src = iframe.get("src", "")
        if "rumble.com/embed/" in src:
            # Εξάγουμε το ID (π.χ. από το /embed/v7clc2e/)
            match = re.search(r'embed/([a-zA-Z0-9]+)', src)
            if match:
                embed_id = match.group(1)
                break

    # Αν δεν βρεθεί σε iframe, ψάχνουμε παντού στον κώδικα για rumble embed links
    if not embed_id:
        match = re.search(r'rumble\.com/embed/([a-zA-Z0-9]+)', r.text)
        if match:
            embed_id = match.group(1)

    if not embed_id:
        print("[!] Could not find any active Rumble embed ID on the page.")
        return

    print(f"[✓] Found active Rumble embed ID: {embed_id}")

    # 2. Τώρα χτυπάμε το embedJS API χρησιμοποιώντας το δυναμικό ID που μόλις βρήκαμε
    api_url = f"https://rumble.com/embedJS/u3/?request=video&v={embed_id}"
    api_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": f"https://rumble.com/embed/{embed_id}/"
    }

    hls_url = None
    try:
        print(f"[*] Requesting Rumble API for video: {embed_id}")
        r_api = requests.get(api_url, headers=api_headers, timeout=10)
        if r_api.status_code == 200:
            import json
            data = r_api.json()
            # Αναζήτηση του hls link στο JSON
            plex_data = data.get("ua", {})
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
                m3u8_matches = re.findall(r'(https?://[^\s\'"]+\.m3u8[^\s\'"]*)', r_api.text)
                if m3u8_matches:
                    hls_url = m3u8_matches[0]
    except Exception as e:
        print(f"[!] API request failed: {e}")

    # Fallback αν το API αποτύχει
    if not hls_url:
        hls_url = f"https://hugh.cdn.rumble.cloud/live/{embed_id}/index.m3u8"

    print(f"[✓] Using stream URL: {hls_url}")

    # 3. Κατέβαστη και επεξεργασία του m3u8 αρχείου
    try:
        r_m3u = requests.get(hls_url, headers=api_headers, timeout=10)
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
                r_sub = requests.get(sub_url, headers=api_headers, timeout=10)
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

        print(f"[✔] Successfully updated {output_file} with ID {embed_id}!")

    except Exception as e:
        print(f"[!] Error downloading m3u8 stream: {e}")

if __name__ == "__main__":
    get_live_m3u8()
