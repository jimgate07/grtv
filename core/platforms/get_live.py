import re
import urllib.request
import json

PAGE_ID = "100064220132182"

def get_stream_id():
    # Χρησιμοποιούμε το κινητό frontend του Facebook με εναλλακτικό User-Agent bot
    url = f"https://mbasic.facebook.com/profile.php?id={PAGE_ID}&v=videos"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'el-GR,el;q=0.9,en;q=0.8',
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            html_content = response.read().decode('utf-8')
            
            # Αναζήτηση IDs βίντεο μέσα στη mbasic έκδοση (δεν μπλοκάρει με Error 400)
            matches = re.findall(r'/video\.php\?v=(\d+)|/watch/\?v=(\d+)|/videos/(\d+)', html_content)
            
            # Καθαρισμός και εύρεση μοναδικών IDs
            valid_ids = []
            for match in matches:
                for group in match:
                    if group and group.isdigit() and len(group) > 8:
                        if group not in valid_ids:
                            valid_ids.append(group)
                            
            if valid_ids:
                print(f"Βρέθηκε ID βίντεο: {valid_ids[0]}")
                return valid_ids[0]
                
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
