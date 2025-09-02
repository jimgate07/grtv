import requests
import re
from bs4 import BeautifulSoup

# URL of the webpage containing the wmsAuthSign
webpage_url = "https://www.alphacyprus.com.cy/live"

# Fetch the content of the webpage
response = requests.get(webpage_url)
response.raise_for_status()
webpage_content = response.text

# Parse the HTML content
soup = BeautifulSoup(webpage_content, "html.parser")

# Find the wmsAuthSign
wmsAuthSign = None
for script in soup.find_all("script"):
    if "wmsAuthSign" in script.text:
        match = re.search(r"wmsAuthSign=([a-zA-Z0-9%_=:-]+)", script.text)
        if match:
            wmsAuthSign = match.group(1)
            break

if not wmsAuthSign:
    raise Exception("wmsAuthSign not found in the webpage")

# Construct the final m3u8 URL
m3u8_base_url = "https://l4.cloudskep.com/alphacyp/acy/playlist.m3u8"
final_m3u8_url = f"{m3u8_base_url}?wmsAuthSign={wmsAuthSign}"

# Fetch the m3u8 content
m3u8_response = requests.get(final_m3u8_url)
m3u8_response.raise_for_status()
m3u8_content = m3u8_response.text

# Replace ANY us*.cloudskep.com with ln2.cloudskep.com
m3u8_content = re.sub(r"https://us\d+\.cloudskep\.com", "https://ln2.cloudskep.com", m3u8_content)

# Save to file
with open("alphacyprus.m3u8", "w", encoding="utf-8") as file:
    file.write(m3u8_content)

print(f"The final m3u8 URL is {final_m3u8_url}")
print("The m3u8 content has been saved to alphacyprus.m3u8 (ln2 version)")
