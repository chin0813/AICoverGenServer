# AICoverGen Server
This project aims to develop a FastAPI server capable of processing song references (YouTube link, local directory, YouTube search, and more in the future) to perform voice modification using AI.

The YouTube download and AI Voice Cover generation functionalities are based on the work from [AICoverGen](https://github.com/SociallyIneptWeeb/AICoverGen).

### Getting Started

Follow these steps to set up and run the server:

1. Ensure you have a Python 3.9 environment or virtual environment on Ubuntu.
2. Install FFmpeg:
    ```sh
    sudo apt install ffmpeg
    ```
3. Install SoX:
    ```sh
    sudo apt-get -y install sox
    ```
4. Install build-essential:
    ```sh
    sudo apt install build-essential
    ```
5. Install the required Python packages:
    ```sh
    pip install -r app/requirements.txt
    ```
6. Start the server:
    ```sh
    uvicorn app.main:app --reload --host 0.0.0.0
    ```

The server will listen on `localhost:8000` or `<external-public-address>:8000`.