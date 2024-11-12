# app/controllers/song_generation.py

# default imports
import os
import json
from urllib.parse import urlparse

# module imports
from app.config import get_logger, Settings
from app.utils import get_hash
from app.services.youtube_download.youtube_download import get_youtube_video_id, search_youtube_videos
from app.services.preprocess.preprocess import preprocess_song, get_audio_paths, do_extract_chorus
from app.services.ai_cover.ai_cover import voice_change, add_audio_effects, pitch_shift
from app.services.postprocess.postprocess import combine_audio

logger = get_logger(__name__)


MDX_MODEL_DIR = os.getenv('MDX_MODEL_DIR', 'mdxnet_models')
def song_cover_pipeline(song_input=None, artist_name=None, song_name=None, extract_chorus=True, voice_model=None, pitch_change=0, keep_files=False, 
                        main_gain=0, backup_gain=0, inst_gain=0, index_rate=0.5, filter_radius=3,
                        rms_mix_rate=0.25, f0_method='rmvpe', crepe_hop_length=128, protect=0.33, pitch_change_all=0,
                        reverb_rm_size=0.15, reverb_wet=0.2, reverb_dry=0.8, reverb_damping=0.7, output_format='mp3',
                        ):
    try:
        logger.display_progress('[~] Starting AI Cover Generation Pipeline...', 0)

        # Step 1: Get song id and determine song directory
        # if youtube url
        if song_input is not None and song_input != '':
            if urlparse(song_input).scheme == 'https':
                input_type = 'yt'
                song_id = get_youtube_video_id(song_input)
                if song_id is None:
                    error_msg = 'Invalid YouTube url.'
                    raise Exception(error_msg)

            # local audio file
            else:
                input_type = 'local'
                song_input = song_input.strip('\"')
                if os.path.exists(song_input):
                    song_id = get_hash(song_input)
                else:
                    error_msg = f'{song_input} does not exist.'
                    song_id = None
                    raise Exception(error_msg)

            song_dir = os.path.join(Settings.OUTPUT_DIR, song_id)
        else:
            input_type = 'yt'
            song_dir = os.path.join(Settings.OUTPUT_DIR, f'{artist_name}_{song_name}'.replace(' ', '_'))

        # Step 2: Preprocess song
        # Separate vocals and instrumentals
        if not os.path.exists(song_dir):
            os.makedirs(song_dir)
            orig_song_path, vocals_path, instrumentals_path, main_vocals_path, backup_vocals_path, main_vocals_dereverb_path = preprocess_song(song_input, input_type, song_dir, 
                artist_name=artist_name, song_name=song_name, extract_chorus=extract_chorus)

        else:
            vocals_path, main_vocals_path = None, None
            paths = get_audio_paths(song_dir)

            # if any of the audio files aren't available or keep intermediate files or extracting chorus again, rerun preprocess
            if any(path is None for path in paths) or keep_files or extract_chorus:
                orig_song_path, vocals_path, instrumentals_path, main_vocals_path, backup_vocals_path, main_vocals_dereverb_path = preprocess_song(song_input, input_type, song_dir,
                    artist_name=artist_name, song_name=song_name, extract_chorus=extract_chorus)
            else:
                orig_song_path, instrumentals_path, main_vocals_dereverb_path, backup_vocals_path = paths

        # Step 3: Generate AI Cover
        pitch_change = pitch_change * 12 + pitch_change_all
        ai_vocals_path = os.path.join(song_dir, f'{os.path.splitext(os.path.basename(orig_song_path))[0]}_{voice_model}_p{pitch_change}_i{index_rate}_fr{filter_radius}_rms{rms_mix_rate}_pro{protect}_{f0_method}{"" if f0_method != "mangio-crepe" else f"_{crepe_hop_length}"}.wav')
        ai_cover_path = os.path.join(song_dir, f'{os.path.splitext(os.path.basename(orig_song_path))[0]} ({voice_model} Ver).{output_format}')

        if not os.path.exists(ai_vocals_path):
            logger.display_progress('[~] Converting voice using RVC...', 0.5)
            voice_change(voice_model, main_vocals_dereverb_path, ai_vocals_path, pitch_change, f0_method, index_rate, filter_radius, rms_mix_rate, protect, crepe_hop_length)

        logger.display_progress('[~] Applying audio effects to Vocals...', 0.8)
        ai_vocals_mixed_path = add_audio_effects(ai_vocals_path, reverb_rm_size, reverb_wet, reverb_dry, reverb_damping)

        if pitch_change_all != 0:
            logger.display_progress('[~] Applying overall pitch change', 0.85)
            instrumentals_path = pitch_shift(instrumentals_path, pitch_change_all)
            backup_vocals_path = pitch_shift(backup_vocals_path, pitch_change_all)

        # Step 4: Combine AI Vocals and Instrumentals
        logger.display_progress('[~] Combining AI Vocals and Instrumentals...', 0.9)
        combine_audio([ai_vocals_mixed_path, backup_vocals_path, instrumentals_path], ai_cover_path, main_gain, backup_gain, inst_gain, output_format)

        if not keep_files:
            logger.display_progress('[~] Removing intermediate audio files...', 0.95)
            intermediate_files = [vocals_path, main_vocals_path, ai_vocals_mixed_path]
            if pitch_change_all != 0:
                intermediate_files += [instrumentals_path, backup_vocals_path]
            for file in intermediate_files:
                if file and os.path.exists(file):
                    os.remove(file)

        return ai_cover_path

    except Exception as e:
        raise Exception(str(e))

def search_song_controller(artist_name, song_name):
    try:
        logger.info(f'Searching for song: {song_name} by {artist_name}')
        search_results = search_youtube_videos(artist_name, song_name)
        return search_results

    except Exception as e:
        raise Exception(str(e))

def get_chorus_controller():
    try:
        song_path = os.path.join('/tmp/song_output/450p7goxZqg', 'John Legend - All of Me (Official Video) (Lisa Ver).mp3')
        chorus_path = os.path.join('/tmp/song_output/450p7goxZqg', 'extracted_chorus.mp3')
        do_extract_chorus(song_path, chorus_path)
        return chorus_path

    except Exception as e:
        raise Exception(str(e))