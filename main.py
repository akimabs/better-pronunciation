import os
import json
import time
import shutil
import string
import requests
import numpy as np
import sounddevice as sd
import soundfile as sf
from vosk import Model, KaldiRecognizer
from termcolor import colored
from pydub import AudioSegment
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration Variables
API_KEY = os.getenv("API_KEY")
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-thinking-exp-01-21:generateContent?key={API_KEY}"
MODEL_PATH = os.getenv("MODEL_PATH", "model")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "split_audio")
WORDS_PER_SECOND = float(os.getenv("WORDS_PER_SECOND"))
MIN_RECORD_DURATION = int(os.getenv("MIN_RECORD_DURATION"))
SAMPLERATE = int(os.getenv("SAMPLERATE"))
USER_NAME = os.getenv("USER_NAME")

# Initialize Vosk Model
if not os.path.exists(MODEL_PATH):
    print("❌ Vosk model not found! Download from: https://alphacephei.com/vosk/models")
    exit()
model = Model(MODEL_PATH)

# Clear terminal screen after loading model
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

clear_screen()

def get_ai_conversation():
    print(colored(f"Get AI Conversation....", "white"))
    """Fetch AI-generated conversation from Gemini API."""
    prompt = {
        "contents": [
            {"parts": [{"text": f"""
You are simulating a daily standup meeting at least 1 minutes for a software engineering team with only:
- Scrum Master (AI, facilitates the meeting).
- {USER_NAME} (User, Software Engineer).

The system requires:
- A scalable and concurrent backend to handle high transaction volumes.
- A robust database architecture to ensure data consistency and integrity.
- A user-friendly and performant frontend for seamless payment interactions.

Each participant should give a brief and realistic update based on the standard standup format:
1. What did you work on yesterday?
2. What are you working on today?
3. Any blockers?

Ensure that:
- The updates are **realistic and varied** in each run.
- The tone is **conversational and natural**.
- The response is formatted **strictly** as a JSON array where each entry contains both "AI" and "User" keys.
- **Avoid AI messages that do not have a corresponding User response.**
- Return **ONLY** the JSON array without additional text, explanations, current name and role, or formatting issues.
                """}]}]
    }
    
    response = requests.post(API_URL, headers={"Content-Type": "application/json"}, json=prompt)
    
    if response.status_code != 200:
        print(colored(f"❌ API Error: {response.status_code} - {response.text}", "red"))
        return []
    
    try:
        response_json = response.json()
        text_response = response_json["candidates"][0]["content"]["parts"][0]["text"].strip("```json").strip("```").strip()
        ai_conversation = json.loads(text_response)
        
        return [(entry["AI"], entry["User"]) for entry in ai_conversation if "AI" in entry and "User" in entry]
    except Exception as e:
        print(colored(f"❌ Error parsing API response: {e}", "red"))
        return []

def calculate_dynamic_duration(text):
    """Calculate duration based on word count, ensuring minimum duration."""
    return max(round(len(text.split()) / WORDS_PER_SECOND, 2), MIN_RECORD_DURATION)

def record_audio(filename, duration):
    """Record user audio for a given duration."""
    print(f"\n🎤 Speak for {duration} seconds...")
    audio_data = sd.rec(int(SAMPLERATE * duration), samplerate=SAMPLERATE, channels=1, dtype=np.int16)
    sd.wait()
    sf.write(filename, audio_data, SAMPLERATE)
    print("✅ Recording complete!")

def transcribe_audio(file_path):
    """Transcribe audio using Vosk."""
    try:
        with sf.SoundFile(file_path) as wf:
            recognizer = KaldiRecognizer(model, wf.samplerate)
            with open(file_path, "rb") as f:
                recognizer.AcceptWaveform(f.read())
                result = json.loads(recognizer.Result())
            return result.get("text", "")
    except Exception as e:
        print(colored(f"❌ Error in transcription: {e}", "red"))
        return ""

def transcribe_with_timestamps(file_path):
    """Transcribe audio with word-level timestamps."""
    try:
        with sf.SoundFile(file_path) as wf:
            recognizer = KaldiRecognizer(model, wf.samplerate)
            recognizer.SetWords(True)
            with open(file_path, "rb") as f:
                recognizer.AcceptWaveform(f.read())
                result = json.loads(recognizer.Result())
            return result.get("result", [])
    except Exception as e:
        print(f"Error in transcription: {e}")
        return []

def split_audio_per_word(audio_file, words):
    """Split audio into separate files per word."""
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    audio = AudioSegment.from_wav(audio_file)
    word_files = []
    
    for i, word in enumerate(words):
        segment = audio[int(word["start"] * 1000):int(word["end"] * 1000)]
        output_file = os.path.join(OUTPUT_DIR, f"word_{i + 1}_{word['word']}.wav")
        segment.export(output_file, format="wav")
        word_files.append(output_file)    
    return word_files

def normalize_text(text):
    """Normalize text by removing punctuation and converting to lowercase."""
    return text.translate(str.maketrans('', '', string.punctuation)).lower()

def evaluate_pronunciation(transcribed_text, correct_text):
    """Compare transcribed text with expected text and highlight mistakes."""
    transcribed_words = normalize_text(transcribed_text).split()
    correct_words = normalize_text(correct_text).split()
    
    mistakes = [(w1, w2) for w1, w2 in zip(transcribed_words, correct_words) if w1 != w2]
    
    highlighted_text = " ".join(
        [colored(w, "red") if w1 != w2 else colored(w, "green")
         for w, w1, w2 in zip(transcribed_words, transcribed_words, correct_words)]
    )
    
    return mistakes, highlighted_text

# Main Program
conversations = get_ai_conversation() or [
    ("AI: Hello! How are you today?", "I'm good, thank you!"),
    ("AI: What's your name?", f"My name is {USER_NAME}."),
]

for ai_text, user_expected in conversations:
    print(f"\n🤖 {colored(ai_text, 'cyan')}")
    time.sleep(1)
    print(f"\n🎯 Now say: {colored(user_expected, 'yellow')}")
    input("Press ENTER to start recording...")
    
    audio_file = "recorded_audio.wav"
    record_audio(audio_file, duration=calculate_dynamic_duration(user_expected))
    
    transcribed_text = transcribe_audio(audio_file)
    mistakes, highlighted_transcription = evaluate_pronunciation(transcribed_text, user_expected)
    words = transcribe_with_timestamps(audio_file)
    
    if words:
        split_audio_per_word(audio_file, words)
        print("✅ Audio split per word!")
    else:
        print("❌ No words detected.")
    
    print("\n=== PRONUNCIATION RESULTS ===")
    print(f"📌 Expected: {colored(user_expected, 'cyan')}")
    print(f"🎤 Spoken: {highlighted_transcription}")
    print(f"❌ Mistakes: {mistakes if mistakes else colored('No mistakes!', 'green')}")
    
    print(colored("✅ Great! Moving to the next conversation.", "green") if not mistakes else colored("⚠️ Try again!", "red"))
    print("\n--- Session Complete ---\n")