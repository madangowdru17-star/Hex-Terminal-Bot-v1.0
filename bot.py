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

# --- PREMIUM EMOJIS FOR TEXT MESSAGES ---
PE = lambda eid, fallback: f'<tg-emoji emoji-id="{eid}">{fallback}</tg-emoji>'

EMOJI_WARN = PE("6267039884016358504", "⚠️")
EMOJI_CHECK = PE("6267008582294705964", "✅")
EMOJI_CROSS = PE("6267000941547885720", "❌")
EMOJI_LOCK = PE("5316522278056399236", "🔒")
EMOJI_CROWN = PE("6267128480601741166", "👑")
EMOJI_DIAMOND = PE("6264791387032523779", "💎")
EMOJI_STAR = PE("6266969287638913443", "⭐")
EMOJI_GIFT = PE("5203996991054432397", "🎁")
EMOJI_FIRE = PE("6264785189394717307", "🔥")
EMOJI_SEARCH = PE("5231012545799666522", "🔍")
EMOJI_PHONE = PE("5947494995798789024", "📞")
EMOJI_BANK = PE("5264895611517300926", "🏦")
EMOJI_LINK = PE("5271604874419647061", "🔗")
EMOJI_CAR = PE("5253752975997803460", "🚘")
EMOJI_CARD = PE("5260561650213220533", "🪪")
EMOJI_USER = PE("5249053508681883137", "👤")
EMOJI_INDIA = PE("6284779941489812433", "🇮🇳")
EMOJI_PAK = PE("5913705895375672082", "🇵🇰")
EMOJI_PHONE2 = PE("5406809207947142040", "📲")
EMOJI_INVITE = PE("5244933196230972438", "👥")
EMOJI_TICKET = PE("5285515895534278367", "🎫")
EMOJI_CREDIT = PE("6267068789146260253", "💰")
EMOJI_REFRESH = PE("5375338737028841420", "🔄")
EMOJI_CLOCK = PE("5382194935057372936", "⏱")
EMOJI_BOLT = PE("6284971355297290197", "⚡")
EMOJI_GREEN = PE("5386367538735104399", "🟩")
EMOJI_BLACK = PE("5116476703002068797", "⬛")
EMOJI_SPARKLE = PE("5467683093693354332", "✨")
EMOJI_ROCKET = PE("5195033767969839232", "🚀")
EMOJI_TOOLS = PE("5462921117423384478", "🛠️")
EMOJI_DISABLED = PE("5373165973203348165", "📴")
EMOJI_FATHER = PE("6147864334077794239", "👨")
EMOJI_LOCATION = PE("5391032818111363540", "📍")
EMOJI_HOME = PE("5280955052582785391", "🏠")
EMOJI_STATE = PE("5388927107315283144", "🏛")
EMOJI_NETWORK = PE("5321141214735508486", "📡")
EMOJI_SIGNAL = PE("6147892053796725336", "📶")
EMOJI_SIM = PE("5800717980266403037", "💳")
EMOJI_CHART = PE("6093382540784046658", "📊")

# --- INLINE BUTTON STYLES (Only work for InlineKeyboardButton) ---
# These are premium emoji IDs for colored buttons
INLINE_BTN_STYLES = {
    "primary": {
        "emoji_id": "5258096772776991776",  # Blue/Primary
        "style": "primary"
    },
    "success": {
        "emoji_id": "5258503720928288433",  # Green/Success
        "style": "success"
    },
    "danger": {
        "emoji_id": "5258331647358540449",  # Red/Danger
        "style": "danger"
    },
    "warning": {
        "emoji_id": "5258478058097409351",  # Yellow/Warning
        "style": None  # Fallback to normal
    },
    "info": {
        "emoji_id": "5258024981144066782",  # Blue/Info
        "style": None
    }
}

# --- BUTTON EMOJIS (Normal Unicode for KeyboardButtons) ---
BTN_PHONE = "📱"
BTN_BANK = "🏦"
BTN_LINK = "🔗"
BTN_AADHAAR = "🪪"
BTN_INDIA = "🇮🇳"
BTN_CAR = "🚘"
BTN_GST = "📋"
BTN_PAK = "🇵🇰"
BTN_PHONE2 = "📲"
BTN_INVITE = "👥"
BTN_TICKET = "🎫"
BTN_CROWN = "👑"
BTN_SEARCH = "🔍"
BTN_MAGNIFY = "🔎"
BTN_USER = "👤"
BTN_ADMIN = "👑"
BTN_STATS = "📊"
BTN_HELP = "❓"
BTN_ABOUT = "ℹ️"
BTN_REDEEM = "🎟️"
BTN_EARN = "💰"
BTN_START = "🚀"

DISCLAIMER = f"\n\n<b>{EMOJI_WARN} ᴅɪꜱᴄʟᴀɪᴍᴇʀ:</b>\n<i>ᴇᴅᴜᴄᴀᴛɪᴏɴᴀʟ ᴘᴜʀᴘᴏꜱᴇꜱ ᴏɴʟʏ. ᴜꜱᴇ ʀᴇꜱᴘᴏɴꜱɪʙʟʏ.</i>"

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
    if code not in codes: return False, f"{EMOJI_CROSS} ɪɴᴠᴀʟɪᴅ ᴄᴏᴅᴇ"
    if codes[code].get("used"): return False, f"{EMOJI_CROSS} ᴀʟʀᴇᴀᴅʏ ᴜꜱᴇᴅ"
    cr = codes[code]["credits"]; codes[code]["used"] = True; codes[code]["used_by"] = str(uid)
    save_json(REDEEM_FILE, codes); bal = add_credits(uid, cr)
    return True, f"{EMOJI_CHECK} +{cr} ᴄʀᴇᴅɪᴛꜱ ᴀᴅᴅᴇᴅ!\n{EMOJI_CREDIT} ʙᴀʟᴀɴᴄᴇ: {bal}"

def get_settings():
    try: return load_json(SETTINGS_FILE)
    except:
        d = {"bypass_maintenance":False,"tgid_enabled":True,"ifsc_enabled":True,"bypass_enabled":True,"mobile_enabled":True,"aadhaar_enabled":True,"rc_enabled":True,"gst_enabled":True,"pak_enabled":True,"indnum_enabled":True,"indnum3_enabled":True,"maintenance_mode":False}
        for k in ["tgid","ifsc","bypass","mobile","aadhaar","rc","gst","pak","indnum","indnum3"]: d[f"maint_msg_{k}"] = f"{EMOJI_TOOLS} {k} is under maintenance."; d[f"maint_{k}"] = False
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
    bars = ["🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛","🟩🟩⬛⬛⬛⬛⬛⬛⬛⬛","🟩🟩🟩⬛⬛⬛⬛⬛⬛⬛","🟩🟩🟩🟩⬛⬛⬛⬛⬛⬛","🟩🟩🟩🟩🟩⬛⬛⬛⬛⬛","🟩🟩🟩🟩🟩🟩⬛⬛⬛⬛","🟩🟩🟩🟩🟩🟩🟩⬛⬛⬛","🟩🟩🟩🟩🟩🟩🟩🟩⬛⬛","🟩🟩🟩🟩🟩🟩🟩🟩🟩⬛","🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩"]
    percentages = ["0%","10%","20%","30%","40%","50%","60%","70%","80%","90%","100%"]
    for i, bar in enumerate(bars):
        try: await msg.edit_text(f"<blockquote>{EMOJI_BOLT} {name}</blockquote>\n<code>{bar} {percentages[i]}</code>", parse_mode=ParseMode.HTML); await asyncio.sleep(0.2)
        except: break

def check_feature_maintenance(feature_key):
    s = get_settings()
    if s.get(f"maint_{feature_key}", False):
        return True, s.get(f"maint_msg_{feature_key}", f"{EMOJI_TOOLS} Under maintenance.")
    return False, ""

async def show_verification_page(update, context):
    try:
        bot = await context.bot.get_me()
        photos = await context.bot.get_user_profile_photos(bot.id, limit=1)
        caption = (
            f"<b>{EMOJI_DIAMOND} {BOT_NAME} {EMOJI_DIAMOND}</b>\n"
            f"<b>@{BOT_USERNAME}</b>\n\n"
            f"<b>{EMOJI_LOCK} ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ʀᴇQᴜɪʀᴇᴅ</b>\n"
            f"<b>ᴊᴏɪɴ ʙᴏᴛʜ ᴄʜᴀɴɴᴇʟꜱ ᴛᴏ ᴜɴʟᴏᴄᴋ</b>\n\n"
            f"<b>{EMOJI_WARN} ɢᴜɪᴅᴇʟɪɴᴇꜱ:</b>\n"
            f"<b>• ᴇᴅᴜᴄᴀᴛɪᴏɴᴀʟ ᴘᴜʀᴘᴏꜱᴇꜱ ᴏɴʟʏ</b>\n"
            f"<b>• ᴜꜱᴇ ᴏɴ ʏᴏᴜʀ ᴏᴡɴ ᴅᴀᴛᴀ</b>\n"
            f"<b>• ʀᴇꜱᴘᴇᴄᴛ ᴘʀɪᴠᴀᴄʏ ʟᴀᴡꜱ</b>\n\n"
            f"<b>{EMOJI_GIFT} +{DAILY_FREE_CREDITS} ᴅᴀɪʟʏ {EMOJI_STAR}</b>\n"
            f"<b>{EMOJI_INVITE} +{INVITE_CREDITS} ᴘᴇʀ ɪɴᴠɪᴛᴇ</b>\n"
            f"<b>{EMOJI_CLOCK} {AUTO_DELETE_TIME}ꜱ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ</b>\n\n"
            f"<b>{EMOJI_CROWN} ᴏᴡɴᴇʀ: @Hexh4ckerOFC</b>\n"
            f"<i>{EMOJI_WARN} ᴍɪꜱᴜꜱᴇ ᴍᴀʏ ʟᴇᴀᴅ ᴛᴏ ʟᴇɢᴀʟ ᴀᴄᴛɪᴏɴ</i>"
        )
        if photos and photos.photos: sent = await update.message.reply_photo(photo=photos.photos[0][-1].file_id, caption=caption, parse_mode=ParseMode.HTML)
        else: sent = await update.message.reply_text(caption, parse_mode=ParseMode.HTML)
        asyncio.create_task(schedule_delete(sent, 120))
    except: pass
    
    buttons = [
        [InlineKeyboardButton("📢 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 𝟷", url=LINK_1)],
        [InlineKeyboardButton("📢 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 𝟸", url=LINK_2)],
        [InlineKeyboardButton("✅ ɪ'ᴠᴇ ᴊᴏɪɴᴇᴅ - ᴠᴇʀɪꜰʏ", callback_data="verify")]
    ]
    sent2 = await update.message.reply_text(f"<blockquote>{EMOJI_LOCK} ᴊᴏɪɴ ʙᴏᴛʜ ᴄʜᴀɴɴᴇʟꜱ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴠᴇʀɪꜰʏ</blockquote>", reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)
    asyncio.create_task(schedule_delete(sent2, 120))

# --- 🎨 CREATE COLORED INLINE BUTTONS WITH PREMIUM EMOJIS ---

def create_colored_button(text: str, callback_data: str = None, url: str = None, color: str = "primary", custom_emoji_id: str = None):
    """
    Create a colored inline button with premium emoji
    
    Colors: "primary" (blue), "success" (green), "danger" (red), "warning" (yellow), "info" (blue)
    """
    style_map = {
        "primary": {"emoji_id": "5258096772776991776", "style": "primary"},
        "success": {"emoji_id": "5258503720928288433", "style": "success"},
        "danger": {"emoji_id": "5258331647358540449", "style": "danger"},
        "warning": {"emoji_id": "5258478058097409351", "style": None},
        "info": {"emoji_id": "5258024981144066782", "style": None}
    }
    
    style_info = style_map.get(color, style_map["primary"])
    emoji_id = custom_emoji_id or style_info["emoji_id"]
    style = style_info["style"]
    
    try:
        # Try creating button with both icon and style
        return InlineKeyboardButton(
            text=text,
            callback_data=callback_data,
            url=url,
            icon_custom_emoji_id=emoji_id,
            style=style
        )
    except TypeError:
        try:
            # Try with just icon (no style)
            return InlineKeyboardButton(
                text=text,
                callback_data=callback_data,
                url=url,
                icon_custom_emoji_id=emoji_id
            )
        except TypeError:
            # Fallback to normal button
            return InlineKeyboardButton(
                text=text,
                callback_data=callback_data,
                url=url
            )

def create_styled_row(buttons_config: list) -> list:
    """Create a row of colored buttons"""
    row = []
    for cfg in buttons_config:
        text = cfg.get("text", "")
        callback_data = cfg.get("callback_data")
        url = cfg.get("url")
        color = cfg.get("color", "primary")
        custom_emoji_id = cfg.get("custom_emoji_id")
        
        btn = create_colored_button(text, callback_data, url, color, custom_emoji_id)
        row.append(btn)
    return row

# --- 📋 MAIN MENU ---

async def main_menu(update, context):
    """Main menu with styled buttons"""
    is_admin = update.effective_user.id == ADMIN_ID
    user = get_user(update.effective_user.id)
    s = get_settings()
    
    # Build keyboard with normal buttons (ReplyKeyboardMarkup doesn't support colors)
    kb = []
    
    # Row 1: TG ID & IFSC
    row1 = []
    if s.get("tgid_enabled", True):
        row1.append(KeyboardButton(f"{BTN_PHONE} ᴛɢ ɪᴅ ➜ {BTN_PHONE2} ɴᴜᴍʙᴇʀ {BTN_SEARCH}"))
    if s.get("ifsc_enabled", True):
        row1.append(KeyboardButton(f"{BTN_BANK} ɪꜰꜱᴄ ɪɴꜰᴏ➜{BTN_MAGNIFY}"))
    if row1:
        kb.append(row1)
    
    # Row 2: Link Bypass
    if s.get("bypass_enabled", True):
        kb.append([KeyboardButton(f"{BTN_LINK} ʟɪɴᴋ ʙʏᴘᴀꜱꜱ")])
    
    # Row 3: Aadhaar & India Number
    row2 = []
    if s.get("aadhaar_enabled", True):
        row2.append(KeyboardButton(f"{BTN_AADHAAR} ᴀᴀᴅʜᴀʀ ɪɴꜰᴏ➜{BTN_USER}"))
    if s.get("mobile_enabled", True):
        row2.append(KeyboardButton(f"{BTN_INDIA} ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ➜{BTN_USER}"))
    if row2:
        kb.append(row2)
    
    # Row 4: RC & GST
    row3 = []
    if s.get("rc_enabled", True):
        row3.append(KeyboardButton(f"{BTN_CAR} ʀᴄ ᴅᴇᴛᴀɪʟꜱ"))
    if s.get("gst_enabled", True):
        row3.append(KeyboardButton(f"{BTN_GST} ɢꜱᴛ ʟᴏᴏᴋᴜᴘ"))
    if row3:
        kb.append(row3)
    
    # Row 5: Pakistan & India Num 2
    row4 = []
    if s.get("pak_enabled", True):
        row4.append(KeyboardButton(f"{BTN_PAK} ᴘᴀᴋ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ"))
    if s.get("indnum_enabled", True):
        row4.append(KeyboardButton(f"{BTN_PHONE2} ɪɴᴅ ɴᴜᴍ ɪɴꜰᴏ 𝟸"))
    if row4:
        kb.append(row4)
    
    # Row 6: India Number 3
    if s.get("indnum3_enabled", True):
        kb.append([KeyboardButton(f"{BTN_INDIA} ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ 𝟹 ➜{BTN_USER}")])
    
    # Row 7: Invite & Redeem
    kb.append([
        KeyboardButton(f"{BTN_INVITE} ɪɴᴠɪᴛᴇ & ᴇᴀʀɴ"),
        KeyboardButton(f"{BTN_TICKET} ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ")
    ])
    
    # Row 8: Help & About
    kb.append([
        KeyboardButton(f"{BTN_HELP} ʜᴇʟᴘ"),
        KeyboardButton(f"{BTN_ABOUT} ᴀʙᴏᴜᴛ")
    ])
    
    # Row 9: Stats
    kb.append([KeyboardButton(f"{BTN_STATS} ꜱᴛᴀᴛꜱ")])
    
    # Admin buttons
    if is_admin:
        kb.append([KeyboardButton(f"{BTN_ADMIN} ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ")])
    
    markup = ReplyKeyboardMarkup(kb, resize_keyboard=True)
    cr = user.get("credits", 0)
    
    # Text with premium emojis
    txt = (
        f"<b>{EMOJI_DIAMOND} ᴘʀᴇᴍɪᴜᴍ ʜᴜʙ {EMOJI_DIAMOND}</b>\n"
        f"<b>{EMOJI_USER} ᴡᴇʟᴄᴏᴍᴇ ʙᴀᴄᴋ,</b> <code>{update.effective_user.first_name}</code>\n\n"
        f"<b>{EMOJI_CHART} ʏᴏᴜʀ ꜱᴛᴀᴛɪꜱᴛɪᴄꜱ:</b>\n"
        f"<b>┃ {EMOJI_CREDIT} ᴄʀᴇᴅɪᴛꜱ: {cr}</b>\n"
        f"<b>┃ {EMOJI_SEARCH} Qᴜᴇʀɪᴇꜱ: {user.get('total_queries',0)}</b>\n"
        f"<b>┃ {EMOJI_INVITE} ɪɴᴠɪᴛᴇꜱ: {user.get('invites',0)}</b>\n\n"
        f"<b>{EMOJI_GIFT} ʀᴇᴡᴀʀᴅꜱ:</b>\n"
        f"<b>{EMOJI_REFRESH} +{DAILY_FREE_CREDITS} ᴅᴀɪʟʏ ꜰʀᴇᴇ</b>\n"
        f"<b>{EMOJI_INVITE} +{INVITE_CREDITS} ᴘᴇʀ ɪɴᴠɪᴛᴇ</b>\n"
        f"<b>{EMOJI_CLOCK} {AUTO_DELETE_TIME}ꜱ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ</b>\n\n"
        f"<b>{EMOJI_STAR} ꜱᴇʟᴇᴄᴛ ᴀ ꜱᴇʀᴠɪᴄᴇ ʙᴇʟᴏᴡ {EMOJI_STAR}</b>"
    )
    
    msg = await update.message.reply_text(txt, reply_markup=markup, parse_mode=ParseMode.HTML)
    asyncio.create_task(schedule_delete(msg, AUTO_DELETE_TIME))

# --- 🔗 API FUNCTIONS ---

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
    if not data: return f"<blockquote>{EMOJI_CROSS} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</blockquote>"
    if isinstance(data, dict) and not data.get("raw_text") and data.get("success"):
        d = data.get("data", data)
        if isinstance(d, dict):
            result = f"<blockquote expandable>{EMOJI_SPARKLE} {EMOJI_PHONE} ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ ɪɴꜰᴏ {EMOJI_SPARKLE}</blockquote>\n"
            if d.get('chat_id') or d.get('userid'): result += f"<blockquote>{EMOJI_SEARCH} ᴄʜᴀᴛ ɪᴅ: <code>{d.get('chat_id', d.get('userid', query))}</code></blockquote>\n"
            if d.get('number'): result += f"<blockquote>{EMOJI_PHONE2} ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ: <code>{d['number']}</code></blockquote>\n"
            if d.get('name'): result += f"<blockquote>{EMOJI_USER} ᴘʀᴏꜰɪʟᴇ ɴᴀᴍᴇ: <code>{d['name']}</code></blockquote>\n"
            return result
    return f"<blockquote>{EMOJI_CROSS} ɴᴏᴛ ꜰᴏᴜɴᴅ</blockquote>"

async def ifsc_lookup(session, code):
    data = await safe_api_fetch(session, f"{IFSC_API}{code.upper()}")
    if not data or isinstance(data, dict) and data.get("raw_text"): return f"<blockquote>{EMOJI_CROSS} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</blockquote>"
    if isinstance(data, dict):
        return (f"<blockquote expandable>{EMOJI_SPARKLE} {EMOJI_BANK} ʙᴀɴᴋ ɪꜰꜱᴄ ᴅᴇᴛᴀɪʟꜱ {EMOJI_SPARKLE}</blockquote>\n"
                f"<blockquote>{EMOJI_BANK} ʙᴀɴᴋ ɴᴀᴍᴇ: <code>{data.get('BANK','N/A')}</code></blockquote>\n"
                f"<blockquote>{EMOJI_LOCATION} ʙʀᴀɴᴄʜ: <code>{data.get('BRANCH','N/A')}</code></blockquote>\n"
                f"<blockquote>{EMOJI_CARD} ɪꜰꜱᴄ ᴄᴏᴅᴇ: <code>{data.get('IFSC',code.upper())}</code></blockquote>\n"
                f"<blockquote>{EMOJI_LOCATION} ᴀᴅᴅʀᴇꜱꜱ: <code>{data.get('ADDRESS','N/A')}</code></blockquote>")
    return f"<blockquote>{EMOJI_CROSS} ɪɴᴠᴀʟɪᴅ ᴄᴏᴅᴇ</blockquote>"

async def bypass_lookup(session, link):
    s = get_settings()
    if s.get("bypass_maintenance",False): return f"<blockquote>{EMOJI_TOOLS} ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ</blockquote>"
    data = await safe_api_fetch(session, f"{SHORTLINK_API}{link}", timeout=20)
    if not data or isinstance(data, dict) and data.get("raw_text"): return f"<blockquote>{EMOJI_CROSS} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</blockquote>"
    if isinstance(data, dict):
        r = data.get('bypassed_url') or data.get('url') or str(data)
        return f"<blockquote expandable>{EMOJI_SPARKLE} {EMOJI_LINK} ʟɪɴᴋ ʙʏᴘᴀꜱꜱᴇᴅ {EMOJI_SPARKLE}</blockquote>\n<blockquote>{EMOJI_LINK} ᴏʀɪɢɪɴᴀʟ ᴜʀʟ: <code>{str(r)}</code></blockquote>"
    return f"<blockquote>{EMOJI_LINK} ʀᴇꜱᴜʟᴛ: <code>{str(data)}</code></blockquote>"

async def gst_lookup(session, gst_number):
    data = await safe_api_fetch(session, f"{GST_API}{gst_number.upper()}", timeout=20)
    if not data or isinstance(data, dict) and data.get("raw_text"): return f"<blockquote>{EMOJI_CROSS} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</blockquote>"
    if isinstance(data, dict) and data.get("status") == "success" and data.get("data"):
        d = data["data"]
        result = f"<blockquote expandable>{EMOJI_SPARKLE} {EMOJI_CARD} ɢꜱᴛ ʙᴜꜱɪɴᴇꜱꜱ ɪɴꜰᴏ {EMOJI_SPARKLE}</blockquote>\n"
        if d.get('TradeName'): result += f"<blockquote>{EMOJI_BANK} ʙᴜꜱɪɴᴇꜱꜱ ɴᴀᴍᴇ: <code>{d['TradeName']}</code></blockquote>\n"
        if d.get('Gstin'): result += f"<blockquote>{EMOJI_CARD} ɢꜱᴛ ɴᴜᴍʙᴇʀ: <code>{d['Gstin']}</code></blockquote>\n"
        return result
    return f"<blockquote>{EMOJI_CROSS} ɪɴᴠᴀʟɪᴅ ɢꜱᴛ</blockquote>"

async def pakistan_lookup(session, number):
    try:
        data = await safe_api_fetch(session, f"{PAK_API}{number}", timeout=20)
        if not data or isinstance(data, dict) and data.get("raw_text"): return f"<blockquote>{EMOJI_CROSS} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</blockquote>"
        if isinstance(data, dict) and data.get("success") and data.get("data"):
            valid = [r for r in data["data"] if isinstance(r, dict) and any(r.get(k) for k in ['name','number','cnic','address'])]
            if not valid: return f"<blockquote>{EMOJI_CROSS} ɴᴏ ᴅᴀᴛᴀ</blockquote>"
            result = f"<blockquote expandable>{EMOJI_SPARKLE} {EMOJI_PAK} ᴘᴀᴋɪꜱᴛᴀɴ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ {EMOJI_SPARKLE}</blockquote>\n"
            for i, r in enumerate(valid[:3], 1):
                if len(valid) > 1: result += f"\n<blockquote>━━ {EMOJI_USER} ʀᴇᴄᴏʀᴅ {i} ━━</blockquote>\n"
                if r.get('number'): result += f"<blockquote>{EMOJI_PHONE2} ᴘʜᴏɴᴇ: <code>{r['number']}</code></blockquote>\n"
                if r.get('name'): result += f"<blockquote>{EMOJI_USER} ɴᴀᴍᴇ: <code>{r['name']}</code></blockquote>\n"
                if r.get('cnic'): result += f"<blockquote>{EMOJI_CARD} ᴄɴɪᴄ: <code>{r['cnic']}</code></blockquote>\n"
                if r.get('address'): result += f"<blockquote>{EMOJI_LOCATION} ᴀᴅᴅʀᴇꜱꜱ: <code>{r['address'][:200]}</code></blockquote>\n"
            return result
        return f"<blockquote>{EMOJI_CROSS} ɴᴏ ᴅᴀᴛᴀ</blockquote>"
    except: return f"<blockquote>{EMOJI_CROSS} ᴇʀʀᴏʀ</blockquote>"

async def indnum_lookup(session, number):
    for attempt in range(3):
        data = await safe_api_fetch(session, f"{IND_NUM_API}{number}", timeout=30)
        if data and isinstance(data, dict) and not data.get("raw_text") and data.get("results"): break
        if attempt < 2: await asyncio.sleep(2)
    if not data or isinstance(data, dict) and data.get("raw_text"): return f"<blockquote>{EMOJI_CROSS} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ</blockquote>"
    results = data.get("results", {})
    if not results: return f"<blockquote>{EMOJI_CROSS} ɴᴏ ʀᴇꜱᴜʟᴛꜱ</blockquote>"
    result = f"<blockquote expandable>{EMOJI_SPARKLE} {EMOJI_PHONE2} ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴀᴅᴠᴀɴᴄᴇᴅ {EMOJI_SPARKLE}</blockquote>\n<blockquote>{EMOJI_PHONE2} ɴᴜᴍʙᴇʀ: <code>{number}</code></blockquote>\n"
    found = False
    s3 = results.get("source_3", {}).get("data", {})
    if isinstance(s3, dict):
        for k, e in [("SIM card",EMOJI_SIM),("Connection",EMOJI_SIGNAL),("Mobile State",EMOJI_LOCATION),("Hometown",EMOJI_HOME)]:
            if s3.get(k): result += f"<blockquote>{e} {k}: <code>{str(s3[k])[:200]}</code></blockquote>\n"; found = True
    s4 = results.get("source_4", {}).get("data", {})
    if isinstance(s4, dict) and s4.get("carrier"): result += f"<blockquote>{EMOJI_NETWORK} ᴄᴀʀʀɪᴇʀ: <code>{s4['carrier']}</code></blockquote>\n"; found = True
    return result if found else f"<blockquote>{EMOJI_CROSS} ɴᴏ ᴅᴀᴛᴀ</blockquote>"

async def indnum3_lookup(session, number):
    url = f"{IND_NUM_API_3}{number}"
    try:
        headers = {'User-Agent': 'Mozilla/5.0','Accept': '*/*'}
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=25), headers=headers, allow_redirects=True) as r:
            text = await r.text()
            if not text or len(text) < 20: return f"<blockquote>{EMOJI_CROSS} ᴇᴍᴘᴛʏ ʀᴇꜱᴘᴏɴꜱᴇ</blockquote>"
            try:
                data = json.loads(text)
                if isinstance(data, dict):
                    result = f"<blockquote expandable>{EMOJI_SPARKLE} {EMOJI_INDIA} ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴛʀᴀᴄᴋɪɴɢ {EMOJI_SPARKLE}</blockquote>\n<blockquote>{EMOJI_PHONE2} ɴᴜᴍʙᴇʀ: <code>{number}</code></blockquote>\n"
                    for k, v in data.items():
                        if v and str(v).strip():
                            result += f"<blockquote>{EMOJI_SEARCH} {k}: <code>{str(v)[:200]}</code></blockquote>\n"
                    return result
            except: pass
            clean = re.sub(r'<[^>]+>', '\n', text)
            lines = [l.strip() for l in clean.split('\n') if l.strip() and len(l.strip()) > 1]
            result = f"<blockquote expandable>{EMOJI_SPARKLE} {EMOJI_INDIA} ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴛʀᴀᴄᴋɪɴɢ {EMOJI_SPARKLE}</blockquote>\n<blockquote>{EMOJI_PHONE2} ɴᴜᴍʙᴇʀ: <code>{number}</code></blockquote>\n"
            found = 0
            for line in lines[:20]:
                if ':' in line:
                    parts = line.split(':', 1)
                    key, val = parts[0].strip(), parts[1].strip() if len(parts) > 1 else ''
                    if val:
                        e = EMOJI_USER if any(w in key.lower() for w in ['name','nama']) else EMOJI_NETWORK if any(w in key.lower() for w in ['carrier','operator','network','sim']) else EMOJI_LOCATION if any(w in key.lower() for w in ['location','address','city','state','area']) else EMOJI_PHONE2 if any(w in key.lower() for w in ['phone','mobile','number','no']) else EMOJI_SEARCH
                        result += f"<blockquote>{e} {key}: <code>{val[:200]}</code></blockquote>\n"; found += 1
            if found == 0: result += f"<blockquote>{EMOJI_CARD} ʀᴀᴡ ᴅᴀᴛᴀ: <code>{clean[:500]}</code></blockquote>\n"
            return result
    except: return f"<blockquote>{EMOJI_CROSS} ᴛɪᴍᴇᴏᴜᴛ</blockquote>"

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
        for field, label in {'Name':f'{EMOJI_USER} ɴᴀᴍᴇ',"Father's Name":f'{EMOJI_FATHER} ꜰᴀᴛʜᴇʀ','Mobile':f'{EMOJI_PHONE2} ᴍᴏʙɪʟᴇ','Address':f'{EMOJI_LOCATION} ᴀᴅᴅʀᴇꜱꜱ','Circle':f'{EMOJI_NETWORK} ᴄɪʀᴄʟᴇ','State':f'{EMOJI_STATE} ꜱᴛᴀᴛᴇ'}.items():
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
    if not records: return f"<blockquote>{EMOJI_CROSS} ɴᴏ ʀᴇᴄᴏʀᴅꜱ ꜰᴏᴜɴᴅ</blockquote>"
    title = {'aadhaar':f'{EMOJI_CARD} ᴀᴀᴅʜᴀʀ','mobile':f'{EMOJI_INDIA} ɪɴᴅ ɴᴜᴍʙᴇʀ','vehicle':f'{EMOJI_CAR} ᴠᴇʜɪᴄʟᴇ'}.get(search_type, f'{EMOJI_CHART} ʀᴇꜱᴜʟᴛ')
    result = f"<blockquote expandable>{EMOJI_SPARKLE} {title} {EMOJI_SPARKLE}</blockquote>\n<blockquote>{EMOJI_CHART} ᴛᴏᴛᴀʟ ʀᴇᴄᴏʀᴅꜱ: {len(records)}</blockquote>\n"
    for i, record in enumerate(records, 1):
        if len(records) > 1: result += f"\n<blockquote>━━ {EMOJI_USER} ʀᴇᴄᴏʀᴅ {i} ━━</blockquote>\n"
        for key, value in record.items(): result += f"<blockquote>{key}: <code>{value}</code></blockquote>\n"
    return result

# --- 👑 ADMIN ---

async def admin_panel(update, context):
    if update.effective_user.id != ADMIN_ID: return
    s = get_settings()
    ms = lambda key: "🔴" if s.get(f"maint_{key}") else "🟢"
    
    # Create colored admin buttons
    kb = [
        create_styled_row([
            {"text": "🎫 ɢᴇɴ ᴄᴏᴅᴇ", "callback_data": "ad_gen", "color": "success"},
            {"text": "📋 ᴄᴏᴅᴇꜱ", "callback_data": "ad_codes", "color": "info"}
        ]),
        create_styled_row([
            {"text": "🎁 ᴀᴅᴅ ᴄʀ", "callback_data": "ad_credit", "color": "warning"},
            {"text": "📢 ʙᴄᴀꜱᴛ", "callback_data": "ad_bcast", "color": "primary"}
        ]),
        create_styled_row([
            {"text": f"{'🔴' if s.get('maintenance_mode') else '🟢'} ɢʟᴏʙᴀʟ", "callback_data": "ad_maint", "color": "danger" if s.get('maintenance_mode') else "success"}
        ]),
        create_styled_row([
            {"text": f"{'🟢' if s.get('tgid_enabled',True) else '🔴'} ᴛɢ", "callback_data": "ad_tgid", "color": "success" if s.get('tgid_enabled',True) else "danger"},
            {"text": f"{ms('tgid')} ᴍ", "callback_data": "ad_maint_tgid", "color": "info"}
        ]),
        create_styled_row([
            {"text": f"{'🟢' if s.get('ifsc_enabled',True) else '🔴'} ɪꜰ", "callback_data": "ad_ifsc", "color": "success" if s.get('ifsc_enabled',True) else "danger"},
            {"text": f"{ms('ifsc')} ᴍ", "callback_data": "ad_maint_ifsc", "color": "info"}
        ]),
        create_styled_row([
            {"text": f"{'🟢' if s.get('bypass_enabled',True) else '🔴'} ʙʏ", "callback_data": "ad_bypass_toggle", "color": "success" if s.get('bypass_enabled',True) else "danger"},
            {"text": f"{ms('bypass')} ᴍ", "callback_data": "ad_maint_bypass", "color": "info"}
        ]),
        create_styled_row([
            {"text": f"{'🟢' if s.get('mobile_enabled',True) else '🔴'} ᴍᴏ", "callback_data": "ad_mobile", "color": "success" if s.get('mobile_enabled',True) else "danger"},
            {"text": f"{ms('mobile')} ᴍ", "callback_data": "ad_maint_mobile", "color": "info"}
        ]),
        create_styled_row([
            {"text": f"{'🟢' if s.get('aadhaar_enabled',True) else '🔴'} ᴀᴀ", "callback_data": "ad_aadhaar", "color": "success" if s.get('aadhaar_enabled',True) else "danger"},
            {"text": f"{ms('aadhaar')} ᴍ", "callback_data": "ad_maint_aadhaar", "color": "info"}
        ]),
        create_styled_row([
            {"text": f"{'🟢' if s.get('rc_enabled',True) else '🔴'} ʀᴄ", "callback_data": "ad_rc", "color": "success" if s.get('rc_enabled',True) else "danger"},
            {"text": f"{ms('rc')} ᴍ", "callback_data": "ad_maint_rc", "color": "info"}
        ]),
        create_styled_row([
            {"text": f"{'🟢' if s.get('gst_enabled',True) else '🔴'} ɢꜱ", "callback_data": "ad_gst", "color": "success" if s.get('gst_enabled',True) else "danger"},
            {"text": f"{ms('gst')} ᴍ", "callback_data": "ad_maint_gst", "color": "info"}
        ]),
        create_styled_row([
            {"text": f"{'🟢' if s.get('pak_enabled',True) else '🔴'} ᴘᴀ", "callback_data": "ad_pak", "color": "success" if s.get('pak_enabled',True) else "danger"},
            {"text": f"{ms('pak')} ᴍ", "callback_data": "ad_maint_pak", "color": "info"}
        ]),
        create_styled_row([
            {"text": f"{'🟢' if s.get('indnum_enabled',True) else '🔴'} ɪɴ2", "callback_data": "ad_indnum", "color": "success" if s.get('indnum_enabled',True) else "danger"},
            {"text": f"{ms('indnum')} ᴍ", "callback_data": "ad_maint_indnum", "color": "info"}
        ]),
        create_styled_row([
            {"text": f"{'🟢' if s.get('indnum3_enabled',True) else '🔴'} ɪɴ3", "callback_data": "ad_indnum3", "color": "success" if s.get('indnum3_enabled',True) else "danger"},
            {"text": f"{ms('indnum3')} ᴍ", "callback_data": "ad_maint_indnum3", "color": "info"}
        ]),
        create_styled_row([
            {"text": "❌ ᴄʟᴏꜱᴇ", "callback_data": "ad_close", "color": "danger"}
        ])
    ]
    
    # Flatten the keyboard
    flat_kb = []
    for row in kb:
        flat_kb.append(row)
    
    txt = f"<blockquote>{EMOJI_CROWN} ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ {EMOJI_CROWN}</blockquote>\n<blockquote>{EMOJI_INVITE} ᴜꜱᴇʀꜱ: {len(load_json(USERS_FILE))} | {EMOJI_TICKET} ᴄᴏᴅᴇꜱ: {len(load_json(REDEEM_FILE))}</blockquote>"
    if update.callback_query:
        await update.callback_query.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(flat_kb), parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(flat_kb), parse_mode=ParseMode.HTML)

async def admin_callback(update, context):
    q = update.callback_query
    if q.from_user.id != ADMIN_ID: await q.answer("❌"); return
    d = q.data; s = get_settings()
    if d == "ad_close": await q.message.delete()
    elif d == "ad_codes":
        codes = load_json(REDEEM_FILE); txt = f"<blockquote>{EMOJI_TICKET} ᴄᴏᴅᴇꜱ: {len(codes)}</blockquote>\n"
        for c, v in list(codes.items())[-15:]: txt += f"<blockquote>{'✅' if not v.get('used') else '❌'} <code>{c}</code> | {v.get('credits')}cr</blockquote>\n"
        await q.message.edit_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d == "ad_gen": ADMIN_STATE[q.from_user.id] = "gen"; await q.message.edit_text(f"<blockquote>{EMOJI_TICKET} ᴇɴᴛᴇʀ ᴄʀᴇᴅɪᴛꜱ:</blockquote>\n<i>100</i>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d == "ad_credit": ADMIN_STATE[q.from_user.id] = "credit"; await q.message.edit_text(f"<blockquote>{EMOJI_GIFT} ᴇɴᴛᴇʀ ɪᴅ ᴀᴍᴏᴜɴᴛ:</blockquote>\n<i>123456789 50</i>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d == "ad_bcast": ADMIN_STATE[q.from_user.id] = "bcast"; await q.message.edit_text(f"<blockquote>{EMOJI_BOLT} ᴇɴᴛᴇʀ ᴍᴇꜱꜱᴀɢᴇ:</blockquote>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d == "ad_maint": s["maintenance_mode"] = not s.get("maintenance_mode", False); save_settings(s); await q.answer(f"Global: {'ON' if s['maintenance_mode'] else 'OFF'}", show_alert=True); await admin_panel(update, context)
    elif d.startswith("ad_maint_"):
        f = d.replace("ad_maint_", ""); s[f"maint_{f}"] = not s.get(f"maint_{f}", False); save_settings(s); await q.answer(f"{f}: {'ON' if s[f'maint_{f}'] else 'OFF'}", show_alert=True); await admin_panel(update, context)
    elif d.startswith("ad_"):
        toggle_map = {"ad_tgid":"tgid_enabled","ad_ifsc":"ifsc_enabled","ad_bypass_toggle":"bypass_enabled","ad_mobile":"mobile_enabled","ad_aadhaar":"aadhaar_enabled","ad_rc":"rc_enabled","ad_gst":"gst_enabled","ad_pak":"pak_enabled","ad_indnum":"indnum_enabled","ad_indnum3":"indnum3_enabled"}
        if d in toggle_map: k = toggle_map[d]; s[k] = not s.get(k,True); save_settings(s); await q.answer(f"{k}: {'ON' if s[k] else 'OFF'}", show_alert=True)
        await admin_panel(update, context)
    elif d == "ad_back": await admin_panel(update, context)
    await q.answer()

# --- 🚀 HELP & ABOUT ---

async def show_help(update, context):
    text = f"""
<blockquote>{EMOJI_HELP} 𝐇𝐄𝐋𝐏 & 𝐆𝐔𝐈𝐃𝐄 {EMOJI_HELP}</blockquote>

<blockquote>{EMOJI_STAR} 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄 𝐅𝐄𝐀𝐓𝐔𝐑𝐄𝐒:</blockquote>

<blockquote>{BTN_PHONE} <b>𝐓𝐆 𝐈𝐃 ➜ 𝐍𝐔𝐌𝐁𝐄𝐑</b>
Get phone number from Telegram ID</blockquote>

<blockquote>{BTN_BANK} <b>𝐈𝐅𝐒𝐂 𝐈𝐍𝐅𝐎</b>
Get bank details from IFSC code</blockquote>

<blockquote>{BTN_LINK} <b>𝐋𝐈𝐍𝐊 𝐁𝐘𝐏𝐀𝐒𝐒</b>
Bypass short links</blockquote>

<blockquote>{BTN_AADHAAR} <b>𝐀𝐀𝐃𝐇𝐀𝐑 𝐈𝐍𝐅𝐎</b>
Get details from Aadhaar number</blockquote>

<blockquote>{BTN_INDIA} <b>𝐈𝐍𝐃 𝐍𝐔𝐌𝐁𝐄𝐑 𝐈𝐍𝐅𝐎</b>
Get Indian number details</blockquote>

<blockquote>{BTN_CAR} <b>𝐑𝐂 𝐃𝐄𝐓𝐀𝐈𝐋𝐒</b>
Get vehicle RC details</blockquote>

<blockquote>{BTN_GST} <b>𝐆𝐒𝐓 𝐋𝐎𝐎𝐊𝐔𝐏</b>
Get business details from GST</blockquote>

<blockquote>{BTN_PAK} <b>𝐏𝐀𝐊 𝐍𝐔𝐌𝐁𝐄𝐑 𝐈𝐍𝐅𝐎</b>
Get Pakistan number details</blockquote>

<blockquote>{EMOJI_GIFT} <b>𝐃𝐀𝐈𝐋𝐘 𝐅𝐑𝐄𝐄: +{DAILY_FREE_CREDITS} ᴄʀᴇᴅɪᴛꜱ</b></blockquote>

<blockquote>{EMOJI_INVITE} <b>𝐈𝐍𝐕𝐈𝐓𝐄: +{INVITE_CREDITS} ᴄʀᴇᴅɪᴛꜱ ᴘᴇʀ ᴜꜱᴇʀ</b></blockquote>

<blockquote>{EMOJI_CLOCK} <b>𝐀𝐔𝐓𝐎 𝐃𝐄𝐋𝐄𝐓𝐄: {AUTO_DELETE_TIME}ꜱ</b></blockquote>
"""
    msg = await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    asyncio.create_task(schedule_delete(msg, 60))

async def show_about(update, context):
    text = f"""
<blockquote>{EMOJI_ABOUT} 𝐀𝐁𝐎𝐔𝐓 𝐁𝐎𝐓 {EMOJI_ABOUT}</blockquote>

<blockquote><b>𝐍𝐀𝐌𝐄:</b> {BOT_NAME}</blockquote>
<blockquote><b>𝐔𝐒𝐄𝐑𝐍𝐀𝐌𝐄:</b> @{BOT_USERNAME}</blockquote>
<blockquote><b>𝐕𝐄𝐑𝐒𝐈𝐎𝐍:</b> 3.0</blockquote>

<blockquote>{EMOJI_DIAMOND} <b>𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐅𝐄𝐀𝐓𝐔𝐑𝐄𝐒</b></blockquote>

<blockquote>• <b>Telegram ID Lookup</b></blockquote>
<blockquote>• <b>IFSC Bank Details</b></blockquote>
<blockquote>• <b>Link Bypass</b></blockquote>
<blockquote>• <b>Aadhaar Info</b></blockquote>
<blockquote>• <b>Mobile Number Tracking</b></blockquote>
<blockquote>• <b>RC Details</b></blockquote>
<blockquote>• <b>GST Lookup</b></blockquote>
<blockquote>• <b>Pakistan Number Info</b></blockquote>
<blockquote>• <b>Colored Admin Buttons 🎨</b></blockquote>

<blockquote>{EMOJI_CROWN} <b>𝐃𝐄𝐕𝐄𝐋𝐎𝐏𝐄𝐃 𝐁𝐘:</b> @Hexh4ckerOFC</blockquote>

<blockquote><i>{EMOJI_WARN} 𝐅𝐎𝐑 𝐄𝐃𝐔𝐂𝐀𝐓𝐈𝐎𝐍𝐀𝐋 𝐏𝐔𝐑𝐏𝐎𝐒𝐄𝐒 𝐎𝐍𝐋𝐘</i></blockquote>
"""
    msg = await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    asyncio.create_task(schedule_delete(msg, 60))

async def show_stats(update, context):
    users = load_json(USERS_FILE)
    total_users = len(users)
    total_queries = sum(u.get('total_queries', 0) for u in users.values())
    total_invites = sum(u.get('invites', 0) for u in users.values())
    total_credits = sum(u.get('credits', 0) for u in users.values())
    
    text = f"""
<blockquote>{EMOJI_STATS} 𝐁𝐎𝐓 𝐒𝐓𝐀𝐓𝐈𝐒𝐓𝐈𝐂𝐒 {EMOJI_STATS}</blockquote>

<blockquote>{EMOJI_USER} <b>𝐓𝐎𝐓𝐀𝐋 𝐔𝐒𝐄𝐑𝐒:</b> {total_users}</blockquote>
<blockquote>{EMOJI_SEARCH} <b>𝐓𝐎𝐓𝐀𝐋 𝐐𝐔𝐄𝐑𝐈𝐄𝐒:</b> {total_queries}</blockquote>
<blockquote>{EMOJI_INVITE} <b>𝐓𝐎𝐓𝐀𝐋 𝐈𝐍𝐕𝐈𝐓𝐄𝐒:</b> {total_invites}</blockquote>
<blockquote>{EMOJI_CREDIT} <b>𝐓𝐎𝐓𝐀𝐋 𝐂𝐑𝐄𝐃𝐈𝐓𝐒:</b> {total_credits}</blockquote>

<blockquote>{EMOJI_DIAMOND} <b>𝐁𝐎𝐓 𝐒𝐓𝐀𝐓𝐔𝐒:</b> 🟢 Active</blockquote>
"""
    msg = await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    asyncio.create_task(schedule_delete(msg, 60))

# --- 🚀 START HANDLER ---

async def start(update, context):
    try:
        uid = update.effective_user.id
        args = context.args
        if args and args[0].startswith("HEX-"):
            users = load_json(USERS_FILE)
            for inviter, data in users.items():
                if data.get("invite_code") == args[0] and inviter != str(uid):
                    cr = process_invite(inviter, uid)
                    try: await context.bot.send_message(chat_id=int(inviter), text=f"<blockquote>{EMOJI_GIFT} +{cr} ᴄʀᴇᴅɪᴛꜱ! ɴᴇᴡ ᴜꜱᴇʀ ᴊᴏɪɴᴇᴅ!</blockquote>", parse_mode=ParseMode.HTML)
                    except: pass
                    break
        user = get_user(uid)
        if not user.get("verified"):
            if await check_channels(uid, context):
                user["verified"] = True
                save_user(uid, user)
                await main_menu(update, context)
                return
            await show_verification_page(update, context)
            return
        await main_menu(update, context)
    except Exception as e:
        logger.error(f"Start: {e}")

async def verify_cb(update, context):
    q = update.callback_query
    if await check_channels(q.from_user.id, context):
        user = get_user(q.from_user.id)
        user["verified"] = True
        save_user(q.from_user.id, user)
        await q.answer("✅ Verified!")
        try: await q.message.delete()
        except: pass
        await main_menu(update, context)
    else:
        await q.answer("❌ Join both!", show_alert=True)

# --- 📝 MESSAGE HANDLER ---

async def msg_handler(update, context):
    try:
        uid = update.effective_user.id
        txt = update.message.text.strip()
        asyncio.create_task(schedule_delete(update.message, AUTO_DELETE_TIME))
        s = get_settings()
        
        if s.get("maintenance_mode", False) and uid != ADMIN_ID:
            m = await update.message.reply_text(f"<blockquote>{EMOJI_TOOLS} Under maintenance</blockquote>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
            return
        
        # Admin states
        if uid == ADMIN_ID and uid in ADMIN_STATE:
            state = ADMIN_STATE.pop(uid)
            if state == "gen":
                try:
                    cr = int(txt)
                    code = generate_redeem_code(cr)
                    msg = await update.message.reply_text(f"<blockquote>{EMOJI_CHECK} <code>{code}</code> | {EMOJI_CREDIT} {cr}cr</blockquote>", parse_mode=ParseMode.HTML)
                except:
                    msg = await update.message.reply_text(f"<blockquote>{EMOJI_CROSS} Number</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(msg))
                return
            elif state == "credit":
                p = txt.split()
                if len(p) >= 2:
                    bal = add_credits(p[0], int(p[1]))
                    msg = await update.message.reply_text(f"<blockquote>{EMOJI_CHECK} +{p[1]} | {bal}</blockquote>", parse_mode=ParseMode.HTML)
                else:
                    msg = await update.message.reply_text(f"<blockquote>{EMOJI_CROSS} Format: ID AMOUNT</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(msg))
                return
            elif state == "bcast":
                users = load_json(USERS_FILE)
                cnt = 0
                for u in users:
                    try:
                        await context.bot.send_message(chat_id=int(u), text=f"{EMOJI_BOLT} {txt}")
                        cnt += 1
                    except: pass
                msg = await update.message.reply_text(f"<blockquote>{EMOJI_CHECK} Sent: {cnt}</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(msg))
                return
        
        # Check verification
        user = get_user(uid)
        if not user.get("verified"):
            if await check_channels(uid, context):
                user["verified"] = True
                save_user(uid, user)
                await main_menu(update, context)
            else:
                await show_verification_page(update, context)
            return
        
        # --- BUTTON HANDLING ---
        
        # Admin Panel
        if txt in [f"{BTN_ADMIN} ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ", f"{BTN_ADMIN} ᴀᴅᴍɪɴ"]:
            await admin_panel(update, context)
            return
        
        # Help
        if txt == f"{BTN_HELP} ʜᴇʟᴘ":
            await show_help(update, context)
            return
        
        # About
        if txt == f"{BTN_ABOUT} ᴀʙᴏᴜᴛ":
            await show_about(update, context)
            return
        
        # Stats
        if txt == f"{BTN_STATS} ꜱᴛᴀᴛꜱ":
            await show_stats(update, context)
            return
        
        # TG ID
        if txt in [f"{BTN_PHONE} ᴛɢ ɪᴅ ➜ {BTN_PHONE2} ɴᴜᴍʙᴇʀ {BTN_SEARCH}"]:
            if not s.get("tgid_enabled", True):
                m = await update.message.reply_text(f"<blockquote>{EMOJI_DISABLED} Disabled</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(m))
                return
            maint, msg = check_feature_maintenance("tgid")
            if maint:
                m = await update.message.reply_text(f"<blockquote>{EMOJI_TOOLS} {msg}</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(m))
                return
            context.user_data['mode'] = 'TG'
            btn = [[InlineKeyboardButton("🤖 @ChatIdInfoBot", url="https://t.me/ChatIdInfoBot")]]
            m = await update.message.reply_text(f"<blockquote>{EMOJI_PHONE} ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ ᴛᴏ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ</blockquote>\n<i>7123181749, 6884112825</i>", reply_markup=InlineKeyboardMarkup(btn), parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
            return
        
        # IFSC
        if txt in [f"{BTN_BANK} ɪꜰꜱᴄ ɪɴꜰᴏ➜{BTN_MAGNIFY}"]:
            if not s.get("ifsc_enabled", True):
                m = await update.message.reply_text(f"<blockquote>{EMOJI_DISABLED} Disabled</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(m))
                return
            maint, msg = check_feature_maintenance("ifsc")
            if maint:
                m = await update.message.reply_text(f"<blockquote>{EMOJI_TOOLS} {msg}</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(m))
                return
            context.user_data['mode'] = 'IFSC'
            m = await update.message.reply_text(f"<blockquote>{EMOJI_BANK} ʙᴀɴᴋ ɪꜰꜱᴄ ᴄᴏᴅᴇ</blockquote>\n<i>SBIN0001234, HDFC0001234</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
            return
        
        # Bypass
        if txt in [f"{BTN_LINK} ʟɪɴᴋ ʙʏᴘᴀꜱꜱ"]:
            if not s.get("bypass_enabled", True):
                m = await update.message.reply_text(f"<blockquote>{EMOJI_DISABLED} Disabled</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(m))
                return
            maint, msg = check_feature_maintenance("bypass")
            if maint:
                m = await update.message.reply_text(f"<blockquote>{EMOJI_TOOLS} {msg}</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(m))
                return
            context.user_data['mode'] = 'SHORTLINK'
            m = await update.message.reply_text(f"<blockquote>{EMOJI_LINK} ʟɪɴᴋ ʙʏᴘᴀꜱꜱ</blockquote>\n<i>https://indianshortner.in/xxxx</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
            return
        
        # Mobile
        if txt == f"{BTN_INDIA} ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ➜{BTN_USER}":
            if not s.get("mobile_enabled", True):
                m = await update.message.reply_text(f"<blockquote>{EMOJI_DISABLED} Disabled</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(m))
                return
            maint, msg = check_feature_maintenance("mobile")
            if maint:
                m = await update.message.reply_text(f"<blockquote>{EMOJI_TOOLS} {msg}</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(m))
                return
            context.user_data['mode'] = 'MOBILE'
            m = await update.message.reply_text(f"<blockquote>{EMOJI_INDIA} ɪɴᴅɪᴀɴ ᴍᴏʙɪʟᴇ ɴᴜᴍʙᴇʀ</blockquote>\n<i>9876543210, 8123456789</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
            return
        
        # Aadhaar
        if txt == f"{BTN_AADHAAR} ᴀᴀᴅʜᴀʀ ɪɴꜰᴏ➜{BTN_USER}":
            if not s.get("aadhaar_enabled", True):
                m = await update.message.reply_text(f"<blockquote>{EMOJI_DISABLED} Disabled</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(m))
                return
            maint, msg = check_feature_maintenance("aadhaar")
            if maint:
                m = await update.message.reply_text(f"<blockquote>{EMOJI_TOOLS} {msg}</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(m))
                return
            context.user_data['mode'] = 'AADHAAR'
            m = await update.message.reply_text(f"<blockquote>{EMOJI_CARD} ᴀᴀᴅʜᴀʀ ɴᴜᴍʙᴇʀ</blockquote>\n<i>123456789012</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
            return
        
        # RC
        if txt == f"{BTN_CAR} ʀᴄ ᴅᴇᴛᴀɪʟꜱ":
            if not s.get("rc_enabled", True):
                m = await update.message.reply_text(f"<blockquote>{EMOJI_DISABLED} Disabled</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(m))
                return
            maint, msg = check_feature_maintenance("rc")
            if maint:
                m = await update.message.reply_text(f"<blockquote>{EMOJI_TOOLS} {msg}</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(m))
                return
            context.user_data['mode'] = 'VEHICLE'
            m = await update.message.reply_text(f"<blockquote>{EMOJI_CAR} ᴠᴇʜɪᴄʟᴇ ɴᴜᴍʙᴇʀ</blockquote>\n<i>KA01AB3256, DL1CX1234</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
            return
        
        # GST
        if txt == f"{BTN_GST} ɢꜱᴛ ʟᴏᴏᴋᴜᴘ":
            if not s.get("gst_enabled", True):
                m = await update.message.reply_text(f"<blockquote>{EMOJI_DISABLED} Disabled</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(m))
                return
            maint, msg = check_feature_maintenance("gst")
            if maint:
                m = await update.message.reply_text(f"<blockquote>{EMOJI_TOOLS} {msg}</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(m))
                return
            context.user_data['mode'] = 'GST'
            m = await update.message.reply_text(f"<blockquote>{EMOJI_CARD} ɢꜱᴛ ɴᴜᴍʙᴇʀ</blockquote>\n<i>19BOKPS7056D1ZI</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
            return
        
        # Pakistan
        if txt == f"{BTN_PAK} ᴘᴀᴋ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ":
            if not s.get("pak_enabled", True):
                m = await update.message.reply_text(f"<blockquote>{EMOJI_DISABLED} Disabled</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(m))
                return
            maint, msg = check_feature_maintenance("pak")
            if maint:
                m = await update.message.reply_text(f"<blockquote>{EMOJI_TOOLS} {msg}</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(m))
                return
            context.user_data['mode'] = 'PAK'
            m = await update.message.reply_text(f"<blockquote>{EMOJI_PAK} ᴘᴀᴋɪꜱᴛᴀɴ ɴᴜᴍʙᴇʀ</blockquote>\n<i>923078750447</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
            return
        
        # IND NUM 2
        if txt == f"{BTN_PHONE2} ɪɴᴅ ɴᴜᴍ ɪɴꜰᴏ 𝟸":
            if not s.get("indnum_enabled", True):
                m = await update.message.reply_text(f"<blockquote>{EMOJI_DISABLED} Disabled</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(m))
                return
            maint, msg = check_feature_maintenance("indnum")
            if maint:
                m = await update.message.reply_text(f"<blockquote>{EMOJI_TOOLS} {msg}</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(m))
                return
            context.user_data['mode'] = 'INDNUM'
            m = await update.message.reply_text(f"<blockquote>{EMOJI_PHONE2} ᴀᴅᴠᴀɴᴄᴇᴅ ɴᴜᴍʙᴇʀ</blockquote>\n<i>6363016966, 9876543210</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
            return
        
        # IND NUM 3
        if txt == f"{BTN_INDIA} ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ 𝟹 ➜{BTN_USER}":
            if not s.get("indnum3_enabled", True):
                m = await update.message.reply_text(f"<blockquote>{EMOJI_DISABLED} Disabled</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(m))
                return
            maint, msg = check_feature_maintenance("indnum3")
            if maint:
                m = await update.message.reply_text(f"<blockquote>{EMOJI_TOOLS} {msg}</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(m))
                return
            context.user_data['mode'] = 'INDNUM3'
            m = await update.message.reply_text(f"<blockquote>{EMOJI_INDIA} ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴛʀᴀᴄᴋɪɴɢ</blockquote>\n<i>6363016966, 9876543210</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
            return
        
        # Invite
        if txt in [f"{BTN_INVITE} ɪɴᴠɪᴛᴇ & ᴇᴀʀɴ", f"{BTN_INVITE} ɪɴᴠɪᴛᴇ"]:
            user = get_user(uid)
            bot_username = context.bot.username or BOT_USERNAME
            link = f"https://t.me/{bot_username}?start={user['invite_code']}"
            m = await update.message.reply_text(f"<blockquote>{EMOJI_INVITE} ɪɴᴠɪᴛᴇ (+{INVITE_CREDITS}ᴄʀ)</blockquote>\n<blockquote><code>{link}</code></blockquote>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m, 120))
            return
        
        # Redeem
        if txt in [f"{BTN_TICKET} ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ"]:
            context.user_data['redeem_mode'] = True
            m = await update.message.reply_text(f"<blockquote>{EMOJI_TICKET} ᴇɴᴛᴇʀ ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ:</blockquote>\n<i>HEX-XXXXXXXXXX</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m, 30))
            return
        
        # Redeem mode
        if context.user_data.get('redeem_mode'):
            context.user_data['redeem_mode'] = False
            if txt.upper().startswith("HEX-"):
                success, msg = redeem_code(uid, txt)
            else:
                msg = f"{EMOJI_CROSS} Invalid code format!"
            m = await update.message.reply_text(f"<blockquote>{msg}</blockquote>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
            return
        
        # Check if in query mode
        mode = context.user_data.get('mode')
        if mode:
            # Check redeem code first
            if txt.upper().startswith("HEX-"):
                success, msg = redeem_code(uid, txt)
                m = await update.message.reply_text(f"<blockquote>{msg}</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(m))
                context.user_data['mode'] = None
                return
            
            user = get_user(uid)
            if user.get("credits", 0) <= 0:
                m = await update.message.reply_text(f"<blockquote>{EMOJI_CROSS} No credits! +10 daily | +3 invite</blockquote>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(m))
                context.user_data['mode'] = None
                return
            
            await run_query(update, context, mode, txt)
            context.user_data['mode'] = None
        
    except Exception as e:
        logger.error(f"Msg: {e}")

async def run_query(update, context, mode, query):
    if not await net_ok():
        m = await update.message.reply_text(f"<blockquote>{EMOJI_CROSS} No internet</blockquote>", parse_mode=ParseMode.HTML)
        asyncio.create_task(schedule_delete(m))
        return
    
    await update.message.reply_chat_action(ChatAction.TYPING)
    names = {'TG':f'{EMOJI_PHONE}','IFSC':f'{EMOJI_BANK}','SHORTLINK':f'{EMOJI_LINK}','AADHAAR':f'{EMOJI_CARD}','MOBILE':f'{EMOJI_INDIA}','VEHICLE':f'{EMOJI_CAR}','GST':f'{EMOJI_CARD}','PAK':f'{EMOJI_PAK}','INDNUM':f'{EMOJI_PHONE2}','INDNUM3':f'{EMOJI_INDIA}'}
    st = await update.message.reply_text(f"<blockquote>{EMOJI_GREEN} ꜱᴇᴀʀᴄʜɪɴɢ...</blockquote>", parse_mode=ParseMode.HTML)
    lt = asyncio.create_task(loading_animation(st, names.get(mode, '')))
    credit_deducted = False
    
    try:
        if mode in ['AADHAAR', 'MOBILE', 'VEHICLE']:
            raw = run_india_script({'AADHAAR':'2','MOBILE':'1','VEHICLE':'4'}[mode], query)
            if raw:
                records = parse_all_india_records(raw)
                result = format_records_result(records, {'AADHAAR':'aadhaar','MOBILE':'mobile','VEHICLE':'vehicle'}[mode])
                if records and f"{EMOJI_CROSS}" not in str(result):
                    use_credit(update.effective_user.id)
                    credit_deducted = True
            else:
                result = f"<blockquote>{EMOJI_CROSS} Script failed</blockquote>"
        else:
            async with aiohttp.ClientSession() as s:
                if mode == 'TG':
                    result = await chatid_lookup(s, query)
                elif mode == 'IFSC':
                    result = await ifsc_lookup(s, query)
                elif mode == 'SHORTLINK':
                    result = await bypass_lookup(s, query)
                elif mode == 'GST':
                    result = await gst_lookup(s, query)
                elif mode == 'PAK':
                    result = await pakistan_lookup(s, query)
                elif mode == 'INDNUM':
                    result = await indnum_lookup(s, query)
                elif mode == 'INDNUM3':
                    result = await indnum3_lookup(s, query)
                else:
                    result = f"{EMOJI_CROSS}"
            
            if result and f"{EMOJI_CROSS}" not in str(result) and "unavailable" not in str(result).lower():
                use_credit(update.effective_user.id)
                credit_deducted = True
        
        lt.cancel()
        try: await lt
        except asyncio.CancelledError: pass
        
        user = get_user(update.effective_user.id)
        final = f"{result}\n{SEP}\n<blockquote>{EMOJI_CREDIT} {'ᴄʀ: '+str(user.get('credits',0)) if credit_deducted else 'ɴᴏ ᴄʀ ᴅᴇᴅᴜᴄᴛᴇᴅ'} | {EMOJI_CLOCK} {AUTO_DELETE_TIME}ꜱ</blockquote>{DISCLAIMER}{FOOTER}"
        sent = await st.edit_text(final, parse_mode=ParseMode.HTML)
        asyncio.create_task(schedule_delete(sent))
    except Exception as e:
        lt.cancel()
        logger.error(f"Query: {e}")
        try:
            await st.edit_text(f"<blockquote>{EMOJI_WARN} ᴇʀʀᴏʀ</blockquote>{FOOTER}", parse_mode=ParseMode.HTML)
        except: pass

# --- 🚀 MAIN ---

def main():
    print("🔄 Hex Terminal Premium Starting...")
    print("🎨 Colored Buttons with Premium Emojis Enabled!")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4"], capture_output=True, timeout=30)
    except: pass
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify_cb, pattern="^verify$"))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^ad_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg_handler))
    
    print(f"{EMOJI_CHECK} {BOT_NAME} Ready!")
    print(f"{EMOJI_DIAMOND} Premium Emojis in Text | Normal Emojis in Reply Buttons")
    print(f"{EMOJI_STAR} Colored Inline Buttons in Admin Panel!")
    
    app.run_polling()

if __name__ == '__main__':
    main()