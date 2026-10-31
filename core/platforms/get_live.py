import re
import urllib.request
import urllib.parse

PAGE_ID = "epirustv1"

def get_stream_id():
    # Χρησιμοποιούμε την κανονική desktop έκδοση ή το βασικό URL της σελίδας
    # διότι τα OpenGraph tags περιέχουν πάντα το τρέχον live ID όταν η σελίδα είναι live.
    target_url = f"https://www.facebook.com/{PAGE_ID}"
    proxy_api = f"https://corsproxy.io/?{urllib.parse.quote(target_url)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'el-GR,el;q=0.9,en;q=0.8'
    }
    
    try:
        req = urllib.request.Request(proxy_api, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode('utf-8')
            
            # Μοτίβα για να πιάσουμε το ID από τα διαθέσιμα links ή τα meta tags της σελίδας
            patterns = [
                r'videos/(\d{10,20})',
                r'watch/\?v=(\d{10,20})',
                r'"video_id"\s*:\s*"(\d{10,20})"',
                r'eid=([A-Za-z0-9\-_]+)',
                r'story_fbid=(\d{10,20})'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html_content)
                if matches:
                    # Φιλτράρουμε τυχόν αριθμούς που είναι ίδιοι με το PAGE_ID αν είχαν πιαστεί κατά λάθος
                    unique_ids = [m for m in matches if m.isdigit() and m != PAGE_ID]
                    unique_ids = list(dict.fromkeys(unique_ids))
                    if unique_ids:
                        print(f"Εντοπίστηκε ενεργό Live ID: {unique_ids[0]}")
                        return unique_ids[0]
                        
            print("Δεν βρέθηκε καμία ενεργή ζωντανή μετάδοση (Live) σταδιακά.")
                
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
