"""KisanSaathi — Voice-Based Multilevel Natural Farming Consultant."""

import logging
import os
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv
from PIL import Image

from modules.llm import get_farming_advice
from modules.mandi import get_mandi_prices
from modules.stt import transcribe_audio
from modules.tts import text_to_speech
from modules.weather import DISTRICTS, get_weather

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent


def _load_prompt(filename: str) -> str:
    path = BASE_DIR / "prompts" / filename
    with open(path, encoding="utf-8") as f:
        return f.read()


DISEASE_PROMPT = _load_prompt("disease_prompt.txt")
WEATHER_MARKET_PROMPT = _load_prompt("weather_market_prompt.txt")

ADVICE_CARD_CSS = """
<div style="
    background: linear-gradient(135deg, #1a2e1a 0%, #243824 100%);
    border: 1px solid #4a7c59;
    border-radius: 16px;
    padding: 20px 24px;
    margin: 12px 0;
    font-family: 'Noto Sans Devanagari', 'Mangal', 'Nirmala UI', sans-serif;
    font-size: 16px;
    line-height: 1.7;
    color: #d4edda;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
">
"""


def _markdown_to_html(text: str) -> str:
    """Convert simple markdown bold to HTML."""
    parts = text.split("**")
    result = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            result.append(f"<strong>{part}</strong>")
        else:
            result.append(part.replace("\n", "<br>"))
    return "".join(result)


def _format_advice_card(text: str) -> str:
    body = _markdown_to_html(text)
    return f"{ADVICE_CARD_CSS}{body}</div>"


def _image_attached(image_filepath: str) -> bool:
    if not image_filepath:
        return False
    try:
        with Image.open(image_filepath) as img:
            img.verify()
        return True
    except Exception:
        return False


def process_disease(audio_filepath, image_filepath):
    """Rog Pahchaan pipeline: STT -> LLM -> TTS."""
    yield "सोच रहा हूँ... / Thinking...", "", None, None

    if not audio_filepath:
        yield (
            "⚠️ Kripya pehle apni awaaz record karein. / Please record your voice first.",
            "",
            _format_advice_card("Kripya microphone se apni samasya batayein."),
            None,
        )
        return

    transcript = transcribe_audio(audio_filepath)
    if not transcript:
        yield (
            "⚠️ Awaaz samajh nahi aayi. Dobara boliye. / Could not understand audio.",
            "",
            _format_advice_card(
                "Maaf kijiye, aapki awaaz samajh nahi aayi. Kripya dobara record karein."
            ),
            None,
        )
        return

    user_text = transcript
    if _image_attached(image_filepath):
        user_text += "\n\nFarmer has also shared a photo of the affected crop/leaf."

    advice = get_farming_advice(user_text, DISEASE_PROMPT)
    advice_html = _format_advice_card(advice)
    audio_out = text_to_speech(advice)

    yield "✅ Salah taiyar hai! / Advice ready!", transcript, advice_html, audio_out


def _weather_icon(condition: str, rain_mm: float) -> str:
    cond_lower = (condition or "").lower()
    if rain_mm and rain_mm > 2:
        return "🌧️"
    if "rain" in cond_lower or "बारिश" in condition or "बौछार" in condition:
        return "🌧️"
    if "cloud" in cond_lower or "बादल" in condition:
        return "⛅"
    if "fog" in cond_lower or "कोहरा" in condition:
        return "🌫️"
    return "☀️"


def _build_weather_card(weather: dict) -> str:
    if weather.get("error"):
        return f"""
        <div style="background:#fff3e0;border-radius:12px;padding:16px;color:#e65100;">
            ⚠️ {weather['error']}
        </div>
        """

    icon = _weather_icon(weather.get("current_condition", ""), weather.get("rain_today_mm", 0))
    forecast_rows = ""
    for day in weather.get("forecast", []):
        rain = day.get("rain_mm", 0) or 0
        day_icon = "🌧️" if rain > 2 else "☀️"
        forecast_rows += f"""
        <tr>
            <td style="padding:6px 12px;color:#e8edf2;">{day_icon} {day.get('date', '')}</td>
            <td style="padding:6px 12px;color:#e8edf2;">🌡️ {day.get('max_temp', '—')}°C / {day.get('min_temp', '—')}°C</td>
            <td style="padding:6px 12px;color:#e8edf2;">💧 {rain} mm</td>
        </tr>
        """

    return f"""
    <div style="
        background: linear-gradient(135deg, #1a2332 0%, #243447 100%);
        border-radius: 16px;
        padding: 20px;
        font-family: 'Noto Sans Devanagari', 'Nirmala UI', sans-serif;
        border: 1px solid #3d5a80;
        color: #e8edf2;
    ">
        <h3 style="margin:0 0 12px 0;color:#7ec8e3;">
            {icon} {weather.get('district', '')} — {weather.get('region', '')} India
        </h3>
        <p style="font-size:18px;margin:8px 0;color:#e8edf2;">
            🌡️ अभी: <strong style="color:#ffffff;">{weather.get('current_temp', '—')}°C</strong>
            &nbsp;|&nbsp; {weather.get('current_condition', '')}
        </p>
        <p style="margin:8px 0;color:#c5d0db;">
            📅 आज: अधिकतम {weather.get('today_max', '—')}°C / न्यूनतम {weather.get('today_min', '—')}°C
            &nbsp;|&nbsp; 💧 बारिश: {weather.get('rain_today_mm', 0)} mm
        </p>
        <table style="width:100%;border-collapse:collapse;margin-top:12px;font-size:14px;color:#e8edf2;">
            <thead>
                <tr style="background:rgba(126,200,227,0.15);">
                    <th style="padding:8px 12px;text-align:left;color:#7ec8e3;">दिन / Day</th>
                    <th style="padding:8px 12px;text-align:left;color:#7ec8e3;">तापमान / Temp</th>
                    <th style="padding:8px 12px;text-align:left;color:#7ec8e3;">बारिश / Rain</th>
                </tr>
            </thead>
            <tbody>{forecast_rows}</tbody>
        </table>
    </div>
    """


def _mandi_to_dataframe(mandi: dict):
    if not mandi:
        return [["—", "—", "—", "—", "—"]]

    crop_labels = {
        "wheat": "गेहूं / Wheat",
        "rice": "चावल / Rice",
        "maize": "मक्का / Maize",
        "tomato": "टमाटर / Tomato",
        "onion": "प्याज / Onion",
        "potato": "आलू / Potato",
        "cotton": "कपास / Cotton",
        "soybean": "सोयाबीन / Soybean",
        "mustard": "सरसों / Mustard",
        "sugarcane": "गन्ना / Sugarcane",
    }

    rows = []
    for crop, info in mandi.items():
        rows.append([
            crop_labels.get(crop, crop),
            info.get("price_per_quintal", "—"),
            info.get("unit", "₹/quintal"),
            info.get("trend", "—"),
            info.get("updated", "today"),
        ])
    return rows


def _format_weather_mandi_prompt(weather: dict, mandi: dict, voice_query: str) -> str:
    lines = [f"District: {weather.get('district', 'Unknown')}", f"Region: {weather.get('region', '')}"]

    if weather.get("error"):
        lines.append(f"Weather error: {weather['error']}")
    else:
        lines.append(f"Current temperature: {weather.get('current_temp')}°C")
        lines.append(f"Condition: {weather.get('current_condition')}")
        lines.append(f"Today max/min: {weather.get('today_max')}°C / {weather.get('today_min')}°C")
        lines.append(f"Rain today: {weather.get('rain_today_mm')} mm")
        lines.append("3-day forecast:")
        for day in weather.get("forecast", []):
            lines.append(
                f"  - {day.get('date')}: max {day.get('max_temp')}°C, "
                f"min {day.get('min_temp')}°C, rain {day.get('rain_mm')} mm"
            )

    lines.append("\nMandi prices for region:")
    for crop, info in mandi.items():
        lines.append(
            f"  - {crop}: ₹{info.get('price_per_quintal')} per quintal, trend: {info.get('trend')}"
        )

    if voice_query:
        lines.append(f"\nFarmer's voice query: {voice_query}")
    else:
        lines.append("\nFarmer did not ask a specific question. Give general advice for today.")

    return "\n".join(lines)


def process_weather_mandi(district, audio_filepath):
    """Mausam & Mandi pipeline."""
    yield "सोच रहा हूँ... / Thinking...", None, None, None, None

    weather = get_weather(district)
    mandi = get_mandi_prices(district)
    weather_html = _build_weather_card(weather)
    mandi_df = _mandi_to_dataframe(mandi)

    voice_query = None
    if audio_filepath:
        voice_query = transcribe_audio(audio_filepath)
        if not voice_query:
            voice_query = None

    prompt_text = _format_weather_mandi_prompt(weather, mandi, voice_query)
    advice = get_farming_advice(prompt_text, WEATHER_MARKET_PROMPT)
    advice_html = _format_advice_card(advice)
    audio_out = text_to_speech(advice)

    yield "✅ Jaankari taiyar hai! / Info ready!", weather_html, mandi_df, advice_html, audio_out


district_choices = list(DISTRICTS.keys())

_api_key = os.environ.get("GROQ_API_KEY", "")
_key_warning = ""
if not _api_key or _api_key == "your_groq_api_key_here":
    _key_warning = """
> ⚠️ **GROQ_API_KEY set nahi hai / API key missing** — Voice aur AI salah ke liye `.env` file mein apni free key daalein: [console.groq.com](https://console.groq.com)
> Mausam & Mandi tab (weather + mandi table) bina key ke kaam karega.
"""

with gr.Blocks(title="KisanSaathi") as demo:
    if _key_warning:
        gr.Markdown(_key_warning)
    gr.Markdown(
        """
        # 🌾 KisanSaathi — आपका डिजिटल किसान साथी
        ### प्राकृतिक खेती के लिए आपका AI सलाहकार
        """
    )

    with gr.Tabs():
        with gr.TabItem("🌿 Rog Pahchaan / रोग पहचान"):
            gr.Markdown(
                """
                **Apni fasal ki samasya batayein / अपनी फसल की समस्या बताएं**
                
                Microphone se record karein (Hindi, Hinglish ya English). Optional: prabhavit patta/fasal ki photo upload karein.
                """
            )
            with gr.Row():
                with gr.Column():
                    disease_audio = gr.Audio(
                        label="🎤 Awaaz Record Karein / Record Voice",
                        sources=["microphone"],
                        type="filepath",
                    )
                    disease_image = gr.Image(
                        label="📷 Photo Upload Karein (Optional) / Upload Photo",
                        type="filepath",
                    )
                    disease_btn = gr.Button("🎤 Salah Lo / सलाह लो", variant="primary")
                with gr.Column():
                    disease_status = gr.Textbox(
                        label="स्थिति / Status",
                        value="तैयार / Ready",
                        interactive=False,
                    )
                    disease_transcript = gr.Textbox(
                        label="लिखित रूप / Transcript",
                        interactive=False,
                        lines=3,
                    )
                    disease_advice = gr.HTML(label="सलाह / Advice")
                    disease_tts = gr.Audio(
                        label="🔊 Hindi Audio / हिंदी ऑडियो",
                        autoplay=True,
                    )

            disease_btn.click(
                fn=process_disease,
                inputs=[disease_audio, disease_image],
                outputs=[disease_status, disease_transcript, disease_advice, disease_tts],
            )

        with gr.TabItem("☀️ Mausam & Mandi / मौसम और मंडी"):
            gr.Markdown(
                """
                **Apne jile ka mausam aur mandi bhav dekhein / अपने जिले का मौसम और मंडी भाव देखें**
                
                Jila chunein. Optional: awaaz se sawal pooch sakte hain.
                """
            )
            weather_district = gr.Dropdown(
                choices=district_choices,
                value=district_choices[0],
                label="🗺️ Jila Chunein / जिला चुनें",
            )
            weather_audio = gr.Audio(
                label="🎤 Sawal Poochhein (Optional) / Ask a Question",
                sources=["microphone"],
                type="filepath",
            )
            weather_btn = gr.Button("☀️ Jaankari Lo / जानकारी लो", variant="primary")
            weather_status = gr.Textbox(
                label="स्थिति / Status",
                value="तैयार / Ready",
                interactive=False,
            )
            weather_card = gr.HTML(label="मौसम / Weather")
            mandi_table = gr.Dataframe(
                headers=["फसल / Crop", "भाव / Price", "इकाई / Unit", "रुझान / Trend", "अपडेट / Updated"],
                label="मंडी भाव / Mandi Prices",
                interactive=False,
            )
            weather_advice = gr.HTML(label="किसान सलाह / Farmer Advice")
            weather_tts = gr.Audio(
                label="🔊 Hindi Audio / हिंदी ऑडियो",
                autoplay=True,
            )

            weather_btn.click(
                fn=process_weather_mandi,
                inputs=[weather_district, weather_audio],
                outputs=[weather_status, weather_card, mandi_table, weather_advice, weather_tts],
            )

    gr.Markdown(
        """
        ---
        *Built for Connecting Dreams Foundation — AI Assignment | Free APIs only*
        """
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        theme=gr.themes.Soft(),
    )
