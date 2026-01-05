import requests
import json
import time

class LLMFormatter:
    def __init__(self):
        self.api_url = "https://llmfoundry.straive.com/openai/v1/chat/completions"
        self.token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRwYXZhbi5rdW1hckBncmFtZW5lci5jb20ifQ.dIjgC3eykiiux4vJW0HvpARLLgjAoVFgU5XJIfZ94hY"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        self.model = "gpt-4o" 

    def generate_structure(self, blocks, song_name="Unknown Song", estimated_start=0):
        """
        Sends blocks to LLM and returns semantic structure.
        """
        print(f"[LLM] Sending blocks for {song_name}...")
        
        # Prepare blocks with IDs and enhanced features
        indexed_blocks = []
        for i, b in enumerate(blocks):
            block_data = {
                "id": i,
                "type": b['type'],
                "start": b['start'],
                "end": b['end'],
                "duration": round(b['end'] - b['start'], 2),
                "is_melodic": b.get('is_melodic', False),
                # New Flag: Did we detect the melody repeating elsewhere?
                "repeats_later": b.get('repeats', False)
            }
            indexed_blocks.append(block_data)

        user_message = json.dumps({
            "song_name": song_name,
            "song_type": "Indian film song",
            "estimated_main_vocals_start_time": estimated_start,
            "blocks": indexed_blocks
        }, indent=2)
        
        system_prompt = """
        You are a Senior Audio ML + Music Intelligence Engineer with strong understanding of Indian (Telugu/Tamil/Hindi) film song structure.
        
        Input: A list of segmented audio blocks with features:
        - Timestamps (start/end)
        - Type (vocals/instrumental)
        - **is_melodic**: True if consistent pitch was detected.
        - **repeats_later**: True if the melody of this block mathematically matches a future block.
        
        Your Goal: Assign a Label to each block ID based on sequence, duration, and features.
        
        CRITICAL: Do NOT change the timestamps. 
        
        **Indian Film Song Logic (Grammar):**
        1. **Pallavi (Chorus)**: 
           - The "Main Theme" of the song. 
           - **MUST have 'repeats_later': true** (The core definition of a Pallavi is that it repeats).
           - Typically starts after the Intro (around 30-60s mark).
        2. **Intro**: 
           - Usually instrumental or soft humming before the main beat.
        3. **Interlude**: 
           - STRICTLY Instrumental sections between vocal blocks.
           - Usually long (> 15s).
        4. **Charanam (Verse)**: 
           - Long vocal blocks that follow an Interlude.
           - Usually there are 2 or 3 Charanams per song.
        5. **Humming / Alaap**: 
           - Short melodic blocks that do NOT repeat identically later (ad-libs).
           
        **HINT:** provided 'estimated_main_vocals_start_time' is a rough guess for the Pallavi start.
        
        Output Format:
        A JSON array of ONLY objects with "id" and "label".
        Example:
        [
          { "id": 0, "label": "Intro (Instrumental)" },
          { "id": 1, "label": "Pallavi" },
          { "id": 2, "label": "Interlude 1" }
        ]
        """
        
        payload = {
            "model": "gpt-4o", 
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.0
        }
    
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            # Clean up potential markdown
            if "```json" in content:
                content = content.replace("```json", "").replace("```", "")
            elif "```" in content:
                 content = content.replace("```", "")
            
            labels_list = json.loads(content.strip())
            
            # Merge labels back into original blocks
            label_map = { item['id']: item['label'] for item in labels_list }
            
            final_structure = []
            for i, b in enumerate(blocks):
                final_structure.append({
                    "label": label_map.get(i, "Unknown"),
                    "start": b['start'],
                    "end": b['end'],
                    "type": b['type']
                })
                
            return final_structure
            
        except Exception as e:
            print(f"[LLM] Error (using Rule-Based Fallback): {e}")
            return self._fallback_logic(blocks)

    def get_song_metadata(self, song_name):
        """
        Asks LLM for specific structural metadata (Intro length, etc.)
        to guide the segmentation.
        """
        print(f"[LLM] Fetching metadata/hints for {song_name}...")
        
        system_prompt = """
        You are a Database of Indian Film Music.
        
        Input: Song Name.
        
        Goal: Provide the ESTIMATED timestamps for key events based on your training data (Popular songs).
        
        Output JSON:
        {
            "has_long_intro": boolean,
            "estimated_vocal_start": number (seconds, approx),
            "structure_hint": "brief description like 'Long flute intro then male vocals'"
        }
        
        If you don't know the specific song, return:
        { "has_long_intro": false, "estimated_vocal_start": 0, "structure_hint": "Unknown" }
        """
        
        user_message = json.dumps({ "song_name": song_name })
        
        payload = {
            "model": "gpt-4o", 
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.0
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=60)
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            if "```json" in content:
                content = content.replace("```json", "").replace("```", "")
            elif "```" in content:
                 content = content.replace("```", "")
                 
            return json.loads(content.strip())
        except Exception as e:
            print(f"[LLM] Metadata fetch warning: {e}")
            return { "has_long_intro": False, "estimated_vocal_start": 0 }

    def get_expected_structure(self, song_name):
        """
        Asks LLM for the FULL estimated structure key timestamps.
        Used for verification comparison.
        """
        print(f"[LLM] Fetching expected structure for {song_name}...")
        
        system_prompt = """
        You are a Database of Indian Film Music.
        
        Input: Song Name.
        
        Goal: Provide the ESTIMATED structure with timestamps based on your knowledge.
        
        Output: A list of segments with label, start, end.
        
        Output JSON:
        [
            { "label": "Intro", "start": 0, "end": 45 },
            { "label": "Pallavi", "start": 45, "end": 90 },
            { "label": "Interlude 1", "start": 90, "end": 120 }
             ...
        ]
        
        If you don't know exact timings, provide your BEST GUESS based on typical song structure for this track.
        """
        
        user_message = json.dumps({ "song_name": song_name })
        
        payload = {
            "model": "gpt-4o", 
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.0
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=60)
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            if not content:
                 print(f"[LLM] Warning: Empty content received from expected structure API.")
                 return []

            if "```json" in content:
                content = content.replace("```json", "").replace("```", "")
            elif "```" in content:
                 content = content.replace("```", "")
                 
            return json.loads(content.strip())
        except Exception as e:
            print(f"[LLM] Expected structure fetch failed (Non-Critical): {e}")
            return []

    def _fallback_logic(self, blocks):
        """
        Deterministic labeling for when LLM is unavailable.
        """
        output = []
        v_count = 0
        i_count = 0
        
        for b in blocks:
            label = "Unknown"
            if b['type'] == 'vocals':
                v_count += 1
                if v_count == 1:
                    label = "Pallavi"
                else:
                    label = f"Charanam {v_count - 1}"
            else:
                i_count += 1
                label = f"Interlude {i_count}"
            
            output.append({
                "label": label,
                "start": b['start'],
                "end": b['end']
            })
        return output

    def generate_lyrics(self, song_name, structure):
        """
        Fetches lyrics for the given structure using LLM.
        """
        print(f"[LLM] Fetching lyrics for {song_name}...")
        
        section_labels = [s['label'] for s in structure if s['label'] not in ['Unknown']]
        
        system_prompt = """
        You are an expert in Indian film music lyrics (Telugu/Tamil/Hindi).
        
        Your Goal: Provide the correct lyrics for the specified song sections.
        
        Input: 
        - Song Name
        - List of Sections (e.g. Pallavi, Charanam 1, Charanam 2)
        
        Output:
        - A JSON object where keys are the SECTION NAMES and values are the LYRICS for that section.
        - If a section is 'Interlude' or 'Instrumental', the text should be "[Instrumental]".
        - If you don't know the lyrics, provide a best guess or empty string.
        - Provide lyrics in the original language (e.g. Telugu) OR transliterated English, whichever is more common/readable for general users. Telugu script is preferred if requested.
        
        Format:
        {
            "Pallavi": "Line 1\nLine 2...",
            "Charanam 1": "Line 1..."
        }
        """
        
        user_message = json.dumps({
            "song_name": song_name,
            "sections": section_labels
        }, indent=2)
        
        payload = {
            "model": "gpt-4o", 
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.1
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            # Clean up markdown
            if "```json" in content:
                content = content.replace("```json", "").replace("```", "")
            elif "```" in content:
                 content = content.replace("```", "")
            
            lyrics_map = json.loads(content.strip())
            return lyrics_map
            
        except Exception as e:
            print(f"[LLM] Lyrics fetch failed: {e}")
            if 'content' in locals():
                print(f"[LLM] Raw Content causing error: {content}")
            return {}
    def generate_comparison_report(self, comparison_data):
        """
        Generates a comparative analysis report for SAM vs Demucs.
        data: List of objects {song, sam_structure, demucs_structure}
        """
        print(f"[LLM] Comparison report generation started for {len(comparison_data)} songs...")
        
        system_prompt = """
        You are an expert Audio Analysis Engineer evaluating two Source Separation models:
        1. SAM (Segment Anything Model)
        2. Demucs (HTDemucs Hybrid Transformer)
        
        Your Goal: Compare their performance in identifying Song Structure (Vocals vs Instrumental).
        
        Input: A list of 8 songs, each with the detected structure from both models.
        
        Analysis Requirements:
        - For each song, identify which model produced a more realistic structure (e.g. less noise, better alignment with expected Pallavi/Charanam).
        - 'SAM' typically segments by visual/spectrogram masks. It might over-segment if noise is present.
        - 'Demucs' operates on waveform stems. It is usually robust but might include breathing/humming as vocals.
        - Look for "Hallucinations": e.g. very short vocal bursts in the middle of long instrumental sections (often false positives).
        - Granularity: Does one model merge sections while the other splits them? Which is better?
        
        Output:
        A Markdown report.
        - Executive Summary: Overall winner and key observations.
        - Song-by-Song Analysis: Brief paragraph for each song comparing the two.
        - Conclusion: Recommendation for future use.
        """
        
        # We process in one go or batches? Context window is large enough for 8 songs summaries.
        # Let's verify data size. A structure might be 20 lines. 8 * 2 * 20 = 320 lines. Fits easily.
        
        user_message_str = json.dumps(comparison_data, indent=2)
        
        payload = {
            "model": "gpt-4o", 
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message_str}
            ],
            "temperature": 0.2
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=120)
            response.raise_for_status()
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
            
        except Exception as e:
            print(f"[LLM] Comparison report generation failed: {e}")
            return "## Comparison Failed\nCould not generate report due to API error."
