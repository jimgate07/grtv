import re
import urllib.request
import urllib.parse

PAGE_ID = "100064220132182"

def get_stream_id():
    # Στοχεύουμε απευθείας την καρτέλα των live μεταδόσεων της σελίδας
    target_url = f"https://m.facebook.com/{PAGE_ID}/live/"
    proxy_api = f"https://corsproxy.io/?{urllib.parse.quote(target_url)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    
    try:
        req = urllib.request.Request(proxy_api, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode('utf-8')
            
            # Αναζήτηση αποκλειστικά για IDs που σχετίζονται με live ή watch links
            patterns = [
                r'/live/videos/.*?/(\d{10,20})',
                r'/watch/\?v=(\d{10,20})',
                r'"video_id"\s*:\s*"(\d{10,20})"'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html_content)
                if matches:
                    unique_ids = [m for m in matches if m.isdigit() and m != PAGE_ID]
                    unique_ids = list(dict.fromkeys(unique_ids))
                    if unique_ids:
                        print(f"Εντοπίστηκε ενεργό Live ID: {unique_ids[0]}")
                        return unique_ids[0]
                        
            print("Δεν βρέθηκε καμία ενεργή ζωντανή μετάδοση (Live).")
                
    except Exception as e:
        print(f"Σφάλμα σύνδεσης: {e}")
            
    return None

if __name__ == "__main__":
    target_id = get_stream_id()
    if target_id:
        print(f"Αποθήκευση Live ID: {target_id}")
        with open("live-id.txt", "w") as f:
            f.write(target_id)
    else:
        print("Δεν ενημερώθηκε το αρχείο διότι δεν υπάρχει live.")
