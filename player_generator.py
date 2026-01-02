import json
from pathlib import Path

class PlayerGenerator:
    def __init__(self):
        pass

    def generate(self, song_path, structure_path, lyrics_data=None):
        """
        Generates an HTML player with structure and optionally lyrics.
        """
        song_path = Path(song_path)
        structure_path = Path(structure_path)
        
        if not structure_path.exists():
             return

        with open(structure_path, 'r', encoding='utf-8') as f:
            structure = json.load(f)

        song_name = song_path.stem
        html_path = song_path.parent / f"{song_name}_player.html"

        # Preparing Lyrics JSON for JS
        lyrics_json = json.dumps(lyrics_data) if lyrics_data else "[]"

        # HTML Template (No Lyrics)
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{song_name} - Structure</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #111; color: #eee; display: flex; flex-direction: column; align-items: center; padding: 20px; height: 100vh; box-sizing: border-box; overflow: hidden; }}
        h1 {{ margin-bottom: 20px; font-weight: 300; letter-spacing: 1px; font-size: 1.5em; }}
        .main-container {{ display: flex; justify-content: center; width: 100%; max-width: 600px; flex: 1; min-height: 0; }}
        
        /* Player & Structure */
        .controls-col {{ flex: 1; display: flex; flex-direction: column; gap: 20px; min-height: 0; }}
        .player-box {{ background: #222; padding: 20px; border-radius: 12px; }}
        audio {{ width: 100%; outline: none; }}
        
        .segments {{ display: flex; flex-direction: column; gap: 8px; overflow-y: auto; flex: 1;background: #1a1a1a; padding: 10px; border-radius: 12px; }}
        .segment {{ 
            background: #333; padding: 12px 16px; border-radius: 8px; cursor: pointer; 
            display: flex; justify-content: space-between; align-items: center; transition: background 0.2s; 
        }}
        .segment:hover {{ background: #444; }}
        .segment.active {{ background: #007acc; color: white; border-left: 4px solid #66b2ff; }}
        .time {{ font-family: monospace; opacity: 0.7; font-size: 0.9em; }}
        .label {{ font-weight: 600; font-size: 1.1em; }}
    </style>
</head>
<body>
    <h1>{song_name}</h1>
    
    <div class="main-container">
        <div class="controls-col">
            <div class="player-box">
                <audio id="audioPlayer" controls>
                    <source src="{song_path.name}" type="audio/mpeg">
                    Your browser does not support the audio element.
                </audio>
            </div>
            <div class="segments">
"""
        
        for idx, section in enumerate(structure):
            start = section.get('start', 0)
            end = section.get('end', 0)
            label = section.get('label', 'Unknown')
            html_content += f"""
                <div class="segment" onclick="playSegment({start}, {end}, this)">
                    <span class="label">{label}</span>
                    <span class="time">{self.format_time(start)} - {self.format_time(end)}</span>
                </div>
"""

        html_content += f"""
            </div>
        </div>
    </div>

    <script>
        const audio = document.getElementById('audioPlayer');
        let currentEnd = null;

        function playSegment(start, end, el) {{
            audio.currentTime = start;
            audio.play();
            currentEnd = end;
            
            document.querySelectorAll('.segment').forEach(s => s.classList.remove('active'));
            el.classList.add('active');
        }}

        audio.addEventListener('timeupdate', () => {{
            const t = audio.currentTime;
            
            // Auto-pause at segment end
            if (currentEnd !== null && t >= currentEnd) {{
                audio.pause();
                currentEnd = null;
                document.querySelectorAll('.segment').forEach(s => s.classList.remove('active'));
            }}
        }});
    </script>
</body>
</html>
"""
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"[PlayerGenerator] Created HTML player with lyrics: {html_path}")

    def format_time(self, seconds):
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m:02d}:{s:02d}"

if __name__ == "__main__":
    pass
