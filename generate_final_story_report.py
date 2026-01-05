import os
import glob
from pathlib import Path
from llm_formatter import LLMFormatter

def read_human_analyses(base_dir):
    """
    Reads all 'human_analysis.md' files from the directory structure.
    """
    analyses = {}
    # Case-insensitive search pattern? 
    # The files are named 'human_analysis.md' or 'Human_Analysis.md' or 'Human_analysis.md'
    # Let's search recursively for ANY .md file with 'analysis' in the name within Demucs folders.
    
    base_path = Path(base_dir)
    demucs_folders = [f for f in base_path.iterdir() if f.is_dir() and f.name.endswith("_Demucs")]
    
    print(f"Scanning {len(demucs_folders)} folders for human analysis...")
    
    for folder in demucs_folders:
        # Try finding the file
        found_file = None
        for file in folder.iterdir():
            if "human" in file.name.lower() and "analysis" in file.name.lower() and file.suffix.lower() == ".md":
                found_file = file
                break
        
        if found_file:
            try:
                with open(found_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    song_name = folder.name.replace("_Demucs", "").replace("_", " ")
                    analyses[song_name] = content
            except Exception as e:
                print(f"Error reading {found_file}: {e}")
    
    return analyses

def generate_story():
    base_dir = r"c:\Users\admin\Desktop\song analysis"
    human_notes = read_human_analyses(base_dir)
    
    if not human_notes:
        print("No human analysis files found!")
        return

    print(f"Found notes for {len(human_notes)} songs: {list(human_notes.keys())}")

    # Prepare LLM Prompt
    formatter = LLMFormatter()
    
    system_prompt = """
    You are Matt Daniels (The Data Journalist from The Pudding). 
    You are writing a deeply engaging, visual, and technical "Data Story" about an experiment to Automate Indian Film Song Analysis.
    
    **Context:**
    We tried to build an AI Pipeline to separate and segment Indian songs (Telugu/Tamil) into parts like "Pallavi" (Chorus), "Charanam" (Verse), and "Interludes".
    We tested two cutting-edge AI models for source separation:
    1. **Demucs (facebook/demucs)**: A waveform-based deep learning model.
    2. **SAM (Segment Anything Model)**: Adapted for audio via spectrogram masking.
    
    **The Data:**
    I will provide you with "Human Analysis Notes" for several songs. These notes contain raw, unfiltered observations comparing Demucs vs SAM performance on specific tracks.
    
    **Your Goal:**
    Synthesize these raw notes into a cohesive, narrative-driven report titled:
    **"The Ghost in the Machine: Can AI Really Understand Indian Music?"**
    
    **Structure of the Story:**
    1.  **The Hook**: Why is this hard? (Indian music complexity, continuous melodies, rich background noise).
    2.  **The Contenders**: Briefly introduce Demucs (The reliable workhorse) vs SAM (The visual artist trying to do audio).
    3.  **The Battleground (Song Analysis)**: Group the songs into thematic clusters based on the human notes.
        *   *The "Violin" Problem*: Discuss how models confuse violins/flutes with vocals (citing "Naa Autograph", "Nuvvostanante").
        *   *The "Noise" Factor*: Discuss how SAM is aggressive at removing noise but sometimes eats the vocals too (citing "Ghallu Ghallu", "Mari Antaga").
        *   *The "Crowd" Effect*: Discuss the challenge of chorus/background voices (citing "Robo").
    4.  **Verdict**: A definitive but nuanced conclusion. Demucs is safer, but SAM has moments of brilliance in noise reduction.
    5.  **Future Outlook**: What's next? (Melodic Fingerprinting, Lyrics transcription).
    
    **Tone:**
    - Journalism-style, storytelling, data-backed but readable.
    - Use quotes from the "Human Analysis" to back up claims.
    - Be honest about failures ("Demucs failed here", "SAM hallucinated there").
    
    **Input Data (Human Notes):**
    {human_notes}
    """
    
    user_message = "Generate the full markdown report/story now."
    
    # We'll use the LLM to generate the report
    payload = {
        "model": "gpt-4o", 
        "messages": [
            {"role": "system", "content": system_prompt.replace("{human_notes}", str(human_notes))},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.4 # Creativity needed
    }
    
    try:
        print("Asking LLM to write the story...")
        import requests
        resp = requests.post(formatter.api_url, headers=formatter.headers, json=payload, timeout=120)
        resp.raise_for_status()
        story = resp.json()["choices"][0]["message"]["content"]
        
        output_path = Path(base_dir) / "The_Indian_AI_Music_Experiment.md"
        with open(output_path, "w", encoding='utf-8') as f:
            f.write(story)
            
        print(f"Story written to: {output_path}")
        
    except Exception as e:
        print(f"Failed to generate story: {e}")

if __name__ == "__main__":
    generate_story()
