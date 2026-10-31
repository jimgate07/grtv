import re
import urllib.request

PAGE_ID = "100064220132182"

def get_stream_id():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'el-GR,el;q=0.9,en;q=0.8',
    }
    
    # Χρησιμοποιούμε τη mobile σελίδα βίντεο του προφίλ σου
    url = f"https://m.facebook.com/profile.php?id={PAGE_ID}&v=videos"
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            html_content = response.read().decode('utf-8')
            
            # Αναζήτηση για IDs βίντεο μέσα στον κώδικα της σελίδας
            matches = re.findall(r'(?:/videos/|/watch/\?v=|video_id=)(\d{10,})', html_content)
            
            if matches:
                unique_ids = list(dict.fromkeys(matches))
                print(f"Βρέθηκε ID βίντεο: {unique_ids[0]}")
                return unique_ids[0]
    except Exception as e:
        print(f"Σφάλμα σύνδεσης: {e}")
            
    return None

if __name__ == "__main__":
    target_id = get_stream_id()
    if target_id:
        print(f"Αποθήκευση ID: {target_id}")
        with open("core/platforms/live-id.txt", "w") as f:
            f.write(target_id)
    else:
        print("Δεν βρέθηκε κανένα βίντεο.")
