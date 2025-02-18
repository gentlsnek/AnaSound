from pydub import AudioSegment
import os

def load_audio(file_path):
    """Loads an audio file (either .mp3 or .wav)."""
    try:
        # Check the file extension
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.mp3':
            audio = AudioSegment.from_mp3(file_path)
        elif file_extension == '.wav':
            audio = AudioSegment.from_wav(file_path)
        else:
            raise ValueError("Unsupported file format. Please use .mp3 or .wav.")
        
        return audio
    except Exception as e:
        raise FileNotFoundError(f"Could not load {file_path}: {e}")

def adjust_audio_length(audio, start_time, end_time):
    """Adjusts the audio length to match the interval (start_time to end_time)."""
    duration = end_time - start_time
    audio_duration_ms = len(audio)

    if duration * 1000 < audio_duration_ms:
        # Trim audio to fit the duration
        return audio[:int(duration * 1000)]
    else:
        # Loop the audio to fill the duration, using integer multiplication
        repeat_count = int((duration * 1000) // audio_duration_ms) + 1
        repeated_audio = audio * repeat_count
        return repeated_audio[:int(duration * 1000)]


def map_tags_to_files(tags, intervals, low_file, medium_file, high_file,instrumental, output_file):
    """Maps the tags to their respective audio files and adjusts length as needed."""
    # Load the audio files
    low_audio = load_audio(low_file)
    medium_audio = load_audio(medium_file)
    high_audio = load_audio(high_file)
    instrumental_audio = load_audio(instrumental)

    final_audio = AudioSegment.silent(duration=0)  # Start with an empty audio

    for tag, (start_time, end_time) in zip(tags, intervals):
        if tag == "low":
            sound_segment = adjust_audio_length(low_audio, start_time, end_time)
        elif tag == "medium":
            sound_segment = adjust_audio_length(medium_audio, start_time, end_time)
        elif tag == "high":
            sound_segment = adjust_audio_length(high_audio, start_time, end_time)
        else:
            continue  # Ignore unknown tags

        # Adjust the length of the instrumental track for the current section
        instrumental_segment = adjust_audio_length(instrumental_audio, start_time, end_time)

        # Combine the sound (vocals) and instrumental
        combined_segment = instrumental_segment.overlay(sound_segment) 

        final_audio += combined_segment

    final_audio.export(output_file, format="wav")
    
    print(f"Final audio saved to {output_file}")


# Example usage

def combine(tags, intervals, filename):
            low_file = "voices/low.wav"
            medium_file = "voices/medium.wav"
            high_file = "voices/high.wav"
            output_file = "output_audio.mp3"
            instrumental = f"separated/mdx_extra/"+filename+"/no_vocals.wav"

            map_tags_to_files(tags, intervals, low_file, medium_file, high_file,instrumental, output_file)