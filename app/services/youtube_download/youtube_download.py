# app/services/youtube_download/youtube_download.py

# default imports
from contextlib import suppress
from urllib.parse import urlparse, parse_qs

import yt_dlp
import os

def get_youtube_video_id(url, ignore_playlist=True):
    """
    Examples:
    http://youtu.be/SA2iWivDJiE
    http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    http://www.youtube.com/embed/SA2iWivDJiE
    http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    """
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        if query.path[1:] == 'watch':
            return query.query[2:]
        return query.path[1:]

    if query.hostname in {'www.youtube.com', 'youtube.com', 'music.youtube.com'}:
        if not ignore_playlist:
            # use case: get playlist id not current video in playlist
            with suppress(KeyError):
                return parse_qs(query.query)['list'][0]
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
        if query.path[:7] == '/watch/':
            return query.path.split('/')[1]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]

    # returns None for invalid YouTube url
    return None


import yt_dlp
import re

def yt_download(link, artist_name, song_name):
    ydl_opts = {
        'format': 'bestaudio',
        'outtmpl': '/tmp/%(title)s.%(ext)s',
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'no_warnings': True,
        'quiet': True,
        'extractaudio': True,
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
    }
    if link:
        query = link
    else: 
        # Search for song
        query = f'{artist_name} {song_name}'
        ydl_opts['default_search'] = 'ytsearch1'
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(query, download=True)
        if 'entries' in result:
            result = result['entries'][0]
        
        # Sanitize the title
        sanitized_title = yt_dlp.utils.sanitize_filename(result['title'])
        output_path = f'/tmp/{sanitized_title}.mp3'
        
        # Rename the downloaded file
        original_path = f"/tmp/{result['title']}.mp3"
        if os.path.exists(original_path):
            os.rename(original_path, output_path)
        
    return output_path

def search_youtube_videos(artist, song, max_results=10):
    search_query = f"{artist} {song}"
    ydl_opts = {
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'no_warnings': True,
        'quiet': True,
        'skip_download': True,
        'default_search': f'ytsearch{max_results}',  # Set max results in search query
        'format': 'bestaudio/best',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Search and fetch information
        results = ydl.extract_info(search_query, download=False)
        
    # Parse and return top video links and titles
    video_links = [
        (entry['title'], entry['webpage_url']) for entry in results['entries'][:max_results]
    ]
    
    return video_links
