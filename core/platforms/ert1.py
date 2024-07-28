import requests

# URL of the M3U8 file to read
url = "https://pintos.giamoglonis.xyz/ch1/index.m3u8"

# Output file name
output_file = "ert1.m3u8"

try:
    # Fetch the content from the URL
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes

    # Write the content to the new file
    with open(output_file, "w") as file:
        file.write(response.text)
        
    print(f"Contents copied to {output_file} successfully.")

except requests.exceptions.RequestException as e:
    print(f"Error fetching the M3U8 file: {e}")
