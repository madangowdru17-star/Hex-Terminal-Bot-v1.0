import logging
import asyncio
import aiohttp
import socket
import json
import random
import string
import subprocess
import re
import os
import sys
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.constants import ParseMode, ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- ⚙️ CONFIGURATION ---
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8687617595:AAGCa0yJTRM52NLItvLkzt7O1mZEkCaNkn4')
ADMIN_ID = int(os.environ.get('ADMIN_ID', '7898928200'))

CHANNEL_1_ID = int(os.environ.get('CHANNEL_1_ID', '-1003240507339'))
CHANNEL_2_ID = int(os.environ.get('CHANNEL_2_ID', '-1003806004135'))

LINK_1 = os.environ.get('LINK_1', 'https://t.me/+dP7xLb3AoE1jNmRl')
LINK_2 = os.environ.get('LINK_2', 'https://t.me/+9vuPcr9LJ8piODdl')

FOOTER = "\n\n<b>⚡ ᴘᴏᴡᴇʀᴇᴅ ʙʏ @Hexh4ckerOFC</b>"
SEP = "━━━━━━━━━━━━━━━━━━━"

# APIs
LOOKUP_API = "https://toxic-tg.vercel.app/?userid="
IFSC_API = "https://ifsc.razorpay.com/"
SHORTLINK_API = "https://link-btpass.onrender.com/bypass?key=9c44ad66b95cef8aecd7a99cfb362ce0&link="
GST_API = "https://gst-0y-vishal.vercel.app/api/gst.js?gstNumber="
PAK_API = "https://api-server-virid-two.vercel.app/number="
IND_NUM_API = "https://all-number-info-rajan-eta.vercel.app/api?number="
IND_NUM_API_3 = "https://exploitsindia.site/track/live.php?term="

VERIFY_SCRIPT = "verify_india.py"

USERS_FILE = os.path.join(os.getcwd(), "users.json")
REDEEM_FILE = os.path.join(os.getcwd(), "redeem_codes.json")
SETTINGS_FILE = os.path.join(os.getcwd(), "settings.json")

DAILY_FREE_CREDITS = 10
INVITE_CREDITS = 3
AUTO_DELETE_TIME = 60

BOT_NAME = "𝗛𝗲𝘅 𝗧𝗲𝗿𝗺𝗶𝗻𝗮𝗹"
BOT_USERNAME = "Hex_Terminal_bot"

# --- PREMIUM EMOJIS FOR MESSAGES ONLY ---
PE = {}  # Premium emoji container

# ⚠️ REPLACE THESE WITH YOUR ACTUAL PREMIUM EMOJI IDs ⚠️
PE['warn'] = '<tg-emoji emoji-id="6267039884016358504">⚠️</tg-emoji>'
PE['crown'] = '<tg-emoji emoji-id="6267039884016358504">👑</tg-emoji>'
PE['star'] = '<tg-emoji emoji-id="6267039884016358504">⭐</tg-emoji>'
PE['fire'] = '<tg-emoji emoji-id="6267039884016358504">🔥</tg-emoji>'
PE['check'] = '<tg-emoji emoji-id="6267039884016358504">✅</tg-emoji>'
PE['cross'] = '<tg-emoji emoji-id="6267039884016358504">❌</tg-emoji>'
PE['lock'] = '<tg-emoji emoji-id="6267039884016358504">🔒</tg-emoji>'
PE['gift'] = '<tg-emoji emoji-id="6267039884016358504">🎁</tg-emoji>'
PE['diamond'] = '<tg-emoji emoji-id="6267039884016358504">💎</tg-emoji>'
PE['rocket'] = '<tg-emoji emoji-id="6267039884016358504">🚀</tg-emoji>'
PE['search'] = '<tg-emoji emoji-id="6267039884016358504">🔍</tg-emoji>'
PE['phone'] = '<tg-emoji emoji-id="6267039884016358504">📞</tg-emoji>'
PE['bank'] = '<tg-emoji emoji-id="6267039884016358504">🏦</tg-emoji>'
PE['link'] = '<tg-emoji emoji-id="6267039884016358504">🔗</tg-emoji>'
PE['car'] = '<tg-emoji emoji-id="6267039884016358504">🚘</tg-emoji>'
PE['card'] = '<tg-emoji emoji-id="6267039884016358504">🪪</tg-emoji>'
PE['user'] = '<tg-emoji emoji-id="6267039884016358504">👤</tg-emoji>'
PE['india'] = '<tg-emoji emoji-id="6267039884016358504">🇮🇳</tg-emoji>'
PE['pak'] = '<tg-emoji emoji-id="6267039884016358504">🇵🇰</tg-emoji>'
PE['mobile'] = '<tg-emoji emoji-id="6267039884016358504">📲</tg-emoji>'
PE['invite'] = '<tg-emoji emoji-id="6267039884016358504">👥</tg-emoji>'
PE['ticket'] = '<tg-emoji emoji-id="6267039884016358504">🎫</tg-emoji>'
PE['credit'] = '<tg-emoji emoji-id="6267039884016358504">💰</tg-emoji>'
PE['refresh'] = '<tg-emoji emoji-id="6267039884016358504">🔄</tg-emoji>'
PE['clock'] = '<tg-emoji emoji-id="6267039884016358504">⏱</tg-emoji>'
PE['bolt'] = '<tg-emoji emoji-id="6267039884016358504">⚡</tg-emoji>'
PE['green'] = '<tg-emoji emoji-id="6267039884016358504">🟩</tg-emoji>'
PE['black'] = '<tg-emoji emoji-id="6267039884016358504">⬛</tg-emoji>'
PE['sparkle'] = '<tg-emoji emoji-id="6267039884016358504">✨</tg-emoji>'
PE['tools'] = '<tg-emoji emoji-id="6267039884016358504">🛠️</tg-emoji>'
PE['disabled'] = '<tg-emoji emoji-id="6267039884016358504">📴</tg-emoji>'

# --- BUTTON EMOJIS (Plain text - works in buttons) ---
BE = {}
BE['phone'] = '📞'
BE['search'] = '🔍'
BE['bank'] = '🏦'
BE['link'] = '🔗'
BE['card'] = '🪪'
BE['user'] = '👤'
BE['india'] = '🇮🇳'
BE['car'] = '🚘'
BE['pak'] = '🇵🇰'
BE['mobile'] = '📲'
BE['invite'] = '👥'
BE['ticket'] = '🎫'
BE['crown'] = '👑'

DISCLAIMER = f"\n\n<b>{PE['warn']} ᴅɪꜱᴄʟᴀɪᴍᴇʀ:</b>\n<i>ᴇᴅᴜᴄᴀᴛɪᴏɴᴀʟ ᴘᴜʀᴘᴏꜱᴇꜱ ᴏɴʟʏ. ᴜꜱᴇ ʀᴇꜱᴘᴏɴꜱɪʙʟʏ.</i>"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

ADMIN_STATE = {}

# --- 💾 DATA FUNCTIONS ---

def load_json(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f: return json.load(f)
    except: return {}

def save_json(filename, data):
    try:
        with open(filename, 'w', encoding='utf-8') as f: json.dump(data, f, indent=2, ensure_ascii=False)
    except: pass

def get_user(user_id):
    users = load_json(USERS_FILE)
    uid = str(user_id)
    today = datetime.now().strftime("%Y-%m-%d")
    if uid not in users:
        users[uid] = {"credits":DAILY_FREE_CREDITS,"total_queries":0,"daily_queries":0,"last_reset":today,"invite_code":f"HEX-{''.join(random.choices(string.ascii_uppercase+string.digits, k=8))}","invites":0,"verified":False}
        save_json(USERS_FILE, users)
    elif users[uid].get("last_reset") != today:
        users[uid]["credits"] = DAILY_FREE_CREDITS
        users[uid]["daily_queries"] = 0
        users[uid]["last_reset"] = today
        save_json(USERS_FILE, users)
    return users[uid]

def save_user(uid, data):
    users = load_json(USERS_FILE); users[str(uid)] = data; save_json(USERS_FILE, users)

def add_credits(uid, amount):
    users = load_json(USERS_FILE); uid = str(uid)
    if uid in users: users[uid]["credits"] = users[uid].get("credits",0) + amount; save_json(USERS_FILE, users); return users[uid]["credits"]
    return 0

def use_credit(uid):
    users = load_json(USERS_FILE); uid = str(uid)
    if uid in users and users[uid].get("credits",0) > 0:
        users[uid]["credits"] -= 1; users[uid]["total_queries"] = users[uid].get("total_queries",0) + 1
        users[uid]["daily_queries"] = users[uid].get("daily_queries",0) + 1; save_json(USERS_FILE, users); return True
    return False

def process_invite(inviter_id, new_id):
    users = load_json(USERS_FILE); inviter = str(inviter_id); new = str(new_id)
    if inviter in users: users[inviter]["credits"] = users[inviter].get("credits",0) + INVITE_CREDITS; users[inviter]["invites"] = users[inviter].get("invites",0) + 1
    if new in users: users[new]["credits"] = users[new].get("credits",0) + INVITE_CREDITS; users[new]["invited_by"] = inviter
    save_json(USERS_FILE, users); return INVITE_CREDITS

def generate_redeem_code(credits):
    code = f"HEX-{''.join(random.choices(string.ascii_uppercase+string.digits, k=10))}"
    codes = load_json(REDEEM_FILE); codes[code] = {"credits":credits,"used":False,"created":datetime.now().isoformat()}
    save_json(REDEEM_FILE, codes); return code

def redeem_code(uid, code):
    codes = load_json(REDEEM_FILE); code = code.upper().strip()
    if code not in codes: return False, "❌ ɪɴᴠᴀʟɪᴅ ᴄᴏᴅᴇ"
    if codes[code].get("used"): return False, "❌ ᴀʟʀᴇᴀᴅʏ ᴜꜱᴇᴅ"
    cr = codes[code]["credits"]; codes[code]["used"] = True; codes[code]["used_by"] = str(uid)
    save_json(REDEEM_FILE, codes); bal = add_credits(uid, cr)
    return True, f"✅ +{cr} ᴄʀᴇᴅɪᴛꜱ ᴀᴅᴅᴇᴅ!\n💰 ʙᴀʟᴀɴᴄᴇ: {bal}"

def get_settings():
    try: return load_json(SETTINGS_FILE)
    except:
        d = {"bypass_maintenance":False,"tgid_enabled":True,"ifsc_enabled":True,"bypass_enabled":True,"mobile_enabled":True,"aadhaar_enabled":True,"rc_enabled":True,"gst_enabled":True,"pak_enabled":True,"indnum_enabled":True,"indnum3_enabled":True,"maintenance_mode":False}
        for k in ["tgid","ifsc","bypass","mobile","aadhaar","rc","gst","pak","indnum","indnum3"]: d[f"maint_msg_{k}"] = "🛠️ Under maintenance."; d[f"maint_{k}"] = False
        save_json(SETTINGS_FILE, d); return d

def save_settings(data): save_json(SETTINGS_FILE, data)

# --- 🔍 VERIFY ---

async def check_channels(uid, context):
    try:
        m1 = await context.bot.get_chat_member(CHANNEL_1_ID, uid)
        m2 = await context.bot.get_chat_member(CHANNEL_2_ID, uid)
        return m1.status in ['member','administrator','creator'] and m2.status in ['member','administrator','creator']
    except: return False

# --- 🛠️ UTILS ---

async def net_ok():
    try: socket.create_connection(("8.8.8.8", 53), timeout=3); return True
    except: return False

async def schedule_delete(msg, delay=AUTO_DELETE_TIME):
    await asyncio.sleep(delay)
    try: await msg.delete()
    except: pass

async def loading_animation(msg, name):
    g = PE['green']; b = PE['black']
    bars = [f"{g}{b*9}",f"{g*2}{b*8}",f"{g*3}{b*7}",f"{g*4}{b*6}",f"{g*5}{b*5}",f"{g*6}{b*4}",f"{g*7}{b*3}",f"{g*8}{b*2}",f"{g*9}{b}",f"{g*10}"]
    percentages = ["0%","10%","20%","30%","40%","50%","60%","70%","80%","90%","100%"]
    for i, bar in enumerate(bars):
        try: await msg.edit_text(f"<blockquote>{PE['bolt']} {name}</blockquote>\n<code>{bar} {percentages[i]}</code>", parse_mode=ParseMode.HTML); await asyncio.sleep(0.2)
        except: break

def check_feature_maintenance(feature_key):
    s = get_settings()
    if s.get(f"maint_{feature_key}", False):
        return True, s.get(f"maint_msg_{feature_key}", "🛠️ Under maintenance.")
    return False, ""

async def show_verification_page(update, context):
    try:
        bot = await context.bot.get_me()
        photos = await context.bot.get_user_profile_photos(bot.id, limit=1)
        caption = (
            f"<b>{PE['bolt']} {BOT_NAME}</b>\n"
            f"<b>@{BOT_USERNAME}</b>\n\n"
            f"<b>{PE['lock']} ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ʀᴇQᴜɪʀᴇᴅ</b>\n"
            f"<b>ᴊᴏɪɴ ʙᴏᴛʜ ᴄʜᴀɴɴᴇʟꜱ ᴛᴏ ᴜɴʟᴏᴄᴋ</b>\n\n"
            f"<b>{PE['warn']} ɢᴜɪᴅᴇʟɪɴᴇꜱ:</b>\n"
            f"<b>• ᴇᴅᴜᴄᴀᴛɪᴏɴᴀʟ ᴘᴜʀᴘᴏꜱᴇꜱ ᴏɴʟʏ</b>\n"
            f"<b>• ᴜꜱᴇ ᴏɴ ʏᴏᴜʀ ᴏᴡɴ ᴅᴀᴛᴀ</b>\n"
            f"<b>• ʀᴇꜱᴘᴇᴄᴛ ᴘʀɪᴠᴀᴄʏ ʟᴀᴡꜱ</b>\n\n"
            f"<b>{PE['gift']} +{DAILY_FREE_CREDITS} ᴅᴀɪʟʏ | {PE['invite']} +{INVITE_CREDITS} ɪɴᴠɪᴛᴇ</b>\n"
            f"<b>{PE['crown']} @Hexh4ckerOFC</b>"
        )
        if photos and photos.photos: sent = await update.message.reply_photo(photo=photos.photos[0][-1].file_id, caption=caption, parse_mode=ParseMode.HTML)
        else: sent = await update.message.reply_text(caption, parse_mode=ParseMode.HTML)
        asyncio.create_task(schedule_delete(sent, 120))
    except: pass
    buttons = [[InlineKeyboardButton("📢 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 𝟷", url=LINK_1)],[InlineKeyboardButton("📢 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 𝟸", url=LINK_2)],[InlineKeyboardButton("✅ ɪ'ᴠᴇ ᴊᴏɪɴᴇᴅ - ᴠᴇʀɪꜰʏ", callback_data="verify")]]
    sent2 = await update.message.reply_text(f"<blockquote>{PE['lock']} ᴊᴏɪɴ ʙᴏᴛʜ ᴄʜᴀɴɴᴇʟꜱ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴠᴇʀɪꜰʏ</blockquote>", reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)
    asyncio.create_task(schedule_delete(sent2, 120))

async def main_menu(update, context):
    """Buttons use PLAIN EMOJIS - Messages use PREMIUM EMOJIS"""
    is_admin = update.effective_user.id == ADMIN_ID
    user = get_user(update.effective_user.id); s = get_settings()
    
    # BUTTONS WITH PLAIN EMOJIS (BE = Button Emoji)
    kb = []
    row = []
    if s.get("tgid_enabled",True): row.append(KeyboardButton(f"{BE['phone']} ᴛɢ ɪᴅ ➜ ɴᴜᴍʙᴇʀ {BE['search']}"))
    if s.get("ifsc_enabled",True): row.append(KeyboardButton(f"{BE['bank']} ɪꜰꜱᴄ ɪɴꜰᴏ➜{BE['search']}"))
    if row: kb.append(row)
    if s.get("bypass_enabled",True): kb.append([KeyboardButton(f"{BE['link']} ʟɪɴᴋ ʙʏᴘᴀꜱꜱ")])
    row2 = []
    if s.get("aadhaar_enabled",True): row2.append(KeyboardButton(f"{BE['card']} ᴀᴀᴅʜᴀʀ ɪɴꜰᴏ➜{BE['user']}"))
    if s.get("mobile_enabled",True): row2.append(KeyboardButton(f"{BE['india']} ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ➜{BE['user']}"))
    if row2: kb.append(row2)
    row3 = []
    if s.get("rc_enabled",True): row3.append(KeyboardButton(f"{BE['car']} ʀᴄ ᴅᴇᴛᴀɪʟꜱ"))
    if s.get("gst_enabled",True): row3.append(KeyboardButton(f"{BE['card']} ɢꜱᴛ ʟᴏᴏᴋᴜᴘ"))
    if row3: kb.append(row3)
    row4 = []
    if s.get("pak_enabled",True): row4.append(KeyboardButton(f"{BE['pak']} ᴘᴀᴋ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ"))
    if s.get("indnum_enabled",True): row4.append(KeyboardButton(f"{BE['mobile']} ɪɴᴅ ɴᴜᴍ ɪɴꜰᴏ 𝟸"))
    if row4: kb.append(row4)
    if s.get("indnum3_enabled",True): kb.append([KeyboardButton(f"{BE['india']} ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ 𝟹 ➜{BE['user']}")])
    kb.append([KeyboardButton(f"{BE['invite']} ɪɴᴠɪᴛᴇ & ᴇᴀʀɴ"), KeyboardButton(f"{BE['ticket']} ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ")])
    if is_admin: kb.append([KeyboardButton(f"{BE['crown']} ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ")])
    
    markup = ReplyKeyboardMarkup(kb, resize_keyboard=True)
    cr = user.get("credits",0)
    
    # MESSAGE WITH PREMIUM EMOJIS (PE = Premium Emoji)
    txt = (
        f"<b>{PE['diamond']} ᴘʀᴇᴍɪᴜᴍ ʜᴜʙ</b>\n"
        f"<b>ᴡᴇʟᴄᴏᴍᴇ</b> <code>{update.effective_user.first_name}</code>\n"
        f"<b>{PE['credit']} ᴄʀ: {cr} | {PE['search']} ǫ: {user.get('total_queries',0)} | {PE['invite']} ɪɴᴠ: {user.get('invites',0)}</b>\n"
        f"<b>{PE['refresh']} +{DAILY_FREE_CREDITS} ᴅᴀɪʟʏ | {PE['clock']} {AUTO_DELETE_TIME}ꜱ</b>\n\n"
        f"<b>ꜱᴇʟᴇᴄᴛ ᴀ ꜱᴇʀᴠɪᴄᴇ ʙᴇʟᴏᴡ</b>"
    )
    
    msg = await update.message.reply_text(txt, reply_markup=markup, parse_mode=ParseMode.HTML)
    asyncio.create_task(schedule_delete(msg, AUTO_DELETE_TIME))

# --- 🔗 API FUNCTIONS (Same as before, using PE for messages) ---

async def safe_api_fetch(session, url, timeout=20):
    for attempt in range(3):
        try:
            headers = {'User-Agent': 'Mozilla/5.0','Accept': '*/*'}
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout), headers=headers, allow_redirects=True) as r:
                text = await r.text()
                if not text: continue
                try: return json.loads(text)
                except: return {"raw_text": text} if text.strip() else None
        except:
            if attempt == 2: return None
            await asyncio.sleep(1)
    return None

async def chatid_lookup(session, query):
    data = await safe_api_fetch(session, f"{LOOKUP_API}{query}")
    if not data: return f"<blockquote>{PE['cross']} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</blockquote>"
    if isinstance(data, dict) and not data.get("raw_text") and data.get("success"):
        d = data.get("data", data)
        if isinstance(d, dict):
            result = f"<blockquote expandable>{PE['sparkle']} {PE['phone']} ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ ɪɴꜰᴏ</blockquote>\n"
            if d.get('chat_id') or d.get('userid'): result += f"<blockquote>🆔 ᴄʜᴀᴛ ɪᴅ: <code>{d.get('chat_id', d.get('userid', query))}</code></blockquote>\n"
            if d.get('number'): result += f"<blockquote>{PE['mobile']} ᴘʜᴏɴᴇ: <code>{d['number']}</code></blockquote>\n"
            if d.get('name'): result += f"<blockquote>{PE['user']} ɴᴀᴍᴇ: <code>{d['name']}</code></blockquote>\n"
            return result
    return f"<blockquote>{PE['cross']} ɴᴏᴛ ꜰᴏᴜɴᴅ</blockquote>"

async def ifsc_lookup(session, code):
    data = await safe_api_fetch(session, f"{IFSC_API}{code.upper()}")
    if not data or isinstance(data, dict) and data.get("raw_text"): return f"<blockquote>{PE['cross']} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</blockquote>"
    if isinstance(data, dict):
        return (f"<blockquote expandable>{PE['sparkle']} {PE['bank']} ɪꜰꜱᴄ ᴅᴇᴛᴀɪʟꜱ</blockquote>\n"
                f"<blockquote>🏛 ʙᴀɴᴋ: <code>{data.get('BANK','N/A')}</code></blockquote>\n"
                f"<blockquote>📍 ʙʀᴀɴᴄʜ: <code>{data.get('BRANCH','N/A')}</code></blockquote>\n"
                f"<blockquote>🔑 ɪꜰꜱᴄ: <code>{data.get('IFSC',code.upper())}</code></blockquote>\n"
                f"<blockquote>📫 ᴀᴅᴅʀᴇꜱꜱ: <code>{data.get('ADDRESS','N/A')}</code></blockquote>")
    return f"<blockquote>{PE['cross']} ɪɴᴠᴀʟɪᴅ</blockquote>"

async def bypass_lookup(session, link):
    s = get_settings()
    if s.get("bypass_maintenance",False): return f"<blockquote>{PE['tools']} ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ</blockquote>"
    data = await safe_api_fetch(session, f"{SHORTLINK_API}{link}", timeout=20)
    if not data or isinstance(data, dict) and data.get("raw_text"): return f"<blockquote>{PE['cross']} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</blockquote>"
    if isinstance(data, dict):
        r = data.get('bypassed_url') or data.get('url') or str(data)
        return f"<blockquote expandable>{PE['sparkle']} {PE['link']} ʙʏᴘᴀꜱꜱᴇᴅ</blockquote>\n<blockquote>🔗 <code>{str(r)}</code></blockquote>"
    return f"<blockquote>🔗 <code>{str(data)}</code></blockquote>"

async def gst_lookup(session, gst_number):
    data = await safe_api_fetch(session, f"{GST_API}{gst_number.upper()}", timeout=20)
    if not data or isinstance(data, dict) and data.get("raw_text"): return f"<blockquote>{PE['cross']} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</blockquote>"
    if isinstance(data, dict) and data.get("status") == "success" and data.get("data"):
        d = data["data"]
        result = f"<blockquote expandable>{PE['sparkle']} {PE['card']} ɢꜱᴛ ɪɴꜰᴏ</blockquote>\n"
        if d.get('TradeName'): result += f"<blockquote>🏢 ɴᴀᴍᴇ: <code>{d['TradeName']}</code></blockquote>\n"
        if d.get('Gstin'): result += f"<blockquote>🔑 ɢꜱᴛ: <code>{d['Gstin']}</code></blockquote>\n"
        return result
    return f"<blockquote>{PE['cross']} ɪɴᴠᴀʟɪᴅ</blockquote>"

async def pakistan_lookup(session, number):
    try:
        data = await safe_api_fetch(session, f"{PAK_API}{number}", timeout=20)
        if not data or isinstance(data, dict) and data.get("raw_text"): return f"<blockquote>{PE['cross']} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</blockquote>"
        if isinstance(data, dict) and data.get("success") and data.get("data"):
            valid = [r for r in data["data"] if isinstance(r, dict) and any(r.get(k) for k in ['name','number','cnic','address'])]
            if not valid: return f"<blockquote>{PE['cross']} ɴᴏ ᴅᴀᴛᴀ</blockquote>"
            result = f"<blockquote expandable>{PE['sparkle']} {PE['pak']} ᴘᴀᴋ ɴᴜᴍʙᴇʀ</blockquote>\n"
            for i, r in enumerate(valid[:3], 1):
                if len(valid) > 1: result += f"\n<blockquote>━━ ʀᴇᴄᴏʀᴅ {i} ━━</blockquote>\n"
                if r.get('number'): result += f"<blockquote>📞: <code>{r['number']}</code></blockquote>\n"
                if r.get('name'): result += f"<blockquote>👤: <code>{r['name']}</code></blockquote>\n"
                if r.get('cnic'): result += f"<blockquote>🪪: <code>{r['cnic']}</code></blockquote>\n"
                if r.get('address'): result += f"<blockquote>📍: <code>{r['address'][:200]}</code></blockquote>\n"
            return result
        return f"<blockquote>{PE['cross']} ɴᴏ ᴅᴀᴛᴀ</blockquote>"
    except: return f"<blockquote>{PE['cross']} ᴇʀʀᴏʀ</blockquote>"

async def indnum_lookup(session, number):
    for attempt in range(3):
        data = await safe_api_fetch(session, f"{IND_NUM_API}{number}", timeout=30)
        if data and isinstance(data, dict) and not data.get("raw_text") and data.get("results"): break
        if attempt < 2: await asyncio.sleep(2)
    if not data or isinstance(data, dict) and data.get("raw_text"): return f"<blockquote>{PE['cross']} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</blockquote>"
    results = data.get("results", {})
    if not results: return f"<blockquote>{PE['cross']} ɴᴏ ʀᴇꜱᴜʟᴛꜱ</blockquote>"
    result = f"<blockquote expandable>{PE['sparkle']} {PE['mobile']} ɪɴᴅ ɴᴜᴍ ᴀᴅᴠᴀɴᴄᴇᴅ</blockquote>\n<blockquote>📞: <code>{number}</code></blockquote>\n"
    found = False
    s3 = results.get("source_3", {}).get("data", {})
    if isinstance(s3, dict):
        for k, e in [("SIM card","💳"),("Connection","📶"),("Mobile State","📍"),("Hometown","🏠")]:
            if s3.get(k): result += f"<blockquote>{e} {k}: <code>{str(s3[k])[:200]}</code></blockquote>\n"; found = True
    s4 = results.get("source_4", {}).get("data", {})
    if isinstance(s4, dict) and s4.get("carrier"): result += f"<blockquote>📡 ᴄᴀʀʀɪᴇʀ: <code>{s4['carrier']}</code></blockquote>\n"; found = True
    return result if found else f"<blockquote>{PE['cross']} ɴᴏ ᴅᴀᴛᴀ</blockquote>"

async def indnum3_lookup(session, number):
    url = f"{IND_NUM_API_3}{number}"
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=25), allow_redirects=True) as r:
            text = await r.text()
            if not text or len(text) < 20: return f"<blockquote>{PE['cross']} ᴇᴍᴘᴛʏ</blockquote>"
            try:
                data = json.loads(text)
                if isinstance(data, dict):
                    result = f"<blockquote expandable>{PE['sparkle']} {PE['india']} ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴛʀᴀᴄᴋɪɴɢ</blockquote>\n<blockquote>📞: <code>{number}</code></blockquote>\n"
                    for k, v in data.items():
                        if v and str(v).strip():
                            result += f"<blockquote>🔹 {k}: <code>{str(v)[:200]}</code></blockquote>\n"
                    return result
            except: pass
            clean = re.sub(r'<[^>]+>', '\n', text)
            lines = [l.strip() for l in clean.split('\n') if l.strip() and len(l.strip()) > 1]
            result = f"<blockquote expandable>{PE['sparkle']} {PE['india']} ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴛʀᴀᴄᴋɪɴɢ</blockquote>\n<blockquote>📞: <code>{number}</code></blockquote>\n"
            found = 0
            for line in lines[:20]:
                if ':' in line:
                    parts = line.split(':', 1)
                    key, val = parts[0].strip(), parts[1].strip() if len(parts) > 1 else ''
                    if val: result += f"<blockquote>🔹 {key}: <code>{val[:200]}</code></blockquote>\n"; found += 1
            if found == 0: result += f"<blockquote>📋 <code>{clean[:500]}</code></blockquote>\n"
            return result
    except: return f"<blockquote>{PE['cross']} ᴛɪᴍᴇᴏᴜᴛ</blockquote>"

# --- 📊 INDIA DATA ---

def clean_text(text):
    if not text: return ""
    return re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)

def run_india_script(choice, value):
    script_path = os.path.join(os.getcwd(), VERIFY_SCRIPT)
    if not os.path.exists(script_path): return None
    try:
        process = subprocess.Popen([sys.executable, script_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=os.getcwd())
        stdout, stderr = process.communicate(f"{choice}\n{value}\n0\n", timeout=45)
        return stdout if stdout and len(stdout) > 20 else None
    except: return None

def parse_all_india_records(raw):
    raw = clean_text(raw) if raw else ""
    if not raw: return []
    records = []
    sections = re.split(r'={5,}|-{5,}|Record\s*\d+[:\s-]*', raw)
    for section in sections:
        section = section.strip()
        if len(section) < 10: continue
        record = {}
        for field, label in {'Name':'👤 ɴᴀᴍᴇ',"Father's Name":'👨 ꜰᴀᴛʜᴇʀ','Mobile':'📱 ᴍᴏʙɪʟᴇ','Address':'📍 ᴀᴅᴅʀᴇꜱꜱ','Circle':'📡 ᴄɪʀᴄʟᴇ','State':'🏛 ꜱᴛᴀᴛᴇ'}.items():
            match = re.search(rf'{re.escape(field)}:\s*([^\n]+)', section, re.IGNORECASE)
            if match and match.group(1).strip() not in ['None','','N/A','null']: record[label] = match.group(1).strip()
        if record:
            seen = set(); unique = {}
            for k, v in record.items():
                if v not in seen: seen.add(v); unique[k] = v
            if unique: records.append(unique)
    final = []; seen = set()
    for r in records:
        combo = tuple(sorted(r.items()))
        if combo not in seen: seen.add(combo); final.append(r)
    return final

def format_records_result(records, search_type):
    if not records: return f"<blockquote>❌ ɴᴏ ʀᴇᴄᴏʀᴅꜱ</blockquote>"
    title = {'aadhaar':'🪪 ᴀᴀᴅʜᴀʀ','mobile':'🇮🇳 ɪɴᴅ ɴᴜᴍʙᴇʀ','vehicle':'🚘 ᴠᴇʜɪᴄʟᴇ'}.get(search_type, '📊 ʀᴇꜱᴜʟᴛ')
    result = f"<blockquote expandable>{PE['sparkle']} {title}</blockquote>\n<blockquote>📊 ʀᴇᴄᴏʀᴅꜱ: {len(records)}</blockquote>\n"
    for i, record in enumerate(records, 1):
        if len(records) > 1: result += f"\n<blockquote>━━ ʀᴇᴄᴏʀᴅ {i} ━━</blockquote>\n"
        for key, value in record.items(): result += f"<blockquote>{key}: <code>{value}</code></blockquote>\n"
    return result

# --- 👑 ADMIN ---

async def admin_panel(update, context):
    if update.effective_user.id != ADMIN_ID: return
    s = get_settings()
    ms = lambda key: "🔴" if s.get(f"maint_{key}") else "🟢"
    kb = [
        [InlineKeyboardButton("🎫 ɢᴇɴ ᴄᴏᴅᴇ", callback_data="ad_gen"), InlineKeyboardButton("📋 ᴄᴏᴅᴇꜱ", callback_data="ad_codes")],
        [InlineKeyboardButton("🎁 ᴀᴅᴅ ᴄʀ", callback_data="ad_credit"), InlineKeyboardButton("📢 ʙᴄᴀꜱᴛ", callback_data="ad_bcast")],
        [InlineKeyboardButton(f"{'🔴' if s.get('maintenance_mode') else '🟢'} ɢʟᴏʙᴀʟ", callback_data="ad_maint")],
        [InlineKeyboardButton(f"{'🟢' if s.get('tgid_enabled',True) else '🔴'} ᴛɢ", callback_data="ad_tgid"), InlineKeyboardButton(f"{ms('tgid')} ᴍ", callback_data="ad_maint_tgid")],
        [InlineKeyboardButton(f"{'🟢' if s.get('ifsc_enabled',True) else '🔴'} ɪꜰ", callback_data="ad_ifsc"), InlineKeyboardButton(f"{ms('ifsc')} ᴍ", callback_data="ad_maint_ifsc")],
        [InlineKeyboardButton(f"{'🟢' if s.get('bypass_enabled',True) else '🔴'} ʙʏ", callback_data="ad_bypass_toggle"), InlineKeyboardButton(f"{ms('bypass')} ᴍ", callback_data="ad_maint_bypass")],
        [InlineKeyboardButton(f"{'🟢' if s.get('mobile_enabled',True) else '🔴'} ᴍᴏ", callback_data="ad_mobile"), InlineKeyboardButton(f"{ms('mobile')} ᴍ", callback_data="ad_maint_mobile")],
        [InlineKeyboardButton(f"{'🟢' if s.get('aadhaar_enabled',True) else '🔴'} ᴀᴀ", callback_data="ad_aadhaar"), InlineKeyboardButton(f"{ms('aadhaar')} ᴍ", callback_data="ad_maint_aadhaar")],
        [InlineKeyboardButton(f"{'🟢' if s.get('rc_enabled',True) else '🔴'} ʀᴄ", callback_data="ad_rc"), InlineKeyboardButton(f"{ms('rc')} ᴍ", callback_data="ad_maint_rc")],
        [InlineKeyboardButton(f"{'🟢' if s.get('gst_enabled',True) else '🔴'} ɢꜱ", callback_data="ad_gst"), InlineKeyboardButton(f"{ms('gst')} ᴍ", callback_data="ad_maint_gst")],
        [InlineKeyboardButton(f"{'🟢' if s.get('pak_enabled',True) else '🔴'} ᴘᴀ", callback_data="ad_pak"), InlineKeyboardButton(f"{ms('pak')} ᴍ", callback_data="ad_maint_pak")],
        [InlineKeyboardButton(f"{'🟢' if s.get('indnum_enabled',True) else '🔴'} ɪɴ2", callback_data="ad_indnum"), InlineKeyboardButton(f"{ms('indnum')} ᴍ", callback_data="ad_maint_indnum")],
        [InlineKeyboardButton(f"{'🟢' if s.get('indnum3_enabled',True) else '🔴'} ɪɴ3", callback_data="ad_indnum3"), InlineKeyboardButton(f"{ms('indnum3')} ᴍ", callback_data="ad_maint_indnum3")],
        [InlineKeyboardButton("❌ ᴄʟᴏꜱᴇ", callback_data="ad_close")]
    ]
    txt = f"<blockquote>👑 ᴀᴅᴍɪɴ</blockquote>\n<blockquote>👥 {len(load_json(USERS_FILE))} | 🎫 {len(load_json(REDEEM_FILE))}</blockquote>"
    if update.callback_query: await update.callback_query.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
    else: await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)

async def admin_callback(update, context):
    q = update.callback_query
    if q.from_user.id != ADMIN_ID: await q.answer("❌"); return
    d = q.data; s = get_settings()
    if d == "ad_close": await q.message.delete()
    elif d == "ad_codes":
        codes = load_json(REDEEM_FILE); txt = f"<blockquote>🎫 {len(codes)}</blockquote>\n"
        for c, v in list(codes.items())[-15:]: txt += f"<blockquote>{'✅' if not v.get('used') else '❌'} <code>{c}</code> | {v.get('credits')}cr</blockquote>\n"
        await q.message.edit_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d == "ad_gen": ADMIN_STATE[q.from_user.id] = "gen"; await q.message.edit_text("<blockquote>🎫 ᴄʀᴇᴅɪᴛꜱ:</blockquote>\n<i>100</i>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d == "ad_credit": ADMIN_STATE[q.from_user.id] = "credit"; await q.message.edit_text("<blockquote>🎁 ɪᴅ ᴀᴍᴏᴜɴᴛ:</blockquote>\n<i>123456789 50</i>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d == "ad_bcast": ADMIN_STATE[q.from_user.id] = "bcast"; await q.message.edit_text("<blockquote>📢 ᴍᴇꜱꜱᴀɢᴇ:</blockquote>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d == "ad_maint": s["maintenance_mode"] = not s.get("maintenance_mode", False); save_settings(s); await q.answer(f"Global: {'ON' if s['maintenance_mode'] else 'OFF'}", show_alert=True); await admin_panel(update, context)
    elif d.startswith("ad_maint_"):
        f = d.replace("ad_maint_", ""); s[f"maint_{f}"] = not s.get(f"maint_{f}", False); save_settings(s); await q.answer(f"{f}: {'ON' if s[f'maint_{f}'] else 'OFF'}", show_alert=True); await admin_panel(update, context)
    elif d.startswith("ad_"):
        toggle_map = {"ad_tgid":"tgid_enabled","ad_ifsc":"ifsc_enabled","ad_bypass_toggle":"bypass_enabled","ad_mobile":"mobile_enabled","ad_aadhaar":"aadhaar_enabled","ad_rc":"rc_enabled","ad_gst":"gst_enabled","ad_pak":"pak_enabled","ad_indnum":"indnum_enabled","ad_indnum3":"indnum3_enabled"}
        if d in toggle_map: k = toggle_map[d]; s[k] = not s.get(k,True); save_settings(s); await q.answer(f"{k}: {'ON' if s[k] else 'OFF'}", show_alert=True)
        await admin_panel(update, context)
    elif d == "ad_back": await admin_panel(update, context)
    await q.answer()

# --- 🚀 HANDLERS ---

async def start(update, context):
    try:
        uid = update.effective_user.id; args = context.args
        if args and args[0].startswith("HEX-"):
            users = load_json(USERS_FILE)
            for inviter, data in users.items():
                if data.get("invite_code") == args[0] and inviter != str(uid):
                    cr = process_invite(inviter, uid)
                    try: await context.bot.send_message(chat_id=int(inviter), text=f"<blockquote>🎉 +{cr} ᴄʀᴇᴅɪᴛꜱ!</blockquote>", parse_mode=ParseMode.HTML)
                    except: pass; break
        user = get_user(uid)
        if not user.get("verified"):
            if await check_channels(uid, context): user["verified"] = True; save_user(uid, user); await main_menu(update, context); return
            await show_verification_page(update, context); return
        await main_menu(update, context)
    except Exception as e: logger.error(f"Start: {e}")

async def verify_cb(update, context):
    q = update.callback_query
    if await check_channels(q.from_user.id, context):
        user = get_user(q.from_user.id); user["verified"] = True; save_user(q.from_user.id, user)
        await q.answer("✅ Verified!")
        try: await q.message.delete()
        except: pass
        await main_menu(update, context)
    else: await q.answer("❌ Join both!", show_alert=True)

async def msg_handler(update, context):
    try:
        uid = update.effective_user.id; txt = update.message.text.strip()
        asyncio.create_task(schedule_delete(update.message, AUTO_DELETE_TIME))
        s = get_settings()
        if s.get("maintenance_mode", False) and uid != ADMIN_ID:
            m = await update.message.reply_text(f"<blockquote>🛠️ Under maintenance</blockquote>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m)); return
        if uid == ADMIN_ID and uid in ADMIN_STATE:
            state = ADMIN_STATE.pop(uid)
            if state == "gen":
                try: cr = int(txt); code = generate_redeem_code(cr); msg = await update.message.reply_text(f"<blockquote>✅ <code>{code}</code> | 💰 {cr}cr</blockquote>", parse_mode=ParseMode.HTML)
                except: msg = await update.message.reply_text("<blockquote>❌ Number</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(msg)); return
            elif state == "credit":
                p = txt.split()
                if len(p) >= 2: bal = add_credits(p[0], int(p[1])); msg = await update.message.reply_text(f"<blockquote>✅ +{p[1]} | {bal}</blockquote>", parse_mode=ParseMode.HTML)
                else: msg = await update.message.reply_text("<blockquote>❌ Format: ID AMOUNT</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(msg)); return
            elif state == "bcast":
                users = load_json(USERS_FILE); cnt = 0
                for u in users:
                    try: await context.bot.send_message(chat_id=int(u), text=f"📢 {txt}"); cnt += 1
                    except: pass
                msg = await update.message.reply_text(f"<blockquote>✅ Sent: {cnt}</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(msg)); return
        user = get_user(uid)
        if not user.get("verified"):
            if await check_channels(uid, context): user["verified"] = True; save_user(uid, user); await main_menu(update, context)
            else: await show_verification_page(update, context)
            return
        
        # BUTTON MATCHING - Use plain text button names
        if txt in [f"{BE['crown']} ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ", f"{BE['crown']} ᴀᴅᴍɪɴ"]: await admin_panel(update, context)
        
        elif txt in [f"{BE['phone']} ᴛɢ ɪᴅ ➜ ɴᴜᴍʙᴇʀ {BE['search']}"]:
            if not s.get("tgid_enabled",True): m=await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("tgid")
            if maint: m=await update.message.reply_text(f"<blockquote>🛠️ {msg}</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'TG'
            btn = [[InlineKeyboardButton("🤖 @ChatIdInfoBot", url="https://t.me/ChatIdInfoBot")]]
            m = await update.message.reply_text(f"<blockquote>{PE['phone']} ᴛɢ ɪᴅ ➜ ɴᴜᴍʙᴇʀ</blockquote>\n<i>7123181749, 6884112825</i>", reply_markup=InlineKeyboardMarkup(btn), parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        
        elif txt in [f"{BE['bank']} ɪꜰꜱᴄ ɪɴꜰᴏ➜{BE['search']}"]:
            if not s.get("ifsc_enabled",True): m=await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("ifsc")
            if maint: m=await update.message.reply_text(f"<blockquote>🛠️ {msg}</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'IFSC'
            m = await update.message.reply_text(f"<blockquote>{PE['bank']} ɪꜰꜱᴄ ᴄᴏᴅᴇ</blockquote>\n<i>SBIN0001234, HDFC0001234</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        
        elif txt in [f"{BE['link']} ʟɪɴᴋ ʙʏᴘᴀꜱꜱ"]:
            if not s.get("bypass_enabled",True): m=await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("bypass")
            if maint: m=await update.message.reply_text(f"<blockquote>🛠️ {msg}</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'SHORTLINK'
            m = await update.message.reply_text(f"<blockquote>{PE['link']} ʟɪɴᴋ ʙʏᴘᴀꜱꜱ</blockquote>\n<i>https://indianshortner.in/xxxx</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        
        elif txt == f"{BE['india']} ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ➜{BE['user']}":
            if not s.get("mobile_enabled",True): m=await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("mobile")
            if maint: m=await update.message.reply_text(f"<blockquote>🛠️ {msg}</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'MOBILE'
            m = await update.message.reply_text(f"<blockquote>{PE['india']} ᴍᴏʙɪʟᴇ ɴᴜᴍʙᴇʀ</blockquote>\n<i>9876543210, 8123456789</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        
        elif txt == f"{BE['card']} ᴀᴀᴅʜᴀʀ ɪɴꜰᴏ➜{BE['user']}":
            if not s.get("aadhaar_enabled",True): m=await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("aadhaar")
            if maint: m=await update.message.reply_text(f"<blockquote>🛠️ {msg}</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'AADHAAR'
            m = await update.message.reply_text(f"<blockquote>{PE['card']} ᴀᴀᴅʜᴀʀ ɴᴜᴍʙᴇʀ</blockquote>\n<i>123456789012</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        
        elif txt == f"{BE['car']} ʀᴄ ᴅᴇᴛᴀɪʟꜱ":
            if not s.get("rc_enabled",True): m=await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("rc")
            if maint: m=await update.message.reply_text(f"<blockquote>🛠️ {msg}</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'VEHICLE'
            m = await update.message.reply_text(f"<blockquote>{PE['car']} ᴠᴇʜɪᴄʟᴇ ɴᴜᴍʙᴇʀ</blockquote>\n<i>KA01AB3256, DL1CX1234</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        
        elif txt == f"{BE['card']} ɢꜱᴛ ʟᴏᴏᴋᴜᴘ":
            if not s.get("gst_enabled",True): m=await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("gst")
            if maint: m=await update.message.reply_text(f"<blockquote>🛠️ {msg}</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'GST'
            m = await update.message.reply_text(f"<blockquote>{PE['card']} ɢꜱᴛ ɴᴜᴍʙᴇʀ</blockquote>\n<i>19BOKPS7056D1ZI</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        
        elif txt == f"{BE['pak']} ᴘᴀᴋ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ":
            if not s.get("pak_enabled",True): m=await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("pak")
            if maint: m=await update.message.reply_text(f"<blockquote>🛠️ {msg}</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'PAK'
            m = await update.message.reply_text(f"<blockquote>{PE['pak']} ᴘᴀᴋ ɴᴜᴍʙᴇʀ</blockquote>\n<i>923078750447</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        
        elif txt == f"{BE['mobile']} ɪɴᴅ ɴᴜᴍ ɪɴꜰᴏ 𝟸":
            if not s.get("indnum_enabled",True): m=await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("indnum")
            if maint: m=await update.message.reply_text(f"<blockquote>🛠️ {msg}</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'INDNUM'
            m = await update.message.reply_text(f"<blockquote>{PE['mobile']} ᴀᴅᴠᴀɴᴄᴇᴅ ɴᴜᴍʙᴇʀ</blockquote>\n<i>6363016966, 9876543210</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        
        elif txt == f"{BE['india']} ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ 𝟹 ➜{BE['user']}":
            if not s.get("indnum3_enabled",True): m=await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("indnum3")
            if maint: m=await update.message.reply_text(f"<blockquote>🛠️ {msg}</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'INDNUM3'
            m = await update.message.reply_text(f"<blockquote>{PE['india']} ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴛʀᴀᴄᴋɪɴɢ</blockquote>\n<i>6363016966, 9876543210</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        
        elif txt in [f"{BE['invite']} ɪɴᴠɪᴛᴇ & ᴇᴀʀɴ", f"{BE['invite']} ɪɴᴠɪᴛᴇ"]:
            user = get_user(uid); bot_username = context.bot.username or BOT_USERNAME
            link = f"https://t.me/{bot_username}?start={user['invite_code']}"
            m = await update.message.reply_text(f"<blockquote>{PE['invite']} ɪɴᴠɪᴛᴇ (+{INVITE_CREDITS}ᴄʀ)</blockquote>\n<blockquote><code>{link}</code></blockquote>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m, 120))
        
        elif txt in [f"{BE['ticket']} ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ"]:
            context.user_data['redeem_mode'] = True
            m = await update.message.reply_text(f"<blockquote>{PE['ticket']} ᴇɴᴛᴇʀ ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ:</blockquote>\n<i>HEX-XXXXXXXXXX</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m, 30))
        
        else:
            if context.user_data.get('redeem_mode'):
                context.user_data['redeem_mode'] = False
                msg = redeem_code(uid, txt)[1] if txt.upper().startswith("HEX-") else "❌ Invalid!"
                m = await update.message.reply_text(f"<blockquote>{msg}</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(m)); return
            
            mode = context.user_data.get('mode')
            if mode:
                if txt.upper().startswith("HEX-"):
                    success, msg = redeem_code(uid, txt)
                    m = await update.message.reply_text(f"<blockquote>{msg}</blockquote>", parse_mode=ParseMode.HTML)
                    asyncio.create_task(schedule_delete(m)); context.user_data['mode'] = None; return
                
                user = get_user(uid)
                if user.get("credits", 0) <= 0:
                    m = await update.message.reply_text(f"<blockquote>{PE['cross']} No credits! +10 daily | +3 invite</blockquote>", parse_mode=ParseMode.HTML)
                    asyncio.create_task(schedule_delete(m)); context.user_data['mode'] = None; return
                
                await run_query(update, context, mode, txt); context.user_data['mode'] = None
    except Exception as e: logger.error(f"Msg: {e}")

async def run_query(update, context, mode, query):
    if not await net_ok():
        m = await update.message.reply_text(f"<blockquote>{PE['cross']} No internet</blockquote>", parse_mode=ParseMode.HTML)
        asyncio.create_task(schedule_delete(m)); return
    
    await update.message.reply_chat_action(ChatAction.TYPING)
    names = {'TG':f'{PE["phone"]}','IFSC':f'{PE["bank"]}','SHORTLINK':f'{PE["link"]}','AADHAAR':f'{PE["card"]}','MOBILE':f'{PE["india"]}','VEHICLE':f'{PE["car"]}','GST':f'{PE["card"]}','PAK':f'{PE["pak"]}','INDNUM':f'{PE["mobile"]}','INDNUM3':f'{PE["india"]}'}
    st = await update.message.reply_text(f"<blockquote>{PE['green']} ꜱᴇᴀʀᴄʜɪɴɢ...</blockquote>", parse_mode=ParseMode.HTML)
    lt = asyncio.create_task(loading_animation(st, names.get(mode, '')))
    credit_deducted = False
    
    try:
        if mode in ['AADHAAR', 'MOBILE', 'VEHICLE']:
            raw = run_india_script({'AADHAAR':'2','MOBILE':'1','VEHICLE':'4'}[mode], query)
            if raw:
                records = parse_all_india_records(raw)
                result = format_records_result(records, {'AADHAAR':'aadhaar','MOBILE':'mobile','VEHICLE':'vehicle'}[mode])
                if records and "❌" not in str(result): use_credit(update.effective_user.id); credit_deducted = True
            else: result = f"<blockquote>{PE['cross']} Script failed</blockquote>"
        else:
            async with aiohttp.ClientSession() as s:
                if mode == 'TG': result = await chatid_lookup(s, query)
                elif mode == 'IFSC': result = await ifsc_lookup(s, query)
                elif mode == 'SHORTLINK': result = await bypass_lookup(s, query)
                elif mode == 'GST': result = await gst_lookup(s, query)
                elif mode == 'PAK': result = await pakistan_lookup(s, query)
                elif mode == 'INDNUM': result = await indnum_lookup(s, query)
                elif mode == 'INDNUM3': result = await indnum3_lookup(s, query)
                else: result = "❌"
            
            if result and "❌" not in str(result) and "unavailable" not in str(result).lower(): use_credit(update.effective_user.id); credit_deducted = True
        
        lt.cancel()
        try: await lt
        except asyncio.CancelledError: pass
        
        user = get_user(update.effective_user.id)
        final = f"{result}\n{SEP}\n<blockquote>{PE['credit']} {'ᴄʀ: '+str(user.get('credits',0)) if credit_deducted else 'ɴᴏ ᴄʀ ᴅᴇᴅᴜᴄᴛᴇᴅ'} | {PE['clock']} {AUTO_DELETE_TIME}ꜱ</blockquote>{DISCLAIMER}{FOOTER}"
        sent = await st.edit_text(final, parse_mode=ParseMode.HTML)
        asyncio.create_task(schedule_delete(sent))
    except Exception as e:
        lt.cancel(); logger.error(f"Query: {e}")
        try: await st.edit_text(f"<blockquote>{PE['warn']} ᴇʀʀᴏʀ</blockquote>{FOOTER}", parse_mode=ParseMode.HTML)
        except: pass

def main():
    print("🔄 Hex Terminal...")
    try: subprocess.run([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4"], capture_output=True, timeout=30)
    except: pass
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify_cb, pattern="^verify$"))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^ad_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg_handler))
    print(f"✅ {BOT_NAME} Ready!")
    print("💎 Premium Emojis in Messages | Plain Emojis in Buttons")
    app.run_polling()

if __name__ == '__main__':
    main()