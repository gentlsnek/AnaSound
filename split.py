import subprocess

def split_audio(input_audio, output_folder="demucs_output"):
    command = [
        "demucs",
        "--two-stems=vocals", output_folder,
        input_audio
    ]
    subprocess.run(command)
    print(f"Separation complete! Check the '{output_folder}' folder.")


if __name__ == "__main__":
    input_audio = "test.mp3"  # Change this to your file
    split_audio(input_audio)
    