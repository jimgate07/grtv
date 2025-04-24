import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

def find_all_m3u8_urls(page_url, depth=0, max_depth=3, visited=None):
    if visited is None:
        visited = set()
    if page_url in visited or depth > max_depth:
        return []
    visited.add(page_url)

    print(f"[{depth}] Scanning: {page_url}")
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(page_url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"   [!] Failed to fetch: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    found = set()

    # Look for m3u8 URLs in scripts (normal and escaped)
    for script in soup.find_all("script"):
        script_content = script.string or script.get_text()

        # Normal .m3u8 URLs
        matches = re.findall(r'(https?://[^\s\'"]+\.m3u8)', script_content)
        found.update(matches)

        # Escaped .m3u8 URLs like https:\/\/rumble.com\/...\.m3u8
        escaped_matches = re.findall(r'https:\\/\\/[^\s\'"]+?\.m3u8', script_content)
        for em in escaped_matches:
            unescaped = em.replace('\\/', '/')
            found.add(unescaped)

    # Look for m3u8 URLs in <video><source>
    for video in soup.find_all("video"):
        for source in video.find_all("source"):
            src = source.get("src")
            if src and ".m3u8" in src:
                found.add(urljoin(page_url, src))

    # Look for direct links to .m3u8 files
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if ".m3u8" in href:
            found.add(urljoin(page_url, href))

    # Recursively scan iframes
    for iframe in soup.find_all("iframe"):
        iframe_src = iframe.get("src")
        if iframe_src:
            iframe_url = urljoin(page_url, iframe_src)
            found.update(find_all_m3u8_urls(iframe_url, depth + 1, max_depth, visited))

    return list(found)

def save_m3u8_content(m3u8_url, output_file='artathens.m3u8'):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(m3u8_url, headers=headers)
        r.raise_for_status()
        lines = r.text.splitlines()

        parsed_url = urlparse(m3u8_url)
        base_path = m3u8_url.rsplit("/", 1)[0]

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

        with open(output_file, 'w') as f:
            f.write("\n".join(modified_lines))

        print(f"[✔] Patched .m3u8 saved to: {output_file}")
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

        # Save the first one
        save_m3u8_content(m3u8_urls[0])
    else:
        print("\n[x] No .m3u8 URLs found.")
