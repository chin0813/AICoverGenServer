# app/config.py
import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

# Load environment variables from .env file
load_dotenv()

class Settings:
    DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    MDX_MODEL_DIR = os.getenv("MDX_MODEL_DIR", "app/assets/mdxnet_models")
    RVC_MODELS_DIR = os.getenv("RVC_MODELS_DIR", "app/assets/rvc_models")
    DEMIX_DIR = os.getenv("DEMIX_DIR", "/tmp/demix")
    SPEC_DIR = os.getenv("SPEC_DIR", "/tmp/spectrogram")
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/tmp/song_output")

def get_logger(name: str = "app"):
    logger = logging.getLogger(name)
    
    if not logger.hasHandlers():
        # Set logging level based on the DEBUG environment variable
        if Settings.DEBUG:
            logger.setLevel(logging.DEBUG)  # Log detailed messages in debug mode
            logger.debug('DEBUG is ON')
        else:
            logger.setLevel(logging.INFO)    # Log normal messages in production mode
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(console_handler)
        
        # Rotating file handler
        file_handler = RotatingFileHandler("app.log", maxBytes=1_000_000, backupCount=5)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(file_handler)

        logger.propagate = False

    def display_progress(message="", progress=0):
        progress = progress * 100
        logger.info(f"Progress: {progress:.2f}% - {message}")
        
    logger.display_progress = display_progress
    
    return logger
