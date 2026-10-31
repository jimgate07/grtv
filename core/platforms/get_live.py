import urllib.request
import urllib.parse
import json

PAGE_ID = "epirustv1" # Μπορείς να βάλεις όποια σελίδα θέλεις

def get_stream_id():
    # Χρησιμοποιούμε το επίσημο Facebook oEmbed API για τη σελίδα/βίντεο
    # Εναλλακτικά, χτυπάμε το syndication feed του Facebook
    target_url = f"https://www.facebook.com/{PAGE_ID}/live/"
    
    # Χρησιμοποιούμε το thingproxy που συχνά περνάει πιο εύκολα τα φίλτρα του Facebook
    proxy_api = f"https://thingproxy.freeboard.io/fetch/{target_url}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    
    try:
        req = urllib.request.Request(proxy_api, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            
            # Ψάχνουμε για το μοναδικό ID μέσα στα διαθέσιμα permalinks ή structured data
            import re
            patterns = [
                r'videos/(\d{10,20})',
                r'watch/\?v=(\d{10,20})',
                r'video_id["\']?\s*[:=]\s*["\']?(\d{10,20})["\']?'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html_content)
                if matches:
                    unique_ids = [m for m in matches if m.isdigit() and m != PAGE_ID]
                    unique_ids = list(dict.fromkeys(unique_ids))
                    if unique_ids:
                        print(f"Εντοπίστηκε ενεργό Live ID: {unique_ids[0]}")
                        return unique_ids[0]
                        
            print("Δεν βρέθηκε ενεργό live μέσω proxy.")
                
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
