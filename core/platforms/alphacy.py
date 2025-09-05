import requests
import re
from urllib.parse import urljoin

def fetch_m3u8_from_site(url):
    """
    Fetches the webpage and tries to extract the first .m3u8 link.
    Handles query strings (?...) and protocol-relative URLs (//...).
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html = response.text

        # Regex to match .m3u8 and include ?query=... if present
        matches = re.findall(r'(https?:\/\/[^\s\'"]+?\.m3u8[^\s\'"]*|\/\/[^\s\'"]+?\.m3u8[^\s\'"]*)', html)

        if matches:
            stream_url = matches[0]

            # If it starts with //, prepend https:
            if stream_url.startswith("//"):
                stream_url = "https:" + stream_url

            # If it's a relative path, make it absolute
            if not stream_url.startswith("http"):
                stream_url = urljoin(url, stream_url)

            return stream_url
        else:
            return None
    except Exception as e:
        print(f"Error fetching site: {e}")
        return None

def create_m3u8(output_file, stream_url):
    """
    Writes a new .m3u8 file with the given stream URL.
    """
    content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=3134643,FRAME-RATE=25,RESOLUTION=1920x1080,CODECS="avc1.42c01f,mp4a.40.2"
{stream_url}
"""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    site_url = "https://aliez.tv/live/uab2p85ge9b1h98355dc/"
    output_file = "test.m3u8"

    stream_url = fetch_m3u8_from_site(site_url)
    if stream_url:
        create_m3u8(output_file, stream_url)
        print(f"β… M3U8 file created: {output_file}")
        print(f"π”— Found stream: {stream_url}")
    else:
        print("β No .m3u8 link found on the page.")
