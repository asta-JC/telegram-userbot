from pyrogram import Client, filters
import asyncio
import re
from datetime import datetime, timedelta, timezone
import httpx
from PIL import Image, ImageDraw, ImageFont
import os
from pyrogram.types import Message
from pydub import AudioSegment
import speech_recognition as sr
from langdetect import detect
from deep_translator import GoogleTranslator

api_id = 22542996
api_hash = "8c7436fa7797dd4527f001a3ff59f269"

app = Client("my_account", api_id=api_id, api_hash=api_hash)


VOICE_DIR = "voices"
os.makedirs(VOICE_DIR, exist_ok=True)

def weather_code_to_emoji(code: int) -> str:
    if code in [0]: return "☀️"
    elif code in [1, 2]: return "🌤"
    elif code in [3]: return "☁️"
    elif code in [45, 48]: return "🌫"
    elif code in [51, 53, 55, 61, 63, 65]: return "🌧"
    elif code in [66, 67, 71, 73, 75, 77, 85, 86]: return "❄️"
    elif code in [95, 96, 99]: return "⛈"
    else: return "🌡"

async def get_andijan_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=40.78&longitude=72.34&current_weather=true"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10.0)
            data = resp.json()
            temp = data["current_weather"]["temperature"]
            code = data["current_weather"]["weathercode"]
            emoji = weather_code_to_emoji(code)
            return f"{emoji} Andijon: {temp}°C"
    except Exception as e:
        print("❌ Ob-havo xatosi:", e)
        return "🌐 Ob-havo topilmadi"

async def update_bio_loop():
    await app.start()
    print("🚀 Bio + rasm + valyuta yangilanishi boshlandi...")

    while True:
        uzbekistan_tz = timezone(timedelta(hours=5))
        now = datetime.now(uzbekistan_tz)
        date_str = now.strftime("%d.%m.%Y")  # Masalan: 22.06.2025
        time_str = now.strftime("%H:%M")
        weekdays_uz = ["Yakshanba", "Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba"]
        weekday_str = weekdays_uz[now.weekday()]  # 0 = Dushanba, 6 = Yakshanba
        weather = await get_andijan_weather()
        bio_text = f"⏰ {time_str} • 📆 {date_str} ({weekday_str}) • {weather}"

        try:
            await app.update_profile(bio=bio_text)
        except Exception as e:
            print(f"⚠️ Bio xatolik: {e}")

        seconds_to_next_minute = 60 - now.second
        await asyncio.sleep(seconds_to_next_minute)

# ==== Voice Transcription ====
@app.on_message(filters.command(["languz", "langen", "langru"]) & filters.reply)
async def transcribe_voice(client: Client, message: Message):
    reply = message.reply_to_message

    if reply.voice:
        audio_file = reply.voice
        ext = "ogg"
    elif reply.audio:
        audio_file = reply.audio
        ext = reply.audio.file_name.split('.')[-1] if reply.audio.file_name else "mp3"
    else:
        await message.reply("Iltimos, bu komandani *voice yoki audio* xabarga reply qilib yuboring.")
        return

    lang_map = {
        "languz": "uz-UZ",
        "langen": "en-US",
        "langru": "ru-RU"
    }
    lang = lang_map.get(message.command[0], "en-US")

    base_name = f"{reply.id}.{ext}"
    input_path = os.path.join(VOICE_DIR, base_name)
    wav_path = os.path.join(VOICE_DIR, f"{reply.id}.wav")

    await client.download_media(audio_file, file_name=input_path)

    try:
        sound = AudioSegment.from_file(input_path)
        sound.export(wav_path, format="wav")
    except Exception as e:
        await message.reply(f"Xatolik: Audio formatni o‘qib bo‘lmadi.\n{e}")
        return

    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language=lang)
        await message.reply(f"📝 **Transkripsiya ({lang}):**\n{text}")
    except Exception as e:
        await message.reply(f"Xatolik: Transkripsiya muvaffaqiyatsiz.\n{e}")

    try:
        os.remove(input_path)
        os.remove(wav_path)
    except:
        pass

# ==== Translate Message ====
@app.on_message(filters.command("translate") & filters.reply)
async def translate_message(client: Client, message: Message):
    reply = message.reply_to_message
    text = reply.text or reply.caption
    if not text:
        await message.reply("Tarjima qilish uchun matn topilmadi.")
        return

    try:
        lang_code = detect(text)
        lang_flag = {
            "en": "\U0001F1EC\U0001F1E7 English",
            "ru": "\U0001F1F7\U0001F1FA Russian",
            "tr": "\U0001F1F9\U0001F1F7 Turkish",
            "fr": "\U0001F1EB\U0001F1F7 French",
            "de": "\U0001F1E9\U0001F1EA German",
            "uz": "\U0001F1FA\U0001F1FF Uzbek",
            "ja": "\U0001F1EF\U0001F1F5 Japanese",
            "ko": "\U0001F1F0\U0001F1F7 Korean",
            "zh-cn": "\U0001F1E8\U0001F1F3 Chinese (Simplified)",
            "zh-tw": "\U0001F1E8\U0001F1F3 Chinese (Traditional)",
            "es": "\U0001F1EA\U0001F1F8 Spanish",
            "it": "\U0001F1EE\U0001F1F9 Italian",
            "pt": "\U0001F1F5\U0001F1F9 Portuguese",
            "pl": "\U0001F1F5\U0001F1F1 Polish",
            "hi": "\U0001F1EE\U0001F1F3 Hindi",
            "ar": "\U0001F1F8\U0001F1E6 Arabic",
            "id": "\U0001F1EE\U0001F1E9 Indonesian",
            "fa": "\U0001F1EE\U0001F1F7 Persian",
            "kk": "\U0001F1F0\U0001F1FF Kazakh",
            "ky": "\U0001F1F0\U0001F1EC Kyrgyz",
            "uk": "\U0001F1FA\U0001F1E6 Ukrainian"
        }.get(lang_code, f"\U0001F310 {lang_code.upper()}")

        translated = GoogleTranslator(source='auto', target='uz').translate(text)
        await message.reply(f"Til: {lang_flag}\nTarjima: {translated}")
    except Exception as e:
        await message.reply(f"Xatolik: tarjima qilinmadi.\n{e}")



@app.on_message()
async def dummy(_, __):
    pass

if __name__ == "__main__":
    app.run(update_bio_loop())
