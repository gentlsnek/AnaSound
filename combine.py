from pydub import AudioSegment, effects
import os
import concurrent.futures

def load_audio(file_path):
    """Loads an audio file and normalizes volume."""
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.mp3':
        return AudioSegment.from_mp3(file_path).normalize()
    elif file_extension == '.wav':
        return AudioSegment.from_wav(file_path).normalize()
    else:
        raise ValueError("Unsupported file format. Please use .mp3 or .wav.")

def estimate_instrumental_frequencies(instrumental_audio):
    """Approximates the dominant frequency range using Pydub's filters."""
    filtered_low = effects.low_pass_filter(instrumental_audio, 500)  # Strong bass
    filtered_mid = effects.low_pass_filter(instrumental_audio, 2000)  # Mids and highs

    low_energy = filtered_low.dBFS
    mid_energy = filtered_mid.dBFS

    return "mid" if mid_energy > low_energy else "low"

def match_vocal_frequencies(vocal_audio, target_range):
    """Applies Pydub filters to adjust vocal frequencies to match the instrumental."""
    if target_range == "low":
        return effects.low_pass_filter(vocal_audio, 500)  # Focus on bass frequencies
    elif target_range == "mid":
        return effects.high_pass_filter(vocal_audio, 500).low_pass_filter(2000)  # Mid-range focus
    return vocal_audio  # No adjustment needed

def adjust_audio_length(audio, duration):
    """Ensures the audio fits the specified duration by trimming or looping."""
    if len(audio) == 0:
        print("Warning: Empty audio segment detected. Using silent fallback.")
        return AudioSegment.silent(duration=int(duration * 1000))  # Return silence instead of crashing
    
    target_duration_ms = int(duration * 1000)
    return (audio * ((target_duration_ms // len(audio)) + 1))[:target_duration_ms]

def apply_crossfade(seg1, seg2, fade_duration=100):
    """Applies a smooth crossfade between two segments."""
    max_fade = min(fade_duration, len(seg2) - 1)  # Ensure fade is valid
    if max_fade <= 0:
        return seg1 + seg2  # Append without crossfade if fade is invalid
    return seg1.append(seg2, crossfade=max_fade)

def map_tags_to_files(tags, intervals, low_file, medium_file, high_file, instrumental_file, output_file):
    """Maps tags to audio files, adjusts their frequencies, and combines them."""
    
    # Load all files in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_instrumental = executor.submit(load_audio, instrumental_file)
        future_low = executor.submit(load_audio, low_file)
        future_medium = executor.submit(load_audio, medium_file)
        future_high = executor.submit(load_audio, high_file)

        instrumental_audio = future_instrumental.result()
        low_audio = future_low.result()
        medium_audio = future_medium.result()
        high_audio = future_high.result()

    # Estimate the dominant frequency range
    target_range = estimate_instrumental_frequencies(instrumental_audio)

    # Map tags to corresponding audio
    audio_files = {
        "low": low_audio,
        "medium": medium_audio,
        "high": high_audio
    }

    precomputed_segments = []

    # Get instrumental track duration
    instrumental_duration = len(instrumental_audio) / 1000  # Convert ms to seconds

    # Process vocal segments with frequency matching
    for tag, (start_time, end_time) in zip(tags, intervals):
        duration = end_time - start_time
        if tag in audio_files:
            vocal_audio = audio_files[tag]

            # Match frequency to instrumental
            matched_vocal = match_vocal_frequencies(vocal_audio, target_range)

            # Adjust length
            matched_vocal = adjust_audio_length(matched_vocal, duration)

            # Extract instrumental segment with validation
            if start_time >= instrumental_duration:
                print(f"Warning: start_time {start_time}s exceeds instrumental duration {instrumental_duration}s. Using silence.")
                instrumental_segment = AudioSegment.silent(duration=int(duration * 1000))
            elif end_time > instrumental_duration:
                print(f"Warning: end_time {end_time}s exceeds instrumental duration {instrumental_duration}s. Trimming.")
                instrumental_segment = instrumental_audio[start_time * 1000:]
            else:
                instrumental_segment = instrumental_audio[start_time * 1000:end_time * 1000]

            # Ensure instrumental segment is not empty
            if len(instrumental_segment) == 0:
                print(f"Warning: Empty instrumental segment at {start_time}-{end_time}. Using silence.")
                instrumental_segment = AudioSegment.silent(duration=int(duration * 1000))

            instrumental_segment = adjust_audio_length(instrumental_segment, duration)

            # Overlay vocals onto instrumental
            combined_segment = instrumental_segment.overlay(matched_vocal)
            precomputed_segments.append(combined_segment)

    # Ensure we don't crash if there are no valid segments
    if not precomputed_segments:
        print("Warning: No valid segments found. Output will be silent.")
        final_audio = AudioSegment.silent(duration=1000)  # 1 second of silence as fallback
    else:
        # Combine all segments with crossfades
        final_audio = precomputed_segments[0]
        for segment in precomputed_segments[1:]:
            final_audio = apply_crossfade(final_audio, segment)

    # Ensure output folder exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Export final audio
    final_audio.export(output_file, format="wav")
    print(f"Final audio saved to {output_file}")

# Example usage
def combine(tags, intervals, filename):
    low_file = "voices/low.wav"
    medium_file = "voices/medium.wav"
    high_file = "voices/high.wav"
    instrumental_file = f"separated/mdx_extra/{filename}/no_vocals.wav"
    output_file = f"outputs/output_{filename}.wav"

    map_tags_to_files(tags, intervals, low_file, medium_file, high_file, instrumental_file, output_file)
