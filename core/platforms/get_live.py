import subprocess
import json

PAGE_URL = "https://www.facebook.com/profile.php?id=100064220132182"

def get_stream_id():
    # Δοκιμή πρώτα στην ενότητα των βίντεο
    try:
        cmd = ["yt-dlp", "--flat-playlist", "--dump-json", f"{PAGE_URL}&v=videos"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        for line in result.stdout.strip().split('\n'):
            if line:
                data = json.loads(line)
                video_id = data.get('id')
                if video_id:
                    print(f"Βρέθηκε ID βίντεο μέσω yt-dlp: {video_id}")
                    return str(video_id)
    except Exception as e:
        print(f"Σφάλμα yt-dlp στα videos: {e}")

    # Δοκιμή στην ενότητα των live αν δεν βρέθηκε στα βίντεο
    try:
        cmd = ["yt-dlp", "--flat-playlist", "--dump-json", f"{PAGE_URL}&v=live"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        for line in result.stdout.strip().split('\n'):
            if line:
                data = json.loads(line)
                video_id = data.get('id')
                if video_id:
                    print(f"Βρέθηκε Live ID μέσω yt-dlp: {video_id}")
                    return str(video_id)
    except Exception as e:
        print(f"Σφάλμα yt-dlp στα live: {e}")

    return None

if __name__ == "__main__":
    target_id = get_stream_id()
    if target_id:
        print(f"Αποθήκευση ID: {target_id}")
        with open("live-id.txt", "w") as f:
            f.write(target_id)
    else:
        print("Δεν βρέθηκε κανένα βίντεο.")
