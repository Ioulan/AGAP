import csv
import json
import os
import time
import subprocess
import urllib.parse

# Use a realistic User-Agent to avoid being blocked by Wikimedia
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

def get_direct_url(file_page_url):
    # Extract filename from URL (e.g. File:Seal_of_the_Armed_Forces_of_the_Philippines.svg)
    filename = file_page_url.split('/')[-1]
    if not filename.startswith("File:"):
        filename = "File:" + filename

    # URL encode the filename for the API
    encoded_filename = urllib.parse.quote(filename)
    api_url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={encoded_filename}&prop=imageinfo&iiprop=url&format=json"

    try:
        # Using curl for the API call too, as urllib is sometimes blocked by Wikimedia's security
        result = subprocess.run([
            "curl", "-s", "-L",
            "-H", f"User-Agent: {USER_AGENT}",
            api_url
        ], capture_output=True, text=True, check=True)

        data = json.loads(result.stdout)
        pages = data.get("query", {}).get("pages", {})
        for page_id in pages:
            imageinfo = pages[page_id].get("imageinfo", [])
            if imageinfo:
                return imageinfo[0].get("url")
    except Exception as e:
        print(f"Error fetching API for {filename}: {e}")
    return None

def download_file(url, dest_path):
    try:
        # Use curl as it's more robust and handles redirects/SSL better than basic urllib
        subprocess.run([
            "curl", "-s", "-L",
            "-H", f"User-Agent: {USER_AGENT}",
            url, "-o", dest_path
        ], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error downloading {url} via curl: {e}")
    except Exception as e:
        print(f"Unexpected error downloading {url}: {e}")
    return False

def main():
    sources_file = 'sources.csv'
    output_dir = 'src/media/logos'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(sources_file, mode='r', encoding='utf-8') as f:
        # We use a raw reader instead of DictReader to handle potential unquoted commas in URLs
        reader = csv.reader(f)
        header = next(reader)

        # Identify column indices
        try:
            file_idx = header.index("File")
            source_idx = header.index("Source")
            # Other columns are not strictly needed but we'll trace them
        except ValueError as e:
            print(f"Error: Missing required columns in {sources_file}: {e}")
            return

        for row in reader:
            if not row: continue

            # Extraction:
            # If the row has more columns than the header, the URL likely contained unquoted commas.
            # We assume 'File' is first and Source is spanning the middle.
            # Standard: [File, Source, License, Modifications] (Length 4)

            target_filename = row[file_idx]

            if len(row) > len(header):
                # The "extra" columns are part of the Source URL (index 1 to -2)
                # This handles cases like: File, URL_PART1, URL_PART2, License, Mods
                source_page_url = ",".join(row[source_idx : -2]).strip()
                print(f"Heads up: Reconstructed malformed URL for {target_filename}")
            else:
                source_page_url = row[source_idx].strip()

            dest_path = os.path.join(output_dir, target_filename)

            if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
                # print(f"Skipping {target_filename}, already exists.")
                continue

            print(f"Fetching direct URL for {target_filename}...")
            direct_url = get_direct_url(source_page_url)

            if direct_url:
                print(f"Downloading {target_filename} from {direct_url}...")
                if download_file(direct_url, dest_path):
                    print(f"Successfully downloaded {target_filename}")
                else:
                    print(f"Failed to download {target_filename}")
            else:
                print(f"Could not find direct URL for {target_filename}")

            # Be nice to Wikimedia API
            time.sleep(0.5)

if __name__ == "__main__":
    main()
