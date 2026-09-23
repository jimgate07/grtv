import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import json

def find_all_m3u8_urls(page_url, depth=0, max_depth=3, visited=None):
    if visited is None:
        visited = set()
    if page_url in visited or depth > max_depth:
        return []
    visited.add(page_url)

    print(f"[{depth}] Scanning: {page_url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.arttv.info/"
    }

    try:
        response = requests.get(page_url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"    [!] Failed to fetch: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    found = set()

    script_texts = []
    # Look for m3u8 URLs in scripts
    for script in soup.find_all("script"):
        content = script.string or script.get_text()
        if content:
            script_texts.append(content)
            # Normal .m3u8 URLs
            matches = re.findall(r'(https?://[^\s\'"]+\.m3u8)', content)
            found.update(matches)

            # Escaped .m3u8 URLs
            escaped_matches = re.findall(r'https:\\/\\/[^\s\'"]+?\.m3u8', content)
            for em in escaped_matches:
                found.add(em.replace('\\/', '/'))

            # Rumble specific JSON parsing if present
            if "rumble.com" in page_url or "embed" in page_url:
                json_matches = re.findall(r'["\'](https?://[^"\']+\.m3u8[^"\']*)["\']', content)
                for jm in json_matches:
                    found.add(jm.replace('\\/', '/'))

    # Look for m3u8 in video tags
    for video in soup.find_all("video"):
        for source in video.find_all("source"):
            src = source.get("src")
            if src and ".m3u8" in src:
                found.add(urljoin(page_url, src))

    # Look for direct links
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if ".m3u8" in href:
            found.add(urljoin(page_url, href))

    # Recursively scan iframes (π.χ. Rumble embed)
    for iframe in soup.find_all("iframe"):
        iframe_src = iframe.get("src")
        if iframe_src:
            iframe_url = urljoin(page_url, iframe_src)
            found.update(find_all_m3u8_urls(iframe_url, depth + 1, max_depth, visited))

    return list(found)

def save_m3u8_content(m3u8_url, output_file='artathens.m3u8'):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://rumble.com/"
    }
    try:
        r = requests.get(m3u8_url, headers=headers, timeout=10)
        r.raise_for_status()
        content = r.text

        # Αν είναι Master Playlist, βρίσκουμε αυτόματα το ενεργό chunklist
        if "#EXT-X-STREAM-INF" in content:
            print("[*] Master playlist detected. Resolving chunklist...")
            lines = content.splitlines()
            sub_playlist_url = None
            
            for i, line in enumerate(lines):
                if "#EXT-X-STREAM-INF" in line:
                    if i + 1 < len(lines):
                        sub_playlist_url = lines[i + 1].strip()
                        break
            
            if sub_playlist_url:
                if not sub_playlist_url.startswith("http"):
                    base_path = m3u8_url.rsplit("/", 1)[0]
                    sub_playlist_url = urljoin(base_path + "/", sub_playlist_url)
                
                print(f"[*] Fetching sub-playlist: {sub_playlist_url}")
                r = requests.get(sub_playlist_url, headers=headers, timeout=10)
                r.raise_for_status()
                content = r.text
                base_path = sub_playlist_url.rsplit("/", 1)[0]
            else:
                base_path = m3u8_url.rsplit("/", 1)[0]
        else:
            base_path = m3u8_url.rsplit("/", 1)[0]

        # Μετατροπή των σχετικών συνδέσμων σε απόλυτα URLs
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

        print(f"[✔] Working chunklist .m3u8 saved to: {output_file}")
    except Exception as e:
        print(f"[!] Error saving .m3u8: {e}")

if __name__ == "__main__":
    start_url = "https://www.arttv.info/p/art.html"
    print(f"[*] Starting scan at: {start_url}")
    m3u8_urls = find_all_m3u8_urls(start_url)

    if m3u8_urls:
        print(f"\n[✓] Found {len(m3u8_urls)} m3u8 URL(s):")
        for i, url in enumerate(m3u8_urls, 1):
            print(f"  {i}. {url}")
        save_m3u8_content(m3u8_urls[0])
    else:
        print("\n[x] No .m3u8 URLs found.")
