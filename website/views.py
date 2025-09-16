from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django_ratelimit.decorators import ratelimit
import json
import requests
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest

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

@csrf_exempt
@ratelimit(key='user_or_ip', rate='5/m', block=True)     # 5 requests/minute
@ratelimit(key='user_or_ip', rate='100/d', block=True)   # 100/day
@require_POST
def gemini_proxy(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON body")

    prompt = payload.get("prompt")
    if not prompt:
        return HttpResponseBadRequest("Missing 'prompt'")

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-2.5-flash-preview-05-20:generateContent"
        f"?key={settings.GEMINI_API_KEY}"
    )
    body = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        r = requests.post(url, json=body, timeout=30)
        r.raise_for_status()
    except requests.RequestException as e:
        return JsonResponse({"error": str(e)}, status=502)

    j = r.json()
    # Normalize response to a simple {text: "..."} for the frontend
    text = (
        j.get("candidates", [{}])[0]
         .get("content", {})
         .get("parts", [{}])[0]
         .get("text")
    )

    if not text:
        # Surface model safety blocks / errors if present
        return JsonResponse({"error": "No text in response", "raw": j}, status=502)

    return JsonResponse({"text": text})