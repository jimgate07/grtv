import re
import urllib.request
import urllib.parse

PAGE_ID = "epirustv1"

def get_stream_id():
    # Στοχεύουμε την mobile έκδοση η οποία επιστρέφει πιο απλό HTML structure
    target_url = f"https://m.facebook.com/{PAGE_ID}/live/"
    proxy_api = f"https://corsproxy.io/?{urllib.parse.quote(target_url)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.50 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'el-GR,el;q=0.9'
    }
    
    try:
        req = urllib.request.Request(proxy_api, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            
            # Δοκιμάζουμε μοτίβα ειδικά για τη mobile πλατφόρμα και τα JSON payloads του Facebook
            patterns = [
                r'video_id["\']?\s*[:=]\s*["\']?(\d{10,20})["\']?',
                r'broadcast_id["\']?\s*[:=]\s*["\']?(\d{10,20})["\']?',
                r'/videos/(\d{10,20})',
                r'/watch/\?v=(\d{10,20})',
                r'story_fbid=(\d{10,20})'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html_content)
                if matches:
                    unique_ids = [m for m in matches if m.isdigit() and m != PAGE_ID]
                    unique_ids = list(dict.fromkeys(unique_ids))
                    if unique_ids:
                        print(f"Εντοπίστηκε έγκυρο Live ID: {unique_ids[0]}")
                        return unique_ids[0]
                        
            print("Δεν βρέθηκε ενεργό live ID στη mobile σελίδα.")
                
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
