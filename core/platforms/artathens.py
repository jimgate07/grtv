import requests
import json
from urllib.parse import urljoin

def get_rumble_live_m3u8(embed_id="v7clc2e", output_file='artathens.m3u8'):
    # Το Rumble χρησιμοποιεί ένα JSON API για να φορτώσει τα δεδομένα του player στα embeds
    api_url = f"https://rumble.com/embedJS/u3/?request=video&v={embed_id}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": f"https://rumble.com/embed/{embed_id}/"
    }

    print(f"[*] Requesting Rumble API for video: {embed_id}")
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Εντοπισμός των διαθέσιμων ροών (HLS streams) στο JSON response
        # Το Rumble συνήθως αποθηκεύει τα links στο πεδίο 'ua' -> 'hls' ή 'live'
        plex_data = data.get("ua", {})
        hls_url = None
        
        # Ψάχνουμε σταδιακά για το hls link μέσα στο JSON
        if "hls" in plex_data:
            hls_data = plex_data["hls"]
            if isinstance(hls_data, dict):
                # Παίρνουμε το url από το dictionary (π.χ. αν έχει αναλύσεις)
                for key, val in hls_data.items():
                    if isinstance(val, dict) and "url" in val:
                        hls_url = val["url"]
                        break
                    elif isinstance(val, str) and val.endswith(".m3u8"):
                        hls_url = val
                        break
            elif isinstance(hls_data, str):
                hls_url = hls_data

        # Αν δεν το βρούμε εκεί, ψάχνουμε γενικά στα ορατά πεδία
        if not hls_url and "meta" in data and "icast" in data["meta"]:
            hls_url = data["meta"]["icast"]

        if not hls_url:
            # Δοκιμή εναλλακτικού σημείου στο JSON
            text_data = response.text
            import re
            m3u8_matches = re.findall(r'(https?://[^\s\'"]+\.m3u8[^\s\'"]*)', text_data)
            if m3u8_matches:
                hls_url = m3u8_matches[0]

        if not hls_url:
            print("[!] Could not extract HLS url from Rumble API JSON.")
            return

        print(f"[✓] Found Master/Stream URL: {hls_url}")

        # Κατεβάζουμε το m3u8 περιεχόμενο
        r_m3u = requests.get(hls_url, headers=headers, timeout=10)
        r_m3u.raise_for_status()
        content = r_m3u.text

        # Αν είναι Master Playlist, απομονώνουμε το chunklist για να παίζει απροβλημάτιστα
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

        # Αποθήκευση στο αρχείο
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(modified_lines))

        print(f"[✔] Successfully updated {output_file}!")

    except Exception as e:
        print(f"[!] Error fetching from Rumble API: {e}")

if __name__ == "__main__":
    # Το ID του βίντεο από το iframe σου (v7clc2e)
    get_rumble_live_m3u8(embed_id="v7clc2e")
