# 🎵 Songs with Transliterations

🌍 **Live Website:** [https://lgtkgtv.github.io/songs_with_tranliterations/](https://lgtkgtv.github.io/songs_with_tranliterations/)

A community-driven archive that translates Hindi and regional songs into English, complete with native Devanagari scripts, Roman transliterations, and deep-dive vocabulary guides. This project is built to help non-native speakers learn language and culture through music.

---

## 🌟 For Visitors & Language Learners
Welcome! You can browse our entire collection of translated songs on our [live website](https://lgtkgtv.github.io/songs_with_tranliterations/). 

Each song page includes:
*   Side-by-side English translations and native scripts.
*   A breakdown of poetic, uncommon, and culturally specific vocabulary.
*   Direct links to the original YouTube videos.

---

## 🤝 How to Contribute a Song
We welcome contributions! You do not need to be a programmer to add a song to this collection. We use AI to do the heavy lifting of translation and formatting.

**Step 1: Generate the Song Data**
1. Copy the text inside the `prompt.txt` file located in this repository.
2. Paste the prompt into an AI assistant (like Google Gemini).
3. Append the YouTube URL or the lyrics of the song you want to add.
4. The AI will generate a strictly formatted YAML block.

**Step 2: Add it to the Repository**
1. Fork this repository.
2. Create a new file in the `data/` folder (e.g., `my_new_song.yaml`).
3. Paste the AI-generated YAML into this file.
4. Submit a Pull Request. 

Once merged, GitHub Actions will automatically rebuild the website and your song will be live!

---

## 💻 For Developers (Local Setup)
The static website is generated using Python and Jinja2. If you want to build the site locally or modify the HTML templates, follow these steps.

**Prerequisites:** Install [uv](https://docs.astral.sh/uv/) for fast Python environment management.

```bash
# 1. Clone the repo
git clone [https://github.com/lgtkgtv/songs_with_tranliterations.git](https://github.com/lgtkgtv/songs_with_tranliterations.git)
cd songs_with_tranliterations

# 2. Set up the environment
uv venv
source .venv/bin/activate
uv pip install jinja2 pyyaml

# 3. Build the site
python build.py

---

## License & Disclaimer
Codebase: Licensed under the MIT License.  
Content: Song lyrics and titles are the property of their respective copyright holders and are provided here strictly for educational, language-learning, and transliteration purposes under "Fair Use" principles.  
 
