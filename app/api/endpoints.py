# app/api/endpoints.py
from fastapi import APIRouter
from app.config import get_logger, Settings
from app.schemas.song_generation import SongGenerationRequest
from app.controllers.song_generation import song_cover_pipeline, search_song_controller, get_chorus_controller
from fastapi.responses import FileResponse
import os

logger = get_logger(__name__)

router = APIRouter()

@router.get("/")
async def read_root():
    """returns a welcome message"""
    logger.info("Root endpoint accessed")
    return {"message": "Konnichiwa, sekai!"}

@router.get("/voice_models")
async def get_models():
    """returns a list of available voice models"""
    logger.info("Models endpoint accessed")
    models = [f for f in os.listdir(Settings.RVC_MODELS_DIR) if not os.path.isfile(os.path.join(Settings.RVC_MODELS_DIR, f))]
    return {"voice_models": models}

@router.post("/generate-song")
async def generate_song(request: SongGenerationRequest):
    logger.info(f'generate_song: {request.model_dump_json()}')
    ai_cover_path = song_cover_pipeline(**request.model_dump())
    filename = os.path.basename(ai_cover_path)
    return FileResponse(ai_cover_path, media_type='application/octet-stream', filename=filename)

dev_router = APIRouter()

@dev_router.post("/search-song")
async def search_song_router(artist_name: str, song_name: str):
    """searches for a song based on artist name and song name"""
    logger.info(f'Search song endpoint accessed with artist name: {artist_name} and song name: {song_name}')
    search_results = search_song_controller(artist_name, song_name)
    return {"results": search_results}

@dev_router.get("/get-chorus")
async def get_chorus():
    """returns the chorus of a song"""
    logger.info("Get chorus endpoint accessed")
    chorus_path = get_chorus_controller()
    filename = os.path.basename(chorus_path)
    return FileResponse(chorus_path, media_type='application/octet-stream', filename=filename)
