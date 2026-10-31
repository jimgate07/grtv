import re
import urllib.request
import urllib.parse

PAGE_ID = "100064220132182"

def get_stream_id():
    # Χρησιμοποιούμε τη γενική δημόσια αναζήτηση βίντεο της σελίδας
    target_url = f"https://m.facebook.com/{PAGE_ID}/videos/"
    
    proxy_api = f"https://corsproxy.io/?{urllib.parse.quote(target_url)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    
    try:
        req = urllib.request.Request(proxy_api, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode('utf-8')
            
            # Εντοπισμός οποιουδήποτε δεκαπενταψήφιου ή εξαψήφιου αριθμού που αντιπροσωπεύει video ID στο Facebook
            matches = re.findall(r'(\d{15,18})', html_content)
            
            if matches:
                # Φιλτράρουμε τους αριθμούς εξαιρώντας το Page ID αν τυχόν εμφανίζεται
                valid_ids = [m for m in matches if m != PAGE_ID]
                unique_ids = list(dict.fromkeys(valid_ids))
                
                if unique_ids:
                    print(f"Βρέθηκε ID βίντεο: {unique_ids[0]}")
                    return unique_ids[0]
                    
            print("Δεν βρέθηκαν IDs.")
                
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
