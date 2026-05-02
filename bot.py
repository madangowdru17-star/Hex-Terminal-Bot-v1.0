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
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8687617595:AAEOeTwFDWquCAH3t497srDtrSRXM9Kaq4g')
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

VERIFY_SCRIPT = "verify_india.py"

USERS_FILE = "users.json"
REDEEM_FILE = "redeem_codes.json"
SETTINGS_FILE = "settings.json"

DAILY_FREE_CREDITS = 6
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
        d = {"bypass_maintenance":False,"bypass_msg":"Bypass maintenance.","tgid_enabled":True,"ifsc_enabled":True,"bypass_enabled":True,"mobile_enabled":True,"aadhaar_enabled":True,"rc_enabled":True}
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
            f"<b>╭━━━━━━━━━━━━━━━━━━╮</b>\n"
            f"<b>┃  🤖 {BOT_NAME}  ┃</b>\n"
            f"<b>┃  @{BOT_USERNAME}    ┃</b>\n"
            f"<b>╰━━━━━━━━━━━━━━━━━━╯</b>\n\n"
            f"<b>🔒 ᴊᴏɪɴ ʙᴏᴛʜ ᴄʜᴀɴɴᴇʟꜱ ᴛᴏ ᴜɴʟᴏᴄᴋ</b>\n\n"
            f"<b>🎁 +{DAILY_FREE_CREDITS} ᴅᴀɪʟʏ | 👥 +{INVITE_CREDITS} ɪɴᴠɪᴛᴇ</b>\n"
            f"<b>⏱ {AUTO_DELETE_TIME}ꜱ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ</b>\n\n"
            f"<b>🛠️ ᴛᴏᴏʟꜱ: ᴛɢ ɪᴅ | ɪꜰꜱᴄ | ʙʏᴘᴀꜱꜱ | ᴍᴏʙɪʟᴇ | ᴀᴀᴅʜᴀᴀʀ | ʀᴄ</b>\n\n"
            f"<b>👑 @Hexh4ckerOFC</b>"
        )
        if photos and photos.photos: await update.message.reply_photo(photo=photos.photos[0][-1].file_id, caption=caption, parse_mode=ParseMode.HTML)
        else: await update.message.reply_text(caption, parse_mode=ParseMode.HTML)
    except: pass
    buttons = [
        [InlineKeyboardButton("📢 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 𝟷", url=LINK_1)],
        [InlineKeyboardButton("📢 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 𝟸", url=LINK_2)],
        [InlineKeyboardButton("✅ ɪ'ᴠᴇ ᴊᴏɪɴᴇᴅ - ᴠᴇʀɪꜰʏ", callback_data="verify")]
    ]
    await update.message.reply_text("<blockquote>🔒 ᴊᴏɪɴ ʙᴏᴛʜ ᴄʜᴀɴɴᴇʟꜱ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴠᴇʀɪꜰʏ</blockquote>", reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)

async def main_menu(update, context):
    is_admin = update.effective_user.id == ADMIN_ID
    user = get_user(update.effective_user.id); s = get_settings()
    kb = []; row = []
    if s.get("tgid_enabled",True): row.append(KeyboardButton("ᴛɢ ɪᴅ ➜ 📞 ɴᴜᴍʙᴇʀ 🔍"))
    if s.get("ifsc_enabled",True): row.append(KeyboardButton("🏦 ɪꜰꜱᴄ ɪɴꜰᴏ➜🔎"))
    if row: kb.append(row)
    if s.get("bypass_enabled",True): kb.append([KeyboardButton("🔗 ʟɪɴᴋ ʙʏᴘᴀꜱꜱ")])
    row2 = []
    if s.get("mobile_enabled",True): row2.append(KeyboardButton("🇮🇳 ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ➜👤"))
    if s.get("aadhaar_enabled",True): row2.append(KeyboardButton("🪪 ᴀᴀᴅʜᴀʀ ɪɴꜰᴏ➜👤"))
    if row2: kb.append(row2)
    if s.get("rc_enabled",True): kb.append([KeyboardButton("🚘 ʀᴄ ᴅᴇᴛᴀɪʟꜱ")])
    kb.append([KeyboardButton("👥 ɪɴᴠɪᴛᴇ & ᴇᴀʀɴ"), KeyboardButton("💎 ʙᴜʏ ᴄʀᴇᴅɪᴛꜱ")])
    if is_admin: kb.append([KeyboardButton("👑 ᴀᴅᴍɪɴ")])
    markup = ReplyKeyboardMarkup(kb, resize_keyboard=True)
    cr = user.get("credits",0); total = user.get("total_queries",0); invites = user.get("invites",0)
    txt = (f"<b>╭━━━━━━━━━━━━━━━━━━╮</b>\n"
           f"<b>┃  🤖 {BOT_NAME}  ┃</b>\n"
           f"<b>┃  @{BOT_USERNAME}    ┃</b>\n"
           f"<b>╰━━━━━━━━━━━━━━━━━━╯</b>\n\n"
           f"<b>👋 ᴡᴇʟᴄᴏᴍᴇ</b> <code>{update.effective_user.first_name}</code>\n\n"
           f"<b>📊 ꜱᴛᴀᴛꜱ:</b>\n"
           f"<b>💰 ᴄʀ: {cr} | 📊 ǫ: {total} | 👥 ɪɴᴠ: {invites}</b>\n\n"
           f"<b>🛠️ ʜᴀᴄᴋɪɴɢ ᴛᴏᴏʟꜱ:</b>\n"
           f"<b>📱 ᴛɢ ɪᴅ → ɴᴜᴍʙᴇʀ | 🏦 ɪꜰꜱᴄ ʙᴀɴᴋ</b>\n"
           f"<b>🔗 ʟɪɴᴋ ʙʏᴘᴀꜱꜱ | 📞 ᴍᴏʙɪʟᴇ ᴏꜱɪɴᴛ</b>\n"
           f"<b>🆔 ᴀᴀᴅʜᴀᴀʀ | 🚘 ʀᴄ ᴠᴇʜɪᴄʟᴇ</b>\n\n"
           f"<b>🔄 +{DAILY_FREE_CREDITS} ᴅᴀɪʟʏ | 👥 +{INVITE_CREDITS} ɪɴᴠɪᴛᴇ</b>\n"
           f"<b>⏱ {AUTO_DELETE_TIME}ꜱ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ | 👑 @Hexh4ckerOFC</b>")
    msg = await update.message.reply_text(txt, reply_markup=markup, parse_mode=ParseMode.HTML)
    MAIN_MENU_MESSAGE_IDS.add(msg.message_id)
    asyncio.create_task(auto_del(msg, AUTO_DELETE_TIME))

# --- 🔗 API ---

async def api_fetch(session, url, timeout=15):
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as r:
            text = await r.text()
            if not text or text.startswith('<!'): return None
            return json.loads(text)
    except: return None

async def chatid_lookup(session, query):
    """FIXED: TG ID to Number with proper JSON parsing"""
    data = await api_fetch(session, f"{LOOKUP_API}{query}")
    if not data: return "<blockquote>❌ ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</blockquote>"
    
    if isinstance(data, dict) and data.get("success"):
        d = data.get("data", {})
        
        result = "<blockquote expandable>✨ 📱 ᴛɢ ɪᴅ → ɴᴜᴍʙᴇʀ</blockquote>\n"
        
        # Data fields with emojis
        if d.get('chat_id'):
            result += f"<blockquote>🆔 ᴄʜᴀᴛ ɪᴅ: <code>{d['chat_id']}</code></blockquote>\n"
        if d.get('number'):
            result += f"<blockquote>📞 ɴᴜᴍʙᴇʀ: <code>{d['number']}</code></blockquote>\n"
        if d.get('country'):
            result += f"<blockquote>🌍 ᴄᴏᴜɴᴛʀʏ: <code>{d['country']}</code></blockquote>\n"
        if d.get('country_code'):
            result += f"<blockquote>📋 ᴄᴏᴅᴇ: <code>{d['country_code']}</code></blockquote>\n"
        
        # YOUR CREDIT
        result += f"\n<blockquote>📡 ᴀᴘɪ: <code>@Hexh4ckerOFC</code></blockquote>\n"
        result += f"<blockquote>✅ ꜱᴛᴀᴛᴜꜱ: <code>{d.get('message', 'Details fetched')}</code></blockquote>"
        
        return result
    
    return "<blockquote>❌ ɴᴏᴛ ꜰᴏᴜɴᴅ - ᴜꜱᴇ @ChatIdInfoBot</blockquote>"

async def ifsc_lookup(session, code):
    data = await api_fetch(session, f"{IFSC_API}{code.upper()}")
    if not data: return "<blockquote>❌ ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</blockquote>"
    if isinstance(data, dict):
        return (f"<blockquote expandable>✨ 🏦 ɪꜰꜱᴄ ɪɴꜰᴏ</blockquote>\n"
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
            'Name': '👤 Name', "Father's Name": '👨 Father',
            "Mother's Name": '👩 Mother', 'Mobile': '📱 Mobile',
            'Alternative Number': '📞 Alternative', 'Address': '📍 Address',
            'Email': '📧 Email', 'Circle': '📡 Circle',
            'DOB': '🎂 DOB', 'Gender': '⚧ Gender',
            'State': '🏛 State', 'District': '🏘️ District',
            'Pincode': '📮 Pincode',
            'RC Number': '🔖 RC', 'Owner Name': '👤 Owner',
            'Registration Date': '📅 Reg Date', 'Registered RTO': '🏢 RTO',
            'Vehicle Class': '🚗 Class', 'Maker Model': '🏭 Maker',
            'Model Name': '🚙 Model', 'Fuel Type': '⛽ Fuel',
            'Insurance Company': '🛡️ Insurance',
            'Insurance Expiry': '📅 Ins Expiry',
            'Fitness Upto': '✅ Fitness', 'Tax Upto': '💰 Tax',
            'Financier Name': '🏦 Financier', 'Phone': '📞 Phone'
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
    title_map = {'aadhaar':'🆔 ᴀᴀᴅʜᴀᴀʀ','mobile':'📞 ɪɴᴅ ɴᴜᴍʙᴇʀ','vehicle':'🚘 ʀᴄ ᴅᴇᴛᴀɪʟꜱ'}
    title = title_map.get(search_type, '📊 ʀᴇꜱᴜʟᴛ')
    result = f"<blockquote expandable>✨ {title}</blockquote>\n"
    result += f"<blockquote>📊 ᴛᴏᴛᴀʟ ʀᴇᴄᴏʀᴅꜱ: {len(records)}</blockquote>\n"
    for i, record in enumerate(records, 1):
        if len(records) > 1: result += f"\n<blockquote>━━━ ʀᴇᴄᴏʀᴅ {i} ━━━</blockquote>\n"
        if search_type == 'aadhaar':
            priority = ['👤 Name','👨 Father','👩 Mother','📱 Mobile','📞 Alternative','📍 Address','📧 Email','📡 Circle','🎂 DOB','⚧ Gender','🏛 State','🏘️ District','📮 Pincode']
        elif search_type == 'mobile':
            priority = ['👤 Name','👨 Father','📱 Mobile','📞 Alternative','📍 Address','📡 Circle','📧 Email','🏛 State']
        else:
            priority = ['🔖 RC','👤 Owner','👨 Father','🚗 Class','🚙 Model','🏭 Maker','⛽ Fuel','📅 Reg Date','🏢 RTO','🛡️ Insurance','📅 Ins Expiry','✅ Fitness','💰 Tax','🏦 Financier','📞 Phone','📍 Address']
        for key in priority:
            if key in record: result += f"<blockquote>{key}: <code>{record[key]}</code></blockquote>\n"
        for key, value in record.items():
            if key not in priority: result += f"<blockquote>{key}: <code>{value}</code></blockquote>\n"
    return result

# --- 👑 ADMIN ---

async def admin_panel(update, context):
    if update.effective_user.id != ADMIN_ID: return
    s = get_settings()
    kb = [
        [InlineKeyboardButton("🎫 ɢᴇɴᴇʀᴀᴛᴇ ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ", callback_data="ad_gen")],
        [InlineKeyboardButton("📋 ᴠɪᴇᴡ ᴄᴏᴅᴇꜱ | 👥 ᴠɪᴇᴡ ᴜꜱᴇʀꜱ", callback_data="ad_codes")],
        [InlineKeyboardButton("🎁 ᴀᴅᴅ ᴄʀᴇᴅɪᴛꜱ ᴛᴏ ᴜꜱᴇʀ", callback_data="ad_credit")],
        [InlineKeyboardButton("📢 ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴍᴇꜱꜱᴀɢᴇ", callback_data="ad_bcast")],
        [InlineKeyboardButton(f"{'🟢' if s.get('tgid_enabled',True) else '🔴'} ᴛɢ ɪᴅ", callback_data="ad_tgid"), InlineKeyboardButton(f"{'🟢' if s.get('ifsc_enabled',True) else '🔴'} ɪꜰꜱᴄ", callback_data="ad_ifsc")],
        [InlineKeyboardButton(f"{'🟢' if s.get('bypass_enabled',True) else '🔴'} ʙʏᴘᴀꜱꜱ", callback_data="ad_bypass_toggle"), InlineKeyboardButton(f"{'🟢' if s.get('mobile_enabled',True) else '🔴'} ᴍᴏʙɪʟᴇ", callback_data="ad_mobile")],
        [InlineKeyboardButton(f"{'🟢' if s.get('aadhaar_enabled',True) else '🔴'} ᴀᴀᴅʜᴀᴀʀ", callback_data="ad_aadhaar"), InlineKeyboardButton(f"{'🟢' if s.get('rc_enabled',True) else '🔴'} ʀᴄ", callback_data="ad_rc")],
        [InlineKeyboardButton("🛠️ ʙʏᴘᴀꜱꜱ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ", callback_data="ad_bypass_maint")],
        [InlineKeyboardButton("❌ ᴄʟᴏꜱᴇ", callback_data="ad_close")]
    ]
    txt = f"<blockquote>👑 ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ</blockquote>\n<blockquote>👥 {len(load_json(USERS_FILE))} ᴜꜱᴇʀꜱ | 🎫 {len(load_json(REDEEM_FILE))} ᴄᴏᴅᴇꜱ</blockquote>"
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
    elif d == "ad_gen": ADMIN_STATE[q.from_user.id] = "gen"; await q.message.edit_text("<blockquote>🎫 ᴇɴᴛᴇʀ ᴄʀᴇᴅɪᴛ ᴀᴍᴏᴜɴᴛ:</blockquote>\n<i>Example: 100</i>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d == "ad_credit": ADMIN_STATE[q.from_user.id] = "credit"; await q.message.edit_text("<blockquote>🎁 ᴇɴᴛᴇʀ: ᴜꜱᴇʀ_ɪᴅ ᴀᴍᴏᴜɴᴛ</blockquote>\n<i>Example: 123456789 50</i>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d == "ad_bcast": ADMIN_STATE[q.from_user.id] = "bcast"; await q.message.edit_text("<blockquote>📢 ᴇɴᴛᴇʀ ᴍᴇꜱꜱᴀɢᴇ:</blockquote>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d.startswith("ad_"):
        toggle_map = {"ad_tgid":"tgid_enabled","ad_ifsc":"ifsc_enabled","ad_bypass_toggle":"bypass_enabled","ad_mobile":"mobile_enabled","ad_aadhaar":"aadhaar_enabled","ad_rc":"rc_enabled"}
        if d in toggle_map: k = toggle_map[d]; s[k] = not s.get(k,True); save_settings(s); await q.answer(f"{k}: {'ON' if s[k] else 'OFF'}", show_alert=True)
        elif d == "ad_bypass_maint": s["bypass_maintenance"] = not s.get("bypass_maintenance",False); save_settings(s); await q.answer(f"Maint: {'ON' if s['bypass_maintenance'] else 'OFF'}", show_alert=True)
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
                    try: await context.bot.send_message(chat_id=int(inviter), text=f"<blockquote>🎉 +{cr} ᴄʀᴇᴅɪᴛꜱ! ɴᴇᴡ ᴜꜱᴇʀ ᴊᴏɪɴᴇᴅ!</blockquote>", parse_mode=ParseMode.HTML)
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
        
        if uid == ADMIN_ID and uid in ADMIN_STATE:
            state = ADMIN_STATE.pop(uid)
            if state == "gen":
                try: cr = int(txt); code = generate_redeem_code(cr); await update.message.reply_text(f"<blockquote>✅ ᴄᴏᴅᴇ ʀᴇᴀᴅʏ</blockquote>\n<blockquote>🎫 <code>{code}</code></blockquote>\n<blockquote>💰 {cr} ᴄʀᴇᴅɪᴛꜱ</blockquote>", parse_mode=ParseMode.HTML)
                except: await update.message.reply_text("<blockquote>❌ ᴇɴᴛᴇʀ ᴀ ɴᴜᴍʙᴇʀ</blockquote>", parse_mode=ParseMode.HTML)
                return
            elif state == "credit":
                p = txt.split()
                if len(p) >= 2: bal = add_credits(p[0], int(p[1])); await update.message.reply_text(f"<blockquote>✅ +{p[1]} | ʙᴀʟ: {bal}</blockquote>", parse_mode=ParseMode.HTML)
                return
            elif state == "bcast":
                users = load_json(USERS_FILE); cnt = 0
                for u in users:
                    try: await context.bot.send_message(chat_id=int(u), text=f"📢 {txt}"); cnt += 1
                    except: pass
                await update.message.reply_text(f"<blockquote>✅ ꜱᴇɴᴛ: {cnt}</blockquote>", parse_mode=ParseMode.HTML)
                return
        
        user = get_user(uid)
        if not user.get("verified"):
            if await check_channels(uid, context): user["verified"] = True; save_user(uid, user); await main_menu(update, context)
            else: await show_verification_page(update, context)
            return
        
        s = get_settings()
        
        if txt in ["👑 ᴀᴅᴍɪɴ"]: await admin_panel(update, context)
        
        elif txt in ["📱 ᴛɢ ɪᴅ ᴛᴏ ɴᴜᴍʙ"]:
            if not s.get("tgid_enabled",True): await update.message.reply_text("<blockquote>📴 ᴅɪꜱᴀʙʟᴇᴅ</blockquote>", parse_mode=ParseMode.HTML); return
            context.user_data['mode'] = 'TG'
            btn = [[InlineKeyboardButton("🤖 @ChatIdInfoBot", url="https://t.me/ChatIdInfoBot")]]
            m = await update.message.reply_text("<blockquote>📱 ᴛɢ ɪᴅ ᴛᴏ ɴᴜᴍʙᴇʀ</blockquote>\n<blockquote>1️⃣ @ChatIdInfoBot</blockquote>\n<blockquote>2️⃣ ꜱᴇʟᴇᴄᴛ ᴜꜱᴇʀ → ɢᴇᴛ ɪᴅ</blockquote>\n<blockquote>3️⃣ ᴇɴᴛᴇʀ ɪᴅ ʜᴇʀᴇ</blockquote>\n<i>Example: 7123181749, 6884112825</i>", reply_markup=InlineKeyboardMarkup(btn), parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m))
        
        elif txt in ["🏦 ɪꜰꜱᴄ ɪɴꜰᴏ"]:
            if not s.get("ifsc_enabled",True): await update.message.reply_text("<blockquote>📴 ᴅɪꜱᴀʙʟᴇᴅ</blockquote>", parse_mode=ParseMode.HTML); return
            context.user_data['mode'] = 'IFSC'
            m = await update.message.reply_text("<blockquote>🏦 ɪꜰꜱᴄ ʙᴀɴᴋ ɪɴꜰᴏ</blockquote>\n<blockquote>Enter IFSC code</blockquote>\n<i>Example: SBIN0001234, HDFC0001234</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m))
        
        elif txt in ["🔗 ʟɪɴᴋ ʙʏᴘᴀꜱꜱ"]:
            if not s.get("bypass_enabled",True): await update.message.reply_text("<blockquote>📴 ᴅɪꜱᴀʙʟᴇᴅ</blockquote>", parse_mode=ParseMode.HTML); return
            context.user_data['mode'] = 'SHORTLINK'
            m = await update.message.reply_text("<blockquote>🔗 ʟɪɴᴋ ʙʏᴘᴀꜱꜱ</blockquote>\n<blockquote>Enter short link</blockquote>\n<i>Example: https://indianshortner.in/xxxx</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m))
        
        elif txt == "📞 ɪɴᴅ ɴᴜᴍʙᴇʀ":
            if not s.get("mobile_enabled",True): await update.message.reply_text("<blockquote>📴 ᴅɪꜱᴀʙʟᴇᴅ</blockquote>", parse_mode=ParseMode.HTML); return
            context.user_data['mode'] = 'MOBILE'
            m = await update.message.reply_text("<blockquote>📞 ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ</blockquote>\n<blockquote>Enter 10-digit mobile</blockquote>\n<i>Example: 9876543210, 8123456789</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m))
        
        elif txt == "🆔 ᴀᴀᴅʜᴀᴀʀ":
            if not s.get("aadhaar_enabled",True): await update.message.reply_text("<blockquote>📴 ᴅɪꜱᴀʙʟᴇᴅ</blockquote>", parse_mode=ParseMode.HTML); return
            context.user_data['mode'] = 'AADHAAR'
            m = await update.message.reply_text("<blockquote>🆔 ᴀᴀᴅʜᴀᴀʀ ᴛᴏ ꜰᴀᴍɪʟʏ</blockquote>\n<blockquote>Enter 12-digit Aadhaar</blockquote>\n<blockquote>📊 Shows all linked records</blockquote>\n<i>Example: 123456789012</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m))
        
        elif txt == "🚘 ʀᴄ ᴅᴇᴛᴀɪʟꜱ":
            if not s.get("rc_enabled",True): await update.message.reply_text("<blockquote>📴 ᴅɪꜱᴀʙʟᴇᴅ</blockquote>", parse_mode=ParseMode.HTML); return
            context.user_data['mode'] = 'VEHICLE'
            m = await update.message.reply_text("<blockquote>🚘 ʀᴄ ᴠᴇʜɪᴄʟᴇ</blockquote>\n<blockquote>Enter vehicle number</blockquote>\n<i>Example: KA01AB3256, DL1CX1234</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m))
        
        elif txt in ["👥 ɪɴᴠɪᴛᴇ & ᴇᴀʀɴ", "👥 ɪɴᴠɪᴛᴇ"]:
            user = get_user(uid); bot_username = context.bot.username or BOT_USERNAME
            link = f"https://t.me/{bot_username}?start={user['invite_code']}"
            m = await update.message.reply_text(f"<blockquote>👥 ɪɴᴠɪᴛᴇ & ᴇᴀʀɴ</blockquote>\n<blockquote>🎁 +{INVITE_CREDITS} ᴄʀᴇᴅɪᴛꜱ ᴘᴇʀ ɪɴᴠɪᴛᴇ</blockquote>\n<blockquote>💡 ʙᴏᴛʜ ɢᴇᴛ +{INVITE_CREDITS} ᴄʀᴇᴅɪᴛꜱ</blockquote>\n<blockquote>🔗 ʏᴏᴜʀ ɪɴᴠɪᴛᴇ ʟɪɴᴋ:</blockquote>\n<blockquote><code>{link}</code></blockquote>\n<blockquote>👥 ɪɴᴠɪᴛᴇꜱ: {user.get('invites',0)}</blockquote>\n<blockquote>💰 ʙᴀʟᴀɴᴄᴇ: {user.get('credits',0)} ᴄʀ</blockquote>", parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m, 120))
        
        elif txt in ["💎 ʙᴜʏ ᴄʀᴇᴅɪᴛꜱ"]:
            await update.message.reply_text("<blockquote>💎 ʙᴜʏ ᴄʀᴇᴅɪᴛꜱ</blockquote>\n<blockquote>📩 @Hexh4ckerOFC</blockquote>\n<blockquote>💬 ᴅᴍ ᴛᴏ ᴘᴜʀᴄʜᴀꜱᴇ</blockquote>\n<blockquote>🎫 ɢᴇᴛ ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ</blockquote>\n<blockquote>🔑 HEX-XXXXXXXXXX</blockquote>", parse_mode=ParseMode.HTML)
        
        else:
            mode = context.user_data.get('mode')
            if mode:
                if txt.upper().startswith("HEX-") and len(txt) > 10:
                    success, msg = redeem_code(uid, txt)
                    await update.message.reply_text(f"<blockquote>{msg}</blockquote>", parse_mode=ParseMode.HTML)
                    context.user_data['mode'] = None; return
                
                user = get_user(uid)
                if user.get("credits", 0) <= 0:
                    await update.message.reply_text("<blockquote>❌ ɴᴏ ᴄʀᴇᴅɪᴛꜱ!</blockquote>\n<blockquote>🔄 +5 ᴅᴀɪʟʏ | 👥 +3 ɪɴᴠɪᴛᴇ | 💎 ʙᴜʏ</blockquote>", parse_mode=ParseMode.HTML)
                    context.user_data['mode'] = None; return
                
                await run_query(update, context, mode, txt); context.user_data['mode'] = None
    except Exception as e: logger.error(f"Msg: {e}")

async def run_query(update, context, mode, query):
    if not await net_ok():
        m = await update.message.reply_text("<blockquote>🔴 ɴᴏ ɪɴᴛᴇʀɴᴇᴛ</blockquote>", parse_mode=ParseMode.HTML)
        asyncio.create_task(auto_del(m)); return
    
    await update.message.reply_chat_action(ChatAction.TYPING)
    names = {'TG':'📱','IFSC':'🏦','SHORTLINK':'🔗','AADHAAR':'🆔','MOBILE':'📞','VEHICLE':'🚘'}
    st = await update.message.reply_text("<blockquote>🟩 ꜱᴇᴀʀᴄʜɪɴɢ...</blockquote>", parse_mode=ParseMode.HTML)
    lt = asyncio.create_task(loading_animation(st, names.get(mode, '')))
    
    try:
        if mode in ['AADHAAR', 'MOBILE', 'VEHICLE']:
            choice_map = {'AADHAAR': '2', 'MOBILE': '1', 'VEHICLE': '4'}
            search_map = {'AADHAAR': 'aadhaar', 'MOBILE': 'mobile', 'VEHICLE': 'vehicle'}
            raw = run_india_script(choice_map[mode], query)
            if raw:
                records = parse_all_india_records(raw)
                result = format_records_result(records, search_map[mode])
            else:
                result = "<blockquote>❌ ꜱᴄʀɪᴘᴛ ꜰᴀɪʟᴇᴅ</blockquote>"
            if not records or "❌" in str(result):
                result = "<blockquote>❌ ɴᴏ ʀᴇᴄᴏʀᴅꜱ</blockquote>"
                lt.cancel()
                try: await lt
                except asyncio.CancelledError: pass
                final = f"{result}\n{SEP}\n<blockquote>💰 ɴᴏ ᴄʀᴇᴅɪᴛ ᴅᴇᴅᴜᴄᴛᴇᴅ</blockquote>{FOOTER}"
                sent = await st.edit_text(final, parse_mode=ParseMode.HTML)
                asyncio.create_task(auto_del(sent)); return
        else:
            async with aiohttp.ClientSession() as s:
                if mode == 'TG': result = await chatid_lookup(s, query)
                elif mode == 'IFSC': result = await ifsc_lookup(s, query)
                elif mode == 'SHORTLINK': result = await bypass_lookup(s, query)
                else: result = "❌"
        
        use_credit(update.effective_user.id)
        lt.cancel()
        try: await lt
        except asyncio.CancelledError: pass
        
        user = get_user(update.effective_user.id)
        final = f"{result}\n{SEP}\n<blockquote>💰 ᴄʀ: {user.get('credits',0)} | ⏱ {AUTO_DELETE_TIME}ꜱ</blockquote>{FOOTER}"
        sent = await st.edit_text(final, parse_mode=ParseMode.HTML)
        asyncio.create_task(auto_del(sent))
    except Exception as e:
        lt.cancel(); logger.error(f"Query: {e}")
        try: await st.edit_text(f"<blockquote>⚠️ ᴇʀʀᴏʀ</blockquote>{FOOTER}", parse_mode=ParseMode.HTML)
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