import json
import pandas as pd
from pathlib import Path

# --- Configuration ---
BASE_DIR = Path(r"c:\Users\admin\Desktop\song analysis")
DATA_DIR = BASE_DIR / "data"
METRICS_CSV = DATA_DIR / "advanced_metrics.csv"
CONFUSION_CSV = DATA_DIR / "Confusion_Proof_Log.csv"
OUTPUT_HTML = BASE_DIR / "end_to_end_dashboard.html"

def load_data():
    if not METRICS_CSV.exists():
        print("Run scripts/advanced_evaluation.py first!")
        return None, None
    metrics_df = pd.read_csv(METRICS_CSV)
    
    confusion_df = pd.DataFrame()
    if CONFUSION_CSV.exists():
        confusion_df = pd.read_csv(CONFUSION_CSV)
        
    return metrics_df, confusion_df

def generate_dashboard():
    df, confusion_df = load_data()
    if df is None: return

    # 1. Aggregations for "Executive Summary" Top Cards
    agg = df.groupby("Model").agg({
        "vocal_F1@0.5": "mean",
        "mean_iou": "mean",
        "fpr_time": "mean",
        "bound_acc_1s": "mean"
    }).to_dict('index')

    dem = agg.get('Demucs', {})
    sam = agg.get('SAM', {})

    # 2. Charts Data (JSON for Chart.js)
    # Pivot for Side-by-Side Bar Charts
    chart_df = df.pivot(index='Song', columns='Model', values=['vocal_F1@0.5', 'mean_iou', 'fpr_time']).fillna(0)
    
    songs = list(chart_df.index)
    
    chart_data = {
        "labels": songs,
        "demucs_f1": chart_df[('vocal_F1@0.5', 'Demucs')].tolist(),
        "sam_f1": chart_df[('vocal_F1@0.5', 'SAM')].tolist(),
        "demucs_iou": chart_df[('mean_iou', 'Demucs')].tolist(),
        "sam_iou": chart_df[('mean_iou', 'SAM')].tolist(),
        "demucs_fpr": chart_df[('fpr_time', 'Demucs')].tolist(),
        "sam_fpr": chart_df[('fpr_time', 'SAM')].tolist(),
    }

    # 3. HTML Template
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>End-to-End Segmentation Analysis</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{ --primary: #2563eb; --secondary: #db2777; --bg: #f8fafc; --card: #ffffff; --text: #1e293b; }}
        body {{ font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 40px; }}
        
        .header {{ margin-bottom: 40px; border-bottom: 1px solid #e2e8f0; padding-bottom: 20px; }}
        .header h1 {{ font-weight: 700; color: #0f172a; margin: 0; }}
        .header p {{ color: #64748b; margin-top: 8px; }}

        /* KPI Cards */
        .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; margin-bottom: 40px; }}
        .card {{ background: var(--card); padding: 24px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; }}
        .card h3 {{ margin: 0 0 10px 0; font-size: 13px; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600; }}
        .card .big-num {{ font-size: 32px; font-weight: 700; color: #0f172a; display: flex; align-items: baseline; gap: 8px; }}
        .card .diff {{ font-size: 14px; font-weight: 500; padding: 2px 8px; border-radius: 99px; }}
        .diff.positive {{ background: #dcfce7; color: #166534; }}
        .diff.negative {{ background: #fee2e2; color: #991b1b; }}

        /* Charts Section */
        .charts-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 40px; }}
        .chart-container {{ background: var(--card); padding: 24px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; height: 320px; }}
        h2 {{ font-size: 18px; font-weight: 600; margin-bottom: 20px; }}

        /* Table Section */
        .table-container {{ background: var(--card); border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; overflow: hidden; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
        th {{ background: #f1f5f9; padding: 12px 16px; text-align: left; font-weight: 600; color: #475569; }}
        td {{ padding: 12px 16px; border-bottom: 1px solid #e2e8f0; }}
        tr:last-child td {{ border-bottom: none; }}
        
        .winner {{ color: #166534; font-weight: 600; }}
        .loser {{ color: #991b1b; }}
    </style>
</head>
<body>

    <div class="header">
        <h1>End-to-End Segmentation Analysis</h1>
        <p>Quantitative Evaluation of Demucs vs SAM based on Hungarian Matching & IoU > 0.5</p>
    </div>

    <!-- Executive Summary KPIs -->
    <div class="kpi-grid">
        <div class="card">
            <h3>Vocal Accuracy (F1)</h3>
            <div class="big-num">
                {dem.get('vocal_F1@0.5', 0):.2f}
                <span class="diff positive" title="Demucs vs SAM">vs {sam.get('vocal_F1@0.5', 0):.2f}</span>
            </div>
            <p style="font-size:12px; color:#64748b; margin:5px 0 0;">Demucs is {(dem.get('vocal_F1@0.5', 0) / (sam.get('vocal_F1@0.5', 0.001) + 0.0001)):.1f}x more accurate</p>
        </div>

        <div class="card">
            <h3>Alignment Quality (IoU)</h3>
            <div class="big-num">
                {dem.get('mean_iou', 0):.2f} 
                <span class="diff positive">vs {sam.get('mean_iou', 0):.2f}</span>
            </div>
            <p style="font-size:12px; color:#64748b; margin:5px 0 0;">Avg Overlap with Ground Truth</p>
        </div>

        <div class="card">
            <h3>Instrumental Confusion</h3>
            <div class="big-num">
                { sam.get('fpr_time', 0):.1%}
                <span class="diff negative">High Risk</span>
            </div>
            <p style="font-size:12px; color:#64748b; margin:5px 0 0;">Time SAM predicts vocal during instrumental</p>
        </div>
        
        <div class="card">
            <h3>Perfect Boundaries (<1s)</h3>
            <div class="big-num">
                {dem.get('bound_acc_1s', 0):.1%}
                <span class="diff positive">vs {sam.get('bound_acc_1s', 0):.1%}</span>
            </div>
            <p style="font-size:12px; color:#64748b; margin:5px 0 0;">% of segments within 1s tolerance</p>
        </div>
    </div>

    <!-- Charts -->
    <div class="charts-grid">
        <div class="chart-container">
            <h2>F1 Score per Song (Structure Integrity)</h2>
            <canvas id="f1Chart"></canvas>
        </div>
        <div class="chart-container">
            <h2>Instrumental Confusion (False Positive Rate)</h2>
            <canvas id="fprChart"></canvas>
        </div>
    </div>

    <!-- Visual Proof: Top Hallucinations -->
    <div class="table-container" style="margin-bottom: 40px;">
        <div style="padding: 16px; border-bottom: 1px solid #e2e8f0; display:flex; justify-content:space-between; align-items:center;">
             <h2 style="margin:0; color:#b91c1c;">Visual Proof: Top Hallucinations (Instrumental as Vocals)</h2>
             <span style="font-size:12px; color:#64748b;">Forensic Evidence from Confusion Logs</span>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Song</th>
                    <th>Model</th>
                    <th>What Human Heard (Truth)</th>
                    <th>Conflict Time</th>
                    <th>False Vocal Duration</th>
                    <th>Severity</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Generate Confusion Rows
    if not confusion_df.empty:
        top_confusions = confusion_df.sort_values(by="Confused Duration (s)", ascending=False).head(10)
        
        for _, row in top_confusions.iterrows():
            model = row['Model']
            badge_color = "#fecaca" if model == 'SAM' else "#bfdbfe"
            text_color = "#991b1b" if model == 'SAM' else "#1e40af"
            
            html += f"""
            <tr>
                <td style="font-weight:600;">{row['Song']}</td>
                <td><span style="background:{badge_color}; color:{text_color}; padding:4px 8px; border-radius:4px; font-weight:600; font-size:12px;">{model}</span></td>
                <td>{row['Ground Truth Segment']}</td>
                <td>{row['GT Start']}s - {row['GT End']}s</td>
                <td>
                    <a href="#" onclick="inspectSegment('{row['Song']}', '{model}', {row['Conflict Start']}, {row['Conflict End']}); return false;" 
                       style="color:#b91c1c; font-weight:bold; text-decoration:underline; cursor:pointer;"
                       title="Click to Audit this Error in the Timeline">
                       {row['Confused Duration (s)']}s
                    </a>
                </td>
                <td><span style="background:#fee2e2; color:#b91c1c; padding:2px 6px; border-radius:99px; font-size:11px;">HIGH RISK</span></td>
            </tr>
            """
    else:
        html += "<tr><td colspan='6' style='text-align:center; padding:20px;'>No significant hallucinations detected.</td></tr>"

    html += """
            </tbody>
        </table>
    </div>

    <!-- Detailed Table -->
    <div class="table-container">
        <div style="padding: 16px; border-bottom: 1px solid #e2e8f0;">
             <h2 style="margin:0;">Detailed Song Performance</h2>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Song</th>
                    <th>Model</th>
                    <th>F1 Score</th>
                    <th>Mean IoU</th>
                    <th>Precision</th>
                    <th>Recall</th>
                    <th>Error Rate (FPR)</th>
                    <th>Boundary Error (s)</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Generate Table Rows
    # Sort by Song then Model for easy comparison
    sorted_df = df.sort_values(by=['Song', 'Model'])
    
    for _, row in sorted_df.iterrows():
        model = row['Model']
        color = "#1e293b"
        if model == 'Demucs': color = "#2563eb" # Blue
        elif model == 'SAM': color = "#db2777" # Pink
        
        # Determine color for FPR (Red if high)
        fpr = row.get('fpr_time', 0)
        fpr_style = "color:#b91c1c; font-weight:bold;" if fpr > 0.05 else "color:#166534;"
        
        html += f"""
        <tr>
            <td>{row['Song']}</td>
            <td style="color:{color}; font-weight:600;">{model}</td>
            <td>{row['vocal_F1@0.5']:.3f}</td>
            <td>{row['mean_iou']:.2f}</td>
            <td>{row['vocal_P@0.5']:.2f}</td>
            <td>{row['vocal_R@0.5']:.2f}</td>
            <td style="{fpr_style}">{fpr:.1%}</td>
            <td>{row.get('avg_start_err', 999):.1f}s</td>
        </tr>
        """

    # Helper for "AI Insights"
    def generate_analyst_comment(seg, model, manual_segs):
        if model == "Manual":
            return "REFERENCE GROUND TRUTH: This is the verified manual label by human annotators."
            
        # 1. Check for Hallucinations (Overlap with Instrumental)
        intruders = []
        for m in manual_segs:
            # Check if Manual is Instrumental/Interlude
            label = (m.get('label', '') or '').lower()
            m_type = (m.get('type', '') or '').lower()
            is_noise = 'inst' in label or 'interlude' in label or m_type == 'instrumental'
            
            if is_noise:
                # Calc Overlap
                start = max(seg['start'], m['start'])
                end = min(seg['end'], m['end'])
                if end > start:
                    intruders.append(end - start)
        
        total_overlap = sum(intruders)
        seg_len = seg['end'] - seg['start']
        
        if total_overlap > 0.5 * seg_len:
             return f"⚠️ <b>CRITICAL ERROR (Hallucination)</b><br>The <b>{model}</b> model hallucinated vocals here for <b>{total_overlap:.1f}s</b>.<br><i>ANALYSIS:</i> This region is labeled as 'Instrumental' in Ground Truth. The model likely confused melodic instruments (e.g., Violin, Synth) for human voice."

        # 2. Check for Alignment (IoU) with Vocal Matches
        vocal_matches = []
        for m in manual_segs:
             if 'instrumental' not in (m.get('type') or 'vocal'):
                s = max(seg['start'], m['start'])
                e = min(seg['end'], m['end'])
                if e > s:
                    union = (seg['end'] - seg['start']) + (m['end'] - m['start']) - (e - s)
                    iou = (e - s) / union
                    vocal_matches.append(iou)
        
        best_iou = max(vocal_matches) if vocal_matches else 0
        
        if best_iou > 0.8:
            return f"✅ <b>EXCELLENT MATCH (IoU: {best_iou:.2f})</b><br><b>{model}</b> perfectly aligned with the ground truth vocals.<br><i>ANALYSIS:</i> Clear vocal isolation achieved."
        elif best_iou > 0.4:
             return f"⚠️ <b>BOUNDARY JITTER (IoU: {best_iou:.2f})</b><br><b>{model}</b> detected the vocals but missed the precise start/end points.<br><i>ANALYSIS:</i> Likely caused by breathing sounds or fade-ins."
        else:
             return f"❌ <b>GHOST SEGMENT</b><br><b>{model}</b> predicted a segment that barely overlaps with any known vocal.<br><i>ANALYSIS:</i> Possible background noise or crowd noise misclassification."

    # 4. Load Detailed Segment Data for Visualization
    songs_data = {}
    manual_folders = list(DATA_DIR.glob("*_Manual"))
    
    for m_folder in manual_folders:
        s_name = m_folder.name.replace("_Manual", "")
        
        # Audio Path (Relative to Dashboard)
        # Try Manual first
        audio_path = ""
        if (m_folder / "song.mp3").exists():
            audio_path = f"data/{m_folder.name}/song.mp3"
        else:
            # Try others
            for v in ["_Demucs", "_SAM"]:
                if (DATA_DIR / f"{s_name}{v}" / "song.mp3").exists():
                    audio_path = f"data/{s_name}{v}/song.mp3"
                    break
        
        # Segments
        segments = {}
        # Pre-load manual for comparison
        manual_data = []
        p_manual = DATA_DIR / f"{s_name}_Manual" / "song_structure.json"
        if p_manual.exists():
            try: manual_data = json.load(open(p_manual, 'r'))
            except: pass

        for variant in ["Manual", "Demucs", "SAM"]:
            suffix = f"_{variant}" if variant != "Manual" else "_Manual"
            p = DATA_DIR / f"{s_name}{suffix}" / "song_structure.json"
            if p.exists():
                 try:
                    with open(p, 'r') as f:
                        raw_segs = json.load(f)
                        # Enrich with AI Insight
                        for s in raw_segs:
                            s['insight'] = generate_analyst_comment(s, variant, manual_data)
                        segments[variant] = raw_segs
                 except: segments[variant] = []
        
        songs_data[s_name] = {
            "audio": audio_path,
            "segments": segments
        }

    html += """
        </tbody>
    </table>
    </div>
    
    <!-- Interactive Detail Modal/Section -->
    <div id="interactiveSection" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.8); z-index:100; padding:40px; box-sizing:border-box; overflow-y:auto;">
        <div style="background:white; border-radius:12px; max-width:1000px; margin:0 auto; padding:30px; position:relative;">
            <button onclick="closeModal()" style="position:absolute; top:20px; right:20px; border:none; background:#f1f5f9; padding:8px 12px; border-radius:6px; cursor:pointer;">Close ✕</button>
            <h2 id="modalTitle">Analysis</h2>
            
            <!-- Audio Player -->
            <div style="background:#f8fafc; padding:20px; border-radius:8px; margin-bottom:20px; display:flex; gap:20px; align-items:center;">
                <div style="width:50px; height:50px; background:#2563eb; color:white; border-radius:50%; display:flex; align-items:center; justify-content:center;">▶</div>
                <div style="flex-grow:1;">
                    <div style="font-weight:600; margin-bottom:5px;">Master Audio Track</div>
                    <audio id="mainAudio" controls style="width:100%"></audio>
                </div>
            </div>

            <!-- AI Analyst Console -->
            <div id="aiConsoleBox" style="background:#1e293b; color:#f8fafc; padding:20px; border-radius:8px; margin-bottom:20px; min-height:80px; border-left: 5px solid #60a5fa; font-family:'Courier New', monospace;">
                <div style="font-size:11px; text-transform:uppercase; letter-spacing:1px; color:#94a3b8; margin-bottom:8px;">🤖 AI Forensic Analyst</div>
                <div id="aiConsole" style="font-size:14px; line-height:1.5;">Select a segment on the timeline to analyze its performance metrics...</div>
            </div>

            <!-- Timeline -->
            <div style="height:400px; margin-bottom:20px;">
                <canvas id="timelineChart"></canvas>
            </div>
            
            <div style="font-size:12px; color:#64748b; text-align:center; display:flex; justify-content:center; gap:15px; flex-wrap:wrap;">
                <span style="display:flex; align-items:center;"><span style="width:12px; height:12px; background:#8b5cf6; margin-right:5px; border-radius:2px;"></span>Pallavi</span>
                <span style="display:flex; align-items:center;"><span style="width:12px; height:12px; background:#10b981; margin-right:5px; border-radius:2px;"></span>Anupallavi</span>
                <span style="display:flex; align-items:center;"><span style="width:12px; height:12px; background:#f97316; margin-right:5px; border-radius:2px;"></span>Charanam</span>
                <span style="display:flex; align-items:center;"><span style="width:12px; height:12px; background:#06b6d4; margin-right:5px; border-radius:2px;"></span>Intro/Outro</span>
                <span style="display:flex; align-items:center;"><span style="width:12px; height:12px; background:#3b82f6; margin-right:5px; border-radius:2px;"></span>Vocals (Generic)</span>
                <span style="display:flex; align-items:center;"><span style="width:12px; height:12px; background:#94a3b8; margin-right:5px; border-radius:2px;"></span>Instrumental</span>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script>
    <script>
        const data = """ + json.dumps(chart_data) + """;
        const songsData = """ + json.dumps(songs_data) + """;
        let timelineChart = null;

        // Chart Config
        const commonOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'top' } },
            scales: { y: { beginAtZero: true } }
        };

        // 1. F1 Chart
        new Chart(document.getElementById('f1Chart'), {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [
                    { label: 'Demucs', data: data.demucs_f1, backgroundColor: '#2563eb', borderRadius: 4 },
                    { label: 'SAM', data: data.sam_f1, backgroundColor: '#db2777', borderRadius: 4 }
                ]
            },
            options: { ...commonOptions, scales: { y: { max: 1 } } }
        });

        // 2. FPR Chart
        new Chart(document.getElementById('fprChart'), {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [
                    { label: 'Demucs', data: data.demucs_fpr, backgroundColor: '#93c5fd', borderRadius: 4 },
                    { label: 'SAM', data: data.sam_fpr, backgroundColor: '#fca5a5', borderRadius: 4 }
                ]
            },
            options: { ...commonOptions, scales: { y: { ticks: { callback: v => (v*100) + '%' } } } }
        });

        // INTERACTIVITY
        let activeChart = null; // Track current chart for updates
        
        function selectSong(songName) {
            const data = songsData[songName];
            if(!data) return;
            
            document.getElementById('interactiveSection').style.display = 'block';
            document.getElementById('modalTitle').innerText = songName + " - Segment Visualization";
            
            // Audio
            const audio = document.getElementById('mainAudio');
            audio.src = data.audio;
            audio.load();
            
            // Timeline
            renderTimeline(data.segments);
            
            // Sync Timeline Highlighting
            audio.ontimeupdate = () => updateTimelineHighlight(audio.currentTime);
        }
        
        function updateTimelineHighlight(currentTime) {
            if(!timelineChart) return;
            
            let needsUpdate = false;
            
            timelineChart.data.datasets.forEach((ds, dsIndex) => {
                const meta = timelineChart.getDatasetMeta(dsIndex);
                
                // Initialize original colors if not saved
                if (!ds.origColors) {
                    ds.origColors = [...ds.backgroundColor];
                    ds.origBorderWidth = ds.borderWidth;
                }
                
                const bgColors = [...ds.origColors];
                const borderWidths = new Array(ds.data.length).fill(2);
                const borderColors = new Array(ds.data.length).fill('#ffffff');
                
                ds.data.forEach((point, idx) => {
                    const start = point.x[0];
                    const end = point.x[1];
                    
                    if (currentTime >= start && currentTime <= end) {
                        // HIGHLIGHT ACTIVE SEGMENT
                        // Use a bright yellow/gold for high visibility
                        bgColors[idx] = '#facc15'; // Yellow-400
                        borderColors[idx] = '#ca8a04'; // Darker Yellow border
                        borderWidths[idx] = 4;
                        needsUpdate = true;
                    } 
                });
                
                // Apply updates if changed
                // Optimization: In a real app we'd check if it actually changed to avoid churn
                // But for this demo, we just assign.
                ds.backgroundColor = bgColors;
                ds.borderColor = borderColors;
                ds.borderWidth = borderWidths;
            });
            
            timelineChart.update('none'); // Efficient update (no animation)
        }
        
        function closeModal() {
            document.getElementById('interactiveSection').style.display = 'none';
            const audio = document.getElementById('mainAudio');
            audio.pause();
            audio.ontimeupdate = null; // Cleanup
        }

        function getSegmentColor(label, type) {
            const l = (label || "").toLowerCase();
            const t = (type || "").toLowerCase();
            
            // Instrumentals
            if(l.includes('inst') || l.includes('interlude') || l.includes('music') || l.includes('bgm') || t === 'instrumental') return '#94a3b8';
            
            // Structural Elements
            if(l.includes('pallavi') && !l.includes('anu')) return '#8b5cf6'; // Purple
            if(l.includes('anu')) return '#10b981'; // Emerald (Anupallavi)
            if(l.includes('charanam') || l.includes('verse')) return '#f97316'; // Orange
            if(l.includes('intro') || l.includes('outro')) return '#06b6d4'; // Cyan
            
            // Default Vocals
            return '#3b82f6'; // Blue
        }

        function renderTimeline(segments) {
            const ctx = document.getElementById('timelineChart').getContext('2d');
            if(timelineChart) timelineChart.destroy();
            
            const datasets = [];
            
            ['Manual', 'Demucs', 'SAM'].forEach((model, idx) => {
                const segs = segments[model] || [];
                
                const dataPoints = [];
                const bgColors = [];
                const borderColors = [];

                segs.forEach(s => {
                    dataPoints.push({
                        x: [s.start, s.end],
                        y: model,
                        label: s.label || s.type,
                        insight: s.insight
                    });

                    // Set Color based on Semantic Label
                    const color = getSegmentColor(s.label, s.type);
                    bgColors.push(color);
                    
                    // Always White Separator
                    borderColors.push('#ffffff');
                });
                
                datasets.push({
                    label: model,
                    data: dataPoints,
                    backgroundColor: bgColors,
                    borderColor: borderColors,
                    borderWidth: 2,
                    borderSkipped: false,
                    barPercentage: 0.7,
                    categoryPercentage: 0.8,
                    borderRadius: 4
                });
            });

            timelineChart = new Chart(ctx, {
                type: 'bar', // We use bar chart
                data: {
                    labels: ['Manual', 'Demucs', 'SAM'],
                    datasets: datasets
                },
                options: {
                    indexAxis: 'y', // Horizontal bars
                    responsive: true,
                    maintainAspectRatio: false,
                    onClick: (e, elements) => {
                         if (!elements || elements.length === 0) return;
                         
                         const el = elements[0];
                         const dsIdx = el.datasetIndex;
                         const dataIdx = el.index;
                         
                         // Get data point from the original array
                         // Note: Chart.js datasets structure
                         const ds = datasets[dsIdx];
                         const point = ds.data[dataIdx]; // This holds x, y, label, insight
                         
                         if(point && point.x) {
                             playSegment(point.x[0], point.x[1]);
                             
                             // Update AI Console
                             const consoleEl = document.getElementById('aiConsole');
                             const insight = point.insight || "No analysis available for this segment.";
                             
                             consoleEl.innerHTML = `
                                <div style="margin-bottom:5px; color:#cbd5e1;"><b>Segment:</b> ${point.label} (${point.x[0].toFixed(1)}s - ${point.x[1].toFixed(1)}s)</div>
                                <div>${insight}</div>
                             `;
                         }
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const d = context.raw;
                                    return `▶ Click to Play | ${d.label}: ${d.x[0].toFixed(1)}s - ${d.x[1].toFixed(1)}s`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            type: 'linear',
                            position: 'bottom',
                            title: { display: true, text: 'Time (seconds)' }
                        }
                    }
                }
            });
        }
        
        // Audio Playback Logic
        let stopTimer = null;
        
        function playSegment(start, end) {
            const audio = document.getElementById('mainAudio');
            
            // Clear previous stop
            if (stopTimer) clearTimeout(stopTimer);
            
            audio.currentTime = start;
            audio.play();
            
            const durationMs = (end - start) * 1000;
            
            // Toast / Visual Feedback?
            console.log(`Playing segment: ${start}s -> ${end}s`);
            
            stopTimer = setTimeout(() => {
                audio.pause();
            }, durationMs);
        }
        
        // Add click handlers to table rows
        document.addEventListener('DOMContentLoaded', () => {
            const rows = document.querySelectorAll('tbody tr');
            rows.forEach(row => {
                const songCell = row.cells[0]; // First cell is Song Name usually
                if(songCell) {
                    row.style.cursor = 'pointer';
                    row.title = 'Click to Visualize';
                    row.onclick = () => selectSong(songCell.innerText.trim());
                    
                    // Hover effect
                    row.onmouseover = () => row.style.background = '#f1f5f9';
                    row.onmouseout = () => row.style.background = 'transparent';
                }
            });
        });
        function inspectSegment(songName, model, start, end) {
            // 1. Open Modal
            selectSong(songName);
            
            // 2. Wait for Chart Render
            setTimeout(() => {
                const chart = Chart.getChart("timelineChart");
                if(!chart) return;
                
                // Map model name to dataset index
                // 0=Manual, 1=Demucs, 2=SAM (based on order in renderTimeline)
                let dsIdx = 0;
                if(model === 'Demucs') dsIdx = 1;
                if(model === 'SAM') dsIdx = 2;
                
                const ds = chart.data.datasets[dsIdx];
                if(!ds) return;
                
                // Find matching segment (Approximate check)
                const point = ds.data.find(d => 
                    Math.abs(d.x[0] - start) < 1.0 && Math.abs(d.x[1] - end) < 1.0
                ) || ds.data.find(d => 
                    // Fallback: Check if point contains the conflict range
                    d.x[0] <= start && d.x[1] >= end
                );
                
                if (point) {
                    playSegment(point.x[0], point.x[1]);
                    
                    const consoleEl = document.getElementById('aiConsole');
                    const insight = point.insight || "No analysis available.";
                    
                    consoleEl.innerHTML = `
                        <div style="border-left: 3px solid #ef4444; padding-left: 10px;">
                            <div style="margin-bottom:5px; color:#fca5a5; font-weight:bold;">🚨 AUDITING ERROR: ${model}</div>
                            <div style="margin-bottom:5px; color:#cbd5e1;"><b>Segment:</b> ${point.label} (${point.x[0].toFixed(1)}s - ${point.x[1].toFixed(1)}s)</div>
                            <div>${insight}</div>
                        </div>
                    `;
                } else {
                    console.log("Segment not found for auto-inspection");
                }
            }, 800);
        }
    </script>
</body>
</html>
    """
    
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"End-to-End Dashboard generated: {OUTPUT_HTML}")

if __name__ == "__main__":
    generate_dashboard()
