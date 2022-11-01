import validators
from validators import ValidationFailure
import os
import ffmpeg

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
    
    files_to_delete = [video_name, output_video_name, "ffmpeg2pass-0.log", "ffmpeg2pass-0.log.mbtree"]
    for file in files_to_delete:
        os.remove(file)
    
    return compressed_video
    

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
    ffmpeg.output(i, os.devnull,
                  **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 1, 'f': 'mp4'}
                  ).overwrite_output().run(quiet=True)
    ffmpeg.output(i, output_file_name,
                  **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 2, 'c:a': 'aac', 'b:a': audio_bitrate}
                  ).overwrite_output().run(quiet=True)
