import re
import urllib.request

# Εδώ βάζεις το αριθμητικό ID της σελίδας σου
PAGE_ID = "100064220132182"

def get_stream_id():
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'el-GR,el;q=0.9,en;q=0.8',
    }
    
    # 1. Έλεγχος στη mobile σελίδα των live με βάση το ID
    live_url = f"https://m.facebook.com/profile.php?id={PAGE_ID}&v=live"
    try:
        req = urllib.request.Request(live_url, headers=headers)
        with urllib.request.urlopen(req) as response:
            html_content = response.read().decode('utf-8')
            matches = re.findall(r'/(?:videos|live)/(\d+)', html_content)
            if matches:
                return matches[0]
    except Exception as e:
        print(f"Σφάλμα κατά τον έλεγχο των live: {e}")

    # 2. Αν δεν βρει live, ψάχνει στη γενική λίστα των βίντεο
    videos_url = f"https://m.facebook.com/profile.php?id={PAGE_ID}&v=videos"
    try:
        req = urllib.request.Request(videos_url, headers=headers)
        with urllib.request.urlopen(req) as response:
            html_content = response.read().decode('utf-8')
            matches = re.findall(r'/videos/(\d+)', html_content)
            if matches:
                unique_ids = list(dict.fromkeys(matches))
                print(f"Δεν βρέθηκε ενεργό live, επιλέχθηκε το τελευταίο βίντεο: {unique_ids[0]}")
                return unique_ids[0]
    except Exception as e:
        print(f"Σφάλμα κατά τον έλεγχο των βίντεο: {e}")
        
    return None

if __name__ == "__main__":
    target_id = get_stream_id()
    if target_id:
        print(f"Αποθήκευση ID: {target_id}")
        with open("live-id.txt", "w") as f:
            f.write(target_id)
    else:
        print("Δεν βρέθηκε κανένα βίντεο.")
