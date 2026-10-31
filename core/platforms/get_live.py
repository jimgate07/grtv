import re
import urllib.request
import urllib.parse

PAGE_ID = "100064220132182"

def get_stream_id():
    target_url = f"https://m.facebook.com/{PAGE_ID}/videos/"
    proxy_api = f"https://corsproxy.io/?{urllib.parse.quote(target_url)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    
    try:
        req = urllib.request.Request(proxy_api, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode('utf-8')
            
            # Αυστηρά μοτίβα που στοχεύουν αποκλειστικά τα IDs βίντεο και όχι τυχαίους αριθμούς
            patterns = [
                r'"video_id"\s*:\s*"(\d+)"',          # Μέσα σε JSON δεδομένα του Facebook
                r'/videos/(\d{10,20})/',               # Στα URL διαδρομής βίντεο
                r'/watch/\?v=(\d{10,20})',             # Στα watch URLs
                r'video_id=(\d{10,20})',               # Σώμα παραμέτρων
                r'/story\.php\?story_fbid=(\d{10,20})' # Stories/Posts βίντεο
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html_content)
                if matches:
                    unique_ids = [m for m in matches if m.isdigit() and m != PAGE_ID]
                    unique_ids = list(dict.fromkeys(unique_ids))
                    if unique_ids:
                        print(f"Βρέθηκε έγκυρο ID βίντεο: {unique_ids[0]}")
                        return unique_ids[0]
                        
            print("Δεν βρέθηκαν έγκυρα IDs με τα αυστηρά patterns.")
                
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
