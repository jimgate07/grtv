import re
import urllib.request
import urllib.parse
import json

PAGE_ID = "100064220132182"

def get_stream_id():
    # Στόχος URL
    target_url = f"https://m.facebook.com/profile.php?id={PAGE_ID}&v=videos"
    
    # Χρησιμοποιούμε έναν δωρεάν δημόσιο proxy (allorigins) για να παρακάμψουμε το IP block του GitHub
    proxy_api = f"https://api.allorigins.win/get?url={urllib.parse.quote(target_url)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    
    try:
        req = urllib.request.Request(proxy_api, headers=headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            html_content = data.get('contents', '')
            
            # Αναζήτηση για IDs βίντεο μέσα στο HTML που επέστρεψε ο proxy
            matches = re.findall(r'(?:/videos/|/watch/\?v=|video_id=|\/video\.php\?v=)(\d{10,})', html_content)
            
            if matches:
                unique_ids = list(dict.fromkeys(matches))
                print(f"Βρέθηκε ID βίντεο μέσω Proxy: {unique_ids[0]}")
                return unique_ids[0]
            else:
                print("Δεν βρέθηκαν IDs στον κώδικα της σελίδας.")
                
    except Exception as e:
        print(f"Σφάλμα σύνδεσης μέσω Proxy: {e}")
            
    return None

if __name__ == "__main__":
    target_id = get_stream_id()
    if target_id:
        print(f"Αποθήκευση ID: {target_id}")
        with open("live-id.txt", "w") as f:
            f.write(target_id)
    else:
        print("Δεν βρέθηκε κανένα βίντεο.")
