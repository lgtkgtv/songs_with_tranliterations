# export GEMINI_API_KEY="your_api_key_here"
# python fetch_songs.py
# process list of urls in urls.txt

import os
import time
import re
import yaml
import urllib.request
from google import genai
from google.genai.errors import APIError

client = genai.Client()

def extract_youtube_id(url):
    """Extracts the 11-character YouTube video ID."""
    match = re.search(r'(?:v=|\/)([a-zA-Z0-9_-]{11})', url)
    return match.group(1) if match else None

def get_processed_youtube_ids(data_dir='data'):
    """Scans existing YAML files in data/ to build a set of already processed video IDs."""
    processed_ids = set()
    if not os.path.exists(data_dir):
        return processed_ids
        
    for filename in os.listdir(data_dir):
        if filename.endswith(('.yaml', '.yml')):
            filepath = os.path.join(data_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, dict) and 'youtube_id' in data:
                        processed_ids.add(str(data['youtube_id']))
            except Exception:
                continue
    return processed_ids

def get_youtube_title(url):
    """Fetches the webpage and extracts the <title> tag to guide the AI."""
    try:
        # We use a standard browser User-Agent so YouTube doesn't block the request
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req, timeout=5).read().decode('utf-8')
        match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
        if match:
            # Clean up the standard " - YouTube" suffix
            return match.group(1).replace(' - YouTube', '').strip()
    except Exception as e:
        print(f"  ⚠️ Warning: Could not fetch video title directly ({e})")
    return None

def extract_yaml(text):
    """Strips markdown block formatting if present."""
    match = re.search(r'```yaml\n(.*?)\n```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def main():
    os.makedirs('data', exist_ok=True)
    
    if not os.path.exists('prompt.txt') or not os.path.exists('urls.txt'):
        print("✗ Error: Ensure both 'prompt.txt' and 'urls.txt' exist in the root directory.")
        return

    with open('prompt.txt', 'r', encoding='utf-8') as f:
        base_prompt = f.read().strip()
        
    with open('urls.txt', 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
        
    processed_ids = get_processed_youtube_ids('data')
    print(f"Loaded {len(processed_ids)} previously processed song(s).")
    print(f"Found {len(urls)} URL(s) in 'urls.txt'.\n")
    
    added_count = 0
    skipped_count = 0
    error_count = 0

    for index, url in enumerate(urls, 1):
        yt_id = extract_youtube_id(url)
        
        if yt_id and yt_id in processed_ids:
            print(f"[{index}/{len(urls)}] ⏭️ Skipping (Already Processed): {url}")
            skipped_count += 1
            continue

        print(f"[{index}/{len(urls)}] 🔄 Processing: {url}")
        
        # --- NEW: Fetch the title and inject it into the prompt ---
        video_title = get_youtube_title(url)
        full_prompt = f"{base_prompt}\n\n**TARGET URL:** {url}"
        if video_title:
            print(f"  ↳ Found Title: {video_title}")
            full_prompt += f"\n**VIDEO TITLE:** {video_title}\n(Please base the transliteration strictly on this song title)."
        
        max_retries = 3
        response_text = None
        
        for attempt in range(1, max_retries + 1):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=full_prompt,
                )
                response_text = response.text
                break
            except APIError as e:
                err_msg = str(e)
                if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "quota" in err_msg.lower():
                    wait_seconds = attempt * 15
                    print(f"  ⚠️ Quota limit reached. Retrying in {wait_seconds}s... (Attempt {attempt}/{max_retries})")
                    time.sleep(wait_seconds)
                else:
                    print(f"  ✗ API Error: {e}")
                    break
            except Exception as e:
                print(f"  ✗ Unexpected Error: {e}")
                break

        if not response_text:
            print(f"  ✗ Failed to retrieve response for {url}")
            error_count += 1
            continue

        try:
            raw_yaml = extract_yaml(response_text)
            parsed_data = yaml.safe_load(raw_yaml)
            
            if not isinstance(parsed_data, dict) or 'title' not in parsed_data:
                raise ValueError("Response does not contain valid YAML schema.")
                
            title = parsed_data.get('title', f'song_{yt_id or index}')
            safe_title = re.sub(r'[^a-z0-9]+', '_', title.lower()).strip('_')
            filename = f"data/{safe_title}.yaml"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(raw_yaml)
                
            print(f"  ✓ Saved: {filename}")
            added_count += 1
            if yt_id:
                processed_ids.add(yt_id)
                
            time.sleep(4)

        except Exception as e:
            print(f"  ✗ Failed to parse or save YAML for {url}: {e}")
            error_count += 1

    print("\n" + "=" * 55)
    print("📊 BATCH PROCESSING SUMMARY")
    print(f"   • Total URLs Evaluated: {len(urls)}")
    print(f"   • New Songs Added:     {added_count}")
    print(f"   • Skipped (Duplicates): {skipped_count}")
    print(f"   • Errors Encountered:   {error_count}")
    print("=" * 55)

    if added_count > 0:
        print("\n🚀 RE-DEPLOYMENT INSTRUCTIONS:")
        print("   git add data/")
        print(f'   git commit -m "Add {added_count} new song transliteration(s)"')
        print("   git push\n")

if __name__ == "__main__":
    main()

    
