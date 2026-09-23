import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, quote

def update_m3u8(output_file='artathens.m3u8'):
    target_url = "https://www.arttv.info/p/art.html"
    # Χρησιμοποιούμε το allorigins proxy για να διαβάσουμε τη σελίδα χωρίς να μας μπλοκάρει
    proxy_url = f"https://api.allorigins.win/get?url={quote(target_url)}"

    print(f"[*] Fetching page via proxy: {target_url}")
    try:
        r = requests.get(proxy_url, timeout=15)
        r.raise_for_status()
        data = r.json()
        html_content = data.get("contents", "")
    except Exception as e:
        print(f"[!] Failed to fetch main page via proxy: {e}")
        return

    soup = BeautifulSoup(html_content, 'html.parser')
    
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
        match = re.search(r'rumble\.com/(?:embed/|live-hls/)v?([a-zA-Z0-9]+)', html_content)
        if match:
            embed_id = match.group(1)

    if not embed_id:
        print("[!] Could not find any active Rumble ID on the page.")
        return

    if embed_id.startswith('v') and embed_id[1:].isalnum():
        embed_id = embed_id[1:]

    print(f"[✓] Found active clean Rumble ID: {embed_id}")

    # Αφού βρήκαμε το ID, κατασκευάζουμε το m3u8 link
    hls_url = f"https://rumble.com/live-hls/{embed_id}/playlist.m3u8"
    print(f"[✓] Using stream URL: {hls_url}")

    # Για να κατεβάσουμε το m3u8 αρχείο, χρησιμοποιούμε έναν εναλλακτικό m3u8 proxy (thingproxy)
    proxied_hls = f"https://thingproxy.freeboard.io/fetch/{hls_url}"

    try:
        r_m3u = requests.get(proxied_hls, timeout=15)
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
                proxied_sub = f"https://thingproxy.freeboard.io/fetch/{sub_url}"
                r_sub = requests.get(proxied_sub, timeout=15)
                r_sub.raise_for_status()
                content = r_sub.text
                base_path = sub_url.rsplit("/", 1)[0]

        # Μετατροπή σχετικών paths σε từλυτα URLs
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
        print(f"[!] Error downloading m3u8 stream via proxy: {e}")

if __name__ == "__main__":
    update_m3u8()
