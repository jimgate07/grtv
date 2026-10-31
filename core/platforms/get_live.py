import re
import urllib.request
import urllib.parse

PAGE_ID = "100064220132182"

def get_stream_id():
    # Στοχεύουμε απευθείας την καρτέλα των βίντεο της σελίδας
    target_url = f"https://m.facebook.com/profile.php?id={PAGE_ID}&v=videos"
    
    proxy_api = f"https://corsproxy.io/?{urllib.parse.quote(target_url)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1'
    }
    
    try:
        req = urllib.request.Request(proxy_api, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode('utf-8')
            
            # Ευρύς εντοπισμός οποιουδήποτε μεγάλου αριθμού που μοιάζει με ID βίντεο στο Facebook
            # Ψάχνει για patterns όπως /videos/ID, /watch/?v=ID, story_fbid=ID κ.λπ.
            matches = re.findall(r'(\d{15,20})', html_content)
            
            if matches:
                # Φιλτράρουμε για να βρούμε τα πιο πιθανά IDs (συνήθως τα FB video IDs είναι γύρω στα 15-16 ψηφία)
                valid_ids = [m for m in matches if len(m) >= 15]
                unique_ids = list(dict.fromkeys(valid_ids))
                
                if unique_ids:
                    print(f"Βρέθηκε ID βίντεο: {unique_ids[0]}")
                    return unique_ids[0]
                    
            print("Δεν βρέθηκαν κατάλληλα IDs στον κώδικα.")
                
    except Exception as e:
        print(f"Σφάλμα σύνδεσης: {e}")
            
    return None

if __name__ == "__main__":
    target_id = get_stream_id()
    if target_id:
        print(f"Αποθήκευση ID: {target_id}")
        with open("live-id.txt", "w") as f:
            f.write(target_id)
    else:
        print("Δεν βρέθηκε κανένα βίντεο.")
