import json
from pathlib import Path
from llm_formatter import LLMFormatter

def run_comparison_analysis():
    base_dir = Path(".")
    
    # 8 songs to compare
    song_roots = [
        "ghallu_ghallu",
        "Mari_Antaga_SVSC_Movie",
        "Naa_Autograph_Sweet_Memories",
        "Narasimha_-_Narasimha",
        "Narasimha_Yekku_Tholi_Mettu",
        "Oh_Sita_Hey_Rama",
        "Pilichina_Ranantava_Song_With",
        "Raja_Edo_Oka_Ragam",
        "Nuvvostanante_Nenoddantana_s",
        "robo"
    ]

    formatter = LLMFormatter()
    full_report_md = "# SAM vs Demucs: Comparative Analysis Report\n\n"
    full_report_md += "This report compares the performance of SAM (Segment Anything Model) vs Demucs (HTDemucs) on 8 Indian songs.\n\n"
    
    comparison_data = []

    for song_root in song_roots:
        sam_dir = base_dir / f"{song_root}_SAM"
        demucs_dir = base_dir / f"{song_root}_Demucs"
        
        # Load detected structures
        sam_json = sam_dir / "song_structure.json"
        demucs_json = demucs_dir / "song_structure.json"
        
        sam_structure = []
        demucs_structure = []
        
        try:
            if sam_json.exists():
                with open(sam_json, 'r') as f:
                    sam_structure = json.load(f)
            
            if demucs_json.exists():
                with open(demucs_json, 'r') as f:
                    demucs_structure = json.load(f)
        except Exception as e:
            print(f"Error loading data for {song_root}: {e}")
            continue

        if not sam_structure or not demucs_structure:
            print(f"Missing data for {song_root}, skipping comparison.")
            continue
            
        print(f"Comparing {song_root}...")
        
        # Prepare data for LLM
        comparison_prompt = f"""
        Analyze and compare the segmentation results for the song "{song_root}".
        
        Structure A (SAM Approach):
        {json.dumps(sam_structure, indent=2)}
        
        Structure B (Demucs Approach):
        {json.dumps(demucs_structure, indent=2)}
        
        Task:
        1. Compare the granularity: Which one detects more specific segments?
        2. Compare vocal alignment: Do they agree on when vocals start/end?
        3. Identify hallucinations: Does one seem to over-segment silence or noise?
        4. Conclusion: Which approach seems more accurate for this specific song and why?
        """
        
        # We use the existing formatter to get this analysis (it uses Gemini)
        # We'll create a new method on LLMFormatter or just reuse a generic prompt method if available.
        # Since LLMFormatter is specific, I'll borrow its genai instance or logic effectively.
        # For now, let's assume I can add a method or just use the model directly if I could Import it.
        # But I don't want to modify llm_formatter.py heavily if I can avoid it.
        # I'll modify llm_formatter.py to expose a 'compare_structures' method.
        
        comparison_data.append({
            "song": song_root,
            "sam": sam_structure,
            "demucs": demucs_structure
        })

    # Now I need a way to actually run this through the LLM. 
    # I will modify llm_formatter.py to add `generate_comparison_report`
    
    # Writing the rest of this script to use that new method
    print("\nGenerating final comparative report via LLM...")
    final_analysis = formatter.generate_comparison_report(comparison_data)
    
    with open("SAM_vs_Demucs_Comparison_Report.md", "w", encoding="utf-8") as f:
        f.write(full_report_md)
        f.write(final_analysis)
        
    print("Report saved to SAM_vs_Demucs_Comparison_Report.md")

if __name__ == "__main__":
    run_comparison_analysis()
