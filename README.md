# Songs with Transliterations

A static website generator built with Python and Jinja2 that compiles Hindi/regional songs into a beautiful, responsive HTML archive with full English translations and vocabulary guides.

## How to Add a New Song

1. Copy the YAML prompt template.
2. Provide the AI with the YouTube link.
3. Save the resulting YAML output into the `data/` directory (e.g., `new_song.yaml`).
4. Commit and push to the `main` branch. 

GitHub Actions will automatically run `build.py` and deploy the updated site to GitHub Pages in seconds.

## Local Development (using `uv`)

```bash
uv venv
source .venv/bin/activate
uv pip install jinja2 pyyaml
python build.py
```


