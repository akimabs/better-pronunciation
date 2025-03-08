# Terminal Based Speech Pronunciation Trainer

![alt text](https://raw.githubusercontent.com/akimabs/better-pronunciation/refs/heads/main/demo.gif "Demo")

## 📌 Description

This project is a **Terminal Based Speech Pronunciation Trainer** that uses **Vosk** for speech-to-text transcription, **Google Gemini API** for conversation simulation. The system helps users improve their English pronunciation by engaging in interactive conversations and providing real-time feedback on their pronunciation.

## 🛠️ Features

- 🔹 **AI-driven conversation simulation** using the Gemini API.
- 🔹 **Voice recording** and automatic transcription with Vosk.
- 🔹 **Pronunciation evaluation** with highlighted errors.
- 🔹 **Audio splitting per word** for detailed analysis.

---

## 🚀 Installation

Before running the project, make sure you have **Python 3.x** installed and activate a virtual environment (**venv**).

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/akimabs/better-pronunciation.git
cd better-pronunciation
```

### 2️⃣ Create & Activate Virtual Environment

##### Linux/macOS

```bash
python -m venv venv
source venv/bin/activate
```

##### Windows

```bash
python -m venv pronunciation_better
venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Download Vosk Model

Download a Vosk model from [Vosk Models](https://alphacephei.com/vosk/models) and extract it into the project folder.
Example for the English model:

```bash
mkdir model
wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
unzip vosk-model-en-us-0.22.zip -d model
```

### 5️⃣ Set Up Gemini API Key

Replace **API_KEY** in the code with your Google Gemini API Key.

### 6️⃣ Run the Program

```bash
python main.py
```

---

## 📝 Configuration

Some adjustable parameters:

- `API_KEY` → Google Gemini API Key.
- `model_path` → Path to the Vosk model.
- `words_per_second` → Speaking speed used to determine recording duration.
- `samplerate` → Audio recording sample rate.

---

## 📂 Project Structure

```
📦 speech-pronunciation-trainer
├── 📂 model                # Vosk model folder
├── 📂 split_audio          # Folder for split audio files
├── 📂 venv                 # Folder for virtual env python
├── 📜 main.py              # Main script
├── 📜 requirements.txt     # Dependencies
├── 📜 .gitignore           # Ignore unnecessary files
└── 📜 README.md            # Documentation
```

---

## 📌 License

This project is released under the **MIT** license.

---

✅ **Happy pronunciation practice!** 🎤
