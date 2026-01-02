import os
from pathlib import Path

def generate_index():
    base_path = Path(r"c:\Users\admin\Desktop\song analysis")
    songs = []
    
    # Scan for directories containing song_player.html
    for item in base_path.iterdir():
        if item.is_dir():
            player_file = item / "song_player.html"
            if player_file.exists():
                # Clean up folder name for display
                display_name = item.name.replace("_", " ").title()
                songs.append({
                    "name": display_name,
                    "path": f"{item.name}/song_player.html",
                    "id": item.name
                })
    
    songs.sort(key=lambda x: x["name"])

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
            --accent: #6366f1;
            --accent-glow: rgba(99, 102, 241, 0.4);
            --text: #f8fafc;
            --text-dim: #94a3b8;
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
            margin-bottom: 60px;
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

        .song-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 24px;
            width: 100%;
            max-width: 1200px;
            animation: fadeInUp 0.8s ease-out 0.2s both;
        }}

        .song-card {{
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 24px;
            text-decoration: none;
            color: inherit;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}

        .song-card:hover {{
            transform: translateY(-8px);
            background: rgba(255, 255, 255, 0.08);
            border-color: var(--accent);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), 0 0 20px var(--accent-glow);
        }}

        .song-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(
                90deg,
                transparent,
                rgba(255, 255, 255, 0.05),
                transparent
            );
            transition: 0.5s;
        }}

        .song-card:hover::before {{
            left: 100%;
        }}

        .song-name {{
            font-size: 1.4rem;
            font-weight: 600;
            margin-bottom: 8px;
            color: #fff;
        }}

        .status-tag {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 100px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            background: rgba(16, 185, 129, 0.1);
            color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.2);
            align-self: flex-start;
        }}

        .action-text {{
            margin-top: 20px;
            font-size: 0.9rem;
            color: var(--accent);
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 600;
        }}

        .action-text svg {{
            transition: transform 0.3s ease;
        }}

        .song-card:hover .action-text svg {{
            transform: translateX(4px);
        }}

        @keyframes fadeInDown {{
            from {{ opacity: 0; transform: translateY(-20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Responsive Grid Adjustments */
        @media (max-width: 640px) {{
            h1 {{ font-size: 2rem; }}
            .song-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>Indian Music Intel</h1>
        <p class="subtitle">Premium Audio Segmentation & Lyric Analysis Dashboard</p>
    </header>

    <div class="song-grid">
"""
    
    for song in songs:
        html_content += f"""
        <a href="{song['path']}" class="song-card">
            <div>
                <div class="status-tag">Ready</div>
                <div class="song-name">{song['name']}</div>
            </div>
            <div class="action-text">
                Browse Structure 
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                    <polyline points="12 5 19 12 12 19"></polyline>
                </svg>
            </div>
        </a>
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
