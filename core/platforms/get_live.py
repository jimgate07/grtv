import subprocess
import json
import sys

# Χρησιμοποιούμε πλέον το canonical URL της σελίδας όπως το δίνει το Facebook
PAGE_URL = "https://www.facebook.com/Volcano-TV"

def get_stream_id():
    try:
        # Χρησιμοποιούμε το yt-dlp με flat-playlist για να σαρώσουμε τα τελευταία posts/videos της σελίδας
        cmd = ["yt-dlp", "--flat-playlist", "--dump-json", PAGE_URL]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"yt-dlp stderr: {result.stderr}", file=sys.stderr)
            
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    data = json.loads(line)
                    # Αναζήτηση ID είτε στο 'id' είτε στο 'url'
                    video_id = data.get('id')
                    if not video_id and 'url' in data:
                        # Αν υπάρχει URL, εξάγουμε το ID από μέσα
                        import re
                        match = re.search(r'(?:videos|watch|\?v=|/posts/)(\d+)', data['url'])
                        if match:
                            video_id = match.group(1)
                            
                    if video_id and str(video_id).isdigit() and len(str(video_id)) > 5:
                        print(f"Βρέθηκε ID βίντεο μέσω yt-dlp: {video_id}")
                        return str(video_id)
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"Σφάλμα εκτέλεσης yt-dlp: {e}")

    return None

if __name__ == "__main__":
    target_id = get_stream_id()
    if target_id:
        print(f"Αποθήκευση ID: {target_id}")
        with open("core/platforms/live-id.txt", "w") as f:
            f.write(target_id)
    else:
        print("Δεν βρέθηκε κανένα βίντεο.")
