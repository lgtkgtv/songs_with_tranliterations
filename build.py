import os
import yaml
from jinja2 import Environment, FileSystemLoader

def build_site():
    env = Environment(loader=FileSystemLoader('templates'))
    song_template = env.get_template('song_template.html')
    index_template = env.get_template('index_template.html')

    os.makedirs('output', exist_ok=True)
    data_dir = 'data'
    
    # List to hold metadata for the index page
    all_songs = []

    for filename in os.listdir(data_dir):
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            filepath = os.path.join(data_dir, filename)
            
            with open(filepath, 'r', encoding='utf-8') as file:
                song_data = yaml.safe_load(file)

            # Generate individual song page
            output_filename = filename.rsplit('.', 1)[0] + '.html'
            output_path = os.path.join('output', output_filename)
            
            html_content = song_template.render(song_data)
            with open(output_path, 'w', encoding='utf-8') as output_file:
                output_file.write(html_content)
            
            # Store metadata for the index page
            song_data['url'] = output_filename
            all_songs.append(song_data)
            print(f"Generated: {output_path}")

    # Sort songs alphabetically by title
    all_songs = sorted(all_songs, key=lambda x: x.get('title', ''))

    # Generate the index.html page
    index_content = index_template.render(songs=all_songs)
    with open(os.path.join('output', 'index.html'), 'w', encoding='utf-8') as index_file:
        index_file.write(index_content)
    
    print("Generated: output/index.html")

if __name__ == "__main__":
    build_site()
