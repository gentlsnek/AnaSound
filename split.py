import subprocess
from tag import scan


def split_audio(input_audio, output_folder="separated"):
    model = "mdx_extra"
    command = ["demucs", "-n", model, "--two-stems", "vocals", input_audio, "-o", output_folder]
    subprocess.run(command, check=True) 
    
    input_audio = input_audio.split("/")[-1].split(".")[0]
    
    scan(input_audio)
    
   
    
    
    
    




