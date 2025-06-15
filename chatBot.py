from pyrogram import Client

api_id = 22542996  # https://my.telegram.org
api_hash = "8c7436fa7797dd4527f001a3ff59f269"

with Client("my_account", api_id=api_id, api_hash=api_hash) as app:
    print("Session created.")
