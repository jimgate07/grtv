import re
import urllib.request
import urllib.parse

# Ορίζεις εδώ τα κανάλια που θέλεις να παρακολουθείς
# Το κλειδί είναι το όνομα του αρχείου/σελίδας
CHANNELS = {
    "epirustv1": "epirustv1",
    "supertvkorinthos": "supertvkorinthos",
    "corfuchannel": "corfuchannel",
    "startmediacorfu": "startmediacorfu",
    "ilektratv": "100063542305429",
    "volcanotv": "100064220132182"
}

def get_stream_id(page_id):
    target_url = f"https://www.facebook.com/{page_id}/live/"
    proxy_api = f"https://r.jina.ai/https://www.facebook.com/{page_id}/live/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    
    try:
        req = urllib.request.Request(proxy_api, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as response:
            content = response.read().decode('utf-8', errors='ignore')
            
            patterns = [
                r'/videos/(\d{10,20})',
                r'/watch/\?v=(\d{10,20})',
                r'videos/.*?/(\d{10,20})'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content)
                if matches:
                    unique_ids = [m for m in matches if m.isdigit() and m != page_id]
                    unique_ids = list(dict.fromkeys(unique_ids))
                    if unique_ids:
                        print(f"[{page_id}] Εντοπίστηκε ενεργό Live ID: {unique_ids[0]}")
                        return unique_ids[0]
                        
            print(f"[{page_id}] Δεν βρέθηκε ενεργό live ID.")
                
    except Exception as e:
        print(f"[{page_id}] Σφάλμα σύνδεσης: {e}")
            
    return None

if __name__ == "__main__":
    for filename_key, page_id in CHANNELS.items():
        print(f"Έλεγχος για τη σελίδα: {page_id}...")
        stream_id = get_stream_id(page_id)
        
        filename = f"{filename_key}.txt"
        if stream_id:
            with open(filename, "w") as f:
                f.write(stream_id)
            print(f"-> Αποθηκεύτηκε στο {filename}\n")
        else:
            # Αν δεν έχει live, καθαρίζουμε το αρχείο ή γράφουμε κενό
            with open(filename, "w") as f:
                f.write("")
            print(f"-> Δεν υπάρχει live. Το αρχείο {filename} καθαρίστηκε.\n")
