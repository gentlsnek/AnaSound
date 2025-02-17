


# has to basically do three things, 
#1. Find the length of a set range of frequencies and tag them
#2. replace taged frequency with set audio file
#3. return new audio file
import librosa
import numpy as np
from pydub import AudioSegment


def split_audio_on_silence(audio_file, silence_threshold=0.001, min_silence_len=500):
    y, sr = librosa.load(audio_file, sr=None)  
    D = np.abs(librosa.stft(y))
    avg_magnitudes = np.mean(D, axis=0)
    times = librosa.frames_to_time(np.arange(len(avg_magnitudes)), sr=sr)
    
    silent_segments = []
    is_silent = avg_magnitudes < silence_threshold
    start = None
    
    for i, silent in enumerate(is_silent):
        if silent and start is None:
            start = times[i] * 1000 
        elif not silent and start is not None:
            end = times[i] * 1000
            if end - start >= min_silence_len:
                silent_segments.append((start, end))
            start = None
    

    audio = AudioSegment.from_file(audio_file)
    start_time = 0
    segments = []
    
    for start, end in silent_segments:
        if start_time < start:
            segment = audio[start_time:int(start)]
            segments.append(segment)
        start_time = int(end)
    
    if start_time < len(audio):
        segments.append(audio[start_time:])
    

    for i, segment in enumerate(segments):
        segment.export(f"segment_{i}.mp3", format="mp3")
    
    return [f"segment_{i}.mp3" for i in range(len(segments))]


segmented_files = split_audio_on_silence("final.mp3")
print(segmented_files)
