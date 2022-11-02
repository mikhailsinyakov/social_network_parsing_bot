import validators
from validators import ValidationFailure
import ffmpeg

import os
import shutil

def is_url(s):
    result = validators.url(s)

    if isinstance(result, ValidationFailure):
        return False

    return result

def get_compressed_video(original_video, target_size):
    video_name = "video.mp4"
    output_video_name = "video_c.mp4"
    with open(video_name, "wb") as f:
        f.write(original_video)

    try:
        compress_video(video_name, output_video_name, target_size)
    except ffmpeg.Error:
        return None

    with open(output_video_name, "rb") as f:
        compressed_video = f.read()
    
    os.remove(video_name)
    os.remove(output_video_name)
    
    return compressed_video


def get_compressed_audio(original_audio, target_size):
    audio_name = "audio.mp3"
    output_audio_name = "audio_c.mp3"
    with open(audio_name, "wb") as f:
        f.write(original_audio)

    try:
        compress_audio(audio_name, output_audio_name, target_size)
    except ffmpeg.Error:
        return None

    with open(output_audio_name, "rb") as f:
        compressed_audio = f.read()
    
    os.remove(audio_name)
    os.remove(output_audio_name)
    
    return compressed_audio
    

def compress_video(video_full_path, output_file_name, target_size):
    min_audio_bitrate = 32000
    max_audio_bitrate = 256000

    probe = ffmpeg.probe(video_full_path)

    duration = float(probe['format']['duration'])
    audio_bitrate = float(next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)['bit_rate'])
    target_total_bitrate = (target_size * 8) / (1.073741824 * duration)

    if 10 * audio_bitrate > target_total_bitrate:
        audio_bitrate = target_total_bitrate / 10
        if audio_bitrate < min_audio_bitrate < target_total_bitrate:
            audio_bitrate = min_audio_bitrate
        elif audio_bitrate > max_audio_bitrate:
            audio_bitrate = max_audio_bitrate
    
    video_bitrate = target_total_bitrate - audio_bitrate

    i = ffmpeg.input(video_full_path)
    ffmpeg.output(i, output_file_name,
                  **{'c:v': 'libx264', 'b:v': video_bitrate, 'c:a': 'aac', 'b:a': audio_bitrate}
                  ).overwrite_output().run(quiet=True)
    

def compress_audio(audio_full_path, output_file_name, target_size):
    min_audio_bitrate = 32000
    max_audio_bitrate = 256000

    probe = ffmpeg.probe(audio_full_path)
    duration = float(probe['format']['duration'])
    target_bitrate = (target_size * 8) / (1.073741824 * duration)
    target_bitrate = max(min(max_audio_bitrate, target_bitrate), min_audio_bitrate)

    i = ffmpeg.input(audio_full_path)
    ffmpeg.output(i, output_file_name,
                  **{'c:a': 'libmp3lame', 'b:a': target_bitrate}
                  ).overwrite_output().run(quiet=True)


def get_video_file(folder_name):
    video_file_names = [filename for filename in os.listdir(folder_name) if os.path.splitext(filename)[1] in [".mov", ".mp4", ".gif"]]
    if not video_file_names:
        return None
    video_file_name = video_file_names[0]

    with open(folder_name + "/" + video_file_name, "rb") as f:
        video = f.read()

    return video

def delete_folder(folder_name):
    shutil.rmtree(folder_name)