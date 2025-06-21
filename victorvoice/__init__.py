# This file makes the 'victorvoice' directory a Python package.

from .synth import (
    VICTOR_AUDIO_AVAILABLE,
    clone_voice,
    generate_voice,
    save_voice,
    list_voices,
    load_voice_data
)

# print("victorvoice package loaded.")

__all__ = [
    "VICTOR_AUDIO_AVAILABLE",
    "clone_voice",
    "generate_voice",
    "save_voice",
    "list_voices",
    "load_voice_data"
]
