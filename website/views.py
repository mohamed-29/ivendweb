from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
import json

import telebot
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser, InputPeerChannel
from telethon import TelegramClient, sync, events
import asyncio
from telethon import TelegramClient

import os
from dotenv import load_dotenv

load_dotenv()

API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SESSION_NAME = "bot_session"





async def _send_bot_message(user_or_username: str, message: str):
    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as bot:
        # This logs in AS THE BOT (no phone number asked)
        await bot.start(bot_token=BOT_TOKEN)

        # user_or_username must be something like "@Mohamed_H_29" or a numeric user id
        # if isinstance(user_or_username, str) and not user_or_username.startswith("@"):
        #     user_or_username = "@" + user_or_username

        await bot.send_message(user_or_username, message)
        bot.disconnect()


def send_bot_message(user_or_username: str, message: str):
    asyncio.run(_send_bot_message(user_or_username, message))

def index(request):
    """
    This view renders the main index page and passes the 
    Gemini API key from the Django settings into the template context.
    """
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            message = request.POST.get('message')
            # Process the data (e.g., save to database, send email)
            # print(f"Received contact form submission: Name={name}, Email={email}, Phone={phone}, Message={message}")
            
            telegram_message = f"New contact form submission:\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}"
            send_bot_message("+201002111162", telegram_message) # Replace with your Telegram username or chat ID
            return redirect('index')
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    
    context = {
        'GEMINI_API_KEY': settings.GEMINI_API_KEY
    }
    return render(request, 'index.html', context)
