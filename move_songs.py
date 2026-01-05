import shutil
from pathlib import Path
import os

def move_songs_to_root():
    """
    Moves all subdirectories from the 'songs' folder to the current working directory (root).
    """
    source_dir = Path("songs")
    dest_dir = Path(".")
    
    if not source_dir.exists():
        print(f"Directory '{source_dir}' does not exist.")
        return

    print(f"Moving song folders from '{source_dir.absolute()}' to '{dest_dir.absolute()}'...")

    # Iterate over items in the songs directory
    moved_count = 0
    for item in source_dir.iterdir():
        if item.is_dir():
            target_path = dest_dir / item.name
            
            if target_path.exists():
                print(f"[Skipping] '{item.name}' already exists in the destination.")
                continue
            
            try:
                # shutil.move works for directories too
                shutil.move(str(item), str(target_path))
                print(f"[Moved] {item.name}")
                moved_count += 1
            except Exception as e:
                print(f"[Error] Failed to move {item.name}: {e}")

    print(f"\nSuccessfully moved {moved_count} folders.")
    
    # Optional: check if songs dir is empty and remove it? 
    # User didn't ask to remove 'songs' folder, so I'll leave it empty.
    
if __name__ == "__main__":
    move_songs_to_root()
