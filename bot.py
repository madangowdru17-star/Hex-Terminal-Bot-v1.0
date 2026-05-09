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
LOOKUP_API = "https://tgchatid.vercel.app/api/lookup?number="
IFSC_API = "https://ifsc.razorpay.com/"
SHORTLINK_API = "https://link-btpass.onrender.com/bypass?key=9c44ad66b95cef8aecd7a99cfb362ce0&link="
GST_API = "https://osint-info.great-site.net/api/gst_lookup.php?gstNumber="
PAK_API = "https://api-server-virid-two.vercel.app/number="

VERIFY_SCRIPT = "verify_india.py"

USERS_FILE = "users.json"
REDEEM_FILE = "redeem_codes.json"
SETTINGS_FILE = "settings.json"

DAILY_FREE_CREDITS = 10
INVITE_CREDITS = 3
AUTO_DELETE_TIME = 60

BOT_NAME = "𝗛𝗲𝘅 𝗧𝗲𝗿𝗺𝗶𝗻𝗮𝗹"
BOT_USERNAME = "Hex_Terminal_bot"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

MAIN_MENU_MESSAGE_IDS = set()
ADMIN_STATE = {}

# --- 💾 DATA FUNCTIONS ---

def load_json(filename):
    try:
        with open(filename, 'r') as f: return json.load(f)
    except: return {}

def save_json(filename, data):
    try:
        with open(filename, 'w') as f: json.dump(data, f, indent=2)
    except: pass

def get_user(user_id):
    users = load_json(USERS_FILE)
    uid = str(user_id)
    today = datetime.now().strftime("%Y-%m-%d")
    if uid not in users:
        users[uid] = {"credits":DAILY_FREE_CREDITS,"total_queries":0,"daily_queries":0,"last_reset":today,"invite_code":f"HEX-{''.join(random.choices(string.ascii_uppercase+string.digits, k=8))}","invites":0,"verified":False}
        save_json(USERS_FILE, users)
    elif users[uid].get("last_reset") != today:
        users[uid]["credits"] = users[uid].get("credits",0) + DAILY_FREE_CREDITS
        users[uid]["daily_queries"] = 0; users[uid]["last_reset"] = today
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
    try:
        with open(SETTINGS_FILE, 'r') as f: return json.load(f)
    except:
        d = {"bypass_maintenance":False,"bypass_msg":"Bypass maintenance.","tgid_enabled":True,"ifsc_enabled":True,"bypass_enabled":True,"mobile_enabled":True,"aadhaar_enabled":True,"rc_enabled":True,"gst_enabled":True,"pak_enabled":True,"maintenance_mode":False,"maintenance_msg":"🛠️ This feature is under maintenance."}
        save_settings(d); return d

def save_settings(data):
    with open(SETTINGS_FILE, 'w') as f: json.dump(data, f, indent=2)

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

async def auto_del(msg, delay=AUTO_DELETE_TIME):
    await asyncio.sleep(delay)
    try:
        if msg.message_id not in MAIN_MENU_MESSAGE_IDS: await msg.delete()
    except: pass

async def delete_user_msg(msg, delay=AUTO_DELETE_TIME):
    await asyncio.sleep(delay)
    try: await msg.delete()
    except: pass

async def loading_animation(msg, name):
    bars = ["🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛","🟩🟩⬛⬛⬛⬛⬛⬛⬛⬛","🟩🟩🟩⬛⬛⬛⬛⬛⬛⬛","🟩🟩🟩🟩⬛⬛⬛⬛⬛⬛","🟩🟩🟩🟩🟩⬛⬛⬛⬛⬛","🟩🟩🟩🟩🟩🟩⬛⬛⬛⬛","🟩🟩🟩🟩🟩🟩🟩⬛⬛⬛","🟩🟩🟩🟩🟩🟩🟩🟩⬛⬛","🟩🟩🟩🟩🟩🟩🟩🟩🟩⬛","🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩"]
    percentages = ["0%","10%","20%","30%","40%","50%","60%","70%","80%","90%","100%"]
    for i, bar in enumerate(bars):
        try: await msg.edit_text(f"<blockquote>⚡ {name}</blockquote>\n<code>{bar} {percentages[i]}</code>", parse_mode=ParseMode.HTML); await asyncio.sleep(0.2)
        except: break

async def show_verification_page(update, context):
    try:
        bot = await context.bot.get_me()
        photos = await context.bot.get_user_profile_photos(bot.id, limit=1)
        caption = (
            f"<b>╭━━━━━━━━━━━━━━━━━━━━━╮</b>\n"
            f"<b>┃   🤖 {BOT_NAME}   ┃</b>\n"
            f"<b>┃   @{BOT_USERNAME}       ┃</b>\n"
            f"<b>╰━━━━━━━━━━━━━━━━━━━━━╯</b>\n\n"
            f"<b>🔒 ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ʀᴇQᴜɪʀᴇᴅ</b>\n"
            f"<b>ᴊᴏɪɴ ʙᴏᴛʜ ᴄʜᴀɴɴᴇʟꜱ ᴛᴏ ᴜɴʟᴏᴄᴋ</b>\n\n"
            f"<b>🎁 +{DAILY_FREE_CREDITS} ᴅᴀɪʟʏ | 👥 +{INVITE_CREDITS} ɪɴᴠɪᴛᴇ</b>\n"
            f"<b>⏱ {AUTO_DELETE_TIME}ꜱ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ</b>\n\n"
            f"<b>👑 @Hexh4ckerOFC</b>"
        )
        if photos and photos.photos: 
            sent = await update.message.reply_photo(photo=photos.photos[0][-1].file_id, caption=caption, parse_mode=ParseMode.HTML)
        else: 
            sent = await update.message.reply_text(caption, parse_mode=ParseMode.HTML)
        asyncio.create_task(auto_del(sent, 120))
    except: pass
    
    buttons = [
        [InlineKeyboardButton("📢 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 𝟷", url=LINK_1)],
        [InlineKeyboardButton("📢 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 𝟸", url=LINK_2)],
        [InlineKeyboardButton("✅ ɪ'ᴠᴇ ᴊᴏɪɴᴇᴅ - ᴠᴇʀɪꜰʏ ɴᴏᴡ", callback_data="verify")]
    ]
    sent2 = await update.message.reply_text("<blockquote>🔒 ᴊᴏɪɴ ʙᴏᴛʜ ᴄʜᴀɴɴᴇʟꜱ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴠᴇʀɪꜰʏ</blockquote>", reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)
    asyncio.create_task(auto_del(sent2, 120))

async def main_menu(update, context):
    is_admin = update.effective_user.id == ADMIN_ID
    user = get_user(update.effective_user.id); s = get_settings()
    
    kb = []
    row = []
    if s.get("tgid_enabled",True): row.append(KeyboardButton("ᴛɢ ɪᴅ ➜ 📞 ɴᴜᴍʙᴇʀ 🔍"))
    if s.get("ifsc_enabled",True): row.append(KeyboardButton("🏦 ɪꜰꜱᴄ ɪɴꜰᴏ➜🔎"))
    if row: kb.append(row)
    if s.get("bypass_enabled",True): kb.append([KeyboardButton("🔗 ʟɪɴᴋ ʙʏᴘᴀꜱꜱ")])
    row2 = []
    if s.get("aadhaar_enabled",True): row2.append(KeyboardButton("🪪 ᴀᴀᴅʜᴀʀ ɪɴꜰᴏ➜👤"))
    if s.get("mobile_enabled",True): row2.append(KeyboardButton("🇮🇳 ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ➜👤"))
    if row2: kb.append(row2)
    row3 = []
    if s.get("rc_enabled",True): row3.append(KeyboardButton("🚘 ʀᴄ ᴅᴇᴛᴀɪʟꜱ"))
    if s.get("gst_enabled",True): row3.append(KeyboardButton("📋 ɢꜱᴛ ʟᴏᴏᴋᴜᴘ"))
    if row3: kb.append(row3)
    if s.get("pak_enabled",True): kb.append([KeyboardButton("🇵🇰 ᴘᴀᴋ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ")])
    kb.append([KeyboardButton("👥 ɪɴᴠɪᴛᴇ & ᴇᴀʀɴ"), KeyboardButton("🎫 ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ")])
    if is_admin: kb.append([KeyboardButton("👑 ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ")])
    
    markup = ReplyKeyboardMarkup(kb, resize_keyboard=True)
    cr = user.get("credits",0); total = user.get("total_queries",0); invites = user.get("invites",0)
    
    txt = (
        f"<b>╭━━━━━━━━━━━━━━━━━━━━━╮</b>\n"
        f"<b>┃   🤖 {BOT_NAME}   ┃</b>\n"
        f"<b>┃   @{BOT_USERNAME}       ┃</b>\n"
        f"<b>╰━━━━━━━━━━━━━━━━━━━━━╯</b>\n\n"
        f"<b>👋 ᴡᴇʟᴄᴏᴍᴇ ʙᴀᴄᴋ,</b> <code>{update.effective_user.first_name}</code>\n\n"
        f"<b>📊 ʏᴏᴜʀ ꜱᴛᴀᴛɪꜱᴛɪᴄꜱ:</b>\n"
        f"<b>┃ 💰 ᴄʀᴇᴅɪᴛꜱ: {cr}</b>\n"
        f"<b>┃ 📊 Qᴜᴇʀɪᴇꜱ: {total}</b>\n"
        f"<b>┃ 👥 ɪɴᴠɪᴛᴇꜱ: {invites}</b>\n\n"
        f"<b>🛠️ ᴀᴠᴀɪʟᴀʙʟᴇ ʜᴀᴄᴋɪɴɢ ᴛᴏᴏʟꜱ:</b>\n"
        f"<b>📱 ᴛɢ ɪᴅ ➜ ɴᴜᴍʙᴇʀ  │  🏦 ɪꜰꜱᴄ ʙᴀɴᴋ</b>\n"
        f"<b>🔗 ʟɪɴᴋ ʙʏᴘᴀꜱꜱ  │  🇮🇳 ᴍᴏʙɪʟᴇ ᴏꜱɪɴᴛ</b>\n"
        f"<b>🪪 ᴀᴀᴅʜᴀʀ ɪɴꜰᴏ  │  🚘 ʀᴄ ᴠᴇʜɪᴄʟᴇ</b>\n"
        f"<b>📋 ɢꜱᴛ ʟᴏᴏᴋᴜᴘ  │  🇵🇰 ᴘᴀᴋ ɴᴜᴍʙᴇʀ</b>\n\n"
        f"<b>🔄 ᴅᴀɪʟʏ +{DAILY_FREE_CREDITS} ᴄʀ  │  👥 ɪɴᴠɪᴛᴇ +{INVITE_CREDITS} ᴄʀ</b>\n"
        f"<b>⏱ ᴀʟʟ ᴍꜱɢ ᴅᴇʟᴇᴛᴇ ɪɴ {AUTO_DELETE_TIME}ꜱ</b>\n\n"
        f"<b>👑 ᴏᴡɴᴇʀ: @Hexh4ckerOFC</b>"
    )
    
    msg = await update.message.reply_text(txt, reply_markup=markup, parse_mode=ParseMode.HTML)
    MAIN_MENU_MESSAGE_IDS.add(msg.message_id)

# --- 🔗 API ---

async def api_fetch(session, url, timeout=15):
    try:
        headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json, text/plain, */*'}
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout), headers=headers) as r:
            text = await r.text()
            if not text: return None
            try: return json.loads(text)
            except: return None
    except: return None

async def chatid_lookup(session, query):
    data = await api_fetch(session, f"{LOOKUP_API}{query}")
    if not data: return "<blockquote>❌ ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</blockquote>"
    if isinstance(data, dict) and data.get("success"):
        d = data.get("data", {})
        result = "<blockquote expandable>✨ 📱 ᴛɢ ɪᴅ ➜ ɴᴜᴍʙᴇʀ</blockquote>\n"
        if d.get('chat_id'): result += f"<blockquote>🆔 ᴄʜᴀᴛ ɪᴅ: <code>{d['chat_id']}</code></blockquote>\n"
        if d.get('number'): result += f"<blockquote>📞 ɴᴜᴍʙᴇʀ: <code>{d['number']}</code></blockquote>\n"
        if d.get('country'): result += f"<blockquote>🌍 ᴄᴏᴜɴᴛʀʏ: <code>{d['country']}</code></blockquote>\n"
        if d.get('country_code'): result += f"<blockquote>📋 ᴄᴏᴅᴇ: <code>{d['country_code']}</code></blockquote>\n"
        return result
    return "<blockquote>❌ ɴᴏᴛ ꜰᴏᴜɴᴅ</blockquote>"

async def ifsc_lookup(session, code):
    data = await api_fetch(session, f"{IFSC_API}{code.upper()}")
    if not data: return "<blockquote>❌ ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</blockquote>"
    if isinstance(data, dict):
        return (f"<blockquote expandable>✨ 🏦 ɪꜰꜱᴄ ʙᴀɴᴋ ɪɴꜰᴏ</blockquote>\n"
                f"<blockquote>🏛 ʙᴀɴᴋ: <code>{data.get('BANK','N/A')}</code></blockquote>\n"
                f"<blockquote>📍 ʙʀᴀɴᴄʜ: <code>{data.get('BRANCH','N/A')}</code></blockquote>\n"
                f"<blockquote>🔑 ɪꜰꜱᴄ: <code>{data.get('IFSC',code.upper())}</code></blockquote>\n"
                f"<blockquote>📫 ᴀᴅᴅʀᴇꜱꜱ: <code>{data.get('ADDRESS','N/A')}</code></blockquote>")
    return "<blockquote>❌ ɪɴᴠᴀʟɪᴅ</blockquote>"

async def bypass_lookup(session, link):
    s = get_settings()
    if s.get("bypass_maintenance",False): return "<blockquote>🛠️ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ</blockquote>"
    data = await api_fetch(session, f"{SHORTLINK_API}{link}", timeout=20)
    if not data: return "<blockquote>❌ ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</blockquote>"
    if isinstance(data, dict):
        r = data.get('bypassed_url') or data.get('url') or str(data)
        return f"<blockquote expandable>✨ 🔗 ʙʏᴘᴀꜱꜱᴇᴅ</blockquote>\n<blockquote>🔗 <code>{str(r)}</code></blockquote>"
    return f"<blockquote>🔗 <code>{str(data)}</code></blockquote>"

async def gst_lookup(session, gst_number):
    data = await api_fetch(session, f"{GST_API}{gst_number.upper()}", timeout=20)
    if not data: return "<blockquote>❌ ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</blockquote>"
    if isinstance(data, dict):
        if data.get("error"): return f"<blockquote>❌ {data.get('error', 'Invalid GST')}</blockquote>"
        d = data.get('data', data)
        if not isinstance(d, dict): d = data
        result = "<blockquote expandable>✨ 📋 ɢꜱᴛ ʟᴏᴏᴋᴜᴘ</blockquote>\n"
        found_any = False
        for field in ['tradeName', 'legalName', 'businessName', 'name', 'lgnm']:
            if d.get(field): result += f"<blockquote>🏢 ɴᴀᴍᴇ: <code>{d[field]}</code></blockquote>\n"; found_any = True; break
        for field in ['gstNumber', 'gstin', 'gst_no', 'GSTIN']:
            if d.get(field): result += f"<blockquote>🔑 ɢꜱᴛ ɴᴏ: <code>{d[field]}</code></blockquote>\n"; found_any = True; break
        for field in ['status', 'Status', 'sts']:
            if d.get(field): status = str(d[field]); status_emoji = "🟢" if 'active' in status.lower() else "🔴"; result += f"<blockquote>{status_emoji} ꜱᴛᴀᴛᴜꜱ: <code>{status}</code></blockquote>\n"; found_any = True; break
        for field in ['registrationDate', 'regDate', 'rgdt']:
            if d.get(field): result += f"<blockquote>📅 ʀᴇɢ ᴅᴀᴛᴇ: <code>{d[field]}</code></blockquote>\n"; found_any = True; break
        for field in ['taxpayerType', 'type', 'dty']:
            if d.get(field): result += f"<blockquote>👤 ᴛʏᴘᴇ: <code>{d[field]}</code></blockquote>\n"; found_any = True; break
        for field in ['state', 'stateName', 'pradr']:
            if d.get(field):
                val = d[field]
                if isinstance(val, dict): val = val.get('stateName', str(val))
                result += f"<blockquote>🏛 ꜱᴛᴀᴛᴇ: <code>{val}</code></blockquote>\n"; found_any = True; break
        for field in ['address', 'principalPlaceOfBusiness', 'pradr']:
            if d.get(field):
                addr = d[field]
                if isinstance(addr, dict):
                    parts = []
                    for k in ['address', 'addr', 'city', 'state', 'pincode']:
                        if addr.get(k): parts.append(str(addr[k]))
                    addr = ', '.join(parts) if parts else str(addr)
                if addr and str(addr).strip(): result += f"<blockquote>📍 ᴀᴅᴅʀᴇꜱꜱ: <code>{str(addr)[:250]}</code></blockquote>\n"; found_any = True; break
        if not found_any: return "<blockquote>❌ ɴᴏ ᴅᴀᴛᴀ</blockquote>"
        return result
    return "<blockquote>❌ ɪɴᴠᴀʟɪᴅ</blockquote>"

async def pakistan_lookup(session, number):
    """FIXED: Pakistan Number Info - Only show real person data"""
    try:
        url = f"{PAK_API}{number}"
        
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as r:
            text = await r.text()
            
            if not text:
                return "<blockquote>❌ ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</blockquote>"
            
            try:
                data = json.loads(text)
            except:
                return "<blockquote>❌ ᴀᴘɪ ᴇʀʀᴏʀ - ᴛʀʏ ᴀɢᴀɪɴ</blockquote>"
            
            if not isinstance(data, dict):
                return "<blockquote>❌ ɪɴᴠᴀʟɪᴅ ʀᴇꜱᴘᴏɴꜱᴇ</blockquote>"
            
            # ONLY process if success is true AND data exists
            if data.get("success") and data.get("data"):
                records = data.get("data", [])
                
                # FILTER: Only keep records that have actual person data (name, number, cnic, or address)
                valid_records = []
                for rec in records:
                    if isinstance(rec, dict):
                        # Check if this record has actual person info
                        has_person_data = False
                        for key in ['name', 'Name', 'number', 'Number', 'cnic', 'CNIC', 'address', 'Address']:
                            if rec.get(key) and str(rec.get(key)).strip():
                                has_person_data = True
                                break
                        if has_person_data:
                            valid_records.append(rec)
                
                if not valid_records:
                    return "<blockquote>❌ ɴᴏ ᴘᴇʀꜱᴏɴ ᴅᴀᴛᴀ ꜰᴏᴜɴᴅ ꜰᴏʀ ᴛʜɪꜱ ɴᴜᴍʙᴇʀ</blockquote>"
                
                result = f"<blockquote expandable>✨ 🇵🇰 ᴘᴀᴋ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ</blockquote>\n"
                
                if len(valid_records) > 1:
                    result += f"<blockquote>📊 ᴛᴏᴛᴀʟ ʀᴇᴄᴏʀᴅꜱ: {len(valid_records)}</blockquote>\n"
                
                for i, record in enumerate(valid_records, 1):
                    if len(valid_records) > 1:
                        result += f"\n<blockquote>━━━ ʀᴇᴄᴏʀᴅ {i} ━━━</blockquote>\n"
                    
                    if record.get('number'):
                        result += f"<blockquote>📞 ɴᴜᴍʙᴇʀ: <code>{record['number']}</code></blockquote>\n"
                    if record.get('name'):
                        result += f"<blockquote>👤 ɴᴀᴍᴇ: <code>{record['name']}</code></blockquote>\n"
                    if record.get('cnic'):
                        result += f"<blockquote>🪪 ᴄɴɪᴄ: <code>{record['cnic']}</code></blockquote>\n"
                    if record.get('address'):
                        result += f"<blockquote>📍 ᴀᴅᴅʀᴇꜱꜱ: <code>{record['address']}</code></blockquote>\n"
                
                return result
            
            return "<blockquote>❌ ɴᴏ ᴅᴀᴛᴀ ꜰᴏᴜɴᴅ ꜰᴏʀ ᴛʜɪꜱ ɴᴜᴍʙᴇʀ</blockquote>"
            
    except asyncio.TimeoutError:
        return "<blockquote>⏱ ᴀᴘɪ ᴛɪᴍᴇᴏᴜᴛ - ᴛʀʏ ᴀɢᴀɪɴ</blockquote>"
    except Exception as e:
        logger.error(f"PAK error: {e}")
        return "<blockquote>❌ ꜱᴇʀᴠɪᴄᴇ ᴇʀʀᴏʀ</blockquote>"

# --- 📊 INDIA DATA PARSING ---

def clean_text(text):
    if not text: return ""
    return re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)

def run_india_script(choice, value):
    script_path = os.path.join(os.getcwd(), VERIFY_SCRIPT)
    if not os.path.exists(script_path): return None
    try:
        process = subprocess.Popen([sys.executable, script_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=os.getcwd(), env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        stdout, stderr = process.communicate(f"{choice}\n{value}\n0\n", timeout=45)
        if stdout and len(stdout) > 20: return stdout
        return None
    except: return None

def parse_all_india_records(raw):
    raw = clean_text(raw) if raw else ""
    if not raw: return []
    all_records = []
    sections = re.split(r'={5,}|-{5,}|Record\s*\d+[:\s-]*', raw)
    for section in sections:
        section = section.strip()
        if len(section) < 10: continue
        record = {}
        fields = {
            'Name': '👤 ɴᴀᴍᴇ', "Father's Name": '👨 ꜰᴀᴛʜᴇʀ',
            "Mother's Name": '👩 ᴍᴏᴛʜᴇʀ', 'Mobile': '📱 ᴍᴏʙɪʟᴇ',
            'Alternative Number': '📞 ᴀʟᴛᴇʀɴᴀᴛɪᴠᴇ', 'Address': '📍 ᴀᴅᴅʀᴇꜱꜱ',
            'Email': '📧 ᴇᴍᴀɪʟ', 'Circle': '📡 ᴄɪʀᴄʟᴇ',
            'DOB': '🎂 ᴅᴏʙ', 'Gender': '⚧ ɢᴇɴᴅᴇʀ',
            'State': '🏛 ꜱᴛᴀᴛᴇ', 'District': '🏘️ ᴅɪꜱᴛʀɪᴄᴛ',
            'Pincode': '📮 ᴘɪɴᴄᴏᴅᴇ',
            'RC Number': '🔖 ʀᴄ ɴᴜᴍʙᴇʀ', 'Owner Name': '👤 ᴏᴡɴᴇʀ',
            'Registration Date': '📅 ʀᴇɢ ᴅᴀᴛᴇ', 'Registered RTO': '🏢 ʀᴛᴏ',
            'Vehicle Class': '🚗 ᴄʟᴀꜱꜱ', 'Maker Model': '🏭 ᴍᴀᴋᴇʀ',
            'Model Name': '🚙 ᴍᴏᴅᴇʟ', 'Fuel Type': '⛽ ꜰᴜᴇʟ',
            'Insurance Company': '🛡️ ɪɴꜱᴜʀᴀɴᴄᴇ',
            'Insurance Expiry': '📅 ɪɴꜱ ᴇxᴘɪʀʏ',
            'Fitness Upto': '✅ ꜰɪᴛɴᴇꜱꜱ', 'Tax Upto': '💰 ᴛᴀx',
            'Financier Name': '🏦 ꜰɪɴᴀɴᴄɪᴇʀ', 'Phone': '📞 ᴘʜᴏɴᴇ'
        }
        for field, label in fields.items():
            match = re.search(rf'{re.escape(field)}:\s*([^\n]+)', section, re.IGNORECASE)
            if match and match.group(1).strip() not in ['None', '', 'N/A', 'null', 'Not Available']:
                record[label] = match.group(1).strip()
        if record:
            seen = set(); unique = {}
            for k, v in record.items():
                if v not in seen: seen.add(v); unique[k] = v
            if unique: all_records.append(unique)
    final = []; seen_combos = set()
    for rec in all_records:
        combo = tuple(sorted(rec.items()))
        if combo not in seen_combos: seen_combos.add(combo); final.append(rec)
    return final

def format_records_result(records, search_type):
    if not records: return "<blockquote>❌ ɴᴏ ʀᴇᴄᴏʀᴅꜱ ꜰᴏᴜɴᴅ</blockquote>"
    title_map = {'aadhaar':'🪪 ᴀᴀᴅʜᴀʀ ɪɴꜰᴏ','mobile':'🇮🇳 ɪɴᴅ ɴᴜᴍʙᴇʀ','vehicle':'🚘 ʀᴄ ᴅᴇᴛᴀɪʟꜱ'}
    title = title_map.get(search_type, '📊 ʀᴇꜱᴜʟᴛ')
    result = f"<blockquote expandable>✨ {title}</blockquote>\n"
    result += f"<blockquote>📊 ᴛᴏᴛᴀʟ ʀᴇᴄᴏʀᴅꜱ: {len(records)}</blockquote>\n"
    for i, record in enumerate(records, 1):
        if len(records) > 1: result += f"\n<blockquote>━━━ ʀᴇᴄᴏʀᴅ {i} ━━━</blockquote>\n"
        if search_type == 'aadhaar':
            priority = ['👤 ɴᴀᴍᴇ','👨 ꜰᴀᴛʜᴇʀ','👩 ᴍᴏᴛʜᴇʀ','📱 ᴍᴏʙɪʟᴇ','📞 ᴀʟᴛᴇʀɴᴀᴛɪᴠᴇ','📍 ᴀᴅᴅʀᴇꜱꜱ','📧 ᴇᴍᴀɪʟ','📡 ᴄɪʀᴄʟᴇ','🎂 ᴅᴏʙ','⚧ ɢᴇɴᴅᴇʀ','🏛 ꜱᴛᴀᴛᴇ','🏘️ ᴅɪꜱᴛʀɪᴄᴛ','📮 ᴘɪɴᴄᴏᴅᴇ']
        elif search_type == 'mobile':
            priority = ['👤 ɴᴀᴍᴇ','👨 ꜰᴀᴛʜᴇʀ','📱 ᴍᴏʙɪʟᴇ','📞 ᴀʟᴛᴇʀɴᴀᴛɪᴠᴇ','📍 ᴀᴅᴅʀᴇꜱꜱ','📡 ᴄɪʀᴄʟᴇ','📧 ᴇᴍᴀɪʟ','🏛 ꜱᴛᴀᴛᴇ']
        else:
            priority = ['🔖 ʀᴄ ɴᴜᴍʙᴇʀ','👤 ᴏᴡɴᴇʀ','👨 ꜰᴀᴛʜᴇʀ','🚗 ᴄʟᴀꜱꜱ','🚙 ᴍᴏᴅᴇʟ','🏭 ᴍᴀᴋᴇʀ','⛽ ꜰᴜᴇʟ','📅 ʀᴇɢ ᴅᴀᴛᴇ','🏢 ʀᴛᴏ','🛡️ ɪɴꜱᴜʀᴀɴᴄᴇ','📅 ɪɴꜱ ᴇxᴘɪʀʏ','✅ ꜰɪᴛɴᴇꜱꜱ','💰 ᴛᴀx','🏦 ꜰɪɴᴀɴᴄɪᴇʀ','📞 ᴘʜᴏɴᴇ','📍 ᴀᴅᴅʀᴇꜱꜱ']
        for key in priority:
            if key in record: result += f"<blockquote>{key}: <code>{record[key]}</code></blockquote>\n"
        for key, value in record.items():
            if key not in priority: result += f"<blockquote>{key}: <code>{value}</code></blockquote>\n"
    return result

# --- 👑 ADMIN ---

async def admin_panel(update, context):
    if update.effective_user.id != ADMIN_ID: return
    s = get_settings()
    maint_status = "🔴" if s.get("maintenance_mode") else "🟢"
    kb = [
        [InlineKeyboardButton("🎫 ɢᴇɴᴇʀᴀᴛᴇ ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ", callback_data="ad_gen")],
        [InlineKeyboardButton("📋 ᴠɪᴇᴡ ᴄᴏᴅᴇꜱ | 👥 ᴠɪᴇᴡ ᴜꜱᴇʀꜱ", callback_data="ad_codes")],
        [InlineKeyboardButton("🎁 ᴀᴅᴅ ᴄʀᴇᴅɪᴛꜱ ᴛᴏ ᴜꜱᴇʀ", callback_data="ad_credit")],
        [InlineKeyboardButton("📢 ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴛᴏ ᴀʟʟ", callback_data="ad_bcast")],
        [InlineKeyboardButton(f"{maint_status} ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ ᴍᴏᴅᴇ", callback_data="ad_maint")],
        [InlineKeyboardButton(f"{'🟢' if s.get('tgid_enabled',True) else '🔴'} ᴛɢ ɪᴅ", callback_data="ad_tgid"), InlineKeyboardButton(f"{'🟢' if s.get('ifsc_enabled',True) else '🔴'} ɪꜰꜱᴄ", callback_data="ad_ifsc")],
        [InlineKeyboardButton(f"{'🟢' if s.get('bypass_enabled',True) else '🔴'} ʙʏᴘᴀꜱꜱ", callback_data="ad_bypass_toggle"), InlineKeyboardButton(f"{'🟢' if s.get('mobile_enabled',True) else '🔴'} ᴍᴏʙɪʟᴇ", callback_data="ad_mobile")],
        [InlineKeyboardButton(f"{'🟢' if s.get('aadhaar_enabled',True) else '🔴'} ᴀᴀᴅʜᴀᴀʀ", callback_data="ad_aadhaar"), InlineKeyboardButton(f"{'🟢' if s.get('rc_enabled',True) else '🔴'} ʀᴄ", callback_data="ad_rc")],
        [InlineKeyboardButton(f"{'🟢' if s.get('gst_enabled',True) else '🔴'} ɢꜱᴛ", callback_data="ad_gst"), InlineKeyboardButton(f"{'🟢' if s.get('pak_enabled',True) else '🔴'} ᴘᴀᴋ", callback_data="ad_pak")],
        [InlineKeyboardButton("🛠️ ʙʏᴘᴀꜱꜱ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ", callback_data="ad_bypass_maint")],
        [InlineKeyboardButton("❌ ᴄʟᴏꜱᴇ ᴘᴀɴᴇʟ", callback_data="ad_close")]
    ]
    txt = f"<blockquote>👑 ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ</blockquote>\n<blockquote>👥 ᴜꜱᴇʀꜱ: {len(load_json(USERS_FILE))} | 🎫 ᴄᴏᴅᴇꜱ: {len(load_json(REDEEM_FILE))}</blockquote>"
    if update.callback_query: await update.callback_query.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
    else: await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)

async def admin_callback(update, context):
    q = update.callback_query
    if q.from_user.id != ADMIN_ID: await q.answer("❌"); return
    d = q.data; s = get_settings()
    if d == "ad_close": await q.message.delete()
    elif d == "ad_codes":
        codes = load_json(REDEEM_FILE); txt = f"<blockquote>🎫 {len(codes)} ᴄᴏᴅᴇꜱ</blockquote>\n"
        for c, v in list(codes.items())[-15:]: txt += f"<blockquote>{'✅' if not v.get('used') else '❌'} <code>{c}</code> | {v.get('credits')}cr</blockquote>\n"
        await q.message.edit_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d == "ad_gen": ADMIN_STATE[q.from_user.id] = "gen"; await q.message.edit_text("<blockquote>🎫 ᴄʀᴇᴅɪᴛꜱ:</blockquote>\n<i>100</i>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d == "ad_credit": ADMIN_STATE[q.from_user.id] = "credit"; await q.message.edit_text("<blockquote>🎁 ɪᴅ ᴀᴍᴏᴜɴᴛ:</blockquote>\n<i>123456789 50</i>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d == "ad_bcast": ADMIN_STATE[q.from_user.id] = "bcast"; await q.message.edit_text("<blockquote>📢 ᴍᴇꜱꜱᴀɢᴇ:</blockquote>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d == "ad_maint":
        s["maintenance_mode"] = not s.get("maintenance_mode", False)
        save_settings(s)
        await q.answer(f"Maintenance: {'ON' if s['maintenance_mode'] else 'OFF'}", show_alert=True)
        await admin_panel(update, context)
    elif d.startswith("ad_"):
        toggle_map = {"ad_tgid":"tgid_enabled","ad_ifsc":"ifsc_enabled","ad_bypass_toggle":"bypass_enabled","ad_mobile":"mobile_enabled","ad_aadhaar":"aadhaar_enabled","ad_rc":"rc_enabled","ad_gst":"gst_enabled","ad_pak":"pak_enabled"}
        if d in toggle_map: k = toggle_map[d]; s[k] = not s.get(k,True); save_settings(s); await q.answer(f"{k}: {'ON' if s[k] else 'OFF'}", show_alert=True)
        elif d == "ad_bypass_maint": s["bypass_maintenance"] = not s.get("bypass_maintenance",False); save_settings(s); await q.answer(f"Bypass Maint: {'ON' if s['bypass_maintenance'] else 'OFF'}", show_alert=True)
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
        asyncio.create_task(delete_user_msg(update.message, AUTO_DELETE_TIME))
        
        s = get_settings()
        if s.get("maintenance_mode", False) and uid != ADMIN_ID:
            m = await update.message.reply_text(f"<blockquote>🛠️ {s.get('maintenance_msg')}</blockquote>", parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m)); return
        
        if uid == ADMIN_ID and uid in ADMIN_STATE:
            state = ADMIN_STATE.pop(uid)
            if state == "gen":
                try: cr = int(txt); code = generate_redeem_code(cr); msg = await update.message.reply_text(f"<blockquote>✅ <code>{code}</code> | 💰 {cr}cr</blockquote>", parse_mode=ParseMode.HTML)
                except: msg = await update.message.reply_text("<blockquote>❌ Number</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(auto_del(msg)); return
            elif state == "credit":
                p = txt.split()
                if len(p) >= 2: bal = add_credits(p[0], int(p[1])); msg = await update.message.reply_text(f"<blockquote>✅ +{p[1]} | {bal}</blockquote>", parse_mode=ParseMode.HTML)
                else: msg = await update.message.reply_text("<blockquote>❌ Format: ID AMOUNT</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(auto_del(msg)); return
            elif state == "bcast":
                users = load_json(USERS_FILE); cnt = 0
                for u in users:
                    try: await context.bot.send_message(chat_id=int(u), text=f"📢 {txt}"); cnt += 1
                    except: pass
                msg = await update.message.reply_text(f"<blockquote>✅ Sent: {cnt}</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(auto_del(msg)); return
        
        user = get_user(uid)
        if not user.get("verified"):
            if await check_channels(uid, context): user["verified"] = True; save_user(uid, user); await main_menu(update, context)
            else: await show_verification_page(update, context)
            return
        
        if txt in ["👑 ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ", "👑 ᴀᴅᴍɪɴ"]: await admin_panel(update, context)
        
        elif txt in ["ᴛɢ ɪᴅ ➜ 📞 ɴᴜᴍʙᴇʀ 🔍"]:
            if not s.get("tgid_enabled",True): await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); return
            context.user_data['mode'] = 'TG'
            btn = [[InlineKeyboardButton("🤖 @ChatIdInfoBot", url="https://t.me/ChatIdInfoBot")]]
            m = await update.message.reply_text("<blockquote>📱 ᴛɢ ɪᴅ ➜ ɴᴜᴍʙᴇʀ</blockquote>\n<blockquote>1️⃣ @ChatIdInfoBot 2️⃣ Select user 3️⃣ Get ID 4️⃣ Enter here</blockquote>\n<i>7123181749, 6884112825</i>", reply_markup=InlineKeyboardMarkup(btn), parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m))
        
        elif txt in ["🏦 ɪꜰꜱᴄ ɪɴꜰᴏ➜🔎"]:
            if not s.get("ifsc_enabled",True): await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); return
            context.user_data['mode'] = 'IFSC'
            m = await update.message.reply_text("<blockquote>🏦 ɪꜰꜱᴄ</blockquote>\n<i>SBIN0001234, HDFC0001234</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m))
        
        elif txt in ["🔗 ʟɪɴᴋ ʙʏᴘᴀꜱꜱ"]:
            if not s.get("bypass_enabled",True): await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); return
            context.user_data['mode'] = 'SHORTLINK'
            m = await update.message.reply_text("<blockquote>🔗 Bypass</blockquote>\n<i>https://indianshortner.in/xxxx</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m))
        
        elif txt == "🇮🇳 ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ➜👤":
            if not s.get("mobile_enabled",True): await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); return
            context.user_data['mode'] = 'MOBILE'
            m = await update.message.reply_text("<blockquote>🇮🇳 Mobile</blockquote>\n<i>9876543210, 8123456789</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m))
        
        elif txt == "🪪 ᴀᴀᴅʜᴀʀ ɪɴꜰᴏ➜👤":
            if not s.get("aadhaar_enabled",True): await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); return
            context.user_data['mode'] = 'AADHAAR'
            m = await update.message.reply_text("<blockquote>🪪 Aadhaar</blockquote>\n<i>123456789012</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m))
        
        elif txt == "🚘 ʀᴄ ᴅᴇᴛᴀɪʟꜱ":
            if not s.get("rc_enabled",True): await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); return
            context.user_data['mode'] = 'VEHICLE'
            m = await update.message.reply_text("<blockquote>🚘 RC</blockquote>\n<i>KA01AB3256, DL1CX1234</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m))
        
        elif txt == "📋 ɢꜱᴛ ʟᴏᴏᴋᴜᴘ":
            if not s.get("gst_enabled",True): await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); return
            context.user_data['mode'] = 'GST'
            m = await update.message.reply_text("<blockquote>📋 GST</blockquote>\n<i>19BOKPS7056D1ZI</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m))
        
        elif txt == "🇵🇰 ᴘᴀᴋ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ":
            if not s.get("pak_enabled",True): await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); return
            context.user_data['mode'] = 'PAK'
            m = await update.message.reply_text("<blockquote>🇵🇰 Pakistan Number</blockquote>\n<i>923078750447, 03078750447</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m))
        
        elif txt in ["👥 ɪɴᴠɪᴛᴇ & ᴇᴀʀɴ", "👥 ɪɴᴠɪᴛᴇ"]:
            user = get_user(uid); bot_username = context.bot.username or BOT_USERNAME
            link = f"https://t.me/{bot_username}?start={user['invite_code']}"
            m = await update.message.reply_text(f"<blockquote>👥 Invite (+{INVITE_CREDITS}cr)</blockquote>\n<blockquote><code>{link}</code></blockquote>\n<blockquote>👥 {user.get('invites',0)} | 💰 {user.get('credits',0)}</blockquote>", parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m, 120))
        
        elif txt in ["🎫 ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ"]:
            context.user_data['redeem_mode'] = True
            m = await update.message.reply_text("<blockquote>🎫 Enter redeem code:</blockquote>\n<i>HEX-XXXXXXXXXX</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m, 30))
        
        else:
            if context.user_data.get('redeem_mode'):
                context.user_data['redeem_mode'] = False
                if txt.upper().startswith("HEX-") and len(txt) > 10:
                    success, msg = redeem_code(uid, txt)
                else:
                    msg = "❌ Invalid format! Use: HEX-XXXXXXXXXX"
                m = await update.message.reply_text(f"<blockquote>{msg}</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(auto_del(m)); return
            
            mode = context.user_data.get('mode')
            if mode:
                if txt.upper().startswith("HEX-") and len(txt) > 10:
                    success, msg = redeem_code(uid, txt)
                    m = await update.message.reply_text(f"<blockquote>{msg}</blockquote>", parse_mode=ParseMode.HTML)
                    asyncio.create_task(auto_del(m)); context.user_data['mode'] = None; return
                
                user = get_user(uid)
                if user.get("credits", 0) <= 0:
                    m = await update.message.reply_text("<blockquote>❌ No credits! +10 daily | +3 invite</blockquote>", parse_mode=ParseMode.HTML)
                    asyncio.create_task(auto_del(m)); context.user_data['mode'] = None; return
                
                await run_query(update, context, mode, txt); context.user_data['mode'] = None
    except Exception as e: logger.error(f"Msg: {e}")

async def run_query(update, context, mode, query):
    if not await net_ok():
        m = await update.message.reply_text("<blockquote>🔴 No internet</blockquote>", parse_mode=ParseMode.HTML)
        asyncio.create_task(auto_del(m)); return
    
    await update.message.reply_chat_action(ChatAction.TYPING)
    names = {'TG':'📱','IFSC':'🏦','SHORTLINK':'🔗','AADHAAR':'🪪','MOBILE':'🇮🇳','VEHICLE':'🚘','GST':'📋','PAK':'🇵🇰'}
    st = await update.message.reply_text("<blockquote>🟩 Searching...</blockquote>", parse_mode=ParseMode.HTML)
    lt = asyncio.create_task(loading_animation(st, names.get(mode, '')))
    
    credit_deducted = False
    
    try:
        if mode in ['AADHAAR', 'MOBILE', 'VEHICLE']:
            choice_map = {'AADHAAR': '2', 'MOBILE': '1', 'VEHICLE': '4'}
            search_map = {'AADHAAR': 'aadhaar', 'MOBILE': 'mobile', 'VEHICLE': 'vehicle'}
            raw = run_india_script(choice_map[mode], query)
            if raw:
                records = parse_all_india_records(raw)
                result = format_records_result(records, search_map[mode])
                if records and "❌" not in str(result):
                    use_credit(update.effective_user.id)
                    credit_deducted = True
            else:
                result = "<blockquote>❌ Script failed</blockquote>"
            
            if not credit_deducted:
                result = "<blockquote>❌ No records</blockquote>"
                lt.cancel()
                try: await lt
                except asyncio.CancelledError: pass
                final = f"{result}\n{SEP}\n<blockquote>💰 No credit deducted</blockquote>{FOOTER}"
                sent = await st.edit_text(final, parse_mode=ParseMode.HTML)
                asyncio.create_task(auto_del(sent)); return
        else:
            async with aiohttp.ClientSession() as s:
                if mode == 'TG': result = await chatid_lookup(s, query)
                elif mode == 'IFSC': result = await ifsc_lookup(s, query)
                elif mode == 'SHORTLINK': result = await bypass_lookup(s, query)
                elif mode == 'GST': result = await gst_lookup(s, query)
                elif mode == 'PAK': result = await pakistan_lookup(s, query)
                else: result = "❌"
            
            if result and "❌" not in str(result) and "unavailable" not in str(result).lower():
                use_credit(update.effective_user.id)
                credit_deducted = True
        
        lt.cancel()
        try: await lt
        except asyncio.CancelledError: pass
        
        user = get_user(update.effective_user.id)
        if not credit_deducted:
            final = f"{result}\n{SEP}\n<blockquote>💰 No credit deducted</blockquote>{FOOTER}"
        else:
            final = f"{result}\n{SEP}\n<blockquote>💰 CR: {user.get('credits',0)} | ⏱ {AUTO_DELETE_TIME}s</blockquote>{FOOTER}"
        sent = await st.edit_text(final, parse_mode=ParseMode.HTML)
        asyncio.create_task(auto_del(sent))
    except Exception as e:
        lt.cancel(); logger.error(f"Query: {e}")
        try: await st.edit_text(f"<blockquote>⚠️ Error</blockquote>{FOOTER}", parse_mode=ParseMode.HTML)
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
    app.run_polling()

if __name__ == '__main__':
    main()