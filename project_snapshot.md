Enjoy your break! It has been a highly productive session. 

You have successfully evolved this from a simple script into a resilient, production-grade automated pipeline and an interactive web application.

Here is the complete project snapshot—including the requirements we captured, the DevSecOps/automation principles we applied, and everything we accomplished—so you can easily pick up exactly where you left off.

---

### 🎵 Project: Automated Song Transliteration Archive

**Objective:** Build an automated, resilient pipeline that extracts YouTube links, uses AI to generate structured semantic metadata and transliterated lyrics (Roman, Devanagari, English), and generates a static, interactive frontend hosted on GitHub Pages.

#### 1. Architecture Overview

| Component | Description | Status |
| --- | --- | --- |
| `fetch_songs.py` | Data pipeline: handles AI requests, scraping, and YAML | Completed |
| `build.py` | Static site generator: merges YAML with HTML templates | Completed |
| `index_template` | Interactive JS datatable with inline YouTube modal | Completed |
| `song_template` | Responsive transliteration grid and vocabulary UI | Completed |

---

#### 2. Accomplishments: Backend & Data Pipeline (`fetch_songs.py`)

We bulletproofed the automation script to run completely unattended without failing, utilizing enterprise-grade DevSecOps principles:

* **Structured Outputs (JSON Schema):** Replaced unpredictable raw text generation with strict JSON schema enforcement to guarantee perfect YAML parsing and eliminate data formatting crashes.
* **Context Anchoring (Anti-Hallucination):** Integrated `urllib` to scrape the actual YouTube video title before calling the AI, ensuring the model translates the correct song rather than guessing based on the URL characters.
* **Idempotency (Deduplication Check):** The script scans the `data/` directory and automatically skips URLs that have already been processed.
* **Pre-Flight Health Check:** Added a minimal-token "ping" function at the start of the script to verify API health and quota availability before initiating the heavy batch process.
* **Resilient Error Handling & Quota Tracking:**
* Implemented **Exponential Backoff** for per-minute rate limits (`429` errors).
* Added a **Hard Halt (3-Strike Rule)** to detect daily quota exhaustion and abort gracefully without hammering the server.


* **Observability (`--debug`):** Added a CLI argument to surface raw API error logs and dump malformed JSON responses into a local `.log` file for easy inspection.
* **Semantic Structure:** Updated the AI prompt to group lyrics by stanzas (Verse, Chorus) and detect recurring lines (`is_repeat: true`) to clean up the UI.

---

#### 3. Accomplishments: Frontend & UI

We upgraded the static templates into a dynamic, client-side application using Vanilla JavaScript, CSS variables, and HTML5 native elements.

* **Interactive Index Dashboard:**
* **Global Search:** Instant text filtering across all columns (songs, actors, singers).
* **Sortable Headers:** Click-to-sort functionality for any column.
* **Customizable View:** A dropdown menu to toggle column visibility (Actors, Composer, Source), preventing horizontal scrolling on smaller screens.


* **Seamless Video Playback:**
* Implemented an HTML5 `<dialog>` modal that scales dynamically to 90vw for a cinematic overlay experience directly on the index page.
* Patched YouTube's "Error 153" by applying `rel="noopener noreferrer"` to strip referrer headers.


* **Automated Thumbnails:** Replaced text links with visual thumbnail cards that automatically pull the correct image scale (`mqdefault`, `hqdefault`, `maxresdefault`) directly from YouTube's image servers.
* **Responsive Song Pages:**
* Built a mobile-friendly metadata grid for Actors, Singers, Lyricists, and Video Resolution.
* Created a responsive 3-column lyrics grid (Roman, Devanagari, English) that gracefully stacks on mobile devices.
* Added a stylish vocabulary dictionary section.



---

#### 4. Next Steps (When you return)

1. **Wait for Quota Reset:** Wait for the Google API daily free-tier quota to reset (midnight Pacific Time).
2. **Run the Pipeline:** Execute `uv run python fetch_songs.py` to process the remaining URLs.
3. **Generate the Site:** Execute `uv run python build.py` to map the new YAML files into the `output/` directory.
4. **Deploy:** Run the git commands (`git add .`, `git commit`, `git push`) to trigger the GitHub Actions deployment.

Whenever you are ready to resume, just drop a message and we can work on the next features (like Dark Mode or pagination)!
