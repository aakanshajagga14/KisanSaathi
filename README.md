# 🌾 KisanSaathi

**Voice-Based Multilevel Natural Farming Consultant for Indian farmers transitioning to organic/natural farming.**

KisanSaathi is a hackathon prototype that gives farmers instant, voice-first advice on crop diseases (with organic-only remedies) and combined weather + mandi market intelligence — all in Hindi/Hinglish.

---

## Problem Statement

Indian farmers moving from chemical to natural/organic farming often lack timely, trustworthy guidance. Extension officers are scarce, and generic internet advice pushes pesticides and synthetic inputs. Farmers need **instant organic farming guidance via voice** — in their own language, on their phone — covering disease identification, weather-aware decisions, and market timing.

---

## Tech Stack

| Tool | Purpose | Cost |
|------|---------|------|
| Gradio | Web UI (Blocks API) | Free |
| Groq Whisper (`whisper-large-v3-turbo`) | Speech-to-text (Hindi/English/Hinglish) | Free |
| Groq LLaMA (`llama-3.3-70b-versatile`) | Farming advice LLM | Free |
| gTTS | Hindi text-to-speech | Free |
| Open-Meteo API | Live weather forecasts | Free |
| Local JSON | Mandi (market) price data | Free |
| Pillow | Image file validation | Free |

---

## Features Implemented

1. **🌿 Rog Pahchaan (Disease Identification & Treatment)** — Record voice symptoms, optional crop photo note, get structured organic remedy advice with Hindi audio playback.
2. **☀️ Mausam & Mandi (Weather & Market Intelligence)** — Select district, view live weather + regional mandi prices, get actionable farming advice with Hindi audio.

---

## How to Run Locally

```bash
git clone https://github.com/aakanshajagga14/KisanSaathi.git
cd KisanSaathi
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GROQ_API_KEY from https://console.groq.com
python app.py
```

Open the URL shown in the terminal (typically `http://127.0.0.1:7860`).

---

## Deploy on Hugging Face Spaces (Recommended)

> **Note:** GitHub Pages only hosts static websites (HTML/CSS). KisanSaathi is a Python Gradio app with server-side API calls, so it **cannot** run on GitHub Pages. Use Hugging Face Spaces instead (free).

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Choose **SDK: Gradio**, visibility **Public**
3. Connect your GitHub repo `aakanshajagga14/KisanSaathi` **or** upload these files
4. Under **Settings → Repository secrets**, add:
   - Name: `GROQ_API_KEY`
   - Value: your Groq API key from [console.groq.com](https://console.groq.com)
5. Hugging Face auto-builds and deploys. Your live app will be at:
   `https://huggingface.co/spaces/<your-username>/KisanSaathi`

No code changes needed — `app.py` at the repo root is auto-detected.

---

## Prompt Design

**Why strict organic-only guardrails:** Farmers transitioning to natural farming are vulnerable to reverting to chemicals when stressed. The system prompt explicitly bans synthetic pesticides and fertilizers, and whitelists known organic remedies (neem, jeevamrit, panchgavya, etc.) so the LLM stays on-mission.

**Why structured Hindi output format:** Farmers scan advice quickly in the field. Fixed sections (रोग/समस्या, कारण, जैविक उपाय, बचाव, KVK सलाह) make responses predictable and easy to hear via TTS.

**Why under-150-word responses:** Long LLM answers are hard to listen to on a phone speaker in a noisy farm environment. Short, structured answers improve comprehension and reduce TTS latency.

---

## Localization Approach

- **STT + TTS:** Groq Whisper auto-detects Hindi, Hinglish, and English; gTTS reads responses back in Hindi (`lang="hi"`).
- **UI:** All labels are bilingual (Hindi + English) for farmers and evaluators.
- **Weather:** 20 major farming districts mapped to lat/lng with live Open-Meteo data (timezone `Asia/Kolkata`).
- **Mandi prices:** Region-based (North/South/East/West/Central) dummy data reflecting realistic crop price spreads across India.

---

## Architecture

```
Farmer Voice (mic)
       │
       ▼
  ┌─────────┐
  │  STT    │  Groq Whisper (whisper-large-v3-turbo)
  └────┬────┘
       │ transcript (+ optional image note / weather+mandi context)
       ▼
  ┌─────────┐
  │  LLM    │  Groq LLaMA 3.3 70B + system prompt guardrails
  └────┬────┘
       │ structured Hindi advice
       ▼
  ┌─────────┐
  │  TTS    │  gTTS (Hindi MP3)
  └────┬────┘
       │
       ▼
  Gradio UI (HTML card + autoplay audio)
```

Tab 2 additionally pulls **Open-Meteo** (weather) and **local mandi JSON** (prices) before the LLM step.

---

## Limitations & Future Scope

- **Dummy mandi data** — prices are hardcoded by region, not live AGMARKNET/e-NAM feeds.
- **No real vision model** — uploaded crop photos only add a text note to the prompt; no actual disease detection from images.
- **No offline support** — requires internet for Groq API, Open-Meteo, and gTTS.
- **Hindi STT accuracy** — depends on Whisper quality; English/Hinglish generally works well, but heavy regional dialects may need fine-tuning or a dedicated Hindi ASR model.

---

*Built for Connecting Dreams Foundation — AI Assignment*
