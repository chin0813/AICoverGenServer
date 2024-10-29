from pathlib import Path
import requests
import os
import urllib
import zipfile
import shutil
import json

MDX_DOWNLOAD_LINK = 'https://github.com/TRvlvr/model_repo/releases/download/all_public_uvr_models/'
RVC_DOWNLOAD_LINK = 'https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/'

BASE_DIR = Path(__file__).resolve().parent
print('BASE_DIR:', BASE_DIR)
mdxnet_models_dir = BASE_DIR / 'mdxnet_models'
rvc_models_dir = BASE_DIR / 'rvc_models'


def dl_model(link, model_name, dir_name):
    with requests.get(f'{link}{model_name}') as r:
        r.raise_for_status()
        with open(dir_name / model_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

def extract_zip(extraction_folder, zip_name):
    os.makedirs(extraction_folder)
    with zipfile.ZipFile(zip_name, 'r') as zip_ref:
        zip_ref.extractall(extraction_folder)
    os.remove(zip_name)

    index_filepath, model_filepath = None, None
    for root, dirs, files in os.walk(extraction_folder):
        for name in files:
            if name.endswith('.index') and os.stat(os.path.join(root, name)).st_size > 1024 * 100:
                index_filepath = os.path.join(root, name)

            if name.endswith('.pth') and os.stat(os.path.join(root, name)).st_size > 1024 * 1024 * 40:
                model_filepath = os.path.join(root, name)

    if not model_filepath:
        raise Exception(f'No .pth model file was found in the extracted zip. Please check {extraction_folder}.')

    # move model and index file to extraction folder
    os.rename(model_filepath, os.path.join(extraction_folder, os.path.basename(model_filepath)))
    if index_filepath:
        os.rename(index_filepath, os.path.join(extraction_folder, os.path.basename(index_filepath)))

    # remove any unnecessary nested folders
    for filepath in os.listdir(extraction_folder):
        if os.path.isdir(os.path.join(extraction_folder, filepath)):
            shutil.rmtree(os.path.join(extraction_folder, filepath))

def download_online_model(url, dir_name):
    try:
        print(f'[~] Downloading voice model with name {dir_name}...')
        zip_name = url.split('/')[-1]
        extraction_folder = os.path.join(rvc_models_dir, dir_name)
        if os.path.exists(extraction_folder):
            raise Exception(f'Voice model directory {dir_name} already exists! Choose a different name for your voice model.')

        if 'pixeldrain.com' in url:
            url = f'https://pixeldrain.com/api/file/{zip_name}'

        urllib.request.urlretrieve(url, zip_name)

        print('[~] Extracting zip...')
        extract_zip(extraction_folder, zip_name)
        return f'[+] {dir_name} Model successfully downloaded!'

    except Exception as e:
        print("Unable to download", e)


if __name__ == '__main__':
    mdx_model_names = ['UVR-MDX-NET-Voc_FT.onnx', 'UVR_MDXNET_KARA_2.onnx', 'Reverb_HQ_By_FoxJoy.onnx']
    for model in mdx_model_names:
        print(f'Downloading {model}...')
        dl_model(MDX_DOWNLOAD_LINK, model, mdxnet_models_dir)

    rvc_model_names = ['hubert_base.pt', 'rmvpe.pt']
    for model in rvc_model_names:
        print(f'Downloading {model}...')
        dl_model(RVC_DOWNLOAD_LINK, model, rvc_models_dir)

    print('All models downloaded!')
    print('Downloading character models...')
    public_models = None
    with open(os.path.join(rvc_models_dir, 'public_models.json'), 'r') as f:
        public_models = json.load(f)
    if public_models is not None:
        voice_models = public_models.get("voice_models", [])
        for voice_model in voice_models:
            download_online_model(voice_model["url"], voice_model["name"])
