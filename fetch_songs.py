import os
import time
import re
import yaml
import json
import urllib.request
import argparse
from google import genai
from google.genai import types
from google.genai.errors import APIError

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

client = genai.Client()

def extract_youtube_id(url):
    match = re.search(r'(?:v=|\/)([a-zA-Z0-9_-]{11})', url)
    return match.group(1) if match else None

def get_processed_youtube_ids(data_dir='data'):
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
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req, timeout=5).read().decode('utf-8')
        match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
        if match:
            return match.group(1).replace(' - YouTube', '').strip()
    except Exception as e:
        print(f"  ⚠️ Warning: Could not fetch video title directly ({e})")
    return None


def check_api_health(client, debug=False):
    """Sends a moderate-sized request to test if sufficient token quota is available."""
    print("🩺 Running pre-flight token quota check...")
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents='Please write a 50-word summary of the Python programming language.',
            config=types.GenerateContentConfig(max_output_tokens=100)
        )
        
        if debug:
            print(f"  [DEBUG] Pre-flight token check passed. Sample response length: {len(response.text)} chars.")
            
        print("  ✓ API is healthy and sufficient token quota is available.\n")
        return True
        
    except APIError as e:
        err_msg = str(e).lower()
        if "429" in err_msg or "resource_exhausted" in err_msg or "quota" in err_msg:
            # Calculate time until Midnight Pacific Time
            pacific_tz = ZoneInfo("America/Los_Angeles")
            now_pt = datetime.now(pacific_tz)
            
            # Next midnight PT
            tomorrow_pt = now_pt + timedelta(days=1)
            reset_time_pt = tomorrow_pt.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Time delta
            time_left = reset_time_pt - now_pt
            hours, remainder = divmod(int(time_left.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            
            print(f"  🚨 PRE-FLIGHT FAILED: Insufficient daily quota.")
            print(f"  ⏳ Google's servers reset in: {hours} hours and {minutes} minutes (Midnight Pacific Time).")
            return False
        else:
            print(f"  ⚠️ Pre-flight API Error: {e}")
            return False
    except Exception as e:
        print(f"  ⚠️ Pre-flight Unexpected Error: {e}")
        return False



def main():
    parser = argparse.ArgumentParser(description="Fetch and transliterate song lyrics using Gemini API.")
    parser.add_argument('--debug', action='store_true', help="Enable verbose debug logging and error dumping.")
    args = parser.parse_args()

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

    # --- NEW: Run the pre-flight check ---
    if not check_api_health(client, args.debug):
        print("🛑 Aborting script. Fix API issues before running the batch.")
        return
    
    if args.debug:
        print("🔍 DEBUG MODE ENABLED: Detailed API errors will be logged.")
    
    added_count = 0
    skipped_count = 0
    error_count = 0
    
    # --- NEW: Global Quota Tracking ---
    daily_quota_hit = False
    consecutive_429_errors = 0 

    song_schema = {
        "type": "OBJECT",
        "properties": {
            "title": {"type": "STRING"},
            "movie": {"type": "STRING"},
            "year": {"type": "STRING"}, 
            "singers": {"type": "STRING"},
            "actors": {
                "type": "ARRAY",
                "items": {"type": "STRING"},
                "description": "List of actors appearing in the video"
            },
            "composer": {"type": "STRING"},
            "lyricist": {"type": "STRING"},
            "youtube_channel": {"type": "STRING"},
            "resolution": {"type": "STRING"},
            "theme": {"type": "STRING"},
            "lyrics": {
                "type": "ARRAY",
                "description": "Group the lyrics logically into stanzas/sections (e.g., Verse, Chorus).",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "section_name": {"type": "STRING"},
                        "lines": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "roman": {"type": "STRING"},
                                    "devanagari": {"type": "STRING"},
                                    "english": {"type": "STRING"},
                                    "is_repeat": {"type": "BOOLEAN"}
                                },
                                "required": ["roman", "devanagari", "english", "is_repeat"]
                            }
                        }
                    },
                    "required": ["section_name", "lines"]
                }
            },
            "vocabulary": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "word": {"type": "STRING"},
                        "pronunciation": {"type": "STRING"},
                        "meaning": {"type": "STRING"}
                    },
                    "required": ["word", "pronunciation", "meaning"]
                }
            }
        },
        "required": ["title", "movie", "year", "singers", "actors", "composer", "lyricist", "youtube_channel", "resolution", "theme", "lyrics", "vocabulary"]
    }

    for index, url in enumerate(urls, 1):
        if daily_quota_hit:
            break

        yt_id = extract_youtube_id(url)
        
        if yt_id and yt_id in processed_ids:
            print(f"[{index}/{len(urls)}] ⏭️ Skipping (Already Processed): {url}")
            skipped_count += 1
            continue

        print(f"[{index}/{len(urls)}] 🔄 Processing: {url}")
        
        video_title = get_youtube_title(url)
        semantic_instruction = (
            "\n\n**IMPORTANT INSTRUCTION FOR LYRICS STRUCTURE:**\n"
            "Analyze the song structure. Group lines into distinct sections (e.g., 'Chorus', 'Verse 1', 'Bridge'). "
            "If a line repeats a previous line verbatim (like a recurring chorus), you must set 'is_repeat' to true for that line."
        )
        
        full_prompt = f"{base_prompt}{semantic_instruction}\n\n**TARGET URL:** {url}"
        if video_title:
            print(f"  ↳ Found Title: {video_title}")
            full_prompt += f"\n**VIDEO TITLE:** {video_title}\n(Please base the transliteration strictly on this song title)."
        
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=song_schema,
            temperature=0.2,
            max_output_tokens=8192
        )
        
        max_retries = 4
        response_text = None
        
        for attempt in range(1, max_retries + 1):
            try:
                if args.debug:
                    print(f"  [DEBUG] Sending request to Gemini API (Attempt {attempt})...")
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=full_prompt,
                    config=config
                )
                response_text = response.text
                
                # --- NEW: Reset quota tracker on success ---
                consecutive_429_errors = 0 
                break
                
            except APIError as e:
                err_msg = str(e).lower()
                if args.debug:
                    print(f"  [DEBUG] Raw API Error Dump: {err_msg}")
                    
                if "429" in err_msg or "resource_exhausted" in err_msg or "quota" in err_msg:
                    consecutive_429_errors += 1
                    
                    # --- NEW: Hard halt condition ---
                    if consecutive_429_errors >= 3:
                        print(f"  🚨 3 consecutive quota errors detected. Halting script to prevent API penalties.")
                        daily_quota_hit = True
                        break
                        
                    wait_seconds = 60 * (2 ** (attempt - 1))
                    print(f"  ⚠️ Quota limit reached. Applying exponential backoff. Waiting {wait_seconds}s... (Consecutive 429s: {consecutive_429_errors}/3)")
                    time.sleep(wait_seconds)
                elif "503" in err_msg or "504" in err_msg or "500" in err_msg:
                    wait_seconds = attempt * 15
                    print(f"  ⚠️ Server busy/timeout. Retrying in {wait_seconds}s... (Attempt {attempt}/{max_retries})")
                    time.sleep(wait_seconds)
                else:
                    print(f"  ✗ Fatal API Error.")
                    break
            except Exception as e:
                print(f"  ✗ Unexpected Error: {e}")
                time.sleep(attempt * 5)

        if daily_quota_hit:
            print("🛑 Batch process aborted due to assumed daily quota exhaustion.")
            break

        if not response_text:
            print(f"  ✗ Failed to retrieve response for {url} after {max_retries} attempts.")
            error_count += 1
            continue

        try:
            parsed_data = json.loads(response_text)
            parsed_data['youtube_id'] = yt_id
            
            title = parsed_data.get('title', f'song_{yt_id or index}')
            safe_title = re.sub(r'[^a-z0-9]+', '_', title.lower()).strip('_')
            filename = f"data/{safe_title}.yaml"
            
            with open(filename, 'w', encoding='utf-8') as f:
                yaml.dump(parsed_data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
                
            print(f"  ✓ Saved: {filename}")
            added_count += 1
            if yt_id:
                processed_ids.add(yt_id)
                
            time.sleep(5)

        except Exception as e:
            print(f"  ✗ Failed to parse JSON or save YAML for {url}: {e}")
            error_count += 1
            if args.debug and response_text:
                debug_file = f"debug_error_{yt_id}.log"
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(response_text)
                print(f"  [DEBUG] Dumped the raw broken AI response to {debug_file} for inspection.")

    print("\n" + "=" * 55)
    print("📊 BATCH PROCESSING SUMMARY")
    print(f"   • Total URLs Evaluated: {len(urls)}")
    print(f"   • New Songs Added:     {added_count}")
    print(f"   • Skipped (Duplicates): {skipped_count}")
    print(f"   • Errors Encountered:   {error_count}")
    print("=" * 55)

if __name__ == "__main__":
    main()
