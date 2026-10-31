import re
import urllib.request
import urllib.parse

PAGE_ID = "100064220132182"

def get_stream_id():
    target_url = f"https://m.facebook.com/profile.php?id={PAGE_ID}&v=videos"
    
    proxy_api = f"https://corsproxy.io/?{urllib.parse.quote(target_url)}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1'
    }
    
    try:
        req = urllib.request.Request(proxy_api, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode('utf-8')
            
            # Ψάχνουμε αποκλειστικά και μόνο μέσα στα links των βίντεο για αριθμούς από 10 έως 20 ψηφία
            matches = re.findall(r'(?:/videos/|/watch/\?v=|video_id=|\/video\.php\?v=)(\d{10,20})', html_content)
            
            if matches:
                # Καθαρισμός τυχόν κενών και επιλογή του πρώτου έγκυρου ID
                unique_ids = [m for m in matches if m.isdigit()]
                unique_ids = list(dict.fromkeys(unique_ids))
                
                if unique_ids:
                    print(f"Βρέθηκε σωστό ID βίντεο: {unique_ids[0]}")
                    return unique_ids[0]
                    
            print("Δεν βρέθηκαν έγκυρα IDs βίντεο στα αντίστοιχα links.")
                
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
