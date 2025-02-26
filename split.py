import subprocess
import os
from tag import scan

def split_audio(input_audio, output_folder="separated"):
    model = "mdx_extra"
    output_path = f"{output_folder}/{model}/{os.path.basename(input_audio).split('.')[0]}"

    # Check if Demucs output already exists
    if os.path.exists(output_path):
        print(f"Skipping Demucs: Output already exists at {output_path}")
    else:
        command = ["demucs", "-n", model, "--two-stems", "vocals", input_audio, "-o", output_folder]
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: Demucs failed with error {e}")
            return
    
    scan(input_audio)



