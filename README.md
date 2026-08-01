Here is the critiqued and improved version of your `README.md`.

### What was fixed:

1. **Removed Duplicates & Conversational Fluff:** Your file accidentally contained two different README drafts pasted together, along with some of my previous chat replies (e.g., "I have officially logged..."). I stripped all of that out.
2. **Unified Audience:** I seamlessly merged the "Visitor/Community" intro with the "Developer/Tech" specs so the repository makes sense to both language learners and programmers.
3. **Fixed Code Blocks:** Several markdown code blocks were missing their closing backticks (`````), which would break the formatting on GitHub. They are now strictly closed and properly highlighted.
4. **Cleaned the Prompt Template:** The manual AI prompt was malformed with repetitive bullet points. I cleaned it up into a distinct, easy-to-copy text block.

---

Copy the block below and replace your entire `README.md` file with it:

```markdown
# 🎵 AI-Powered Song Transliteration Archive

🌍 **Live Website:** [https://lgtkgtv.github.io/songs_with_tranliterations/](https://lgtkgtv.github.io/songs_with_tranliterations/)

A community-driven, AI-powered static site that translates, transliterates, and semantically structures Hindi and regional songs into English. Complete with native Devanagari scripts, Roman transliterations, and deep-dive vocabulary guides, this project is built to help non-native speakers learn language and culture through music.

---

## 🌟 Features
* **Semantic Structure:** AI detects song structures (Verses, Chorus) and neatly collapses repeated lines for a cleaner UI.
* **Sticky Vocabulary:** A side panel with word meanings and pronunciations that follows the user as they scroll.
* **Smart Rate-Limiting:** The data fetch utility includes a pre-flight token check, exponential backoff, and daily quota detection to safely interact with the Gemini Free Tier API.
* **Fully Static:** Generates pure HTML/CSS using Python and Jinja2, hosted effortlessly on GitHub Pages.

---

## 💻 Local Setup & Prerequisites

The site is built using Python. We recommend using [uv](https://docs.astral.sh/uv/) for fast, lightweight environment management.

```bash
# 1. Clone the repository
git clone https://github.com/lgtkgtv/songs_with_tranliterations.git
cd songs_with_tranliterations

# 2. Set your Gemini API key
export GEMINI_API_KEY="your_api_key_here"

# 3. Install dependencies via uv
uv pip install jinja2 pyyaml google-genai

```

---

## ⚙️ Workflow 1: Automated Batch Processing (Primary)

Use this method to automatically fetch and process a list of YouTube URLs using the Gemini API.

1. **Add URLs:** Paste the YouTube links you want to process into `urls.txt` (one per line).
2. **Fetch Data:** Run the automated fetcher script. It will test your API quota, scrape video titles, and generate structured YAML files for each song in the `data/` directory.
```bash
uv run python fetch_songs.py

```


*(Tip: run with `--debug` for verbose API error logging).*
3. **Build the Site:** Generate the updated HTML pages.
```bash
uv run python build.py

```



---

## ✍️ Workflow 2: Manual Processing (Fallback)

If you hit your API quota limits or want to contribute a song manually without running the scripts, you can use any AI chat interface (Gemini Web, ChatGPT, Claude) to generate the data.

**1. Copy and paste this exact prompt into your AI assistant:**

```text
Please generate the complete YAML transliteration data for the following song. 

Analyze the song structure and group lines into distinct sections (e.g., 'Chorus', 'Verse 1'). 
If a line repeats a previous line verbatim, set 'is_repeat: true' for that line.
Provide a rich vocabulary list with pronunciations.

Output ONLY valid YAML. Do not use markdown code blocks. Follow this exact schema structure:
- title, youtube_id, movie, year, singers, actors (list), composer, lyricist, youtube_channel, resolution, theme
- lyrics (list of sections):
  - section_name
  - lines (list):
    - roman, devanagari, english, is_repeat (boolean)
- vocabulary (list):
  - word, pronunciation, meaning

URL: [PASTE_YOUR_URL_HERE]

```

**2. Save the Output:**
Save the AI's raw YAML output as a new file in the `data/` folder (e.g., `data/my_new_song.yaml`).

**3. Build the Site:**
Run the build script to generate the HTML for your manually added song:

```bash
uv run python build.py

```

---

## 🗺️ Future Roadmap (TBD)

* **Platform-Agnostic Video Support:** Refactor the schema (replace `youtube_id` with `video_url` and `thumbnail_url`) and update HTML templates to support videos hosted on platforms outside of YouTube (e.g., Vimeo, DailyMotion, self-hosted).

---

## ⚖️ License & Disclaimer

* **Codebase:** Licensed under the MIT License.
* **Content:** Song lyrics, titles, and video embeds are the property of their respective copyright holders and are provided here strictly for educational, language-learning, and transliteration purposes under "Fair Use" principles.

```

<FollowUp label="Want to automate the build step?" query="Can you help me write a GitHub Actions YAML file so the site automatically runs build.py and publishes to GitHub Pages every time I push a new song?" />

```
