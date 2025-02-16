import subprocess
from anachange import change_pitch

def split_audio(input_audio, output_folder="separated"):
    command = ["demucs"," --two-stems=vocals" ,input_audio,output_folder]
    subprocess.run(command)
    print(f"Separation complete! Check the '{output_folder}' folder.")
    
    change_pitch(f"{output_folder}/vocals.wav", 2)
    
    

