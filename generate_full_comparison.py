import json
from pathlib import Path

# CSS for the comparison page
CSS = """
<style>
    :root {
        --bg: #0a0a0c;
        --card-bg: #111;
        --manual-bg: rgba(16, 185, 129, 0.05);
        --demucs-bg: rgba(236, 72, 153, 0.05);
        --sam-bg: rgba(99, 102, 241, 0.05);
        --text: #eee;
        --border: rgba(255,255,255,0.1);
    }
    body {
        font-family: 'Segoe UI', sans-serif;
        background: var(--bg);
        color: var(--text);
        margin: 0;
        padding: 20px;
        height: 100vh;
        display: flex;
        flex-direction: column;
    }
    h1 { text-align: center; margin: 0 0 20px 0; }
    .back-link { position: absolute; top: 20px; left: 20px; color: #fff; text-decoration: none; opacity: 0.7; }
    
    .grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 20px;
        flex: 1;
        min-height: 0; /* Important for scroll */
    }
    
    .col {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 12px;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    
    .col-header {
        padding: 15px;
        text-align: center;
        font-weight: bold;
        border-bottom: 1px solid var(--border);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .manual-col .col-header { background: var(--manual-bg); color: #34d399; }
    .demucs-col .col-header { background: var(--demucs-bg); color: #f472b6; }
    .sam-col .col-header { background: var(--sam-bg); color: #818cf8; }
    
    .player-section {
        padding: 15px;
        background: rgba(0,0,0,0.2);
        border-bottom: 1px solid var(--border);
    }
    audio { width: 100%; height: 32px; }
    
    .metrics {
        padding: 10px 15px;
        font-size: 0.85em;
        color: #aaa;
        border-bottom: 1px solid var(--border);
        display: flex;
        justify-content: space-between;
    }
    
    .segments-list {
        flex: 1;
        overflow-y: auto;
        padding: 10px;
    }
    
    .segment {
        display: flex;
        justify-content: space-between;
        padding: 8px 12px;
        margin-bottom: 5px;
        background: rgba(255,255,255,0.05);
        border-radius: 6px;
        cursor: pointer;
        transition: background 0.2s;
        font-size: 0.9em;
    }
    .segment:hover { background: rgba(255,255,255,0.1); }
    .segment.active { background: #fff; color: #000; }
    .segment.active .time { color: #333; }
    
    .label { font-weight: 600; }
    .time { font-family: monospace; color: #888; font-size: 0.9em; }
    
    .empty-state {
        padding: 40px;
        text-align: center;
        color: #555;
        font-style: italic;
    }
</style>
"""

JS_TEMPLATE = """
<script>
    class ColumnPlayer {
        constructor(id) {
            this.id = id;
            this.audio = document.getElementById('audio-' + id);
            this.container = document.getElementById('segments-' + id);
            this.currentEnd = null;
            
            if(this.audio) {
                this.audio.addEventListener('timeupdate', () => this.checkTime());
            }
        }
        
        playSegment(start, end, el) {
            if(!this.audio) return;
            
            this.audio.currentTime = start;
            this.audio.play();
            this.currentEnd = end;
            
            // UI
            const segs = this.container.querySelectorAll('.segment');
            segs.forEach(s => s.classList.remove('active'));
            el.classList.add('active');
        }
        
        checkTime() {
            if (this.currentEnd !== null && this.audio.currentTime >= this.currentEnd) {
                this.audio.pause();
                this.currentEnd = null;
                const active = this.container.querySelector('.segment.active');
                if(active) active.classList.remove('active');
            }
        }
    }

    const manualPlayer = new ColumnPlayer('manual');
    const demucsPlayer = new ColumnPlayer('demucs');
    const samPlayer = new ColumnPlayer('sam');
</script>
"""

def format_time(seconds):
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"

def render_column(version_name, class_name, folder_path, base_path):
    """
    Renders the HTML for a single column (Manual, Demucs, or SAM).
    """
    col_id = version_name.lower()
    
    html = f'<div class="col {class_name}">'
    html += f'<div class="col-header">{version_name}</div>'
    
    if not folder_path:
        html += '<div class="empty-state">Data Not Available</div>'
        html += '</div>'
        return html

    folder = Path(folder_path)
    
    # Check for audio
    # Usually song.mp3 or visuals/vocals.wav depending on what we want to play.
    # The user wants to listen to the song or stems. The existing players played 'song.mp3' or 'vocals.wav'.
    # In manual folders we copied 'song.mp3'. In Demucs/SAM folders we have 'song.mp3'.
    # For splitting, we rely on song.mp3 usually.
    audio_file = folder / "song.mp3"
    audio_rel = ""
    if audio_file.exists():
        audio_rel = f"{folder.name}/song.mp3"
    else:
        # Fallback to separated/htdemucs/song/vocals.mp3 if song.mp3 missing?
        # Let's try to find *any* audio.
        # But logically, song.mp3 should be there.
        pass

    # Read Structure
    structure_file = folder / "song_structure.json"
    structure = []
    if structure_file.exists():
        try:
            with open(structure_file, 'r') as f:
                structure = json.load(f)
        except:
            pass

    # 1. Player Section
    if audio_rel:
        html += f"""
        <div class="player-section">
            <audio id="audio-{col_id}" controls>
                <source src="{audio_rel}" type="audio/mpeg">
            </audio>
        </div>
        """
    else:
        html += '<div class="player-section" style="color:#f44">Audio Missing</div>'

    # 2. Metrics (Count)
    html += f'<div class="metrics">{len(structure)} Segments Identified</div>'

    # 3. Segments List
    html += f'<div class="segments-list" id="segments-{col_id}">'
    for seg in structure:
        start = seg.get('start', 0)
        end = seg.get('end', 0)
        label = seg.get('label', 'Unknown')
        dur = end - start
        
        onclick = f"{col_id}Player.playSegment({start}, {end}, this)"
        
        html += f"""
        <div class="segment" onclick="{onclick}">
            <span class="label">{label}</span>
            <span class="time">{format_time(start)} - {format_time(end)}</span>
        </div>
        """
    html += '</div>' # End list

    html += '</div>' # End Col
    return html

def generate_comparison_pages():
    base_path = Path(r"c:\Users\admin\Desktop\song analysis")
    
    # 1. Group Songs
    grouped_songs = {} # { "Display Title": { "Manual": path, "Demucs": path, "SAM": path } }
    
    for item in base_path.iterdir():
        if item.is_dir():
            name = item.name
            
            # Identify variant
            variant = None
            title_key = None
            
            if name.endswith("_Manual"):
                variant = "Manual"
                title_key = name[:-7]
            elif name.endswith("_Demucs"):
                variant = "Demucs"
                title_key = name[:-7]
            elif name.endswith("_SAM"):
                variant = "SAM"
                title_key = name[:-4]
            else:
                # Might be other folders or originals without suffix? 
                # Assuming our pipeline is consistent with suffixes now.
                # If pure song folder, ignore or treat as raw?
                # User specifically asked for comparison of these 3.
                continue
                
            display_title = title_key.replace("_", " ").title()
            
            if display_title not in grouped_songs:
                grouped_songs[display_title] = {}
            
            grouped_songs[display_title][variant] = item

    # 2. Generate Comparison HTML for each Group
    for title, variants in grouped_songs.items():
        print(f"Generating comparison for: {title}")
        
        # Paths to pass to renderer
        manual_path = variants.get("Manual")
        demucs_path = variants.get("Demucs")
        sam_path    = variants.get("SAM")
        
        # Safe filename for the html
        safe_name = title.replace(" ", "_")
        html_filename = base_path / f"compare_{safe_name}.html"
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title} - Comparison</title>
            {CSS}
        </head>
        <body>
            <a href="index.html" class="back-link">← Back to Dashboard</a>
            <h1>{title}</h1>
            
            <div class="grid">
                {render_column("Manual", "manual-col", manual_path, base_path)}
                {render_column("Demucs", "demucs-col", demucs_path, base_path)}
                {render_column("SAM", "sam-col", sam_path, base_path)}
            </div>
            
            {JS_TEMPLATE}
        </body>
        </html>
        """
        
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

    # 3. Update Index to Point to these pages
    update_index_with_comparisons(grouped_songs, base_path)

def update_index_with_comparisons(grouped_songs, base_path):
    sorted_names = sorted(grouped_songs.keys())
    
    item_rows = ""
    for title in sorted_names:
        variants = grouped_songs[title]
        safe_name = title.replace(" ", "_")
        link = f"compare_{safe_name}.html"
        
        # Check availability for tags
        has_manual = "Manual" in variants
        has_demucs = "Demucs" in variants
        has_sam = "SAM" in variants
        
        def tag(label, active, color):
            op = "1" if active else "0.2"
            return f'<span style="color:{color}; opacity:{op}; font-size:0.8em; border:1px solid {color}; padding: 2px 6px; border-radius:4px; margin-right:5px;">{label}</span>'
            
        tags = ""
        tags += tag("MANUAL", has_manual, "#34d399")
        tags += tag("DEMUCS", has_demucs, "#f472b6")
        tags += tag("SAM", has_sam, "#818cf8")
        
        item_rows += f"""
        <a href="{link}" class="song-card">
            <div class="song-info">
                <div class="song-name">{title}</div>
                <div class="tags">{tags}</div>
            </div>
            <div class="arrow">→</div>
        </a>
        """

    index_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Indian Music Intel</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        body {{ background: #0a0a0c; color: #eee; font-family: 'Outfit', sans-serif; padding: 40px; display: flex; flex-direction: column; align-items: center; }}
        h1 {{ margin-bottom: 40px; font-weight: 300; letter-spacing: 1px; }}
        .list {{ width: 100%; max-width: 800px; display: flex; flex-direction: column; gap: 15px; }}
        .song-card {{
            background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; text-decoration: none; color: inherit;
            display: flex; justify-content: space-between; align-items: center; border: 1px solid rgba(255,255,255,0.1); transition: transform 0.2s;
        }}
        .song-card:hover {{ transform: translateY(-2px); background: rgba(255,255,255,0.08); borderColor: #6366f1; }}
        .song-name {{ font-size: 1.2em; font-weight: 600; margin-bottom: 5px; }}
        .tags {{ display: flex; }}
        .arrow {{ opacity: 0.5; }}
    </style>
</head>
<body>
    <h1>Song Analysis Dashboard</h1>
    <div class="list">
        {item_rows}
    </div>
</body>
</html>
    """
    
    with open(base_path / "index.html", "w", encoding='utf-8') as f:
        f.write(index_html)
    print("Index updated.")

if __name__ == "__main__":
    generate_comparison_pages()
