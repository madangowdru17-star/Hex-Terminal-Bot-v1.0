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

# Data storage files - Works on Railway AND GitHub
USERS_FILE = os.path.join(os.getcwd(), "users.json")
REDEEM_FILE = os.path.join(os.getcwd(), "redeem_codes.json")
SETTINGS_FILE = os.path.join(os.getcwd(), "settings.json")
BACKUP_DIR = os.path.join(os.getcwd(), "backups")

DAILY_FREE_CREDITS = 10
INVITE_CREDITS = 3
AUTO_DELETE_TIME = 60

BOT_NAME = "𝗛𝗲𝘅 𝗧𝗲𝗿𝗺𝗶𝗻𝗮𝗹"
BOT_USERNAME = "Hex_Terminal_bot"

DISCLAIMER = "\n\n<b>⚠️ ᴅɪꜱᴄʟᴀɪᴍᴇʀ:</b>\n<i>ᴇᴅᴜᴄᴀᴛɪᴏɴᴀʟ ᴘᴜʀᴘᴏꜱᴇꜱ ᴏɴʟʏ. ᴍɪꜱᴜꜱᴇ ᴍᴀʏ ʟᴇᴀᴅ ᴛᴏ ʟᴇɢᴀʟ ᴀᴄᴛɪᴏɴ ᴜɴᴅᴇʀ ᴄʏʙᴇʀᴄʀɪᴍᴇ ʟᴀᴡꜱ. ᴡᴇ ᴅᴏ ɴᴏᴛ ꜱᴜᴘᴘᴏʀᴛ ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴀᴄᴄᴇꜱꜱ, ꜰʀᴀᴜᴅ, ᴏʀ ᴍᴀʟɪᴄɪᴏᴜꜱ ᴀᴄᴛɪᴠɪᴛʏ. ᴜꜱᴇ ʀᴇꜱᴘᴏɴꜱɪʙʟʏ.</i>"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

ADMIN_STATE = {}

# --- 💾 DATA FUNCTIONS WITH BACKUP ---

def ensure_backup_dir():
    """Create backup directory if not exists"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

def backup_data(filename):
    """Backup data file"""
    ensure_backup_dir()
    if os.path.exists(filename):
        backup_name = os.path.join(BACKUP_DIR, f"{os.path.basename(filename)}.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak")
        try:
            import shutil
            shutil.copy2(filename, backup_name)
            logger.info(f"Backup created: {backup_name}")
        except Exception as e:
            logger.error(f"Backup failed: {e}")

def load_json(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"Loaded {filename}: {len(data)} records")
            return data
    except:
        logger.warning(f"File not found or empty: {filename}, creating new")
        return {}

def save_json(filename, data):
    try:
        # Backup old file first
        if os.path.exists(filename):
            backup_data(filename)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {filename}: {len(data)} records")
    except Exception as e:
        logger.error(f"Save failed: {e}")

def get_user(user_id):
    users = load_json(USERS_FILE)
    uid = str(user_id)
    today = datetime.now().strftime("%Y-%m-%d")
    if uid not in users:
        users[uid] = {"credits":DAILY_FREE_CREDITS,"total_queries":0,"daily_queries":0,"last_reset":today,"invite_code":f"HEX-{''.join(random.choices(string.ascii_uppercase+string.digits, k=8))}","invites":0,"verified":False}
        save_json(USERS_FILE, users)
    elif users[uid].get("last_reset") != today:
        old_credits = users[uid].get("credits", 0)
        users[uid]["credits"] = DAILY_FREE_CREDITS
        users[uid]["daily_queries"] = 0
        users[uid]["last_reset"] = today
        save_json(USERS_FILE, users)
        logger.info(f"Daily reset for {uid}: {old_credits} → {DAILY_FREE_CREDITS}")
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
        d = {"bypass_maintenance":False,"bypass_msg":"Bypass maintenance.","tgid_enabled":True,"ifsc_enabled":True,"bypass_enabled":True,"mobile_enabled":True,"aadhaar_enabled":True,"rc_enabled":True,"gst_enabled":True,"pak_enabled":True,"indnum_enabled":True,"indnum3_enabled":True,"maintenance_mode":False,"maintenance_msg":"🛠️ Under maintenance."}
        for k in ["tgid","ifsc","bypass","mobile","aadhaar","rc","gst","pak","indnum","indnum3"]: d[f"maint_msg_{k}"] = f"🛠️ {k} is under maintenance."; d[f"maint_{k}"] = False
        save_json(SETTINGS_FILE, d); return d

def save_settings(data):
    save_json(SETTINGS_FILE, data)

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
    bars = ["🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛","🟩🟩⬛⬛⬛⬛⬛⬛⬛⬛","🟩🟩🟩⬛⬛⬛⬛⬛⬛⬛","🟩🟩🟩🟩⬛⬛⬛⬛⬛⬛","🟩🟩🟩🟩🟩⬛⬛⬛⬛⬛","🟩🟩🟩🟩🟩🟩⬛⬛⬛⬛","🟩🟩🟩🟩🟩🟩🟩⬛⬛⬛","🟩🟩🟩🟩🟩🟩🟩🟩⬛⬛","🟩🟩🟩🟩🟩🟩🟩🟩🟩⬛","🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩"]
    percentages = ["0%","10%","20%","30%","40%","50%","60%","70%","80%","90%","100%"]
    network_stages = ["ᴄᴏɴɴᴇᴄᴛɪɴɢ...","ᴀᴘɪ ʟɪɴᴋɪɴɢ...","ꜰᴇᴛᴄʜɪɴɢ ᴅᴀᴛᴀ...","ᴘʀᴏᴄᴇꜱꜱɪɴɢ...","ᴠᴇʀɪꜰʏɪɴɢ...","ʟᴏᴀᴅɪɴɢ ʀᴇꜱᴜʟᴛꜱ...","ᴀʟᴍᴏꜱᴛ ᴅᴏɴᴇ...","ꜰɪɴᴀʟɪᴢɪɴɢ...","ᴄᴏᴍᴘʟᴇᴛɪɴɢ...","✅ ᴄᴏᴍᴘʟᴇᴛᴇ!"]
    for i, bar in enumerate(bars):
        try: await msg.edit_text(f"<blockquote>⚡ {name}</blockquote>\n<code>{bar} {percentages[i]}</code>\n<blockquote>📡 {network_stages[i]}</blockquote>", parse_mode=ParseMode.HTML); await asyncio.sleep(0.2)
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
            f"<b>╭━━━━━━━━━━━━━━━━━━━━━╮</b>\n"
            f"<b>┃   🤖 {BOT_NAME}   ┃</b>\n"
            f"<b>┃   @{BOT_USERNAME}       ┃</b>\n"
            f"<b>╰━━━━━━━━━━━━━━━━━━━━━╯</b>\n\n"
            f"<b>🔒 ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ʀᴇQᴜɪʀᴇᴅ</b>\n"
            f"<b>ᴊᴏɪɴ ʙᴏᴛʜ ᴄʜᴀɴɴᴇʟꜱ ᴛᴏ ᴜɴʟᴏᴄᴋ</b>\n\n"
            f"<b>📋 ɢᴜɪᴅᴇʟɪɴᴇꜱ:</b>\n"
            f"<b>• ᴇᴅᴜᴄᴀᴛɪᴏɴᴀʟ ᴘᴜʀᴘᴏꜱᴇꜱ ᴏɴʟʏ</b>\n"
            f"<b>• ᴜꜱᴇ ᴏɴ ʏᴏᴜʀ ᴏᴡɴ ᴅᴀᴛᴀ</b>\n"
            f"<b>• ʀᴇꜱᴘᴇᴄᴛ ᴘʀɪᴠᴀᴄʏ ʟᴀᴡꜱ</b>\n\n"
            f"<b>🎁 +{DAILY_FREE_CREDITS} ᴅᴀɪʟʏ | 👥 +{INVITE_CREDITS} ɪɴᴠɪᴛᴇ</b>\n"
            f"<b>⏱ {AUTO_DELETE_TIME}ꜱ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ</b>\n\n"
            f"<b>👑 @Hexh4ckerOFC</b>\n"
            f"<i>⚠️ ᴍɪꜱᴜꜱᴇ ᴍᴀʏ ʟᴇᴀᴅ ᴛᴏ ʟᴇɢᴀʟ ᴀᴄᴛɪᴏɴ</i>"
        )
        if photos and photos.photos: sent = await update.message.reply_photo(photo=photos.photos[0][-1].file_id, caption=caption, parse_mode=ParseMode.HTML)
        else: sent = await update.message.reply_text(caption, parse_mode=ParseMode.HTML)
        asyncio.create_task(schedule_delete(sent, 120))
    except: pass
    buttons = [[InlineKeyboardButton("📢 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 𝟷", url=LINK_1)],[InlineKeyboardButton("📢 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 𝟸", url=LINK_2)],[InlineKeyboardButton("✅ ɪ'ᴠᴇ ᴊᴏɪɴᴇᴅ - ᴠᴇʀɪꜰʏ ɴᴏᴡ", callback_data="verify")]]
    sent2 = await update.message.reply_text("<blockquote>🔒 ᴊᴏɪɴ ʙᴏᴛʜ ᴄʜᴀɴɴᴇʟꜱ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴠᴇʀɪꜰʏ</blockquote>", reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)
    asyncio.create_task(schedule_delete(sent2, 120))

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
    row4 = []
    if s.get("pak_enabled",True): row4.append(KeyboardButton("🇵🇰 ᴘᴀᴋ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ"))
    if s.get("indnum_enabled",True): row4.append(KeyboardButton("📲 ɪɴᴅ ɴᴜᴍ ɪɴꜰᴏ 𝟸"))
    if row4: kb.append(row4)
    if s.get("indnum3_enabled",True): kb.append([KeyboardButton("🇮🇳 ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ 𝟹 ➜👤")])
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
        f"<b>📊 ʏᴏᴜʀ ᴀᴄᴄᴏᴜɴᴛ ꜱᴜᴍᴍᴀʀʏ:</b>\n"
        f"<b>┃ 💰 ᴄʀᴇᴅɪᴛ ʙᴀʟᴀɴᴄᴇ: {cr}</b>\n"
        f"<b>┃ 📊 ᴛᴏᴛᴀʟ Qᴜᴇʀɪᴇꜱ: {total}</b>\n"
        f"<b>┃ 👥 ɪɴᴠɪᴛᴇꜱ ꜱᴇɴᴛ: {invites}</b>\n\n"
        f"<b>📋 ᴀᴠᴀɪʟᴀʙʟᴇ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ᴛᴏᴏʟꜱ:</b>\n"
        f"<b>📱 ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ ➜ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ</b>\n"
        f"<b>🏦 ʙᴀɴᴋ ɪꜰꜱᴄ ᴄᴏᴅᴇ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ</b>\n"
        f"<b>🔗 ꜱʜᴏʀᴛ ʟɪɴᴋ ᴜʀʟ ʙʏᴘᴀꜱꜱᴇʀ</b>\n"
        f"<b>🇮🇳 ɪɴᴅɪᴀɴ ᴍᴏʙɪʟᴇ ɴᴜᴍʙᴇʀ ʟᴏᴏᴋᴜᴘ</b>\n"
        f"<b>🪪 ᴀᴀᴅʜᴀʀ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ᴅᴇᴛᴀɪʟꜱ</b>\n"
        f"<b>🚘 ᴠᴇʜɪᴄʟᴇ ʀᴄ ʀᴇɢɪꜱᴛʀᴀᴛɪᴏɴ ɪɴꜰᴏ</b>\n"
        f"<b>📋 ɢꜱᴛ ʙᴜꜱɪɴᴇꜱꜱ ɴᴜᴍʙᴇʀ ʟᴏᴏᴋᴜᴘ</b>\n"
        f"<b>🇵🇰 ᴘᴀᴋɪꜱᴛᴀɴ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ</b>\n"
        f"<b>📲 ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴀᴅᴠᴀɴᴄᴇᴅ ɪɴꜰᴏ</b>\n"
        f"<b>🇮🇳 ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴛʀᴀᴄᴋɪɴɢ ɪɴꜰᴏ (ɴᴇᴡ!)</b>\n\n"
        f"<b>💡 ᴅᴀɪʟʏ ʀᴇᴡᴀʀᴅꜱ:</b>\n"
        f"<b>🔄 +{DAILY_FREE_CREDITS} ꜰʀᴇᴇ ᴄʀᴇᴅɪᴛꜱ ᴇᴠᴇʀʏ 24 ʜᴏᴜʀꜱ</b>\n"
        f"<b>👥 +{INVITE_CREDITS} ᴄʀᴇᴅɪᴛꜱ ᴘᴇʀ ꜰʀɪᴇɴᴅ ɪɴᴠɪᴛᴇᴅ</b>\n"
        f"<b>🎫 ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇꜱ ꜰᴏʀ ᴇxᴛʀᴀ ᴄʀᴇᴅɪᴛꜱ</b>\n\n"
        f"<b>⏱ ᴀʟʟ ᴍᴇꜱꜱᴀɢᴇꜱ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ɪɴ {AUTO_DELETE_TIME}ꜱ</b>\n"
        f"<b>🔄 ᴄʀᴇᴅɪᴛꜱ ʀᴇꜰʀᴇꜱʜ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴀᴛ ᴍɪᴅɴɪɢʜᴛ</b>\n\n"
        f"<b>👑 ᴏᴡɴᴇʀ: @Hexh4ckerOFC</b>\n"
        f"<i>⚠️ ᴇᴅᴜᴄᴀᴛɪᴏɴᴀʟ ᴘᴜʀᴘᴏꜱᴇꜱ ᴏɴʟʏ. ᴜꜱᴇ ʀᴇꜱᴘᴏɴꜱɪʙʟʏ.</i>"
    )
    
    msg = await update.message.reply_text(txt, reply_markup=markup, parse_mode=ParseMode.HTML)
    asyncio.create_task(schedule_delete(msg, AUTO_DELETE_TIME))

# --- 🔗 API ---

async def safe_api_fetch(session, url, timeout=20):
    """Safe API fetch with retry - handles both JSON and HTML/PHP responses"""
    for attempt in range(3):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout), headers=headers, allow_redirects=True) as r:
                text = await r.text()
                if not text: 
                    logger.warning(f"Empty response from {url[:60]}")
                    continue
                
                logger.info(f"API Response ({len(text)} chars): {text[:200]}")
                
                # Try JSON first
                try:
                    return json.loads(text)
                except:
                    # Return raw text for HTML/PHP responses
                    if text.strip():
                        return {"raw_text": text, "is_html": True}
                    if attempt == 2:
                        return None
                    await asyncio.sleep(1)
        except asyncio.TimeoutError:
            logger.warning(f"Timeout on attempt {attempt+1}")
            if attempt == 2: return None
            await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"Fetch error on attempt {attempt+1}: {e}")
            if attempt == 2: return None
            await asyncio.sleep(1)
    return None

async def chatid_lookup(session, query):
    data = await safe_api_fetch(session, f"{LOOKUP_API}{query}")
    if not data: return "<blockquote>❌ ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</blockquote>"
    if isinstance(data, dict):
        if data.get("raw_text"): return f"<blockquote>📋 ʀᴀᴡ ʀᴇꜱᴘᴏɴꜱᴇ:</blockquote>\n<blockquote><code>{data['raw_text'][:300]}</code></blockquote>"
        if data.get("success"):
            d = data.get("data", data)
            if isinstance(d, dict):
                result = "<blockquote expandable>✨ 📱 ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ ɪɴꜰᴏ</blockquote>\n"
                if d.get('chat_id') or d.get('userid'): result += f"<blockquote>🆔 ᴄʜᴀᴛ ɪᴅ: <code>{d.get('chat_id', d.get('userid', query))}</code></blockquote>\n"
                if d.get('number'): result += f"<blockquote>📞 ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ: <code>{d['number']}</code></blockquote>\n"
                if d.get('name'): result += f"<blockquote>👤 ᴘʀᴏꜰɪʟᴇ ɴᴀᴍᴇ: <code>{d['name']}</code></blockquote>\n"
                return result
        if data.get("message"): return f"<blockquote>❌ {data['message']}</blockquote>"
    return "<blockquote>❌ ɴᴏ ᴅᴀᴛᴀ ꜰᴏᴜɴᴅ</blockquote>"

async def ifsc_lookup(session, code):
    data = await safe_api_fetch(session, f"{IFSC_API}{code.upper()}")
    if not data: return "<blockquote>❌ ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</blockquote>"
    if isinstance(data, dict) and not data.get("raw_text"):
        return (f"<blockquote expandable>✨ 🏦 ʙᴀɴᴋ ɪꜰꜱᴄ ᴅᴇᴛᴀɪʟꜱ</blockquote>\n"
                f"<blockquote>🏛 ʙᴀɴᴋ ɴᴀᴍᴇ: <code>{data.get('BANK','N/A')}</code></blockquote>\n"
                f"<blockquote>📍 ʙʀᴀɴᴄʜ: <code>{data.get('BRANCH','N/A')}</code></blockquote>\n"
                f"<blockquote>🔑 ɪꜰꜱᴄ ᴄᴏᴅᴇ: <code>{data.get('IFSC',code.upper())}</code></blockquote>\n"
                f"<blockquote>📫 ᴀᴅᴅʀᴇꜱꜱ: <code>{data.get('ADDRESS','N/A')}</code></blockquote>")
    return "<blockquote>❌ ɪɴᴠᴀʟɪᴅ ᴄᴏᴅᴇ</blockquote>"

async def bypass_lookup(session, link):
    s = get_settings()
    if s.get("bypass_maintenance",False): return "<blockquote>🛠️ ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ</blockquote>"
    data = await safe_api_fetch(session, f"{SHORTLINK_API}{link}", timeout=20)
    if not data: return "<blockquote>❌ ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</blockquote>"
    if isinstance(data, dict) and not data.get("raw_text"):
        r = data.get('bypassed_url') or data.get('url') or str(data)
        return f"<blockquote expandable>✨ 🔗 ʟɪɴᴋ ʙʏᴘᴀꜱꜱᴇᴅ</blockquote>\n<blockquote>🔗 ᴏʀɪɢɪɴᴀʟ ᴜʀʟ: <code>{str(r)}</code></blockquote>"
    return f"<blockquote>🔗 ʀᴇꜱᴜʟᴛ: <code>{str(data)}</code></blockquote>"

async def gst_lookup(session, gst_number):
    data = await safe_api_fetch(session, f"{GST_API}{gst_number.upper()}", timeout=20)
    if not data: return "<blockquote>❌ ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</blockquote>"
    if isinstance(data, dict) and not data.get("raw_text") and data.get("status") == "success" and data.get("data"):
        d = data["data"]
        result = "<blockquote expandable>✨ 📋 ɢꜱᴛ ʙᴜꜱɪɴᴇꜱꜱ ɪɴꜰᴏ</blockquote>\n"
        if d.get('TradeName'): result += f"<blockquote>🏢 ʙᴜꜱɪɴᴇꜱꜱ ɴᴀᴍᴇ: <code>{d['TradeName']}</code></blockquote>\n"
        if d.get('Gstin'): result += f"<blockquote>🔑 ɢꜱᴛ ɴᴜᴍʙᴇʀ: <code>{d['Gstin']}</code></blockquote>\n"
        if d.get('Status'):
            status_map = {'ACT': '🟢 ᴀᴄᴛɪᴠᴇ', 'SUS': '🔴 ꜱᴜꜱᴘᴇɴᴅᴇᴅ', 'CAN': '⚫ ᴄᴀɴᴄᴇʟʟᴇᴅ'}
            result += f"<blockquote>📊 ꜱᴛᴀᴛᴜꜱ: {status_map.get(d['Status'], d['Status'])}</blockquote>\n"
        if d.get('DtReg'): result += f"<blockquote>📅 ʀᴇɢɪꜱᴛᴇʀᴇᴅ ᴏɴ: <code>{d['DtReg']}</code></blockquote>\n"
        return result
    return "<blockquote>❌ ɪɴᴠᴀʟɪᴅ ɢꜱᴛ ɴᴜᴍʙᴇʀ</blockquote>"

async def pakistan_lookup(session, number):
    try:
        data = await safe_api_fetch(session, f"{PAK_API}{number}", timeout=20)
        if not data: return "<blockquote>❌ ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</blockquote>"
        if isinstance(data, dict) and not data.get("raw_text") and data.get("success") and data.get("data"):
            records = data["data"]
            valid = [r for r in records if isinstance(r, dict) and any(r.get(k) for k in ['name','number','cnic','address'])]
            if not valid: return "<blockquote>❌ ɴᴏ ᴅᴀᴛᴀ</blockquote>"
            result = f"<blockquote expandable>✨ 🇵🇰 ᴘᴀᴋɪꜱᴛᴀɴ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ</blockquote>\n"
            for i, r in enumerate(valid[:3], 1):
                if len(valid) > 1: result += f"\n<blockquote>━━ ʀᴇᴄᴏʀᴅ {i} ━━</blockquote>\n"
                if r.get('number'): result += f"<blockquote>📞 ᴘʜᴏɴᴇ: <code>{r['number']}</code></blockquote>\n"
                if r.get('name'): result += f"<blockquote>👤 ɴᴀᴍᴇ: <code>{r['name']}</code></blockquote>\n"
                if r.get('cnic'): result += f"<blockquote>🪪 ᴄɴɪᴄ: <code>{r['cnic']}</code></blockquote>\n"
                if r.get('address'): result += f"<blockquote>📍 ᴀᴅᴅʀᴇꜱꜱ: <code>{r['address'][:200]}</code></blockquote>\n"
            return result
        return "<blockquote>❌ ɴᴏ ᴅᴀᴛᴀ</blockquote>"
    except: return "<blockquote>❌ ᴇʀʀᴏʀ</blockquote>"

async def indnum_lookup(session, number):
    """Indian Number Info 2"""
    for attempt in range(3):
        data = await safe_api_fetch(session, f"{IND_NUM_API}{number}", timeout=30)
        if data and isinstance(data, dict) and not data.get("raw_text") and data.get("results"):
            break
        if attempt < 2:
            await asyncio.sleep(2)
    
    if not data: return "<blockquote>❌ ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</blockquote>"
    if isinstance(data, dict) and data.get("raw_text"): return "<blockquote>❌ ᴀᴘɪ ʀᴇᴛᴜʀɴᴇᴅ ʜᴛᴍʟ</blockquote>"
    if not isinstance(data, dict): return "<blockquote>❌ ɪɴᴠᴀʟɪᴅ ʀᴇꜱᴘᴏɴꜱᴇ</blockquote>"
    
    results = data.get("results", {})
    if not results: return "<blockquote>❌ ɴᴏ ʀᴇꜱᴜʟᴛꜱ</blockquote>"
    
    result = f"<blockquote expandable>✨ 📲 ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴀᴅᴠᴀɴᴄᴇᴅ ɪɴꜰᴏ</blockquote>\n"
    result += f"<blockquote>📞 Qᴜᴇʀɪᴇᴅ ɴᴜᴍʙᴇʀ: <code>{number}</code></blockquote>\n"
    found_any = False
    
    s3 = results.get("source_3", {}).get("data", {})
    if isinstance(s3, dict):
        for key, emoji in [("SIM card","💳"),("Connection","📶"),("Mobile State","📍"),("Hometown","🏠"),("Language","🗣"),("Owner Name","👤"),("Owner Address","📍"),("Complaints","⚠️"),("Tracker Id","🪪"),("Tracking History","📌"),("Tower Locations","📡"),("Mobile Locations","📍"),("Owner Personality","🧠")]:
            if s3.get(key):
                val = str(s3[key])[:300]
                result += f"<blockquote>{emoji} {key}: <code>{val}</code></blockquote>\n"
                found_any = True
    
    s4 = results.get("source_4", {}).get("data", {})
    if isinstance(s4, dict):
        if s4.get("carrier"): result += f"<blockquote>📡 ɴᴇᴛᴡᴏʀᴋ ᴄᴀʀʀɪᴇʀ: <code>{s4['carrier']}</code></blockquote>\n"; found_any = True
        if s4.get("country"): result += f"<blockquote>🌍 ᴄᴏᴜɴᴛʀʏ: <code>{s4['country']}</code></blockquote>\n"
    
    s8 = results.get("source_8", {}).get("data", {})
    if isinstance(s8, dict) and s8.get("success"):
        tc_data = s8.get("data", {})
        tc_results = tc_data.get("results", {}) if isinstance(tc_data, dict) else {}
        if isinstance(tc_results, dict):
            if tc_results.get("name"): result += f"<blockquote>👤 ᴛʀᴜᴇᴄᴀʟʟᴇʀ ɴᴀᴍᴇ: <code>{tc_results['name']}</code></blockquote>\n"; found_any = True
    
    if not found_any: return "<blockquote>❌ ɴᴏ ᴅᴇᴛᴀɪʟᴇᴅ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ꜰᴏᴜɴᴅ</blockquote>"
    return result

async def indnum3_lookup(session, number):
    """FIXED: Indian Number Info 3 - exploitsindia.site"""
    url = f"{IND_NUM_API_3}{number}"
    logger.info(f"INDNUM3 URL: {url}")
    
    try:
        # Use custom headers for PHP site
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=25), headers=headers, allow_redirects=True) as r:
            text = await r.text()
            logger.info(f"INDNUM3 Response ({len(text)} chars): {text[:300]}")
            
            if not text or len(text) < 20:
                return "<blockquote>❌ ᴇᴍᴘᴛʏ ʀᴇꜱᴘᴏɴꜱᴇ ꜰʀᴏᴍ ᴀᴘɪ</blockquote>"
            
            # Try to parse as JSON first
            try:
                data = json.loads(text)
                if isinstance(data, dict):
                    result = f"<blockquote expandable>✨ 🇮🇳 ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴛʀᴀᴄᴋɪɴɢ</blockquote>\n"
                    result += f"<blockquote>📞 ɴᴜᴍʙᴇʀ: <code>{number}</code></blockquote>\n"
                    
                    for key, emoji in [('name','👤'),('carrier','📡'),('location','📍'),('state','🏛'),('city','🏙️'),('operator','📶')]:
                        if data.get(key) and str(data[key]).strip():
                            result += f"<blockquote>{emoji} {key.title()}: <code>{str(data[key])[:200]}</code></blockquote>\n"
                    
                    # Show all fields if no standard ones found
                    if not any(data.get(k) for k in ['name','carrier','location','state']):
                        for k, v in list(data.items())[:8]:
                            if v and str(v).strip() and k.lower() not in ['success','message','error','status']:
                                result += f"<blockquote>🔹 {k}: <code>{str(v)[:200]}</code></blockquote>\n"
                    
                    return result
            except:
                pass
            
            # Parse HTML/PHP response
            clean = re.sub(r'<[^>]+>', ' ', text)
            clean = re.sub(r'&[a-z]+;', ' ', clean)
            clean = re.sub(r'\s+', ' ', clean).strip()
            
            result = f"<blockquote expandable>✨ 🇮🇳 ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴛʀᴀᴄᴋɪɴɢ</blockquote>\n"
            result += f"<blockquote>📞 ɴᴜᴍʙᴇʀ: <code>{number}</code></blockquote>\n"
            
            # Extract useful information from text
            patterns = {
                '👤 ɴᴀᴍᴇ': r'(?:Name|NAME|name)[:\s]*([A-Za-z\s]+)',
                '📡 ᴄᴀʀʀɪᴇʀ': r'(?:Carrier|CARRIER|carrier|Operator|operator)[:\s]*([A-Za-z\s]+)',
                '📍 ʟᴏᴄᴀᴛɪᴏɴ': r'(?:Location|location|City|city|State|state)[:\s]*([A-Za-z\s,]+)',
                '📞 ᴘʜᴏɴᴇ': r'(?:Phone|phone|Mobile|mobile|Number|number)[:\s]*([0-9+\-\s]+)',
            }
            
            found = False
            for label, pattern in patterns.items():
                match = re.search(pattern, clean, re.IGNORECASE)
                if match and match.group(1).strip():
                    result += f"<blockquote>{label}: <code>{match.group(1).strip()[:200]}</code></blockquote>\n"
                    found = True
            
            if not found:
                # Show cleaned text
                if len(clean) > 500: clean = clean[:497] + '...'
                result += f"<blockquote>📋 ᴅᴀᴛᴀ: <code>{clean}</code></blockquote>\n"
            
            return result
            
    except asyncio.TimeoutError:
        logger.error("INDNUM3 Timeout")
        return "<blockquote>⏱ ᴀᴘɪ ᴛɪᴍᴇᴏᴜᴛ - ᴛʀʏ ᴀɢᴀɪɴ</blockquote>"
    except Exception as e:
        logger.error(f"INDNUM3 Error: {e}")
        return f"<blockquote>⚠️ ᴇʀʀᴏʀ: {str(e)[:100]}</blockquote>"

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
        fields = {'Name': '👤 ɴᴀᴍᴇ', "Father's Name": '👨 ꜰᴀᴛʜᴇʀ', 'Mobile': '📱 ᴍᴏʙɪʟᴇ', 'Alternative Number': '📞 ᴀʟᴛᴇʀɴᴀᴛᴇ', 'Address': '📍 ᴀᴅᴅʀᴇꜱꜱ', 'Circle': '📡 ᴄɪʀᴄʟᴇ', 'State': '🏛 ꜱᴛᴀᴛᴇ', 'RC Number': '🔖 ʀᴄ ɴᴜᴍʙᴇʀ', 'Owner Name': '👤 ᴏᴡɴᴇʀ', 'Registration Date': '📅 ʀᴇɢ ᴅᴀᴛᴇ', 'Vehicle Class': '🚗 ᴠᴇʜɪᴄʟᴇ ᴄʟᴀꜱꜱ', 'Fuel Type': '⛽ ꜰᴜᴇʟ ᴛʏᴘᴇ', 'Insurance Company': '🛡️ ɪɴꜱᴜʀᴀɴᴄᴇ', 'Phone': '📞 ᴘʜᴏɴᴇ'}
        for field, label in fields.items():
            match = re.search(rf'{re.escape(field)}:\s*([^\n]+)', section, re.IGNORECASE)
            if match and match.group(1).strip() not in ['None', '', 'N/A', 'null']: record[label] = match.group(1).strip()
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
    title_map = {'aadhaar':'🪪 ᴀᴀᴅʜᴀʀ','mobile':'🇮🇳 ɪɴᴅ ɴᴜᴍʙᴇʀ','vehicle':'🚘 ᴠᴇʜɪᴄʟᴇ'}
    title = title_map.get(search_type, '📊 ꜱᴇᴀʀᴄʜ ʀᴇꜱᴜʟᴛꜱ')
    result = f"<blockquote expandable>✨ {title}</blockquote>\n"
    result += f"<blockquote>📊 ᴛᴏᴛᴀʟ ʀᴇᴄᴏʀᴅꜱ: {len(records)}</blockquote>\n"
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
        [InlineKeyboardButton("🎫 ɢᴇɴᴇʀᴀᴛᴇ ᴄᴏᴅᴇ", callback_data="ad_gen"), InlineKeyboardButton("📋 ᴠɪᴇᴡ ᴄᴏᴅᴇꜱ", callback_data="ad_codes")],
        [InlineKeyboardButton("🎁 ᴀᴅᴅ ᴄʀᴇᴅɪᴛꜱ", callback_data="ad_credit"), InlineKeyboardButton("📢 ʙʀᴏᴀᴅᴄᴀꜱᴛ", callback_data="ad_bcast")],
        [InlineKeyboardButton(f"{'🔴' if s.get('maintenance_mode') else '🟢'} ɢʟᴏʙᴀʟ ᴍᴀɪɴᴛ", callback_data="ad_maint")],
        [InlineKeyboardButton(f"{'🟢' if s.get('tgid_enabled',True) else '🔴'} ᴛɢ", callback_data="ad_tgid"), InlineKeyboardButton(f"{ms('tgid')} ᴍᴛɢ", callback_data="ad_maint_tgid")],
        [InlineKeyboardButton(f"{'🟢' if s.get('ifsc_enabled',True) else '🔴'} ɪꜰ", callback_data="ad_ifsc"), InlineKeyboardButton(f"{ms('ifsc')} ᴍɪꜰ", callback_data="ad_maint_ifsc")],
        [InlineKeyboardButton(f"{'🟢' if s.get('bypass_enabled',True) else '🔴'} ʙʏ", callback_data="ad_bypass_toggle"), InlineKeyboardButton(f"{ms('bypass')} ᴍʙʏ", callback_data="ad_maint_bypass")],
        [InlineKeyboardButton(f"{'🟢' if s.get('mobile_enabled',True) else '🔴'} ᴍᴏ", callback_data="ad_mobile"), InlineKeyboardButton(f"{ms('mobile')} ᴍᴍᴏ", callback_data="ad_maint_mobile")],
        [InlineKeyboardButton(f"{'🟢' if s.get('aadhaar_enabled',True) else '🔴'} ᴀᴀ", callback_data="ad_aadhaar"), InlineKeyboardButton(f"{ms('aadhaar')} ᴍᴀᴀ", callback_data="ad_maint_aadhaar")],
        [InlineKeyboardButton(f"{'🟢' if s.get('rc_enabled',True) else '🔴'} ʀᴄ", callback_data="ad_rc"), InlineKeyboardButton(f"{ms('rc')} ᴍʀᴄ", callback_data="ad_maint_rc")],
        [InlineKeyboardButton(f"{'🟢' if s.get('gst_enabled',True) else '🔴'} ɢꜱ", callback_data="ad_gst"), InlineKeyboardButton(f"{ms('gst')} ᴍɢꜱ", callback_data="ad_maint_gst")],
        [InlineKeyboardButton(f"{'🟢' if s.get('pak_enabled',True) else '🔴'} ᴘᴀ", callback_data="ad_pak"), InlineKeyboardButton(f"{ms('pak')} ᴍᴘᴀ", callback_data="ad_maint_pak")],
        [InlineKeyboardButton(f"{'🟢' if s.get('indnum_enabled',True) else '🔴'} ɪɴ2", callback_data="ad_indnum"), InlineKeyboardButton(f"{ms('indnum')} ᴍɪɴ2", callback_data="ad_maint_indnum")],
        [InlineKeyboardButton(f"{'🟢' if s.get('indnum3_enabled',True) else '🔴'} ɪɴ3", callback_data="ad_indnum3"), InlineKeyboardButton(f"{ms('indnum3')} ᴍɪɴ3", callback_data="ad_maint_indnum3")],
        [InlineKeyboardButton("🛠️ ʙʏᴘᴀꜱꜱ ᴍᴀɪɴᴛ", callback_data="ad_bypass_maint"), InlineKeyboardButton("❌ ᴄʟᴏꜱᴇ", callback_data="ad_close")]
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
    elif d == "ad_gen": ADMIN_STATE[q.from_user.id] = "gen"; await q.message.edit_text("<blockquote>🎫 ᴇɴᴛᴇʀ ᴄʀᴇᴅɪᴛꜱ:</blockquote>\n<i>100</i>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d == "ad_credit": ADMIN_STATE[q.from_user.id] = "credit"; await q.message.edit_text("<blockquote>🎁 ᴇɴᴛᴇʀ ɪᴅ ᴀᴍᴏᴜɴᴛ:</blockquote>\n<i>123456789 50</i>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d == "ad_bcast": ADMIN_STATE[q.from_user.id] = "bcast"; await q.message.edit_text("<blockquote>📢 ᴇɴᴛᴇʀ ᴍᴇꜱꜱᴀɢᴇ:</blockquote>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d == "ad_maint": s["maintenance_mode"] = not s.get("maintenance_mode", False); save_settings(s); await q.answer(f"Global: {'ON' if s['maintenance_mode'] else 'OFF'}", show_alert=True); await admin_panel(update, context)
    elif d.startswith("ad_maint_"):
        f = d.replace("ad_maint_", ""); s[f"maint_{f}"] = not s.get(f"maint_{f}", False); save_settings(s); await q.answer(f"{f}: {'🔴 ON' if s[f'maint_{f}'] else '🟢 OFF'}", show_alert=True); await admin_panel(update, context)
    elif d.startswith("ad_"):
        toggle_map = {"ad_tgid":"tgid_enabled","ad_ifsc":"ifsc_enabled","ad_bypass_toggle":"bypass_enabled","ad_mobile":"mobile_enabled","ad_aadhaar":"aadhaar_enabled","ad_rc":"rc_enabled","ad_gst":"gst_enabled","ad_pak":"pak_enabled","ad_indnum":"indnum_enabled","ad_indnum3":"indnum3_enabled"}
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
            m = await update.message.reply_text(f"<blockquote>🛠️ {s.get('maintenance_msg')}</blockquote>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m)); return
        if uid == ADMIN_ID and uid in ADMIN_STATE:
            state = ADMIN_STATE.pop(uid)
            if state == "gen":
                try: cr = int(txt); code = generate_redeem_code(cr); msg = await update.message.reply_text(f"<blockquote>✅ ᴄᴏᴅᴇ ʀᴇᴀᴅʏ</blockquote>\n<blockquote>🎫 <code>{code}</code> | 💰 {cr}cr</blockquote>", parse_mode=ParseMode.HTML)
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
        if txt in ["👑 ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ", "👑 ᴀᴅᴍɪɴ"]: await admin_panel(update, context)
        elif txt in ["ᴛɢ ɪᴅ ➜ 📞 ɴᴜᴍʙᴇʀ 🔍"]:
            if not s.get("tgid_enabled",True): m=await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("tgid")
            if maint: m=await update.message.reply_text(f"<blockquote>🛠️ {msg}</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'TG'
            btn = [[InlineKeyboardButton("🤖 @ChatIdInfoBot", url="https://t.me/ChatIdInfoBot")]]
            m = await update.message.reply_text("<blockquote>📱 ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ</blockquote>\n<i>7123181749</i>", reply_markup=InlineKeyboardMarkup(btn), parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        elif txt in ["🏦 ɪꜰꜱᴄ ɪɴꜰᴏ➜🔎"]:
            if not s.get("ifsc_enabled",True): m=await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("ifsc"); 
            if maint: m=await update.message.reply_text(f"<blockquote>🛠️ {msg}</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'IFSC'
            m = await update.message.reply_text("<blockquote>🏦 IFSC</blockquote>\n<i>SBIN0001234</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        elif txt in ["🔗 ʟɪɴᴋ ʙʏᴘᴀꜱꜱ"]:
            if not s.get("bypass_enabled",True): m=await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("bypass")
            if maint: m=await update.message.reply_text(f"<blockquote>🛠️ {msg}</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'SHORTLINK'
            m = await update.message.reply_text("<blockquote>🔗 Bypass</blockquote>\n<i>https://indianshortner.in/xxxx</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        elif txt == "🇮🇳 ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ➜👤":
            if not s.get("mobile_enabled",True): m=await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("mobile")
            if maint: m=await update.message.reply_text(f"<blockquote>🛠️ {msg}</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'MOBILE'
            m = await update.message.reply_text("<blockquote>🇮🇳 Mobile</blockquote>\n<i>9876543210</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        elif txt == "🪪 ᴀᴀᴅʜᴀʀ ɪɴꜰᴏ➜👤":
            if not s.get("aadhaar_enabled",True): m=await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("aadhaar")
            if maint: m=await update.message.reply_text(f"<blockquote>🛠️ {msg}</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'AADHAAR'
            m = await update.message.reply_text("<blockquote>🪪 Aadhaar</blockquote>\n<i>123456789012</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        elif txt == "🚘 ʀᴄ ᴅᴇᴛᴀɪʟꜱ":
            if not s.get("rc_enabled",True): m=await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("rc")
            if maint: m=await update.message.reply_text(f"<blockquote>🛠️ {msg}</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'VEHICLE'
            m = await update.message.reply_text("<blockquote>🚘 RC</blockquote>\n<i>KA01AB3256</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        elif txt == "📋 ɢꜱᴛ ʟᴏᴏᴋᴜᴘ":
            if not s.get("gst_enabled",True): m=await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("gst")
            if maint: m=await update.message.reply_text(f"<blockquote>🛠️ {msg}</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'GST'
            m = await update.message.reply_text("<blockquote>📋 GST</blockquote>\n<i>19BOKPS7056D1ZI</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        elif txt == "🇵🇰 ᴘᴀᴋ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ":
            if not s.get("pak_enabled",True): m=await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("pak")
            if maint: m=await update.message.reply_text(f"<blockquote>🛠️ {msg}</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'PAK'
            m = await update.message.reply_text("<blockquote>🇵🇰 Pakistan</blockquote>\n<i>923078750447</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        elif txt == "📲 ɪɴᴅ ɴᴜᴍ ɪɴꜰᴏ 𝟸":
            if not s.get("indnum_enabled",True): m=await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("indnum")
            if maint: m=await update.message.reply_text(f"<blockquote>🛠️ {msg}</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'INDNUM'
            m = await update.message.reply_text("<blockquote>📲 IndNum 2</blockquote>\n<i>6363016966</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        elif txt == "🇮🇳 ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ 𝟹 ➜👤":
            if not s.get("indnum3_enabled",True): m=await update.message.reply_text("<blockquote>📴 Disabled</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("indnum3")
            if maint: m=await update.message.reply_text(f"<blockquote>🛠️ {msg}</blockquote>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'INDNUM3'
            m = await update.message.reply_text("<blockquote>🇮🇳 ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴛʀᴀᴄᴋɪɴɢ</blockquote>\n<blockquote>Send any 10-digit Indian number</blockquote>\n<i>6363016966, 9876543210</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        elif txt in ["👥 ɪɴᴠɪᴛᴇ & ᴇᴀʀɴ", "👥 ɪɴᴠɪᴛᴇ"]:
            user = get_user(uid); bot_username = context.bot.username or BOT_USERNAME
            link = f"https://t.me/{bot_username}?start={user['invite_code']}"
            m = await update.message.reply_text(f"<blockquote>👥 Invite (+{INVITE_CREDITS}cr)</blockquote>\n<blockquote><code>{link}</code></blockquote>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m, 120))
        elif txt in ["🎫 ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ"]:
            context.user_data['redeem_mode'] = True
            m = await update.message.reply_text("<blockquote>🎫 Enter redeem code:</blockquote>\n<i>HEX-XXXXXXXXXX</i>", parse_mode=ParseMode.HTML)
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
                    m = await update.message.reply_text("<blockquote>❌ No credits!</blockquote>", parse_mode=ParseMode.HTML)
                    asyncio.create_task(schedule_delete(m)); context.user_data['mode'] = None; return
                await run_query(update, context, mode, txt); context.user_data['mode'] = None
    except Exception as e: logger.error(f"Msg: {e}")

async def run_query(update, context, mode, query):
    if not await net_ok():
        m = await update.message.reply_text("<blockquote>🔴 No internet</blockquote>", parse_mode=ParseMode.HTML)
        asyncio.create_task(schedule_delete(m)); return
    await update.message.reply_chat_action(ChatAction.TYPING)
    names = {'TG':'📱','IFSC':'🏦','SHORTLINK':'🔗','AADHAAR':'🪪','MOBILE':'🇮🇳','VEHICLE':'🚘','GST':'📋','PAK':'🇵🇰','INDNUM':'📲','INDNUM3':'🇮🇳'}
    st = await update.message.reply_text("<blockquote>🟩 Searching...</blockquote>", parse_mode=ParseMode.HTML)
    lt = asyncio.create_task(loading_animation(st, names.get(mode, '')))
    credit_deducted = False
    try:
        if mode in ['AADHAAR', 'MOBILE', 'VEHICLE']:
            raw = run_india_script({'AADHAAR':'2','MOBILE':'1','VEHICLE':'4'}[mode], query)
            if raw:
                records = parse_all_india_records(raw)
                result = format_records_result(records, {'AADHAAR':'aadhaar','MOBILE':'mobile','VEHICLE':'vehicle'}[mode])
                if records and "❌" not in str(result): use_credit(update.effective_user.id); credit_deducted = True
            else: result = "<blockquote>❌ Script failed</blockquote>"
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
        final = f"{result}\n{SEP}\n<blockquote>💰 {'ᴄʀ: '+str(user.get('credits',0)) if credit_deducted else 'ɴᴏ ᴄʀ ᴅᴇᴅᴜᴄᴛᴇᴅ'} | ⏱ {AUTO_DELETE_TIME}ꜱ</blockquote>{DISCLAIMER}{FOOTER}"
        sent = await st.edit_text(final, parse_mode=ParseMode.HTML)
        asyncio.create_task(schedule_delete(sent))
    except Exception as e:
        lt.cancel(); logger.error(f"Query: {e}")
        try: await st.edit_text(f"<blockquote>⚠️ ᴇʀʀᴏʀ</blockquote>{FOOTER}", parse_mode=ParseMode.HTML)
        except: pass

def main():
    print("🔄 Hex Terminal Starting...")
    try: subprocess.run([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4"], capture_output=True, timeout=30)
    except: pass
    
    # Show data storage location
    print(f"📁 Data stored in: {os.getcwd()}")
    print(f"📁 Users file: {USERS_FILE}")
    print(f"📁 Backup dir: {BACKUP_DIR}")
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify_cb, pattern="^verify$"))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^ad_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg_handler))
    print(f"✅ {BOT_NAME} Ready!")
    print("🇮🇳 INDNUM3 Fixed | 💾 Auto-backup enabled")
    app.run_polling()

if __name__ == '__main__':
    main()