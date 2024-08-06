from gradio2api.gr_fastapi import LocalGradioAppRouter
from fastapi import FastAPI

import numpy as np
import gradio as gr

app = FastAPI()

def sepia(input_img):
    sepia_filter = np.array([
        [0.393, 0.769, 0.189],
        [0.349, 0.686, 0.168],
        [0.272, 0.534, 0.131]
    ])
    sepia_img = input_img.dot(sepia_filter.T)
    sepia_img /= sepia_img.max()
    return sepia_img

demo_sepia = gr.Interface(sepia, gr.Image(), "image",api_name="sepia")

notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def generate_tone(note, octave, duration):
    sr = 48000
    a4_freq, tones_from_a4 = 440, 12 * (octave - 4) + (note - 9)
    frequency = a4_freq * 2 ** (tones_from_a4 / 12)
    duration = int(duration)
    audio = np.linspace(0, duration, duration * sr)
    audio = (20000 * np.sin(audio * (2 * np.pi * frequency))).astype(np.int16)
    return sr, audio

demo_generate_tone = gr.Interface(
    generate_tone,
    [
        gr.Dropdown(notes, type="index"),
        gr.Slider(4, 6, step=1),
        gr.Number(value=1, label="Duration in seconds"),
    ],
    "audio",
    api_name="generate_tone",
)

demo = gr.TabbedInterface(
  interface_list=[demo_sepia, demo_generate_tone],
  tab_names=["sepia", "generate_tone"],
)

router = LocalGradioAppRouter(app=demo)

app = gr.mount_gradio_app(app,demo,path="/gradio")
app.include_router(
  router=router,
  prefix="/api",
)