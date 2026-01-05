import os
from pathlib import Path

def generate_index():
    base_path = Path(r"c:\Users\admin\Desktop\song analysis")
    
    # Structure: { "Song Name": { "SAM": path, "Demucs": path, "Manual": path } }
    grouped_songs = {}

    # Scan directories
    for item in base_path.iterdir():
        if item.is_dir():
            player_file = item / "song_player.html"
            if player_file.exists():
                folder_name = item.name
                
                # Determine Type and Base Name
                version_type = "Original"
                base_name = folder_name
                
                if folder_name.endswith("_SAM"):
                    version_type = "SAM"
                    base_name = folder_name[:-4]
                elif folder_name.endswith("_Demucs"):
                    version_type = "Demucs"
                    base_name = folder_name[:-7]
                elif folder_name.endswith("_Manual"):
                    version_type = "Manual"
                    base_name = folder_name[:-7]
                
                # Normalize Title (replace underscores)
                display_title = base_name.replace("_", " ").title()
                
                if display_title not in grouped_songs:
                    grouped_songs[display_title] = {}
                
                grouped_songs[display_title][version_type] = f"{folder_name}/song_player.html"

    # Sort songs alphabetically
    sorted_song_names = sorted(grouped_songs.keys())

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Indian Music Analysis Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #0a0a0c;
            --card-bg: rgba(255, 255, 255, 0.05);
            --header-bg: rgba(0, 0, 0, 0.3);
            --text: #f8fafc;
            --text-dim: #94a3b8;
            
            --sam-color: #818cf8;
            --demucs-color: #f472b6;
            --manual-color: #34d399;
        }}

        body {{
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 40px 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(99, 102, 241, 0.1) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(236, 72, 153, 0.1) 0%, transparent 40%);
        }}

        header {{
            text-align: center;
            margin-bottom: 40px;
            animation: fadeInDown 0.8s ease-out;
        }}

        h1 {{
            font-size: 3rem;
            font-weight: 600;
            margin: 0;
            background: linear-gradient(135deg, #fff 0%, #94a3b8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.02em;
        }}

        p.subtitle {{
            color: var(--text-dim);
            font-size: 1.1rem;
            margin-top: 10px;
        }}

        .table-container {{
            width: 100%;
            max-width: 1200px;
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            overflow: hidden;
            animation: fadeInUp 0.8s ease-out 0.2s both;
        }}

        .grid-header {{
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1fr; /* Song Name | Manual | Demucs | SAM */
            padding: 20px 24px;
            background: var(--header-bg);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            font-weight: 600;
            color: var(--text-dim);
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 0.05em;
        }}

        .grid-row {{
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1fr;
            padding: 20px 24px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            align-items: center;
            transition: background 0.2s;
        }}

        .grid-row:last-child {{
            border-bottom: none;
        }}

        .grid-row:hover {{
            background: rgba(255, 255, 255, 0.03);
        }}

        .song-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #fff;
        }}

        .version-cell {{
            display: flex;
            align-items: center;
        }}

        .version-btn {{
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 500;
            transition: all 0.2s;
            border: 1px solid transparent;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 120px; /* Fixed width for alignment */
            text-align: center;
        }}

        .version-btn:hover {{
            transform: translateY(-2px);
        }}

        /* Manual Style */
        .btn-manual {{
            background: rgba(16, 185, 129, 0.1);
            color: var(--manual-color);
            border-color: rgba(16, 185, 129, 0.2);
        }}
        .btn-manual:hover {{
            background: rgba(16, 185, 129, 0.2);
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
        }}

        /* Demucs Style */
        .btn-demucs {{
            background: rgba(236, 72, 153, 0.1);
            color: var(--demucs-color);
            border-color: rgba(236, 72, 153, 0.2);
        }}
        .btn-demucs:hover {{
            background: rgba(236, 72, 153, 0.2);
            box-shadow: 0 4px 12px rgba(236, 72, 153, 0.2);
        }}

        /* SAM Style */
        .btn-sam {{
            background: rgba(99, 102, 241, 0.1);
            color: var(--sam-color);
            border-color: rgba(99, 102, 241, 0.2);
        }}
        .btn-sam:hover {{
            background: rgba(99, 102, 241, 0.2);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
        }}
        
        .btn-disabled {{
            opacity: 0.1;
            cursor: default;
            filter: grayscale(1);
            border: 1px solid rgba(255,255,255,0.05);
            background: transparent;
            color: var(--text-dim);
        }}
        .btn-disabled:hover {{
            transform: none;
            box-shadow: none;
            background: transparent;
        }}

        @keyframes fadeInDown {{
            from {{ opacity: 0; transform: translateY(-20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        @media (max-width: 768px) {{
            .grid-header {{ display: none; }}
            .grid-row {{
                grid-template-columns: 1fr;
                gap: 12px;
                text-align: center;
            }}
            .version-cell {{ justify-content: center; }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>Indian Music Intel</h1>
        <p class="subtitle">Comparison Dashboard: Manual vs Demucs vs SAM</p>
    </header>

    <div class="table-container">
        <div class="grid-header">
            <div>Song Title</div>
            <div>Manual</div>
            <div>Demucs</div>
            <div>SAM</div>
        </div>
"""

    for name in sorted_song_names:
        versions = grouped_songs[name]
        
        # Helper to generate button or placeholder
        def get_btn(v_type, css_class, label):
            if v_type in versions:
                return f'<a href="{versions[v_type]}" class="version-btn {css_class}">{label}</a>'
            else:
                 return f'<span class="version-btn {css_class} btn-disabled">N/A</span>'

        html_content += f"""
        <div class="grid-row">
            <div class="song-title">{name}</div>
            <div class="version-cell">{get_btn("Manual", "btn-manual", "Open Analysis")}</div>
            <div class="version-cell">{get_btn("Demucs", "btn-demucs", "Open Analysis")}</div>
            <div class="version-cell">{get_btn("SAM", "btn-sam", "Open Analysis")}</div>
        </div>
"""

    html_content += """
    </div>
</body>
</html>
"""

    with open(base_path / "index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated index.html at {base_path / 'index.html'}")

if __name__ == "__main__":
    generate_index()
