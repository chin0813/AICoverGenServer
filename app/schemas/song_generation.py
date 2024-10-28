# app/schemas/song_generation.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class SongGenerationRequest(BaseModel):
    song_input: str = Field(description='Link to a YouTube video or the filepath to a local mp3/wav file to create an AI cover of')
    voice_model: str = Field(description='Name of the folder in the rvc_models directory containing the RVC model file and optional index file to use')
    pitch_change: int = Field(description='Change the pitch of AI Vocals only. Generally, use 1 for male to female and -1 for vice-versa. (Octaves)')
    keep_files: Optional[bool] = Field(default=False, description='Whether to keep all intermediate audio files generated in the song_output/id directory, e.g. Isolated Vocals/Instrumentals')
    index_rate: Optional[float] = Field(default=0.5, description='A decimal number used to reduce/resolve the timbre leakage problem. If set to 1, more biased towards the timbre quality of the training dataset')
    filter_radius: Optional[int] = Field(default=3, description='A number between 0 and 7. If >=3: apply median filtering to the harvested pitch results. The value represents the filter radius and can reduce breathiness.')
    rms_mix_rate: Optional[float] = Field(default=0.25, description="Control how much to use the original vocal's loudness (0) or a fixed loudness (1).")
    pitch_detection_algo: Optional[str] = Field(default='rmvpe', description='Best option is rmvpe (clarity in vocals), then mangio-crepe (smoother vocals).')
    crepe_hop_length: Optional[int] = Field(default=128, description='If pitch detection algo is mangio-crepe, controls how often it checks for pitch changes in milliseconds.')
    protect: Optional[float] = Field(default=0.33, description='Protect voiceless consonants and breath sounds to prevent artifacts. Set to 0.5 to disable. Decrease to increase protection, but may reduce indexing accuracy.')
    main_vol: Optional[int] = Field(default=0, description='Volume change for AI main vocals in decibels.')
    backup_vol: Optional[int] = Field(default=0, description='Volume change for backup vocals in decibels.')
    inst_vol: Optional[int] = Field(default=0, description='Volume change for instrumentals in decibels.')
    pitch_change_all: Optional[int] = Field(default=0, description='Change the pitch/key of vocals and instrumentals. Changing this slightly reduces sound quality.')
    reverb_size: Optional[float] = Field(default=0.15, description='Reverb room size between 0 and 1')
    reverb_wetness: Optional[float] = Field(default=0.2, description='Reverb wet level between 0 and 1')
    reverb_dryness: Optional[float] = Field(default=0.8, description='Reverb dry level between 0 and 1')
    reverb_damping: Optional[float] = Field(default=0.7, description='Reverb damping between 0 and 1')
    output_format: Optional[str] = Field(default='mp3', description='Output format of audio file. mp3 for smaller file size, wav for best quality')

    @field_validator('index_rate')
    def check_index_rate(cls, v):
        if v is not None and not (0.0 <= v <= 1.0):
            raise ValueError('index_rate must be between 0.0 and 1.0')
        return v

    @field_validator('filter_radius')
    def check_filter_radius(cls, v):
        if v is not None and not (0 <= v <= 7):
            raise ValueError('filter_radius must be between 0 and 7')
        return v

    @field_validator('rms_mix_rate')
    def check_rms_mix_rate(cls, v):
        if v is not None and not (0.0 <= v <= 1.0):
            raise ValueError('rms_mix_rate must be between 0.0 and 1.0')
        return v

    @field_validator('protect')
    def check_protect(cls, v):
        if v is not None and not (0.0 <= v <= 1.0):
            raise ValueError('protect must be between 0.0 and 1.0')
        return v

    @field_validator('reverb_size')
    def check_reverb_size(cls, v):
        if v is not None and not (0.0 <= v <= 1.0):
            raise ValueError('reverb_size must be between 0.0 and 1.0')
        return v

    @field_validator('reverb_wetness')
    def check_reverb_wetness(cls, v):
        if v is not None and not (0.0 <= v <= 1.0):
            raise ValueError('reverb_wetness must be between 0.0 and 1.0')
        return v

    @field_validator('reverb_dryness')
    def check_reverb_dryness(cls, v):
        if v is not None and not (0.0 <= v <= 1.0):
            raise ValueError('reverb_dryness must be between 0.0 and 1.0')
        return v

    @field_validator('reverb_damping')
    def check_reverb_damping(cls, v):
        if v is not None and not (0.0 <= v <= 1.0):
            raise ValueError('reverb_damping must be between 0.0 and 1.0')
        return v
