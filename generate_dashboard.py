import pandas as pd
import json
from pathlib import Path

# Config
BASE_DIR = r"c:\Users\admin\Desktop\song analysis"
DATA_FILE = Path(BASE_DIR) / "data" / "Full_Segment_Analysis.csv"
OUTPUT_HTML = Path(BASE_DIR) / "analysis_dashboard.html"

def generate_dashboard():
    # 1. Load Data
    try:
        df = pd.read_csv(DATA_FILE)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # 2. Aggregations for Charts
    # Group by Song and Model
    song_stats = df.groupby(['Song Name', 'Model']).apply(
        lambda x: pd.Series({
            'Mean_IoU': x['IoU'].mean(),
            'Vocal_FPR': (x['Error Type'].str.contains('Instrumental->Vocal', na=False).sum()) / 
                         (len(x[x['Manual Type']=='instrumental']) if len(x[x['Manual Type']=='instrumental']) > 0 else 1)
        })
    ).reset_index()

    # Pivot for Chart.js easy consumption
    # Structure: { labels: [Song1, Song2...], demucs_iou: [...], sam_iou: [...], ... }
    songs = sorted(df['Song Name'].unique())
    
    demucs_data = song_stats[song_stats['Model'] == 'Demucs'].set_index('Song Name').reindex(songs).fillna(0)
    sam_data = song_stats[song_stats['Model'] == 'SAM'].set_index('Song Name').reindex(songs).fillna(0)
    
    chart_data = {
        "labels": songs,
        "demucs_iou": demucs_data['Mean_IoU'].tolist(),
        "sam_iou": sam_data['Mean_IoU'].tolist(),
        "demucs_fpr": demucs_data['Vocal_FPR'].tolist(),
        "sam_fpr": sam_data['Vocal_FPR'].tolist()
    }

    # 3. Aggregates for Cards
    avg_demucs_iou = df[df['Model'] == 'Demucs']['IoU'].mean()
    avg_sam_iou = df[df['Model'] == 'SAM']['IoU'].mean()
    
    # FPR Aggregate
    # Calculate global FPR: Total Confusions / Total Instrumental manual segments
    def calc_global_fpr(model):
        model_df = df[df['Model'] == model]
        confusions = model_df['Error Type'].str.contains('Instrumental->Vocal', na=False).sum()
        total_instr = len(model_df[model_df['Manual Type'] == 'instrumental'])
        return confusions / total_instr if total_instr > 0 else 0

    avg_demucs_fpr = calc_global_fpr('Demucs')
    avg_sam_fpr = calc_global_fpr('SAM')

    # 4. Raw Data for Table (Convert full DF to dict)
    raw_table_data = df.to_dict(orient='records')

    # 5. HTML Template with Embedded Data & Timeline Logic
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Segmentation Analysis Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; background-color: #f8fafc; margin: 0; padding: 30px; color: #1e293b; }}
        h1, h2, h3 {{ margin: 0 0 10px 0; }}
        
        .header {{ margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center; }}
        .header h1 {{ font-weight: 700; color: #0f172a; letter-spacing: -0.5px; }}
        .header p {{ color: #64748b; margin-top: 5px; }}
        
        /* Select Box */
        .select-container select {{
            padding: 10px 16px; font-size: 16px; border-radius: 8px; border: 1px solid #cbd5e1;
            background: white; color: #334155; font-family: inherit; font-weight: 500;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05); outline: none; transition: border-color 0.2s;
        }}
        .select-container select:focus {{ border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59,130,246,0.1); }}

        /* Layout */
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 30px; }}
        .card, .chart-box, .table-container {{ background: white; padding: 24px; border-radius: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }}
        
        /* Stats Cards */
        .stat-card-group {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }}
        .stat-card {{ background: #f8fafc; padding: 16px; border-radius: 12px; }}
        .stat-card h3 {{ font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase; margin-bottom: 8px; }}
        .stat-card .value {{ font-size: 24px; font-weight: 700; color: #0f172a; }}
        .stat-card .sub {{ font-size: 13px; margin-top: 4px; font-weight: 500; }}

        /* Timeline Section */
        .timeline-box {{ grid-column: 1 / -1; height: 350px; background: white; padding: 24px; border-radius: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; margin-bottom: 30px; }}

        /* Utility Colors */
        .text-green {{ color: #10b981; }}
        .text-red {{ color: #ef4444; }}

        /* Table */
        table {{ width: 100%; border-collapse: separate; border-spacing: 0; font-size: 14px; }}
        th {{ text-align: left; padding: 16px; border-bottom: 2px solid #f1f5f9; color: #64748b; font-weight: 600; background: #fff; position: sticky; top: 0; }}
        td {{ padding: 14px 16px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }}
        tr:last-child td {{ border-bottom: none; }}
        .badge {{ padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; letter-spacing: 0.3px; }}
        .badge-red {{ background: #fecaca; color: #991b1b; }}
        .badge-yellow {{ background: #fef08a; color: #854d0e; }}
        .badge-gray {{ background: #f1f5f9; color: #475569; }}
    </style>
</head>
<body>

    <div class="header">
        <div>
            <h1>Detailed Segmentation Audit</h1>
            <p>Interactive Analysis of {len(songs)} Songs | Demucs vs SAM</p>
        </div>
        <div class="select-container">
            <select id="songSelector">
                <option value="all">Overview (All Songs)</option>
            </select>
        </div>
    </div>

    <!-- Overview Stats (Hidden when specific song selected) -->
    <div id="overviewStats" class="grid">
        <div class="chart-box" style="height:320px;">
            <canvas id="iouChart"></canvas>
        </div>
        <div class="chart-box" style="height:320px;">
            <canvas id="fprChart"></canvas>
        </div>
    </div>

    <!-- Timeline Visualizer (Shown when song selected) -->
    <div id="timelineSection" class="timeline-box" style="display:none;">
        <div style="display:flex; justify-content:space-between; margin-bottom:15px;">
            <h3>Segment Alignment Timeline</h3>
            <div style="font-size:12px; display:flex; gap:15px;">
                <span style="display:flex; align-items:center;"><span style="width:10px; height:10px; background:#3b82f6; border-radius:2px; margin-right:5px;"></span> Vocals</span>
                <span style="display:flex; align-items:center;"><span style="width:10px; height:10px; background:#94a3b8; border-radius:2px; margin-right:5px;"></span> Instrumental</span>
            </div>
        </div>
        <canvas id="timelineChart"></canvas>
    </div>

    <!-- Table -->
    <div class="table-container">
        <h3 id="tableTitle">Detailed Segment Errors</h3>
        <table id="errorTable">
            <thead>
                <tr>
                    <th>Song</th>
                    <th>Model</th>
                    <th>Manual Segment</th>
                    <th>Time Range</th>
                    <th>IoU</th>
                    <th>Error Type</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>
    </div>

    <script>
        // RAW DATA
        const chartData = {json.dumps(chart_data)};
        const rawTableData = {json.dumps(raw_table_data)};
        const songs = chartData.labels;

        // --- 1. Populate Dropdown ---
        const selector = document.getElementById('songSelector');
        songs.forEach(song => {{
            const opt = document.createElement('option');
            opt.value = song;
            opt.innerText = song;
            selector.appendChild(opt);
        }});

        // --- 2. Overview Charts (Global) ---
        let iouChart, fprChart, timelineChart;

        function initOverviewCharts() {{
            const ctxIoU = document.getElementById('iouChart').getContext('2d');
            iouChart = new Chart(ctxIoU, {{
                type: 'bar',
                data: {{
                    labels: chartData.labels,
                    datasets: [
                        {{ label: 'Demucs', data: chartData.demucs_iou, backgroundColor: '#3b82f6', borderRadius: 4 }},
                        {{ label: 'SAM', data: chartData.sam_iou, backgroundColor: '#ef4444', borderRadius: 4 }}
                    ]
                }},
                options: {{
                    maintainAspectRatio: false,
                    plugins: {{ title: {{ display: true, text: 'Mean IoU (Alignment)' }}, legend: {{ position: 'bottom' }} }},
                    scales: {{ y: {{ beginAtZero: true, max: 1 }} }}
                }}
            }});

            const ctxFPR = document.getElementById('fprChart').getContext('2d');
            fprChart = new Chart(ctxFPR, {{
                type: 'bar',
                data: {{
                    labels: chartData.labels,
                    datasets: [
                        {{ label: 'Demucs', data: chartData.demucs_fpr, backgroundColor: '#93c5fd', borderRadius: 4 }},
                        {{ label: 'SAM', data: chartData.sam_fpr, backgroundColor: '#fca5a5', borderRadius: 4 }}
                    ]
                }},
                options: {{
                    maintainAspectRatio: false,
                    plugins: {{ title: {{ display: true, text: 'Vocal False Positive Rate' }}, legend: {{ position: 'bottom' }} }},
                    scales: {{ y: {{ beginAtZero: true, ticks: {{ callback: v => (v*100)+'%' }} }} }}
                }}
            }});
        }}

        initOverviewCharts();

        // --- 3. Timeline Logic ---
        function updateTimeline(songName) {{
            const ctx = document.getElementById('timelineChart').getContext('2d');
            if (timelineChart) timelineChart.destroy();

            // Filter data for this song
            const songData = rawTableData.filter(r => r['Song Name'] === songName);
            
            // We need 3 datasets: Manual, Demucs, SAM
            // Each dataset contains bars: {{x: [start, end], y: 'Provider'}}
            
            const parseSegments = (provider, modelFilter) => {{
                let dataPoints = [];
                let seenRanges = new Set(); // Avoid duplicates in table rows if any
                
                // If provider is Manual, get unique Manual segments
                // If provider is Demucs/SAM, find prediction rows
                
                let sourceData = songData;
                if (modelFilter) sourceData = songData.filter(r => r['Model'] === modelFilter);
                
                // For Manual, we iterate the rows but filter unique manual starts
                // Manual segments are repeated for Demucs/SAM rows, so just take from one model (or all and dedupe)
                
                if (provider === 'Manual') {{
                    // Use a map to dedupe by start time
                    const map = new Map();
                    sourceData.forEach(r => {{
                        if (!map.has(r['Manual Start']) && r['Manual Start'] !== '-' && r['Manual Start'] !== null) {{
                            const isVocal = (r['Manual Type'] || '').toLowerCase().includes('vocal');
                            map.set(r['Manual Start'], {{
                                x: [r['Manual Start'], r['Manual End']],
                                y: 'Manual (Ground Truth)',
                                type: isVocal ? 'vocal' : 'instrumental',
                                label: r['Manual Segment']
                            }});
                        }}
                    }});
                    return Array.from(map.values());
                }} 
                else {{
                    // For Predictions, iterate rows where model matches
                    // Predictions are in 'Predicted Start'
                    const map = new Map();
                    sourceData.forEach(r => {{
                        if (r['Predicted Start'] !== '-' && r['Predicted Start'] !== null) {{
                            // Try to infer type if not explicitly available, but we can guess relative to manual?
                            // Actually we don't track predicted type in CSV unfortunately, only Manual Type
                            // BUT we do know: Instrumental->Vocal matches have Manual=Instr, Pred=Vocal.
                            // We might have to assume Pred type based on context or IoU match.
                            // Simplified: color Gray for now unless we know for sure.
                            // Wait, evaluate_segmentation.py did check types.
                            
                            // Let's use a trick: If it matched a "Vocal" manual segment, it's likely Vocal.
                            // If it's an insertion, we assume Vocal? (Because SAM hallucinates vocals)
                            
                            const key = r['Predicted Start'];
                            map.set(key, {{
                                x: [r['Predicted Start'], r['Predicted End']],
                                y: provider,
                                type: 'unknown', // Gray by default
                                label: 'Segment'
                            }});
                        }}
                    }});
                    return Array.from(map.values());
                }}
            }};

            const manualSegs = parseSegments('Manual');
            const demucsSegs = parseSegments('Demucs', 'Demucs');
            const samSegs = parseSegments('SAM', 'SAM');

            // Color logic
            const getColor = (type) => type === 'vocal' ? '#3b82f6' : '#94a3b8';

            timelineChart = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: ['Manual (Ground Truth)', 'Demucs', 'SAM'],
                    datasets: [
                        {{
                            label: 'Segments',
                            data: [...manualSegs, ...demucsSegs, ...samSegs],
                            backgroundColor: (ctx) => getColor(ctx.raw?.type),
                            borderColor: 'white',
                            borderWidth: 1,
                            barPercentage: 0.5
                        }}
                    ]
                }},
                options: {{
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        x: {{ type: 'linear', position: 'bottom', title: {{ display: true, text: 'Time (s)' }} }},
                        y: {{ stacked: true }} // Not strictly stacked but keeps order
                    }},
                    plugins: {{
                        tooltip: {{
                            callbacks: {{
                                label: (ctx) => `${{ctx.raw.label}}: ${{ctx.raw.x[0]}}s - ${{ctx.raw.x[1]}}s`
                            }}
                        }},
                        legend: {{ display: false }}
                    }}
                }}
            }});
        }}

        // --- 4. Table Logic ---
        function renderTable(data) {{
            const tbody = document.querySelector('#errorTable tbody');
            tbody.innerHTML = '';
            
            // If data is massive, we could slice, but for 10 songs it's fine
            const rowsToRender = data.filter(r => r.IoU !== undefined); // Simple valid row check

            rowsToRender.forEach(row => {{
                const tr = document.createElement('tr');
                
                let badge = '';
                if (row['Error Type'] && row['Error Type'] !== 'nan') {{
                     if (row['Error Type'].includes('Confusion')) badge = `<span class="badge badge-red">${{row['Error Type']}}</span>`;
                     else if (row['Error Type'].includes('Boundary')) badge = `<span class="badge badge-yellow">${{row['Error Type']}}</span>`;
                     else badge = `<span class="badge badge-gray">${{row['Error Type']}}</span>`;
                }}

                tr.innerHTML = `
                    <td>${{row['Song Name']}}</td>
                    <td><b>${{row['Model']}}</b></td>
                    <td>${{row['Manual Segment'] || '-'}}</td>
                    <td>${{row['Manual Start'] ?? row['Predicted Start']}} - ${{row['Manual End'] ?? row['Predicted End']}}</td>
                    <td>${{row['IoU'] !== undefined ? row['IoU'] : '-'}}</td>
                    <td>${{badge}}</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        // --- 5. Interaction Handler ---
        selector.addEventListener('change', (e) => {{
            const song = e.target.value;
            
            if (song === 'all') {{
                document.getElementById('overviewStats').style.display = 'grid';
                document.getElementById('timelineSection').style.display = 'none';
                document.getElementById('tableTitle').innerText = 'Detailed Segment Errors (All Songs)';
                renderTable(rawTableData);
            }} else {{
                document.getElementById('overviewStats').style.display = 'none';
                document.getElementById('timelineSection').style.display = 'block';
                document.getElementById('tableTitle').innerText = `Segment Analysis: ${{song}}`;
                
                // Filter table
                const filtered = rawTableData.filter(r => r['Song Name'] === song);
                renderTable(filtered);
                
                // Draw Timeline
                updateTimeline(song);
            }}
        }});

        // Initial render
        renderTable(rawTableData);
    </script>
</body>
</html>
    """

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Dashboard generated at {OUTPUT_HTML}")

if __name__ == "__main__":
    generate_dashboard()
