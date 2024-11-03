# app/services/preprocess/preprocess.py

# default imports
import os
import json
import shlex
import subprocess
import allin1.analyze
import librosa
import numpy as np

# module imports
from app.config import get_logger, Settings
from app.services.youtube_download.youtube_download import yt_download
from app.services.preprocess.mdx import run_mdx

import allin1

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning, module="natten.functional")

logger = get_logger(__name__)

mdx_model_params = None
with open(os.path.join(Settings.MDX_MODEL_DIR, 'model_data.json')) as infile:
    mdx_model_params = json.load(infile)

def get_audio_paths(song_dir):
    orig_song_path = None
    instrumentals_path = None
    main_vocals_dereverb_path = None
    backup_vocals_path = None

    for file in os.listdir(song_dir):
        if file.endswith('_Instrumental.wav'):
            instrumentals_path = os.path.join(song_dir, file)
            orig_song_path = instrumentals_path.replace('_Instrumental', '')

        elif file.endswith('_Vocals_Main_DeReverb.wav'):
            main_vocals_dereverb_path = os.path.join(song_dir, file)

        elif file.endswith('_Vocals_Backup.wav'):
            backup_vocals_path = os.path.join(song_dir, file)

    return orig_song_path, instrumentals_path, main_vocals_dereverb_path, backup_vocals_path

def convert_to_stereo(audio_path):
    wave, sr = librosa.load(audio_path, mono=False, sr=44100)

    # check if mono
    if type(wave[0]) != np.ndarray:
        stereo_path = f'{os.path.splitext(audio_path)[0]}_stereo.wav'
        command = shlex.split(f'ffmpeg -y -loglevel error -i "{audio_path}" -ac 2 -f wav "{stereo_path}"')
        subprocess.run(command)
        return stereo_path
    else:
        return audio_path

def preprocess_song(song_input, input_type, song_output_dir, artist_name=None, song_name=None, extract_chorus=True):
    keep_orig = False
    if input_type == 'yt':
        logger.display_progress('[~] Downloading song...', 0)
        song_link = song_input.split('&')[0] if song_input else None
        orig_song_path = yt_download(song_link, artist_name, song_name)
    elif input_type == 'local':
        orig_song_path = song_input
        keep_orig = True
    else:
        orig_song_path = None

    logger.info(f'orig_song_path: {orig_song_path}')
    
    if extract_chorus:
        chorus_path = os.path.join(song_output_dir, f'{os.path.basename(orig_song_path).replace(".wav", "")}_Chorus.wav')
        do_extract_chorus(orig_song_path, chorus_path)
        orig_song_path = chorus_path

    orig_song_path = convert_to_stereo(orig_song_path)

    logger.display_progress('[~] Separating Vocals from Instrumental...', 0.1)
    vocals_path, instrumentals_path = run_mdx(mdx_model_params, song_output_dir, os.path.join(Settings.MDX_MODEL_DIR, 'UVR-MDX-NET-Voc_FT.onnx'), orig_song_path, denoise=True, keep_orig=keep_orig)

    logger.display_progress('[~] Separating Main Vocals from Backup Vocals...', 0.2)
    backup_vocals_path, main_vocals_path = run_mdx(mdx_model_params, song_output_dir, os.path.join(Settings.MDX_MODEL_DIR, 'UVR_MDXNET_KARA_2.onnx'), vocals_path, suffix='Backup', invert_suffix='Main', denoise=True)

    logger.display_progress('[~] Applying DeReverb to Vocals...', 0.3)
    _, main_vocals_dereverb_path = run_mdx(mdx_model_params, song_output_dir, os.path.join(Settings.MDX_MODEL_DIR, 'Reverb_HQ_By_FoxJoy.onnx'), main_vocals_path, invert_suffix='DeReverb', exclude_main=True, denoise=True)

    return orig_song_path, vocals_path, instrumentals_path, main_vocals_path, backup_vocals_path, main_vocals_dereverb_path

def do_extract_chorus(audio_path, chorus_path, padding=3, max_duration=30, choose_longest=False):
    result = allin1.analyze(audio_path, demix_dir=Settings.DEMIX_DIR, spec_dir=Settings.SPEC_DIR)
    chorus_info = []
    if result.segments:
        chorus_info = [s for s in result.segments if s.label == 'chorus']
    logger.info(f'Chorus segments: {chorus_info}')
    if not chorus_info:
        raise Exception("No chorus found in the song")

    # Merge back-to-back chorus segments
    merged_chorus_segments = []
    current_segment = chorus_info[0]
    for segment in chorus_info[1:]:
        # Calculate the potential new end time with padding
        potential_end = max(current_segment.end, segment.end) + padding
        potential_start = max(current_segment.start - padding, 0)
        potential_duration = potential_end - potential_start

        if segment.start <= (current_segment.end + padding) and potential_duration <= max_duration:
            current_segment.end = max(current_segment.end, segment.end)
        else:
            merged_chorus_segments.append(current_segment)
            current_segment = segment
    merged_chorus_segments.append(current_segment)

    if choose_longest:
        # Find the longest merged chorus segment
        logger.info(f'Extracting longest chorus from {audio_path} to {chorus_path}')
        longest_chorus_segment = max(merged_chorus_segments, key=lambda s: s.end - s.start)
        # Extract the longest chorus segment
        chorus_start = max(longest_chorus_segment.start - padding, 0)
        chorus_end = longest_chorus_segment.end + padding
        chorus_duration = min(chorus_end - chorus_start, max_duration)
    else:
        # Extract the first merged chorus segment
        logger.info(f'Extracting first chorus from {audio_path} to {chorus_path}')
        chorus_start = max(merged_chorus_segments[0].start - padding, 0)
        chorus_end = merged_chorus_segments[0].end + padding
        chorus_duration = min(chorus_end - chorus_start, max_duration)
    command = shlex.split(f'ffmpeg -y -loglevel error -i "{audio_path}" -ss {chorus_start} -t {chorus_duration} "{chorus_path}"')
    subprocess.run(command)