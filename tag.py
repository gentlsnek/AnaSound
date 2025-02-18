import librosa as lb
import numpy as np
import os
from combine import combine

def process_vocals(input_audio, output_folder="separated"):
    model = "mdx_extra"
    fname = os.path.basename(input_audio).rsplit(".", 1)[0]
    vocals_path = f"{output_folder}/{model}/{fname}/vocals.wav"

    if not os.path.exists(vocals_path):
        raise FileNotFoundError(f"Error: {vocals_path} not found. Check if Demucs completed successfully.")

    y, sr = lb.load(vocals_path, sr=None)  # Load without resampling
    y = y.astype(np.float32)  # Ensure float format

    return y, sr

def tag_audio_sections(y, sr, hop_length=1024, low_thresh=500, mid_thresh=2000):
    """Tags sections of the audio into High, Medium, and Low based on dominant frequency range."""
    
    # Compute STFT
    S = np.abs(lb.stft(y, n_fft=2048, hop_length=hop_length))

    # Get frequency bins
    freqs = lb.fft_frequencies(sr=sr, n_fft=2048)

    # Identify frequency indices
    low_idx = np.where(freqs < low_thresh)[0]
    mid_idx = np.where((freqs >= low_thresh) & (freqs < mid_thresh))[0]
    high_idx = np.where(freqs >= mid_thresh)[0]

    # Compute energy in each band over time
    low_energy = np.sum(S[low_idx, :], axis=0)
    mid_energy = np.sum(S[mid_idx, :], axis=0)
    high_energy = np.sum(S[high_idx, :], axis=0)

    # Assign tags based on dominant energy
    tags = []
    times = lb.times_like(low_energy, sr=sr, hop_length=hop_length)
    
    prev_tag = None
    tag_list = []
    time_intervals = []
    
    start_time = times[0]
    
    for i in range(len(times)):
        if high_energy[i] > mid_energy[i] and high_energy[i] > low_energy[i]:
            current_tag = "high"
        elif mid_energy[i] > low_energy[i]:
            current_tag = "medium"
        else:
            current_tag = "low"

        # If tag changes, store previous segment
        if current_tag != prev_tag and prev_tag is not None:
            time_intervals.append((round(start_time, 2), round(times[i], 2)))
            tag_list.append(prev_tag)
            start_time = times[i]  # New start time for next segment
        
        prev_tag = current_tag

    # Append the last segment
    if prev_tag is not None:
        time_intervals.append((round(start_time, 2), round(times[-1], 2)))
        tag_list.append(prev_tag)

    return tag_list, time_intervals

def scan(input_audio, output_folder="separated"):
    y, sr = process_vocals(input_audio, output_folder)
    tags, intervals = tag_audio_sections(y, sr)
    filename = os.path.basename(input_audio).rsplit(".", 1)[0]

    combine(tags, intervals,filename)