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

DAILY_FREE_CREDITS = 5
INVITE_CREDITS = 3
AUTO_DELETE_TIME = 60

BOT_NAME = "Hex Terminal"
BOT_USERNAME = "Hex_Terminal_bot"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

MAIN_MENU_MESSAGE_IDS = set()
ADMIN_STATE = {}

# --- 💾 DATA ---

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
    if code not in codes: return False, "❌ Invalid code"
    if codes[code].get("used"): return False, "❌ Already used"
    cr = codes[code]["credits"]; codes[code]["used"] = True; codes[code]["used_by"] = str(uid)
    save_json(REDEEM_FILE, codes); bal = add_credits(uid, cr)
    return True, f"✅ +{cr} credits!\n💰 Balance: {bal}"

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
    for i, bar in enumerate(bars):
        try: await msg.edit_text(f"<blockquote>⚡ {name}</blockquote>\n<code>{bar} {i*10}%</code>", parse_mode=ParseMode.HTML); await asyncio.sleep(0.25)
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
            f"<b>🔒 Join both channels</b>\n"
            f"<b>🎁 +{DAILY_FREE_CREDITS} daily | 👥 +{INVITE_CREDITS} invite</b>\n\n"
            f"<b>👑 @Hexh4ckerOFC</b>"
        )
        if photos and photos.photos: await update.message.reply_photo(photo=photos.photos[0][-1].file_id, caption=caption, parse_mode=ParseMode.HTML)
        else: await update.message.reply_text(caption, parse_mode=ParseMode.HTML)
    except: pass
    buttons = [
        [InlineKeyboardButton("📢 Join Channel 1", url=LINK_1)],
        [InlineKeyboardButton("📢 Join Channel 2", url=LINK_2)],
        [InlineKeyboardButton("✅ I've Joined - Verify", callback_data="verify")]
    ]
    await update.message.reply_text("<blockquote>🔒 Join both channels then verify</blockquote>", reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)

async def main_menu(update, context):
    is_admin = update.effective_user.id == ADMIN_ID
    user = get_user(update.effective_user.id); s = get_settings()
    kb = []; row = []
    if s.get("tgid_enabled",True): row.append(KeyboardButton("📱 ᴛɢ ɪᴅ ᴛᴏ ɴᴜᴍʙ"))
    if s.get("ifsc_enabled",True): row.append(KeyboardButton("🏦 ɪꜰꜱᴄ ɪɴꜰᴏ"))
    if row: kb.append(row)
    if s.get("bypass_enabled",True): kb.append([KeyboardButton("🔗 ʟɪɴᴋ ʙʏᴘᴀꜱꜱ")])
    row2 = []
    if s.get("mobile_enabled",True): row2.append(KeyboardButton("📞 ɪɴᴅ ɴᴜᴍʙᴇʀ"))
    if s.get("aadhaar_enabled",True): row2.append(KeyboardButton("🆔 ᴀᴀᴅʜᴀᴀʀ"))
    if row2: kb.append(row2)
    if s.get("rc_enabled",True): kb.append([KeyboardButton("🚘 ʀᴄ ᴅᴇᴛᴀɪʟꜱ")])
    kb.append([KeyboardButton("👥 ɪɴᴠɪᴛᴇ & ᴇᴀʀɴ"), KeyboardButton("💎 ʙᴜʏ ᴄʀᴇᴅɪᴛꜱ")])
    if is_admin: kb.append([KeyboardButton("👑 ᴀᴅᴍɪɴ")])
    markup = ReplyKeyboardMarkup(kb, resize_keyboard=True)
    cr = user.get("credits",0); total = user.get("total_queries",0); invites = user.get("invites",0)
    txt = (f"<blockquote>💎 ᴘʀᴇᴍɪᴜᴍ ʜᴜʙ</blockquote>\n"
           f"<blockquote>ᴡᴇʟᴄᴏᴍᴇ <code>{update.effective_user.first_name}</code></blockquote>\n"
           f"<blockquote>💰 ᴄʀ: {cr} | 📊 ǫ: {total} | 👥 ɪɴᴠ: {invites}</blockquote>\n"
           f"<blockquote>🔄 +{DAILY_FREE_CREDITS} ᴅᴀɪʟʏ | ⏱ {AUTO_DELETE_TIME}ꜱ</blockquote>")
    msg = await update.message.reply_text(txt, reply_markup=markup, parse_mode=ParseMode.HTML)
    MAIN_MENU_MESSAGE_IDS.add(msg.message_id)

# --- 🔗 API ---

async def api_fetch(session, url, timeout=15):
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as r:
            text = await r.text()
            if not text or text.startswith('<!'): return None
            return json.loads(text)
    except: return None

async def chatid_lookup(session, query):
    data = await api_fetch(session, f"{LOOKUP_API}{query}")
    if not data: return "<blockquote>❌ Service unavailable</blockquote>"
    if isinstance(data, dict) and data.get("success"):
        d = data.get("data", {})
        return f"<blockquote expandable>✨ 📱 ᴛɢ ɪᴅ ᴛᴏ ɴᴜᴍʙᴇʀ</blockquote>\n<blockquote>🆔 Chat ID: <code>{d.get('chat_id','N/A')}</code></blockquote>\n<blockquote>📞 Number: <code>{d.get('number','N/A')}</code></blockquote>\n<blockquote>🌍 Country: <code>{d.get('country','N/A')}</code></blockquote>"
    return "<blockquote>❌ Not found</blockquote>"

async def ifsc_lookup(session, code):
    data = await api_fetch(session, f"{IFSC_API}{code.upper()}")
    if not data: return "<blockquote>❌ Service unavailable</blockquote>"
    if isinstance(data, dict):
        return f"<blockquote expandable>✨ 🏦 ɪꜰꜱᴄ ɪɴꜰᴏ</blockquote>\n<blockquote>🏛 Bank: <code>{data.get('BANK','N/A')}</code></blockquote>\n<blockquote>📍 Branch: <code>{data.get('BRANCH','N/A')}</code></blockquote>\n<blockquote>🔑 IFSC: <code>{data.get('IFSC',code.upper())}</code></blockquote>\n<blockquote>📫 Address: <code>{data.get('ADDRESS','N/A')}</code></blockquote>"
    return "<blockquote>❌ Invalid</blockquote>"

async def bypass_lookup(session, link):
    s = get_settings()
    if s.get("bypass_maintenance",False): return "<blockquote>🛠️ Maintenance</blockquote>"
    data = await api_fetch(session, f"{SHORTLINK_API}{link}", timeout=20)
    if not data: return "<blockquote>❌ Service unavailable</blockquote>"
    if isinstance(data, dict):
        r = data.get('bypassed_url') or data.get('url') or str(data)
        return f"<blockquote expandable>✨ 🔗 ʙʏᴘᴀꜱꜱᴇᴅ</blockquote>\n<blockquote>🔗 <code>{str(r)}</code></blockquote>"
    return f"<blockquote>🔗 <code>{str(data)}</code></blockquote>"

# --- 📊 INDIA DATA - FIXED PARSING ---

def run_india_script(choice, value):
    """Run verify_india.py with proper error handling"""
    script_path = os.path.join(os.getcwd(), VERIFY_SCRIPT)
    
    if not os.path.exists(script_path):
        logger.error(f"Script not found: {script_path}")
        # List files in directory for debugging
        logger.info(f"Files in directory: {os.listdir(os.getcwd())}")
        return None
    
    try:
        # Install requirements if needed
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4"], 
                         capture_output=True, timeout=30)
        except: pass
        
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.getcwd(),
            env={**os.environ, "PYTHONIOENCODING": "utf-8"}
        )
        
        input_data = f"{choice}\n{value}\n0\n"
        stdout, stderr = process.communicate(input_data, timeout=45)
        
        if stderr:
            logger.warning(f"Script stderr: {stderr[:300]}")
        
        if stdout and len(stdout) > 20:
            logger.info(f"Script output: {len(stdout)} chars")
            return stdout
        
        return None
    except subprocess.TimeoutExpired:
        logger.error("Script timeout")
        process.kill()
        return None
    except Exception as e:
        logger.error(f"Script error: {e}")
        return None

def clean_text(text):
    if not text: return ""
    return re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)

def parse_india_output(raw, search_type):
    """Parse output from verify_india.py"""
    if not raw: return None
    
    raw = clean_text(raw)
    lines = raw.split('\n')
    found_data = {}
    
    # Common fields
    name_match = re.search(r'Name:\s*([^\n]+)', raw)
    father_match = re.search(r"Father'?s?\s*Name:\s*([^\n]+)", raw)
    mobile_match = re.search(r'Mobile:\s*([^\n]+)', raw)
    alt_match = re.search(r'Alternative\s*Number:\s*([^\n]+)', raw)
    address_match = re.search(r'Address:\s*([^\n]+)', raw)
    circle_match = re.search(r'Circle:\s*([^\n]+)', raw)
    state_match = re.search(r'State:\s*([^\n]+)', raw)
    email_match = re.search(r'Email:\s*([^\n]+)', raw)
    
    if name_match: found_data['name'] = name_match.group(1).strip()
    if father_match: found_data['father'] = father_match.group(1).strip()
    if mobile_match: found_data['mobile'] = mobile_match.group(1).strip()
    if alt_match: found_data['alt'] = alt_match.group(1).strip()
    if address_match: found_data['address'] = address_match.group(1).strip()
    if circle_match: found_data['circle'] = circle_match.group(1).strip()
    if state_match: found_data['state'] = state_match.group(1).strip()
    if email_match: found_data['email'] = email_match.group(1).strip()
    
    # RC specific
    rc_match = re.search(r'RC\s*Number:\s*([^\n]+)', raw)
    owner_match = re.search(r'Owner\s*Name:\s*([^\n]+)', raw)
    rto_match = re.search(r'Registered\s*RTO:\s*([^\n]+)', raw)
    reg_match = re.search(r'Registration\s*Date:\s*([^\n]+)', raw)
    vehicle_match = re.search(r'Vehicle\s*Class:\s*([^\n]+)', raw)
    maker_match = re.search(r'Maker\s*Model:\s*([^\n]+)', raw)
    fuel_match = re.search(r'Fuel\s*Type:\s*([^\n]+)', raw)
    insurance_match = re.search(r'Insurance\s*Company:\s*([^\n]+)', raw)
    ins_exp_match = re.search(r'Insurance\s*Expiry:\s*([^\n]+)', raw)
    fitness_match = re.search(r'Fitness\s*Upto:\s*([^\n]+)', raw)
    tax_match = re.search(r'Tax\s*Upto:\s*([^\n]+)', raw)
    phone_match = re.search(r'Phone:\s*([^\n]+)', raw)
    
    if rc_match: found_data['rc'] = rc_match.group(1).strip()
    if owner_match: found_data['owner'] = owner_match.group(1).strip()
    if rto_match: found_data['rto'] = rto_match.group(1).strip()
    if reg_match: found_data['reg_date'] = reg_match.group(1).strip()
    if vehicle_match: found_data['class'] = vehicle_match.group(1).strip()
    if maker_match: found_data['maker'] = maker_match.group(1).strip()
    if fuel_match: found_data['fuel'] = fuel_match.group(1).strip()
    if insurance_match: found_data['insurance'] = insurance_match.group(1).strip()
    if ins_exp_match: found_data['ins_exp'] = ins_exp_match.group(1).strip()
    if fitness_match: found_data['fitness'] = fitness_match.group(1).strip()
    if tax_match: found_data['tax'] = tax_match.group(1).strip()
    if phone_match: found_data['phone'] = phone_match.group(1).strip()
    
    return found_data if found_data else None

def format_india_result(data, search_type):
    """Format parsed data into Telegram message"""
    if not data: return "<blockquote>❌ No records found</blockquote>"
    
    if search_type == 'aadhaar':
        result = "<blockquote expandable>✨ 🆔 ᴀᴀᴅʜᴀᴀʀ ɪɴꜰᴏ</blockquote>\n"
        if 'name' in data: result += f"<blockquote>👤 Name: <code>{data['name']}</code></blockquote>\n"
        if 'father' in data: result += f"<blockquote>👨 Father: <code>{data['father']}</code></blockquote>\n"
        if 'mobile' in data: result += f"<blockquote>📱 Mobile: <code>{data['mobile']}</code></blockquote>\n"
        if 'alt' in data: result += f"<blockquote>📞 Alternative: <code>{data['alt']}</code></blockquote>\n"
        if 'address' in data: result += f"<blockquote>📍 Address: <code>{data['address'][:250]}</code></blockquote>\n"
        if 'circle' in data: result += f"<blockquote>📡 Circle: <code>{data['circle']}</code></blockquote>\n"
        if 'state' in data: result += f"<blockquote>🏛 State: <code>{data['state']}</code></blockquote>\n"
        if 'email' in data: result += f"<blockquote>📧 Email: <code>{data['email']}</code></blockquote>\n"
        return result
    
    elif search_type == 'mobile':
        result = "<blockquote expandable>✨ 📞 ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ</blockquote>\n"
        if 'name' in data: result += f"<blockquote>👤 Name: <code>{data['name']}</code></blockquote>\n"
        if 'father' in data: result += f"<blockquote>👨 Father: <code>{data['father']}</code></blockquote>\n"
        if 'mobile' in data: result += f"<blockquote>📱 Mobile: <code>{data['mobile']}</code></blockquote>\n"
        if 'alt' in data: result += f"<blockquote>📞 Alternative: <code>{data['alt']}</code></blockquote>\n"
        if 'address' in data: result += f"<blockquote>📍 Address: <code>{data['address'][:250]}</code></blockquote>\n"
        if 'circle' in data: result += f"<blockquote>📡 Circle: <code>{data['circle']}</code></blockquote>\n"
        if 'state' in data: result += f"<blockquote>🏛 State: <code>{data['state']}</code></blockquote>\n"
        return result
    
    elif search_type == 'vehicle':
        result = "<blockquote expandable>✨ 🚘 ʀᴄ ᴅᴇᴛᴀɪʟꜱ</blockquote>\n"
        if 'rc' in data: result += f"<blockquote>🔖 RC: <code>{data['rc']}</code></blockquote>\n"
        if 'owner' in data: result += f"<blockquote>👤 Owner: <code>{data['owner']}</code></blockquote>\n"
        if 'father' in data: result += f"<blockquote>👨 Father: <code>{data['father']}</code></blockquote>\n"
        if 'reg_date' in data: result += f"<blockquote>📅 Reg Date: <code>{data['reg_date']}</code></blockquote>\n"
        if 'rto' in data: result += f"<blockquote>🏢 RTO: <code>{data['rto']}</code></blockquote>\n"
        if 'class' in data: result += f"<blockquote>🚗 Class: <code>{data['class']}</code></blockquote>\n"
        if 'maker' in data: result += f"<blockquote>🏭 Maker: <code>{data['maker']}</code></blockquote>\n"
        if 'fuel' in data: result += f"<blockquote>⛽ Fuel: <code>{data['fuel']}</code></blockquote>\n"
        if 'insurance' in data: result += f"<blockquote>🛡️ Insurance: <code>{data['insurance']}</code></blockquote>\n"
        if 'ins_exp' in data: result += f"<blockquote>📅 Ins Expiry: <code>{data['ins_exp']}</code></blockquote>\n"
        if 'fitness' in data: result += f"<blockquote>✅ Fitness: <code>{data['fitness']}</code></blockquote>\n"
        if 'tax' in data: result += f"<blockquote>💰 Tax: <code>{data['tax']}</code></blockquote>\n"
        if 'phone' in data: result += f"<blockquote>📞 Phone: <code>{data['phone']}</code></blockquote>\n"
        if 'address' in data: result += f"<blockquote>📍 Address: <code>{data['address'][:200]}</code></blockquote>\n"
        return result
    
    return "<blockquote>❌ No data</blockquote>"

# --- 👑 ADMIN ---

async def admin_panel(update, context):
    if update.effective_user.id != ADMIN_ID: return
    s = get_settings()
    kb = [
        [InlineKeyboardButton("🎫 Generate Code", callback_data="ad_gen")],
        [InlineKeyboardButton("📋 Codes | 👥 Users", callback_data="ad_codes")],
        [InlineKeyboardButton("🎁 Add Credits", callback_data="ad_credit")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="ad_bcast")],
        [InlineKeyboardButton(f"{'🟢' if s.get('tgid_enabled',True) else '🔴'} TG ID", callback_data="ad_tgid"), InlineKeyboardButton(f"{'🟢' if s.get('ifsc_enabled',True) else '🔴'} IFSC", callback_data="ad_ifsc")],
        [InlineKeyboardButton(f"{'🟢' if s.get('bypass_enabled',True) else '🔴'} Bypass", callback_data="ad_bypass_toggle"), InlineKeyboardButton(f"{'🟢' if s.get('mobile_enabled',True) else '🔴'} Mobile", callback_data="ad_mobile")],
        [InlineKeyboardButton(f"{'🟢' if s.get('aadhaar_enabled',True) else '🔴'} Aadhaar", callback_data="ad_aadhaar"), InlineKeyboardButton(f"{'🟢' if s.get('rc_enabled',True) else '🔴'} RC", callback_data="ad_rc")],
        [InlineKeyboardButton("🛠️ Bypass Maint", callback_data="ad_bypass_maint")],
        [InlineKeyboardButton("❌ Close", callback_data="ad_close")]
    ]
    txt = f"<blockquote>👑 Admin</blockquote>\n<blockquote>👥 {len(load_json(USERS_FILE))} | 🎫 {len(load_json(REDEEM_FILE))}</blockquote>"
    if update.callback_query: await update.callback_query.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
    else: await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)

async def admin_callback(update, context):
    q = update.callback_query
    if q.from_user.id != ADMIN_ID: await q.answer("❌"); return
    d = q.data; s = get_settings()
    if d == "ad_close": await q.message.delete()
    elif d == "ad_codes":
        codes = load_json(REDEEM_FILE); txt = f"<blockquote>🎫 {len(codes)} codes</blockquote>\n"
        for c, v in list(codes.items())[-10:]: txt += f"<blockquote>{'✅' if not v.get('used') else '❌'} <code>{c}</code> | {v.get('credits')}cr</blockquote>\n"
        await q.message.edit_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d == "ad_gen": ADMIN_STATE[q.from_user.id] = "gen"; await q.message.edit_text("<blockquote>🎫 Credits:</blockquote>\n<i>100</i>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d == "ad_credit": ADMIN_STATE[q.from_user.id] = "credit"; await q.message.edit_text("<blockquote>🎁 ID AMOUNT:</blockquote>\n<i>123456789 50</i>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d == "ad_bcast": ADMIN_STATE[q.from_user.id] = "bcast"; await q.message.edit_text("<blockquote>📢 Message:</blockquote>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
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
                    try: await context.bot.send_message(chat_id=int(inviter), text=f"<blockquote>🎉 +{cr} credits!</blockquote>", parse_mode=ParseMode.HTML)
                    except: pass
                    break
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
        await q.answer("✅ Verified!"); 
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
                try: cr = int(txt); code = generate_redeem_code(cr); await update.message.reply_text(f"<blockquote>✅ <code>{code}</code> | 💰 {cr}cr</blockquote>", parse_mode=ParseMode.HTML)
                except: await update.message.reply_text("<blockquote>❌ Number</blockquote>", parse_mode=ParseMode.HTML)
                return
            elif state == "credit":
                p = txt.split()
                if len(p) >= 2: bal = add_credits(p[0], int(p[1])); await update.message.reply_text(f"<blockquote>✅ +{p[1]} | {bal}</blockquote>", parse_mode=ParseMode.HTML)
                return
            elif state == "bcast":
                users = load_json(USERS_FILE); cnt = 0
                for u in users:
                    try: await context.bot.send_message(chat_id=int(u), text=f"📢 {txt}"); cnt += 1
                    except: pass
                await update.message.reply_text(f"<blockquote>✅ {cnt}</blockquote>", parse_mode=ParseMode.HTML)
                return
        user = get_user(uid)
        if not user.get("verified"):
            if await check_channels(uid, context): user["verified"] = True; save_user(uid, user); await main_menu(update, context)
            else: await show_verification_page(update, context)
            return
        s = get_settings()
        if txt in ["👑 ᴀᴅᴍɪɴ"]: await admin_panel(update, context)
        elif txt in ["📱 ᴛɢ ɪᴅ ᴛᴏ ɴᴜᴍʙ"]:
            if not s.get("tgid_enabled",True): await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); return
            context.user_data['mode'] = 'TG'
            btn = [[InlineKeyboardButton("🤖 @ChatIdInfoBot", url="https://t.me/ChatIdInfoBot")]]
            m = await update.message.reply_text("<blockquote>📱 Enter Chat ID:</blockquote>\n<i>7123181749</i>", reply_markup=InlineKeyboardMarkup(btn), parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m))
        elif txt in ["🏦 ɪꜰꜱᴄ ɪɴꜰᴏ"]:
            if not s.get("ifsc_enabled",True): await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); return
            context.user_data['mode'] = 'IFSC'; m = await update.message.reply_text("<blockquote>🏦 Enter IFSC:</blockquote>\n<i>SBIN0001234</i>", parse_mode=ParseMode.HTML); asyncio.create_task(auto_del(m))
        elif txt in ["🔗 ʟɪɴᴋ ʙʏᴘᴀꜱꜱ"]:
            if not s.get("bypass_enabled",True): await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); return
            context.user_data['mode'] = 'SHORTLINK'; m = await update.message.reply_text("<blockquote>🔗 Enter link:</blockquote>\n<i>https://indianshortner.in/xxxx</i>", parse_mode=ParseMode.HTML); asyncio.create_task(auto_del(m))
        elif txt == "📞 ɪɴᴅ ɴᴜᴍʙᴇʀ":
            if not s.get("mobile_enabled",True): await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); return
            context.user_data['mode'] = 'MOBILE'; m = await update.message.reply_text("<blockquote>📞 Enter 10-digit mobile:</blockquote>\n<i>9876543210</i>", parse_mode=ParseMode.HTML); asyncio.create_task(auto_del(m))
        elif txt == "🆔 ᴀᴀᴅʜᴀᴀʀ":
            if not s.get("aadhaar_enabled",True): await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); return
            context.user_data['mode'] = 'AADHAAR'; m = await update.message.reply_text("<blockquote>🆔 Enter 12-digit Aadhaar:</blockquote>\n<i>123456789012</i>", parse_mode=ParseMode.HTML); asyncio.create_task(auto_del(m))
        elif txt == "🚘 ʀᴄ ᴅᴇᴛᴀɪʟꜱ":
            if not s.get("rc_enabled",True): await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); return
            context.user_data['mode'] = 'VEHICLE'; m = await update.message.reply_text("<blockquote>🚘 Enter vehicle number:</blockquote>\n<i>KA01AB3256</i>", parse_mode=ParseMode.HTML); asyncio.create_task(auto_del(m))
        elif txt in ["👥 ɪɴᴠɪᴛᴇ & ᴇᴀʀɴ", "👥 ɪɴᴠɪᴛᴇ"]:
            user = get_user(uid); bot_username = context.bot.username or BOT_USERNAME
            link = f"https://t.me/{bot_username}?start={user['invite_code']}"
            m = await update.message.reply_text(f"<blockquote>👥 Invite (+{INVITE_CREDITS} cr)</blockquote>\n<blockquote><code>{link}</code></blockquote>\n<blockquote>👥 {user.get('invites',0)} | 💰 {user.get('credits',0)}</blockquote>", parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m, 120))
        elif txt in ["💎 ʙᴜʏ ᴄʀᴇᴅɪᴛꜱ"]:
            await update.message.reply_text("<blockquote>💎 @Hexh4ckerOFC</blockquote>\n<blockquote>🔑 HEX-XXXXXXXXXX</blockquote>", parse_mode=ParseMode.HTML)
        else:
            mode = context.user_data.get('mode')
            if mode:
                if txt.upper().startswith("HEX-") and len(txt) > 10: success, msg = redeem_code(uid, txt); await update.message.reply_text(f"<blockquote>{msg}</blockquote>", parse_mode=ParseMode.HTML); context.user_data['mode'] = None; return
                user = get_user(uid)
                if user.get("credits", 0) <= 0: await update.message.reply_text("<blockquote>❌ No credits!</blockquote>", parse_mode=ParseMode.HTML); context.user_data['mode'] = None; return
                await run_query(update, context, mode, txt); context.user_data['mode'] = None
            else: await main_menu(update, context)
    except Exception as e: logger.error(f"Msg: {e}")

async def run_query(update, context, mode, query):
    if not await net_ok(): m = await update.message.reply_text("<blockquote>🔴 No internet</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(auto_del(m)); return
    await update.message.reply_chat_action(ChatAction.TYPING)
    names = {'TG':'📱','IFSC':'🏦','SHORTLINK':'🔗','AADHAAR':'🆔','MOBILE':'📞','VEHICLE':'🚘'}
    st = await update.message.reply_text("<blockquote>🟩 Searching...</blockquote>", parse_mode=ParseMode.HTML)
    lt = asyncio.create_task(loading_animation(st, names.get(mode, '')))
    
    try:
        if mode in ['AADHAAR', 'MOBILE', 'VEHICLE']:
            choice_map = {'AADHAAR': '2', 'MOBILE': '1', 'VEHICLE': '4'}
            search_map = {'AADHAAR': 'aadhaar', 'MOBILE': 'mobile', 'VEHICLE': 'vehicle'}
            
            logger.info(f"Running {search_map[mode]} lookup for: {query}")
            raw = run_india_script(choice_map[mode], query)
            
            if raw:
                parsed = parse_india_output(raw, search_map[mode])
                result = format_india_result(parsed, search_map[mode])
                logger.info(f"Result: {result[:100] if result else 'None'}")
            else:
                result = "<blockquote>❌ Script execution failed</blockquote>\n<blockquote>Check Railway logs for details</blockquote>"
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
        final = f"{result}\n{SEP}\n<blockquote>💰 CR: {user.get('credits',0)} | ⏱ {AUTO_DELETE_TIME}s</blockquote>{FOOTER}"
        sent = await st.edit_text(final, parse_mode=ParseMode.HTML)
        asyncio.create_task(auto_del(sent))
    except Exception as e:
        lt.cancel(); logger.error(f"Query error: {e}")
        try: await st.edit_text(f"<blockquote>⚠️ Error: {str(e)[:80]}</blockquote>{FOOTER}", parse_mode=ParseMode.HTML)
        except: pass

def main():
    print("🔄 Hex Terminal starting...")
    print(f"📁 Files: {os.listdir(os.getcwd())}")
    
    # Install requirements
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4", "lxml"], 
                     capture_output=True, timeout=30)
        print("✅ Dependencies installed")
    except Exception as e:
        print(f"⚠️ Pip install: {e}")
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify_cb, pattern="^verify$"))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^ad_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg_handler))
    
    print(f"✅ {BOT_NAME} Ready!")
    app.run_polling()

if __name__ == '__main__':
    main()