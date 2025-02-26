import os
from split import split_audio
import sys

def main():
    if len(sys.argv) > 1:
        audio = sys.argv[1]  # Allow command-line argument
    else:
        audio = input("Enter audio file name: ")

    if not os.path.exists(audio):
        print(f"Error: File '{audio}' not found.")
        return

    split_audio(audio)

if __name__ == "__main__":
    main()
