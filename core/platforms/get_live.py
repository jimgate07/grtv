import re
import urllib.request

# Βάλτε το username της σελίδας σας στο Facebook
PAGE_NAME = "100064220132182"

def get_stream_id():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    # 1. Δοκιμή πρώτα στη σελίδα των live
    live_url = f"https://www.facebook.com/{PAGE_NAME}/live/"
    try:
        req = urllib.request.Request(live_url, headers=headers)
        with urllib.request.urlopen(req) as response:
            html_content = response.read().decode('utf-8')
            matches = re.findall(r'/(?:videos|live)/(\d+)', html_content)
            if matches:
                # Επιστρέφει το πρώτο έγκυρο ID που θα βρει στα live
                return matches[0]
    except Exception as e:
        print(f"Σφάλμα κατά τον έλεγχο των live: {e}")

    # 2. Αν δεν βρει live, ψάχνει στη γενική λίστα των βίντεο για το πιο πρόσφατο
    videos_url = f"https://www.facebook.com/{PAGE_NAME}/videos/"
    try:
        req = urllib.request.Request(videos_url, headers=headers)
        with urllib.request.urlopen(req) as response:
            html_content = response.read().decode('utf-8')
            matches = re.findall(r'/videos/(\d+)', html_content)
            if matches:
                # Φιλτράρουμε τυχόν επαναλαμβανόμενα IDs και παίρνουμε το πιο πρόσφατο
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
