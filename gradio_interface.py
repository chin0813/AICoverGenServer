import gradio as gr
from app.controllers.song_generation import song_cover_pipeline
from app.config import get_logger, Settings
import os

# def song_cover_pipeline(*args, **kwargs):
#     print("song_cover_pipeline")
#     print(args, kwargs)
#     pass

logger = get_logger(__name__)

def get_models():
    rvc_models_dir = os.path.join(os.getcwd(), Settings.RVC_MODELS_DIR)
    models = [f for f in os.listdir(rvc_models_dir) if not os.path.isfile(os.path.join(rvc_models_dir, f))]
    if "LUNA" in models:
        default_model = "LUNA"
    else:
        default_model = models[0]
    return {"voice_models": models, "default_model": default_model}

def save_uploaded_file(uploaded_file):
    print('save_uploaded_file', uploaded_file)
    upload_dir = "/tmp/upload"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())
    return file_path

def generate_function(input_type, uploaded_file, *args, **kwargs):
    new_args = list(args)
    if input_type == "Upload Audio":
        new_args[0] = uploaded_file
    return song_cover_pipeline(*new_args, **kwargs)


with gr.Blocks() as demo:
    gr.Markdown("""# AI Song Cover Generator from Youtube Video""")
    with gr.Row():
        with gr.Column():
            gr.Markdown("""## Input Params""")
            with gr.Blocks():
                input_type = gr.Radio(["Search", "URL", "Upload Audio"], label="Input Type", value="Search")
                song_input = gr.Textbox(label="Youtube URL", visible=False)
                with gr.Row():
                    artist_name = gr.Textbox(label="Artist Name", visible=True)
                    song_name = gr.Textbox(label="Song Name", visible=True)
                uploaded_file = gr.Audio(label="Upload Audio File", type='filepath', sources='upload', interactive=True, visible=False)
                def update_visibility(input_type):
                    if input_type == "Search":
                        return gr.update(visible=False), gr.update(visible=True), gr.update(visible=True), gr.update(visible=False)
                    elif input_type == "URL":
                        return gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)
                    elif input_type == "Upload Audio":
                        return gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=True)

                input_type.change(fn=update_visibility, inputs=input_type, outputs=[song_input, artist_name, song_name, uploaded_file])
                extract_chorus = gr.Checkbox(label="Extract Chorus", value=True)
                voice_model = gr.Dropdown(label="Voice Model", choices=get_models()["voice_models"], value=get_models()["default_model"])
                pitch_change = gr.Slider(label="Main Vocal Pitch Change (Octave)", value=0, step=1, minimum=-2, maximum=2)
            gr.Markdown("""---""")
            gr.Markdown("""## Optional Params""")
            with gr.Blocks():
                index_rate = gr.Slider(label="Index Rate", value=0.5, step=0.1, minimum=0.1, maximum=1)
                filter_radius = gr.Slider(label="Filter Radius", value=3, step=1, minimum=1, maximum=10)
                rms_mix_rate = gr.Slider(label="RMS Mix Rate", value=0.25, step=0.05, minimum=0, maximum=1)
                protect = gr.Slider(label="Protect", value=0.33, step=0.01, minimum=0, maximum=1)
                f0_method = gr.Dropdown(label="F0 Method", choices=["rmvpe", "crepe"], value="rmvpe")
                crepe_hop_length = gr.Slider(label="Crepe Hop Length", value=128, step=1, minimum=1, maximum=512)
                main_gain = gr.Slider(label="Main Gain", value=0, step=0.1, minimum=0, maximum=1)
                backup_gain = gr.Slider(label="Backup Gain", value=0, step=0.1, minimum=0, maximum=1)
                inst_gain = gr.Slider(label="Instrumental Gain", value=0, step=0.1, minimum=0, maximum=1)
                pitch_change_all = gr.Slider(label="Pitch Change (All)", value=0, step=1, minimum=-12, maximum=212)
                keep_files = gr.Checkbox(label="Keep Intermediate Files", value=False)
                reverb_rm_size = gr.Slider(label="Reverb Room Size", value=0.15, step=0.01, minimum=0, maximum=1)
                reverb_wet = gr.Slider(label="Reverb Wet", value=0.2, step=0.01, minimum=0, maximum=1)
                reverb_dry = gr.Slider(label="Reverb Dry", value=0.8, step=0.01, minimum=0, maximum=1)
                reverb_damping = gr.Slider(label="Reverb Damping", value=0.7, step=0.01, minimum=0, maximum=1)
        with gr.Column():
            gr.Markdown("""## Output""")
            gr.Markdown("""---""")
            with gr.Row():
                output_format = gr.Dropdown(label="Output Format", choices=["mp3", "wav"], value="mp3")
                generate_button = gr.Button("Generate Song Cover")
            update_progress = gr.Progress(track_tqdm=True)
            output = gr.Audio(None, type="filepath")

    def display_progress(message="", progress=0):
        update_progress(progress, desc=message)
    logger.display_progress = display_progress
    generate_button.click(fn=generate_function, inputs=[input_type, uploaded_file, uploaded_file if input_type=="Upload Audio" else song_input, artist_name, song_name, extract_chorus, voice_model, pitch_change, keep_files, 
                                                      main_gain, backup_gain, inst_gain, index_rate, filter_radius, rms_mix_rate, f0_method, 
                                                      crepe_hop_length, protect, pitch_change_all, reverb_rm_size, reverb_wet, reverb_dry, 
                                                      reverb_damping, output_format], outputs=output)

demo.launch()