import re
import urllib.request
import urllib.parse

PAGE_ID = "epirustv1"

def get_stream_id():
    # Δοκιμάζουμε απευθείας το URL των βίντεο της σελίδας
    target_url = f"https://www.facebook.com/{PAGE_ID}/videos"
    proxy_api = f"https://corsproxy.io/?{urllib.parse.quote(target_url)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'el-GR,el;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    try:
        req = urllib.request.Request(proxy_api, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            
            # Αναζήτηση για live videos ή general video IDs στη σελίδα βίντεο
            patterns = [
                r'/videos/(\d{10,20})/',
                r'"video_id"\s*:\s*"(\d{10,20})"',
                r'owner_id\\":\\"' + PAGE_ID + '\\".*?video_id\\":\\"(\d{10,20})\\"',
                r'(\d{15,20})' # Γενικό μοτίβο για μεγάλα IDs βίντεο στο Facebook
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html_content)
                if matches:
                    unique_ids = [m for m in matches if m.isdigit() and m != PAGE_ID]
                    unique_ids = list(dict.fromkeys(unique_ids))
                    if unique_ids:
                        print(f"Εντοπίστηκε Live ID: {unique_ids[0]}")
                        return unique_ids[0]
                        
            print("Δεν βρέθηκε ενεργό live.")
                
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
