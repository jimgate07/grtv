import re
import urllib.request

PAGE_ID = "100064220132182"

def get_stream_id():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'el-GR,el;q=0.9,en;q=0.8',
    }
    
    # Δοκιμάζουμε απευθείας τη standard mobile σελίδα προφίλ
    urls = [
        f"https://m.facebook.com/profile.php?id={PAGE_ID}",
        f"https://m.facebook.com/profile.php?id={PAGE_ID}&v=videos",
        f"https://m.facebook.com/profile.php?id={PAGE_ID}&v=live"
    ]
    
    for url in urls:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                html_content = response.read().decode('utf-8')
                
                # Αναζήτηση για IDs βίντεο σε διάφορες μορφές links του Facebook
                # Ψάχνει για /videos/ID, /watch/?v=ID ή video_id=ID
                matches = re.findall(r'(?:/videos/|/watch/\?v=|video_id=)(\d{10,})', html_content)
                
                if matches:
                    # Αφαιρούμε τα διπλότυπα κρατώντας τη σειρά εμφάνισης
                    unique_ids = list(dict.fromkeys(matches))
                    print(f"Βρέθηκε ID βίντεο: {unique_ids[0]}")
                    return unique_ids[0]
        except Exception as e:
            print(f"Σφάλμα στο URL {url}: {e}")
            
    return None

if __name__ == "__main__":
    target_id = get_stream_id()
    if target_id:
        print(f"Αποθήκευση ID: {target_id}")
        with open("live-id.txt", "w") as f:
            f.write(target_id)
    else:
        print("Δεν βρέθηκε κανένα βίντεο.")
