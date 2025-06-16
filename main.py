from pyrogram import Client, filters
import asyncio
import re
from datetime import datetime, timedelta, timezone
import httpx

api_id = 22542996
api_hash = "8c7436fa7797dd4527f001a3ff59f269"

app = Client("my_account", api_id=api_id, api_hash=api_hash)

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

def weather_code_to_emoji(code: int) -> str:
    if code in [0]:
        return "☀️"  # Clear
    elif code in [1, 2]:
        return "🌤"  # Mostly clear
    elif code in [3]:
        return "☁️"  # Overcast
    elif code in [45, 48]:
        return "🌫"  # Fog
    elif code in [51, 53, 55, 61, 63, 65]:
        return "🌧"  # Rain
    elif code in [66, 67, 71, 73, 75, 77, 85, 86]:
        return "❄️"  # Snow
    elif code in [95, 96, 99]:
        return "⛈"  # Thunder
    else:
        return "🌡"  # Unknown

async def update_bio_loop():
    await app.start()
    print("📝 Bio + ob‑havo yangilanishi boshlandi...")

    while True:
        uzbekistan_tz = timezone(timedelta(hours=5))
        now = datetime.now(uzbekistan_tz)
        time_str = now.strftime("%H:%M")
        weather = await get_andijan_weather()
        bio_text = f"⏰ {time_str} • {weather}"

        try:
            await app.update_profile(bio=bio_text)
            print(f"✅ Bio yangilandi: {bio_text}")
        except Exception as e:
            print(f"⚠️ Xatolik: {e}")

        seconds_to_next_minute = 60 - now.second
        await asyncio.sleep(seconds_to_next_minute)
        

# Barcha komandalarni kutib turadi (kerak bo‘lsa boshqa handlerlar ham shu yerda ishlaydi)
@app.on_message()
async def dummy(_, __):
    pass

# Ishga tushurish
if __name__ == "__main__":
    app.run(update_bio_loop())
