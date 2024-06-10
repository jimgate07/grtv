import requests
from bs4 import BeautifulSoup
import re

def get_wmsAuthSign():
    url = "https://www.alphacyprus.com.cy/live"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        script = soup.find('script', text=lambda t: 'wmsAuthSign' in t if t else False)
        if script:
            match = re.search(r'wmsAuthSign\s*:\s*"([^"]+)"', script.string)
            if match:
                return match.group(1)
    return None

def create_m3u8_file(wmsAuthSign):
    stream_url = f"https://l4.cloudskep.com/alphacyp/acy/playlist.m3u8?wmsAuthSign={wmsAuthSign}"
    m3u8_content = f"#EXTM3U\n#EXT-X-STREAM-INF:BANDWIDTH=2560000\n{stream_url}\n"
    with open("alphacy.m3u8", "w") as file:
        file.write(m3u8_content)
    print("alphacy.m3u8 file created successfully.")

wmsAuthSign = get_wmsAuthSign()
if wmsAuthSign:
    print(f'wmsAuthSign: {wmsAuthSign}')
    create_m3u8_file(wmsAuthSign)
else:
    print('wmsAuthSign not found')
