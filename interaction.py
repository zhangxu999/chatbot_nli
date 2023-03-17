import requests
import json
import whisper
import torch
import pyaudio
import wave
from pydub import AudioSegment
from gtts import gTTS
import os

# OPEN AI WHISPER
#DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DEVICE = "cpu"

# GETTING SOUND
# Define constants for PyAudio
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5

# Create an instance of PyAudio
audio = pyaudio.PyAudio()

# Open the microphone stream
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK_SIZE)

# Record audio
frames = []
print("Listening...")
for i in range(0, int(RATE / CHUNK_SIZE * RECORD_SECONDS)):
    data = stream.read(CHUNK_SIZE)
    frames.append(data)

# Close the microphone stream
stream.stop_stream()
stream.close()

# Terminate PyAudio
audio.terminate()

# Save the recorded audio to a WAV file
wave_file = wave.open("recorded_audio.wav", "wb")
wave_file.setnchannels(CHANNELS)
wave_file.setsampwidth(audio.get_sample_size(FORMAT))
wave_file.setframerate(RATE)
wave_file.writeframes(b"".join(frames))
wave_file.close()

# Convert the WAV file to an MP3 file
wav_audio = AudioSegment.from_wav("recorded_audio.wav")
wav_audio.export("recorded_audio.mp3", format="mp3")

# RASA
headers = {
    "Content-Type": "application/json"
}

# Whisper
model = whisper.load_model("base", DEVICE)
result = model.transcribe("recorded_audio.mp3")


audio = whisper.load_audio("recorded_audio.mp3")
audio = whisper.pad_or_trim(audio)

text_input = result["text"]
mel = whisper.log_mel_spectrogram(audio)

_, probs = model.detect_language(mel)
lang_detected = max(probs, key=probs.get)

if lang_detected != "en":
    res = model.transcribe("recorded_audio.mp3", task = "translate")
    text_input = res["text"]


data = {
    "sender": "test_user",
    "message": text_input
}


response = requests.post("http://0.0.0.0:5005/webhooks/rest/webhook", json=data, headers=headers)


try:
    text = response.json()[0]['text']
    response.raise_for_status()
    print(text)
    tts = gTTS(text, lang=lang_detected)
    tts.save("respuesta_rasa.mp3")
    print(data["message"])
    print(response.json())
    response

except:
    texto = "ERROR"
    tts = gTTS(texto, lang=lang_detected)
    tts.save("respuesta_rasa.mp3")


os.system("mpg321 respuesta_rasa.mp3")
