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
        border-bottom: 1px solid var(--border);
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    .player-label { font-size: 0.8em; color: #888; margin-bottom: 4px; display: block; }
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
        border: 1px solid transparent;
    }
    .segment:hover { background: rgba(255,255,255,0.1); border-color: rgba(255,255,255,0.2); }
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

def render_column(version_name, class_name, folder_path, base_path, metrics_data=None):
    """
    Renders the HTML for a single column (Manual, Demucs, or SAM).
    """
    col_id = version_name.lower()
    
    html = f'<div class="col {class_name}">'
    
    # Header with Metrics
    stats_html = ""
    if metrics_data and "metrics" in metrics_data:
        m = metrics_data["metrics"]
        stats_html = f"""
        <div class="metric-header">
            Mean IoU: {m.get('mean_iou', 0):.2f} | FPR: {m.get('fpr', 0):.1%}
        </div>
        """
        
    html += f'<div class="col-header">{version_name}{stats_html}</div>'
    
    if not folder_path:
        html += '<div class="empty-state">Data Not Available</div>'
        html += '</div>'
        return html

    folder = Path(folder_path)
    
    # ... Finding Audio Logic (Same as before) ...
    vocals_rel = ""
    novocals_rel = ""
    sep_dir = folder / "separated"
    if sep_dir.exists():
        def find_best_audio(candidates):
            if not candidates: return None
            candidates.sort(key=lambda p: (p.suffix != '.mp3', p.name))
            return candidates[0]
            
        voc_candidates = list(sep_dir.rglob("vocals.*"))
        novoc_candidates = list(sep_dir.rglob("no_vocals.*"))
        
        best_voc = find_best_audio(voc_candidates)
        if best_voc:
             try: vocals_rel = best_voc.relative_to(base_path).as_posix()
             except: pass
            
        best_novoc = find_best_audio(novoc_candidates)
        if best_novoc:
            try: novocals_rel = best_novoc.relative_to(base_path).as_posix()
            except: pass
    
    main_audio_rel = ""
    local_song = folder / "song.mp3"
    
    if local_song.exists():
        try: main_audio_rel = local_song.relative_to(base_path).as_posix()
        except: pass
    else:
        name = folder.name
        base_name = ""
        if "_Demucs" in name: base_name = name.replace("_Demucs", "")
        elif "_SAM" in name: base_name = name.replace("_SAM", "")
        elif "_Manual" in name: base_name = name.replace("_Manual", "")
        
        if base_name:
            manual_sib = folder.parent / f"{base_name}_Manual" / "song.mp3"
            if manual_sib.exists():
                 try: main_audio_rel = manual_sib.relative_to(base_path).as_posix()
                 except: pass
            else:
                 for suffix in ["_Demucs", "_SAM", "_Manual"]:
                     sib = folder.parent / f"{base_name}{suffix}" / "song.mp3"
                     if sib.exists():
                        try: main_audio_rel = sib.relative_to(base_path).as_posix()
                        except: pass
                        break

    # Read Structure
    structure_file = folder / "song_structure.json"
    structure = []
    if structure_file.exists():
        try:
            with open(structure_file, 'r') as f:
                structure = json.load(f)
        except: pass

    # --- HTML RENDER ---
    html += '<div class="player-section">'
    
    # 1. Main Player
    if main_audio_rel:
        mime = "audio/wav"
        if main_audio_rel.endswith(".mp3"): mime = "audio/mpeg"
        html += f"""
        <div>
            <span class="player-label">Full Song (Active for Segments)</span>
            <audio id="audio-{col_id}" controls>
                <source src="{main_audio_rel}" type="{mime}">
            </audio>
        </div>
        """
    else:
        html += '<div style="color:#f44">Full Audio Missing</div>'
        
    # 2. Raw Stems
    if vocals_rel:
        v_mime = "audio/mpeg" if vocals_rel.endswith(".mp3") else "audio/wav"
        html += f"""
        <div style="margin-top:10px; border-top:1px dashed #333; padding-top:10px;">
            <span class="player-label">Raw Vocals (Stem)</span>
            <audio controls><source src="{vocals_rel}" type="{v_mime}"></audio>
        </div>
        """
        
    if novocals_rel:
        nv_mime = "audio/mpeg" if novocals_rel.endswith(".mp3") else "audio/wav"
        html += f"""
        <div>
            <span class="player-label">No Vocals (Instrumental)</span>
            <audio controls><source src="{novocals_rel}" type="{nv_mime}"></audio>
        </div>
        """
    html += '</div>' 

    # 3. Metrics
    html += f'<div class="metrics">{len(structure)} Segments Identified</div>'

    # 4. Segments List
    html += f'<div class="segments-list" id="segments-{col_id}">'
    
    # Prepare segment metrics lookups
    seg_metrics_lookup = {}
    if metrics_data and "segments" in metrics_data:
        # Index by start time (approximate) to avoid O(N^2) although N is small
        for sm in metrics_data["segments"]:
            # Rounding to 1 decimal place for matching
            k = round(sm['start'], 1)
            seg_metrics_lookup[k] = sm

    for seg in structure:
        start = seg.get('start', 0)
        end = seg.get('end', 0)
        label = seg.get('label', 'Unknown')
        dur = end - start
        
        onclick = f"{col_id}Player.playSegment({start}, {end}, this)"
        
        # Metric Badge
        badge_html = ""
        metric = seg_metrics_lookup.get(round(start, 1))
        
        # If not found exact match, try fuzzy search in list
        if not metric and metrics_data:
             for sm in metrics_data["segments"]:
                 if abs(sm['start'] - start) < 0.2:
                     metric = sm
                     break
        
        if metric:
            iou = metric['iou']
            err = metric.get('error_type')
            
            cls = "badge-gray"
            if iou > 0.7: cls = "badge-good"
            elif iou > 0.4: cls = "badge-warn"
            else: cls = "badge-bad"
            
            icon = ""
            if err == "Confusion": icon = "⚠️ "
            elif err == "Hallucination": icon = "👻 "
            
            badge_html = f'<span class="badge {cls}">{icon}IoU: {iou}</span>'

        html += f"""
        <div class="segment" onclick="{onclick}">
            <div style="display:flex; justify-content:space-between; width:100%;">
                <span class="label">{label}{badge_html}</span>
                <span class="time">{format_time(start)} - {format_time(end)}</span>
            </div>
        </div>
        """
    html += '</div>' # End list
    html += '</div>' # End Col
    return html

def generate_comparison_pages():
    base_path = Path(r"c:\Users\admin\Desktop\song analysis")
    
    # Load Metrics
    metrics_path = base_path / "data" / "quantitative_analysis.json"
    qa_data = {}
    if metrics_path.exists():
        with open(metrics_path, 'r') as f:
            qa_data = json.load(f)

    # 1. Group Songs
    grouped_songs = {}
    
    for item in (base_path / "data").iterdir():
        if item.is_dir():
            name = item.name
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
            else: continue
                
            display_title = title_key.replace("_", " ").title()
            # Store raw key too for metrics lookup
            if display_title not in grouped_songs:
                grouped_songs[display_title] = { "raw_key": title_key }
            
            grouped_songs[display_title][variant] = item

    # 2. Generate Comparison HTML
    for title, variants in grouped_songs.items():
        print(f"Generating comparison for: {title}")
        raw_key = variants.get("raw_key")
        
        manual_path = variants.get("Manual")
        demucs_path = variants.get("Demucs")
        sam_path    = variants.get("SAM")
        
        # Get metrics for this song
        song_metrics = qa_data.get(raw_key, {})
        
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
            <style>
                .badge {{ font-size: 0.7em; padding: 2px 6px; border-radius: 4px; margin-left:8px; font-weight:bold; }}
                .badge-good {{ background: #10b981; color: #fff; }}
                .badge-warn {{ background: #f59e0b; color: #fff; }}
                .badge-bad {{ background: #ef4444; color: #fff; }}
                .metric-header {{ font-size: 0.8em; color: #888; margin-top: 5px; }}
            </style>
        </head>
        <body>
            <a href="index.html" class="back-link">← Back to Dashboard</a>
            <h1>{title}</h1>
            
            <div class="grid">
                {render_column("Manual", "manual-col", manual_path, base_path, None)}
                {render_column("Demucs", "demucs-col", demucs_path, base_path, song_metrics.get("Demucs"))}
                {render_column("SAM", "sam-col", sam_path, base_path, song_metrics.get("SAM"))}
            </div>
            
            {JS_TEMPLATE}
        </body>
        </html>
        """
        
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)

    # 3. Update Index
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
