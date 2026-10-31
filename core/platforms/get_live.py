import re
import urllib.request
import urllib.parse

PAGE_ID = "100064220132182"

def get_stream_id():
    # Δοκιμάζουμε απευθείας την ενότητα των posts/videos όπου εμφανίζονται οι ζωντανές μεταδόσεις
    target_url = f"https://m.facebook.com/profile.php?id={PAGE_ID}&v=timeline"
    
    proxy_api = f"https://corsproxy.io/?{urllib.parse.quote(target_url)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1'
    }
    
    try:
        req = urllib.request.Request(proxy_api, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode('utf-8')
            
            # Αναζήτηση για μοτίβα fbid, story_fbid ή video IDs στον κώδικα
            patterns = [
                r'fbid=(\d{15,20})',
                r'video_id=(\d{15,20})',
                r'/videos/(\d{15,20})',
                r'/watch/\?v=(\d{15,20})',
                r'story_fbid%3D(\d{15,20})'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html_content)
                if matches:
                    unique_ids = list(dict.fromkeys(matches))
                    if unique_ids:
                        print(f"Βρέθηκε έγκυρο ID βίντεο/post: {unique_ids[0]}")
                        return unique_ids[0]
                        
            print("Δεν βρέθηκαν IDs με τα τρέχοντα patterns.")
                
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
