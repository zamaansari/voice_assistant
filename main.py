import pvporcupine
import pyaudio
import struct
import pyttsx3
import os
import json
import queue
import vosk
import google.generativeai as genai



# Initialize speech engine
engine = pyttsx3.init()
engine.setProperty("rate", 150)



# Load Vosk model
model = vosk.Model("vosk-model-small-en-us-0.15")
q = queue.Queue()

# Function to speak
def speak(text):
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

# Function to process voice commands
def handle_command(text):
    text = text.lower()
    if "hello" in text:
        speak("Hi, how can I help you?")
    elif "time" in text:
        from datetime import datetime
        now = datetime.now().strftime("%I:%M %p")
        speak(f"The time is {now}")
    elif "open youtube" in text:
        os.system("start https://youtube.com")
        speak("Opening YouTube")
    else:
        speak("activating face recognition")  

# Initialize Porcupine for hotword detection
porcupine = pvporcupine.create(
    access_key="HM/bMvHTIv8zBGbzFYFMJeWg21QtXrPiYUs0smp8aIbe0a6JjgpxnQ==",  
    keywords=["jarvis"]
)

pa = pyaudio.PyAudio()
stream = pa.open(rate=porcupine.sample_rate,
                 channels=1,
                 format=pyaudio.paInt16,
                 input=True,
                 frames_per_buffer=porcupine.frame_length)

print("🎙️ Assistant is listening... Say 'Jarvis'")

# Secondary stream for Vosk
vosk_stream = pa.open(rate=16000, channels=1, format=pyaudio.paInt16, input=True, frames_per_buffer=8192)
recognizer = vosk.KaldiRecognizer(model, 16000)

try:
    while True:
        # Hotword detection
        pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        result = porcupine.process(pcm)

        if result >= 0:
            print("🔓 Wake word detected!")
            speak("Welcome sir, Activating face recognition")

            # Capture next voice input
            print("🎧 Listening for command...")
            vosk_stream.start_stream()
            while True:
                data = vosk_stream.read(4000, exception_on_overflow=False)
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    command_text = result.get("text", "")
                    if command_text:
                        print(f"🗣️ You said: {command_text}")
                        handle_command(command_text)
                        break
except KeyboardInterrupt:
    print("🛑 Stopping assistant...")

finally:
    stream.stop_stream()
    stream.close()
    vosk_stream.stop_stream()
    vosk_stream.close()
    pa.terminate()
    porcupine.delete()
