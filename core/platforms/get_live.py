import re
import urllib.request

# Βάλτε το username της σελίδας σας στο Facebook
PAGE_NAME = "100063980712662"

def get_live_id():
    url = f"https://www.facebook.com/{PAGE_NAME}/live/"
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            html_content = response.read().decode('utf-8')
            
            # Ψάχνει στο HTML της σελίδας για το μοτίβο του βίντεο ID του Facebook
            # Συνήθως τα live URLs περιέχουν /videos/ ή /live/ ακολουθούμενα από αριθμούς
            matches = re.findall(r'/(?:videos|live)/(\d+)', html_content)
            
            if matches:
                # Επιστρέφει το πρώτο μοναδικό ID που θα βρει
                return matches[0]
    except Exception as e:
        print(f"Σφάλμα κατά την ανάγνωση: {e}")
        
    return None

if __name__ == "__main__":
    new_id = get_live_id()
    if new_id:
        print(f"Βρέθηκε ενεργό Live ID: {new_id}")
        with open("live-id.txt", "w") as f:
            f.write(new_id)
    else:
        print("Δεν βρέθηκε ενεργό live αυτή τη στιγμή.")
