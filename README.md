# AICoverGen Server
This project aims to develop a FastAPI server capable of processing song references (YouTube link, local directory, YouTube search, and more in the future) to perform voice modification using AI.

The YouTube download and AI Voice Cover generation functionalities are based on the work from [AICoverGen](https://github.com/SociallyIneptWeeb/AICoverGen).

Music Structure Analysis for Chorus Extraction from [all-in-one](https://github.com/mir-aidj/all-in-one/tree/main)

### Getting Started

Follow these steps to set up and run the server:

1. Ensure you have a Python 3.9 environment or virtual environment on Ubuntu.
    ```sh
    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install python3.9 python3.9-dev python3.9-venv
    python3.9 -m venv venv
    source venv/bin/activate
    ```
2. Install FFmpeg:
    ```sh
    sudo apt install -y ffmpeg
    ```
3. Install SoX:
    ```sh
    sudo apt-get -y install sox
    ```
4. Install build-essential:
    ```sh
    sudo apt install build-essential
    ```
5. Install cuDNN if needed
    
    Check for correct cuDNN version and CUDA version, replace it in install_cudnn.sh file
    ```sh
    ./install_cudnn.sh
    ```
6. Install the required Python packages:
    ```sh
    pip install -r app/requirements.txt
    ```

7. download models
    ```sh
    cd app/assets/
    python download_models.py
    cd ../..
    ```
    
8. Start the server:
    ```sh
    uvicorn app.main:app --reload --host 0.0.0.0
    ```

    The server will listen on `localhost:8000` or `<external-public-address>:8000`.

    use POST /generate-song api

    sample payload:
    {
        "artist_name": "John Legend",
        "song_name": "All of me",
        "voice_model": "Lisa",
        "extract_chorus": true,
        "pitch_change": 1
    }


### Tested using:

1 x RTX 4000 Ada

9 vCPU 50 GB RAM

image: runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04