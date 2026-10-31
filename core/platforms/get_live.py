import subprocess
import json
import sys

PAGE_URL = "https://www.facebook.com/profile.php?id=100064220132182"

def get_stream_id():
    # Δοκιμή στην κεντρική σελίδα του προφίλ
    try:
        cmd = ["yt-dlp", "--flat-playlist", "--dump-json", PAGE_URL]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"yt-dlp stderr: {result.stderr}", file=sys.stderr)
            
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    data = json.loads(line)
                    video_id = data.get('id')
                    if video_id:
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
