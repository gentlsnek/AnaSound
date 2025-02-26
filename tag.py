import numpy as np
import os
from combine import combine
from pydub import AudioSegment

def process_vocals(input_audio, output_folder="separated"):
    model = "mdx_extra"
    fname = os.path.basename(input_audio).rsplit(".", 1)[0]
    vocals_path = f"{output_folder}/{model}/{fname}/vocals.wav"

    if not os.path.exists(vocals_path):
        raise FileNotFoundError(f"Error: {vocals_path} not found. Check if Demucs completed successfully.")

    return vocals_path

def tag_audio_sections(vocals_path, low_thresh=500, mid_thresh=2000):
    """Tags sections of the audio into High, Medium, and Low based on dominant frequency range."""
    
    audio = AudioSegment.from_wav(vocals_path)
    samples = np.array(audio.get_array_of_samples())
    
    # Split into chunks (e.g., 100ms)
    chunk_size = audio.frame_rate // 10  # 100ms chunks
    num_chunks = len(samples) // chunk_size
    
    tags = []
    time_intervals = []
    
    for i in range(num_chunks):
        start_time = i * 0.1
        end_time = (i + 1) * 0.1

        chunk = samples[i * chunk_size:(i + 1) * chunk_size]
        power_spectrum = np.abs(np.fft.rfft(chunk))  # Compute FFT
        
        freqs = np.fft.rfftfreq(len(chunk), d=1/audio.frame_rate)
        low_energy = power_spectrum[freqs < low_thresh].sum()
        mid_energy = power_spectrum[(freqs >= low_thresh) & (freqs < mid_thresh)].sum()
        high_energy = power_spectrum[freqs >= mid_thresh].sum()

        if high_energy > mid_energy and high_energy > low_energy:
            current_tag = "high"
        elif mid_energy > low_energy:
            current_tag = "medium"
        else:
            current_tag = "low"

        if not tags or tags[-1] != current_tag:
            tags.append(current_tag)
            time_intervals.append((round(start_time, 2), round(end_time, 2)))
            
        
    print(f"Detected tags: {tags}")
    print(f"Time intervals: {time_intervals}")
    return tags, time_intervals

def scan(input_audio, output_folder="separated"):
    vocals_path = process_vocals(input_audio, output_folder)
    tags, intervals = tag_audio_sections(vocals_path)
    filename = os.path.basename(input_audio).rsplit(".", 1)[0]

    combine(tags, intervals, filename)
