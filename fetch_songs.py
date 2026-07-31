# export GEMINI_API_KEY="your_api_key_here"
# python fetch_songs.py
# process list of urls in urls.txt

import os
import time
import re
import yaml
from google import genai

# The SDK automatically picks up the GEMINI_API_KEY environment variable.
client = genai.Client()

def extract_yaml(text):
    """
    Strips markdown formatting if the model wraps the response in ```yaml ... ```
    """
    match = re.search(r'```yaml\n(.*?)\n```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def main():
    os.makedirs('data', exist_ok=True)
    
    with open('prompt.txt', 'r', encoding='utf-8') as f:
        base_prompt = f.read().strip()
        
    with open('urls.txt', 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
        
    print(f"Found {len(urls)} URLs to process.")
    
    for index, url in enumerate(urls, 1):
        print(f"\n[{index}/{len(urls)}] Processing: {url}")
        
        # Append the specific URL to your master prompt
        full_prompt = f"{base_prompt}\n\n**TARGET URL:** {url}"
        
        try:
            # We use gemini-2.5-flash as it is fast, highly capable, and cost-effective
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=full_prompt,
            )
            
            raw_yaml = extract_yaml(response.text)
            
            # Parse the YAML to extract the song title for a clean filename
            parsed_data = yaml.safe_load(raw_yaml)
            title = parsed_data.get('title', f'song_{index}')
            
            # Clean the title to be filesystem-friendly (e.g., "Yeh Ratein" -> "yeh_ratein")
            safe_title = re.sub(r'[^a-z0-9]+', '_', title.lower()).strip('_')
            filename = f"data/{safe_title}.yaml"
            
            # Save the file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(raw_yaml)
                
            print(f"  ✓ Success! Saved to {filename}")
            
            # --- Quota & Cost Management ---
            # The Gemini free tier allows 15 Requests Per Minute (RPM) and 1,500 Requests Per Day (RPD).
            # We pause for 5 seconds between requests to ensure we do not exceed the 15 RPM limit.
            if index < len(urls):
                print("  ⏳ Sleeping for 5 seconds to respect free-tier API rate limits...")
                time.sleep(5)
                
        except yaml.YAMLError as e:
            print(f"  ✗ Error parsing YAML for {url}. The AI output might be malformed: {e}")
        except Exception as e:
            print(f"  ✗ API Error processing {url}: {e}")

    print("\nBatch processing complete!")

if __name__ == "__main__":
    main()

