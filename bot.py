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
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    CallbackQuery,
    Message
)
from pyrogram.enums import ButtonStyle, ParseMode

# --- ⚙️ CONFIGURATION ---
API_ID = int(os.environ.get('API_ID', '37996037'))
API_HASH = os.environ.get('API_HASH', '47ee9fa07b5eeb865edb3d79ada726a5')
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8687617595:AAGCa0yJTRM52NLItvLkzt7O1mZEkCaNkn4')
ADMIN_ID = int(os.environ.get('ADMIN_ID', '7898928200'))

# SINGLE CHANNEL
CHANNEL_ID = int(os.environ.get('CHANNEL_ID', '-1003240507339'))
CHANNEL_LINK = os.environ.get('CHANNEL_LINK', 'https://t.me/+dP7xLb3AoE1jNmRl')

FOOTER = "\n\n⚡ ᴘᴏᴡᴇʀᴇᴅ ʙʏ @Hexh4ckerOFC"
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

# ============================================================
# PREMIUM EMOJI IDs (ONLY 1 PER TEXT)
# ============================================================

EMOJI_IDS = {
    "warn": "6267039884016358504",
    "check": "6267008582294705964",
    "cross": "6267000941547885720",
    "lock": "5316522278056399236",
    "crown": "6267128480601741166",
    "diamond": "6264791387032523779",
    "star": "6266969287638913443",
    "gift": "5203996991054432397",
    "phone": "5947494995798789024",
    "bank": "5264895611517300926",
    "link": "5271604874419647061",
    "car": "5253752975997803460",
    "card": "5260561650213220533",
    "user": "5249053508681883137",
    "india": "6284779941489812433",
    "pak": "5913705895375672082",
    "phone2": "5406809207947142040",
    "invite": "5244933196230972438",
    "ticket": "5285515895534278367",
    "credit": "6267068789146260253",
    "refresh": "5375338737028841420",
    "clock": "5382194935057372936",
    "bolt": "6284971355297290197",
    "green": "5386367538735104399",
    "sparkle": "5467683093693354332",
    "tools": "5462921117423384478",
    "disabled": "5373165973203348165",
    "location": "5391032818111363540",
    "home": "5280955052582785391",
    "state": "5388927107315283144",
    "network": "5321141214735508486",
    "signal": "6147892053796725336",
    "sim": "5800717980266403037",
    "chart": "6093382540784046658",
    "help": "5244933196230972438",
    "about": "5285515895534278367",
    "stats": "6093382540784046658",
    "admin": "6267128480601741166",
    "rocket": "5195033767969839232",
    "search": "5231012545799666522",
    "fire": "6264785189394717307",
    "magnify": "5258024981144066782"
}

# For button icons (INTEGERS)
BUTTON_EMOJI_IDS = {
    "phone": 5947494995798789024,
    "bank": 5264895611517300926,
    "link": 5271604874419647061,
    "car": 5253752975997803460,
    "card": 5260561650213220533,
    "user": 5249053508681883137,
    "india": 6284779941489812433,
    "pak": 5913705895375672082,
    "phone2": 5406809207947142040,
    "invite": 5244933196230972438,
    "ticket": 5285515895534278367,
    "credit": 6267068789146260253,
    "refresh": 5375338737028841420,
    "clock": 5382194935057372936,
    "bolt": 6284971355297290197,
    "green": 5386367538735104399,
    "search": 5231012545799666522,
    "crown": 6267128480601741166,
    "diamond": 6264791387032523779,
    "star": 6266969287638913443,
    "gift": 5203996991054432397,
    "check": 6267008582294705964,
    "cross": 6267000941547885720,
    "lock": 5316522278056399236,
    "warn": 6267039884016358504,
    "tools": 5462921117423384478,
    "disabled": 5373165973203348165,
    "location": 5391032818111363540,
    "home": 5280955052582785391,
    "state": 5388927107315283144,
    "network": 5321141214735508486,
    "signal": 6147892053796725336,
    "sim": 5800717980266403037,
    "chart": 6093382540784046658,
    "help": 5244933196230972438,
    "about": 5285515895534278367,
    "stats": 6093382540784046658,
    "admin": 6267128480601741166,
    "rocket": 5195033767969839232,
    "sparkle": 5467683093693354332,
    "magnify": 5258024981144066782,
    "fire": 6264785189394717307
}

# --- PREMIUM EMOJIS FOR TEXT (ONLY 1 PER TEXT) ---
def get_pe(eid, fallback):
    return f'<tg-emoji emoji-id="{eid}">{fallback}</tg-emoji>'

EMOJI_WARN = get_pe(EMOJI_IDS["warn"], "⚠️")
EMOJI_CHECK = get_pe(EMOJI_IDS["check"], "✅")
EMOJI_CROSS = get_pe(EMOJI_IDS["cross"], "❌")
EMOJI_LOCK = get_pe(EMOJI_IDS["lock"], "🔒")
EMOJI_CROWN = get_pe(EMOJI_IDS["crown"], "👑")
EMOJI_DIAMOND = get_pe(EMOJI_IDS["diamond"], "💎")
EMOJI_STAR = get_pe(EMOJI_IDS["star"], "⭐")
EMOJI_GIFT = get_pe(EMOJI_IDS["gift"], "🎁")
EMOJI_PHONE = get_pe(EMOJI_IDS["phone"], "📞")
EMOJI_BANK = get_pe(EMOJI_IDS["bank"], "🏦")
EMOJI_LINK = get_pe(EMOJI_IDS["link"], "🔗")
EMOJI_CAR = get_pe(EMOJI_IDS["car"], "🚘")
EMOJI_CARD = get_pe(EMOJI_IDS["card"], "🪪")
EMOJI_USER = get_pe(EMOJI_IDS["user"], "👤")
EMOJI_INDIA = get_pe(EMOJI_IDS["india"], "🇮🇳")
EMOJI_PAK = get_pe(EMOJI_IDS["pak"], "🇵🇰")
EMOJI_PHONE2 = get_pe(EMOJI_IDS["phone2"], "📲")
EMOJI_INVITE = get_pe(EMOJI_IDS["invite"], "👥")
EMOJI_TICKET = get_pe(EMOJI_IDS["ticket"], "🎫")
EMOJI_CREDIT = get_pe(EMOJI_IDS["credit"], "💰")
EMOJI_REFRESH = get_pe(EMOJI_IDS["refresh"], "🔄")
EMOJI_CLOCK = get_pe(EMOJI_IDS["clock"], "⏱")
EMOJI_BOLT = get_pe(EMOJI_IDS["bolt"], "⚡")
EMOJI_GREEN = get_pe(EMOJI_IDS["green"], "🟩")
EMOJI_SPARKLE = get_pe(EMOJI_IDS["sparkle"], "✨")
EMOJI_TOOLS = get_pe(EMOJI_IDS["tools"], "🛠️")
EMOJI_DISABLED = get_pe(EMOJI_IDS["disabled"], "📴")
EMOJI_LOCATION = get_pe(EMOJI_IDS["location"], "📍")
EMOJI_NETWORK = get_pe(EMOJI_IDS["network"], "📡")
EMOJI_SIGNAL = get_pe(EMOJI_IDS["signal"], "📶")
EMOJI_SIM = get_pe(EMOJI_IDS["sim"], "💳")
EMOJI_CHART = get_pe(EMOJI_IDS["chart"], "📊")
EMOJI_HELP = get_pe(EMOJI_IDS["help"], "❓")
EMOJI_ABOUT = get_pe(EMOJI_IDS["about"], "ℹ️")
EMOJI_STATS = get_pe(EMOJI_IDS["stats"], "📊")
EMOJI_SEARCH = get_pe(EMOJI_IDS["search"], "🔍")
EMOJI_FIRE = get_pe(EMOJI_IDS["fire"], "🔥")
EMOJI_MAGNIFY = get_pe(EMOJI_IDS["magnify"], "🔎")

DISCLAIMER = f"\n\n{EMOJI_WARN} ᴅɪꜱᴄʟᴀɪᴍᴇʀ:\nᴇᴅᴜᴄᴀᴛɪᴏɴᴀʟ ᴘᴜʀᴘᴏꜱᴇꜱ ᴏɴʟʏ. ᴜꜱᴇ ʀᴇꜱᴘᴏɴꜱɪʙʟʏ."

# --- Initialize Bot ---
app = Client(
    "hex_terminal_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

ADMIN_STATE = {}
USER_PAGE = {}  # Track current page per user

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

async def check_channel(uid):
    try:
        member = await app.get_chat_member(CHANNEL_ID, uid)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        if member.status == 'restricted' and member.is_member:
            return True
        return False
    except Exception as e:
        print(f"Channel check error for {uid}: {e}")
        return False

# --- 🛠️ UTILS ---

async def net_ok():
    try: socket.create_connection(("8.8.8.8", 53), timeout=3); return True
    except: return False

async def schedule_delete(msg, delay=AUTO_DELETE_TIME):
    await asyncio.sleep(delay)
    try: await msg.delete()
    except: pass

def check_feature_maintenance(feature_key):
    s = get_settings()
    if s.get(f"maint_{feature_key}", False):
        return True, s.get(f"maint_msg_{feature_key}", f"{EMOJI_TOOLS} Under maintenance.")
    return False, ""

# ============================================================
# CREATE COLORED INLINE BUTTONS
# ============================================================

BUTTON_STYLES = {
    "primary": ButtonStyle.PRIMARY,
    "success": ButtonStyle.SUCCESS,
    "danger": ButtonStyle.DANGER,
}

def create_colored_button(text: str, callback_data: str = None, url: str = None, color: str = "primary", icon_emoji_id: int = None):
    style = BUTTON_STYLES.get(color, ButtonStyle.PRIMARY)
    if not icon_emoji_id:
        icon_emoji_id = BUTTON_EMOJI_IDS["star"]
    try:
        return InlineKeyboardButton(
            text=text,
            callback_data=callback_data,
            url=url,
            icon_custom_emoji_id=icon_emoji_id,
            style=style
        )
    except:
        try:
            return InlineKeyboardButton(
                text=text,
                callback_data=callback_data,
                url=url,
                icon_custom_emoji_id=icon_emoji_id
            )
        except:
            return InlineKeyboardButton(
                text=text,
                callback_data=callback_data,
                url=url
            )

def create_styled_row(buttons_config: list) -> list:
    row = []
    for cfg in buttons_config:
        text = cfg.get("text", "")
        callback_data = cfg.get("callback_data")
        url = cfg.get("url")
        color = cfg.get("color", "primary")
        icon_emoji_id = cfg.get("icon_emoji_id")
        btn = create_colored_button(text, callback_data, url, color, icon_emoji_id)
        row.append(btn)
    return row

# ============================================================
# MAIN MENU WITH PAGINATION (8 BUTTONS PER PAGE)
# ============================================================

async def show_verification_page(message: Message):
    try:
        bot_info = await app.get_me()
        caption = (
            f"{EMOJI_DIAMOND} {BOT_NAME} {EMOJI_DIAMOND}\n"
            f"@{BOT_USERNAME}\n\n"
            f"{EMOJI_LOCK} ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ʀᴇQᴜɪʀᴇᴅ\n"
            f"ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜɴʟᴏᴄᴋ\n\n"
            f"{EMOJI_WARN} ɢᴜɪᴅᴇʟɪɴᴇꜱ:\n"
            f"• ᴇᴅᴜᴄᴀᴛɪᴏɴᴀʟ ᴘᴜʀᴘᴏꜱᴇꜱ ᴏɴʟʏ\n"
            f"• ᴜꜱᴇ ᴏɴ ʏᴏᴜʀ ᴏᴡɴ ᴅᴀᴛᴀ\n"
            f"• ʀᴇꜱᴘᴇᴄᴛ ᴘʀɪᴠᴀᴄʏ ʟᴀᴡꜱ\n\n"
            f"{EMOJI_GIFT} +{DAILY_FREE_CREDITS} ᴅᴀɪʟʏ {EMOJI_STAR}\n"
            f"{EMOJI_INVITE} +{INVITE_CREDITS} ᴘᴇʀ ɪɴᴠɪᴛᴇ\n"
            f"{EMOJI_CLOCK} {AUTO_DELETE_TIME}ꜱ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ\n\n"
            f"{EMOJI_CROWN} ᴏᴡɴᴇʀ: @Hexh4ckerOFC\n"
            f"{EMOJI_WARN} ᴍɪꜱᴜꜱᴇ ᴍᴀʏ ʟᴇᴀᴅ ᴛᴏ ʟᴇɢᴀʟ ᴀᴄᴛɪᴏɴ"
        )
        sent = await message.reply_text(caption, parse_mode=ParseMode.HTML)
        asyncio.create_task(schedule_delete(sent, 120))
    except: pass
    
    buttons = [
        create_styled_row([
            {"text": "ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", "url": CHANNEL_LINK, "color": "primary", "icon_emoji_id": BUTTON_EMOJI_IDS["link"]}
        ]),
        create_styled_row([
            {"text": "ɪ'ᴠᴇ ᴊᴏɪɴᴇᴅ - ᴠᴇʀɪꜰʏ", "callback_data": "verify", "color": "success", "icon_emoji_id": BUTTON_EMOJI_IDS["check"]}
        ])
    ]
    
    flat_buttons = []
    for row in buttons:
        flat_buttons.append(row)
    
    sent2 = await message.reply_text(
        f"{EMOJI_LOCK} ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴠᴇʀɪꜰʏ",
        reply_markup=InlineKeyboardMarkup(flat_buttons),
        parse_mode=ParseMode.HTML
    )
    asyncio.create_task(schedule_delete(sent2, 120))

async def main_menu(message: Message, page: int = 0):
    """Main menu with 8 buttons per page, 2-color combination"""
    is_admin = message.from_user.id == ADMIN_ID
    user = get_user(message.from_user.id)
    s = get_settings()
    cr = user.get("credits", 0)
    
    # All buttons configuration - 2 color combination (Primary + Success alternating)
    all_buttons = []
    
    # Page 1 - 8 buttons (Primary + Success alternating)
    if s.get("tgid_enabled", True):
        all_buttons.append({"text": "ᴛɢ ɪᴅ ➜ ɴᴜᴍʙᴇʀ", "callback_data": "menu_tgid", "color": "primary", "icon_emoji_id": BUTTON_EMOJI_IDS["phone"]})
    if s.get("ifsc_enabled", True):
        all_buttons.append({"text": "ɪꜰꜱᴄ ɪɴꜰᴏ", "callback_data": "menu_ifsc", "color": "success", "icon_emoji_id": BUTTON_EMOJI_IDS["bank"]})
    if s.get("bypass_enabled", True):
        all_buttons.append({"text": "ʟɪɴᴋ ʙʏᴘᴀꜱꜱ", "callback_data": "menu_bypass", "color": "primary", "icon_emoji_id": BUTTON_EMOJI_IDS["link"]})
    if s.get("aadhaar_enabled", True):
        all_buttons.append({"text": "ᴀᴀᴅʜᴀʀ ɪɴꜰᴏ", "callback_data": "menu_aadhaar", "color": "success", "icon_emoji_id": BUTTON_EMOJI_IDS["card"]})
    if s.get("mobile_enabled", True):
        all_buttons.append({"text": "ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ", "callback_data": "menu_mobile", "color": "primary", "icon_emoji_id": BUTTON_EMOJI_IDS["india"]})
    if s.get("rc_enabled", True):
        all_buttons.append({"text": "ʀᴄ ᴅᴇᴛᴀɪʟꜱ", "callback_data": "menu_rc", "color": "success", "icon_emoji_id": BUTTON_EMOJI_IDS["car"]})
    if s.get("gst_enabled", True):
        all_buttons.append({"text": "ɢꜱᴛ ʟᴏᴏᴋᴜᴘ", "callback_data": "menu_gst", "color": "primary", "icon_emoji_id": BUTTON_EMOJI_IDS["card"]})
    if s.get("pak_enabled", True):
        all_buttons.append({"text": "ᴘᴀᴋ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ", "callback_data": "menu_pak", "color": "success", "icon_emoji_id": BUTTON_EMOJI_IDS["pak"]})
    
    # Page 2 - Remaining buttons
    if s.get("indnum_enabled", True):
        all_buttons.append({"text": "ɪɴᴅ ɴᴜᴍ ɪɴꜰᴏ 𝟸", "callback_data": "menu_indnum", "color": "primary", "icon_emoji_id": BUTTON_EMOJI_IDS["phone2"]})
    if s.get("indnum3_enabled", True):
        all_buttons.append({"text": "ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ 𝟹", "callback_data": "menu_indnum3", "color": "success", "icon_emoji_id": BUTTON_EMOJI_IDS["india"]})
    all_buttons.append({"text": "ɪɴᴠɪᴛᴇ & ᴇᴀʀɴ", "callback_data": "menu_invite", "color": "primary", "icon_emoji_id": BUTTON_EMOJI_IDS["invite"]})
    all_buttons.append({"text": "ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ", "callback_data": "menu_redeem", "color": "success", "icon_emoji_id": BUTTON_EMOJI_IDS["ticket"]})
    all_buttons.append({"text": "ʜᴇʟᴘ", "callback_data": "menu_help", "color": "primary", "icon_emoji_id": BUTTON_EMOJI_IDS["help"]})
    
    # Admin button
    if is_admin:
        all_buttons.append({"text": "ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ", "callback_data": "menu_admin", "color": "danger", "icon_emoji_id": BUTTON_EMOJI_IDS["admin"]})
    
    # Calculate pagination
    items_per_page = 8
    total_pages = (len(all_buttons) + items_per_page - 1) // items_per_page
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, len(all_buttons))
    page_buttons = all_buttons[start_idx:end_idx]
    
    # Build keyboard - 2 buttons per row (2-color combination)
    kb = []
    for i in range(0, len(page_buttons), 2):
        row_config = page_buttons[i:i+2]
        kb.append(create_styled_row(row_config))
    
    # Navigation row
    nav_row = []
    if page > 0:
        nav_row.append({"text": "◀️ ʙᴀᴄᴋ", "callback_data": f"page_{page-1}", "color": "primary", "icon_emoji_id": BUTTON_EMOJI_IDS["sparkle"]})
    if page < total_pages - 1:
        nav_row.append({"text": "ɴᴇxᴛ ▶️", "callback_data": f"page_{page+1}", "color": "success", "icon_emoji_id": BUTTON_EMOJI_IDS["sparkle"]})
    if nav_row:
        kb.append(create_styled_row(nav_row))
    
    flat_kb = []
    for row in kb:
        flat_kb.append(row)
    
    markup = InlineKeyboardMarkup(flat_kb)
    
    # Page indicator
    page_info = f"ᴘᴀɢᴇ {page+1}/{total_pages}" if total_pages > 1 else ""
    
    txt = (
        f"{EMOJI_DIAMOND} ᴘʀᴇᴍɪᴜᴍ ʜᴜʙ {EMOJI_DIAMOND}\n"
        f"{EMOJI_USER} ᴡᴇʟᴄᴏᴍᴇ ʙᴀᴄᴋ, <code>{message.from_user.first_name}</code>\n\n"
        f"{EMOJI_CHART} ʏᴏᴜʀ ꜱᴛᴀᴛɪꜱᴛɪᴄꜱ:\n"
        f"┃ {EMOJI_CREDIT} ᴄʀᴇᴅɪᴛꜱ: {cr}\n"
        f"┃ {EMOJI_SEARCH} Qᴜᴇʀɪᴇꜱ: {user.get('total_queries',0)}\n"
        f"┃ {EMOJI_INVITE} ɪɴᴠɪᴛᴇꜱ: {user.get('invites',0)}\n\n"
        f"{EMOJI_GIFT} ʀᴇᴡᴀʀᴅꜱ:\n"
        f"{EMOJI_REFRESH} +{DAILY_FREE_CREDITS} ᴅᴀɪʟʏ ꜰʀᴇᴇ\n"
        f"{EMOJI_INVITE} +{INVITE_CREDITS} ᴘᴇʀ ɪɴᴠɪᴛᴇ\n"
        f"{EMOJI_CLOCK} {AUTO_DELETE_TIME}ꜱ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ\n\n"
        f"{EMOJI_STAR} ꜱᴇʟᴇᴄᴛ ᴀ ꜱᴇʀᴠɪᴄᴇ ʙᴇʟᴏᴡ {EMOJI_STAR}\n"
        f"{page_info}"
    )
    
    sent = await message.reply_text(txt, reply_markup=markup, parse_mode=ParseMode.HTML)
    asyncio.create_task(schedule_delete(sent, AUTO_DELETE_TIME))

async def show_info_quote(message: Message, title: str, content: str):
    """Show info in Telegram Quote UI style"""
    text = f"""
<blockquote expandable>
<b>{EMOJI_STAR} {title}</b>

{content}
</blockquote>

<blockquote>
<i>{EMOJI_WARN} ᴛʏᴘᴇ ʏᴏᴜʀ ɪɴᴘᴜᴛ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ</i>
</blockquote>
"""
    sent = await message.reply_text(text, parse_mode=ParseMode.HTML)
    asyncio.create_task(schedule_delete(sent, 60))

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
    if not data: return f"{EMOJI_CROSS} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"
    if isinstance(data, dict) and not data.get("raw_text") and data.get("success"):
        d = data.get("data", data)
        if isinstance(d, dict):
            result = f"{EMOJI_SPARKLE} ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ ɪɴꜰᴏ {EMOJI_SPARKLE}\n"
            if d.get('chat_id') or d.get('userid'): result += f"{EMOJI_SEARCH} ᴄʜᴀᴛ ɪᴅ: <code>{d.get('chat_id', d.get('userid', query))}</code>\n"
            if d.get('number'): result += f"{EMOJI_PHONE2} ᴘʜᴏɴᴇ: <code>{d['number']}</code>\n"
            if d.get('name'): result += f"{EMOJI_USER} ɴᴀᴍᴇ: <code>{d['name']}</code>\n"
            return result
    return f"{EMOJI_CROSS} ɴᴏᴛ ꜰᴏᴜɴᴅ"

async def ifsc_lookup(session, code):
    data = await safe_api_fetch(session, f"{IFSC_API}{code.upper()}")
    if not data or isinstance(data, dict) and data.get("raw_text"): return f"{EMOJI_CROSS} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"
    if isinstance(data, dict):
        return (f"{EMOJI_SPARKLE} ʙᴀɴᴋ ɪꜰꜱᴄ ᴅᴇᴛᴀɪʟꜱ {EMOJI_SPARKLE}\n"
                f"{EMOJI_BANK} ʙᴀɴᴋ: <code>{data.get('BANK','N/A')}</code>\n"
                f"{EMOJI_LOCATION} ʙʀᴀɴᴄʜ: <code>{data.get('BRANCH','N/A')}</code>\n"
                f"{EMOJI_CARD} ɪꜰꜱᴄ: <code>{data.get('IFSC',code.upper())}</code>\n"
                f"{EMOJI_LOCATION} ᴀᴅᴅʀᴇꜱꜱ: <code>{data.get('ADDRESS','N/A')}</code>")
    return f"{EMOJI_CROSS} ɪɴᴠᴀʟɪᴅ ᴄᴏᴅᴇ"

async def bypass_lookup(session, link):
    s = get_settings()
    if s.get("bypass_maintenance",False): return f"{EMOJI_TOOLS} ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ"
    data = await safe_api_fetch(session, f"{SHORTLINK_API}{link}", timeout=20)
    if not data or isinstance(data, dict) and data.get("raw_text"): return f"{EMOJI_CROSS} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"
    if isinstance(data, dict):
        r = data.get('bypassed_url') or data.get('url') or str(data)
        return f"{EMOJI_SPARKLE} ʟɪɴᴋ ʙʏᴘᴀꜱꜱᴇᴅ {EMOJI_SPARKLE}\n{EMOJI_LINK} ᴜʀʟ: <code>{str(r)}</code>"
    return f"{EMOJI_LINK} ʀᴇꜱᴜʟᴛ: <code>{str(data)}</code>"

async def gst_lookup(session, gst_number):
    data = await safe_api_fetch(session, f"{GST_API}{gst_number.upper()}", timeout=20)
    if not data or isinstance(data, dict) and data.get("raw_text"): return f"{EMOJI_CROSS} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"
    if isinstance(data, dict) and data.get("status") == "success" and data.get("data"):
        d = data["data"]
        result = f"{EMOJI_SPARKLE} ɢꜱᴛ ʙᴜꜱɪɴᴇꜱꜱ ɪɴꜰᴏ {EMOJI_SPARKLE}\n"
        if d.get('TradeName'): result += f"{EMOJI_BANK} ɴᴀᴍᴇ: <code>{d['TradeName']}</code>\n"
        if d.get('Gstin'): result += f"{EMOJI_CARD} ɢꜱᴛ: <code>{d['Gstin']}</code>\n"
        return result
    return f"{EMOJI_CROSS} ɪɴᴠᴀʟɪᴅ ɢꜱᴛ"

async def pakistan_lookup(session, number):
    try:
        data = await safe_api_fetch(session, f"{PAK_API}{number}", timeout=20)
        if not data or isinstance(data, dict) and data.get("raw_text"): return f"{EMOJI_CROSS} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"
        if isinstance(data, dict) and data.get("success") and data.get("data"):
            valid = [r for r in data["data"] if isinstance(r, dict) and any(r.get(k) for k in ['name','number','cnic','address'])]
            if not valid: return f"{EMOJI_CROSS} ɴᴏ ᴅᴀᴛᴀ"
            result = f"{EMOJI_SPARKLE} ᴘᴀᴋɪꜱᴛᴀɴ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ {EMOJI_SPARKLE}\n"
            for i, r in enumerate(valid[:3], 1):
                if len(valid) > 1: result += f"\n━━ ʀᴇᴄᴏʀᴅ {i} ━━\n"
                if r.get('number'): result += f"{EMOJI_PHONE2} ᴘʜᴏɴᴇ: <code>{r['number']}</code>\n"
                if r.get('name'): result += f"{EMOJI_USER} ɴᴀᴍᴇ: <code>{r['name']}</code>\n"
                if r.get('cnic'): result += f"{EMOJI_CARD} ᴄɴɪᴄ: <code>{r['cnic']}</code>\n"
                if r.get('address'): result += f"{EMOJI_LOCATION} ᴀᴅᴅʀᴇꜱꜱ: <code>{r['address'][:200]}</code>\n"
            return result
        return f"{EMOJI_CROSS} ɴᴏ ᴅᴀᴛᴀ"
    except: return f"{EMOJI_CROSS} ᴇʀʀᴏʀ"

async def indnum_lookup(session, number):
    for attempt in range(3):
        data = await safe_api_fetch(session, f"{IND_NUM_API}{number}", timeout=30)
        if data and isinstance(data, dict) and not data.get("raw_text") and data.get("results"): break
        if attempt < 2: await asyncio.sleep(2)
    if not data or isinstance(data, dict) and data.get("raw_text"): return f"{EMOJI_CROSS} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"
    results = data.get("results", {})
    if not results: return f"{EMOJI_CROSS} ɴᴏ ʀᴇꜱᴜʟᴛꜱ"
    result = f"{EMOJI_SPARKLE} ᴀᴅᴠᴀɴᴄᴇᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ {EMOJI_SPARKLE}\n{EMOJI_PHONE2} ɴᴜᴍʙᴇʀ: <code>{number}</code>\n"
    found = False
    s3 = results.get("source_3", {}).get("data", {})
    if isinstance(s3, dict):
        for k, e in [("SIM card",EMOJI_SIM),("Connection",EMOJI_SIGNAL),("Mobile State",EMOJI_LOCATION),("Hometown",EMOJI_HOME)]:
            if s3.get(k): result += f"{e} {k}: <code>{str(s3[k])[:200]}</code>\n"; found = True
    s4 = results.get("source_4", {}).get("data", {})
    if isinstance(s4, dict) and s4.get("carrier"): result += f"{EMOJI_NETWORK} ᴄᴀʀʀɪᴇʀ: <code>{s4['carrier']}</code>\n"; found = True
    return result if found else f"{EMOJI_CROSS} ɴᴏ ᴅᴀᴛᴀ"

async def indnum3_lookup(session, number):
    url = f"{IND_NUM_API_3}{number}"
    try:
        headers = {'User-Agent': 'Mozilla/5.0','Accept': '*/*'}
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=25), headers=headers, allow_redirects=True) as r:
            text = await r.text()
            if not text or len(text) < 20: return f"{EMOJI_CROSS} ᴇᴍᴘᴛʏ ʀᴇꜱᴘᴏɴꜱᴇ"
            try:
                data = json.loads(text)
                if isinstance(data, dict):
                    result = f"{EMOJI_SPARKLE} ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴛʀᴀᴄᴋɪɴɢ {EMOJI_SPARKLE}\n{EMOJI_PHONE2} ɴᴜᴍʙᴇʀ: <code>{number}</code>\n"
                    for k, v in data.items():
                        if v and str(v).strip():
                            result += f"{EMOJI_SEARCH} {k}: <code>{str(v)[:200]}</code>\n"
                    return result
            except: pass
            clean = re.sub(r'<[^>]+>', '\n', text)
            lines = [l.strip() for l in clean.split('\n') if l.strip() and len(l.strip()) > 1]
            result = f"{EMOJI_SPARKLE} ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴛʀᴀᴄᴋɪɴɢ {EMOJI_SPARKLE}\n{EMOJI_PHONE2} ɴᴜᴍʙᴇʀ: <code>{number}</code>\n"
            found = 0
            for line in lines[:20]:
                if ':' in line:
                    parts = line.split(':', 1)
                    key, val = parts[0].strip(), parts[1].strip() if len(parts) > 1 else ''
                    if val:
                        e = EMOJI_USER if any(w in key.lower() for w in ['name','nama']) else EMOJI_NETWORK if any(w in key.lower() for w in ['carrier','operator','network','sim']) else EMOJI_LOCATION if any(w in key.lower() for w in ['location','address','city','state','area']) else EMOJI_PHONE2 if any(w in key.lower() for w in ['phone','mobile','number','no']) else EMOJI_SEARCH
                        result += f"{e} {key}: <code>{val[:200]}</code>\n"; found += 1
            if found == 0: result += f"{EMOJI_CARD} ʀᴀᴡ ᴅᴀᴛᴀ: <code>{clean[:500]}</code>\n"
            return result
    except: return f"{EMOJI_CROSS} ᴛɪᴍᴇᴏᴜᴛ"

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
        for field, label in {'Name':f'{EMOJI_USER} ɴᴀᴍᴇ',"Father's Name":f'{EMOJI_USER} ꜰᴀᴛʜᴇʀ','Mobile':f'{EMOJI_PHONE2} ᴍᴏʙɪʟᴇ','Address':f'{EMOJI_LOCATION} ᴀᴅᴅʀᴇꜱꜱ','Circle':f'{EMOJI_NETWORK} ᴄɪʀᴄʟᴇ','State':f'{EMOJI_STATE} ꜱᴛᴀᴛᴇ'}.items():
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
    if not records: return f"{EMOJI_CROSS} ɴᴏ ʀᴇᴄᴏʀᴅꜱ ꜰᴏᴜɴᴅ"
    title = {'aadhaar':f'{EMOJI_CARD} ᴀᴀᴅʜᴀʀ','mobile':f'{EMOJI_INDIA} ɪɴᴅ ɴᴜᴍʙᴇʀ','vehicle':f'{EMOJI_CAR} ᴠᴇʜɪᴄʟᴇ'}.get(search_type, f'{EMOJI_CHART} ʀᴇꜱᴜʟᴛ')
    result = f"{EMOJI_SPARKLE} {title} {EMOJI_SPARKLE}\n{EMOJI_CHART} ᴛᴏᴛᴀʟ: {len(records)}\n"
    for i, record in enumerate(records, 1):
        if len(records) > 1: result += f"\n━━ ʀᴇᴄᴏʀᴅ {i} ━━\n"
        for key, value in record.items(): result += f"{key}: <code>{value}</code>\n"
    return result

# --- 👑 ADMIN PANEL (FIXED) ---

async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID: return
    s = get_settings()
    ms = lambda key: "🔴" if s.get(f"maint_{key}") else "🟢"
    
    kb = [
        create_styled_row([
            {"text": "ɢᴇɴ ᴄᴏᴅᴇ", "callback_data": "admin_gen", "color": "success", "icon_emoji_id": BUTTON_EMOJI_IDS["ticket"]},
            {"text": "ᴄᴏᴅᴇꜱ", "callback_data": "admin_codes", "color": "info", "icon_emoji_id": BUTTON_EMOJI_IDS["ticket"]}
        ]),
        create_styled_row([
            {"text": "ᴀᴅᴅ ᴄʀ", "callback_data": "admin_credit", "color": "warning", "icon_emoji_id": BUTTON_EMOJI_IDS["gift"]},
            {"text": "ʙᴄᴀꜱᴛ", "callback_data": "admin_bcast", "color": "primary", "icon_emoji_id": BUTTON_EMOJI_IDS["bolt"]}
        ]),
        create_styled_row([
            {"text": f"{'🔴' if s.get('maintenance_mode') else '🟢'} ɢʟᴏʙᴀʟ", "callback_data": "admin_maint", "color": "danger" if s.get('maintenance_mode') else "success"}
        ]),
        create_styled_row([
            {"text": f"{'🟢' if s.get('tgid_enabled',True) else '🔴'} ᴛɢ", "callback_data": "admin_tgid", "color": "success" if s.get('tgid_enabled',True) else "danger"},
            {"text": f"{ms('tgid')} ᴍ", "callback_data": "admin_maint_tgid", "color": "info"}
        ]),
        create_styled_row([
            {"text": f"{'🟢' if s.get('ifsc_enabled',True) else '🔴'} ɪꜰ", "callback_data": "admin_ifsc", "color": "success" if s.get('ifsc_enabled',True) else "danger"},
            {"text": f"{ms('ifsc')} ᴍ", "callback_data": "admin_maint_ifsc", "color": "info"}
        ]),
        create_styled_row([
            {"text": f"{'🟢' if s.get('bypass_enabled',True) else '🔴'} ʙʏ", "callback_data": "admin_bypass", "color": "success" if s.get('bypass_enabled',True) else "danger"},
            {"text": f"{ms('bypass')} ᴍ", "callback_data": "admin_maint_bypass", "color": "info"}
        ]),
        create_styled_row([
            {"text": f"{'🟢' if s.get('mobile_enabled',True) else '🔴'} ᴍᴏ", "callback_data": "admin_mobile", "color": "success" if s.get('mobile_enabled',True) else "danger"},
            {"text": f"{ms('mobile')} ᴍ", "callback_data": "admin_maint_mobile", "color": "info"}
        ]),
        create_styled_row([
            {"text": f"{'🟢' if s.get('aadhaar_enabled',True) else '🔴'} ᴀᴀ", "callback_data": "admin_aadhaar", "color": "success" if s.get('aadhaar_enabled',True) else "danger"},
            {"text": f"{ms('aadhaar')} ᴍ", "callback_data": "admin_maint_aadhaar", "color": "info"}
        ]),
        create_styled_row([
            {"text": f"{'🟢' if s.get('rc_enabled',True) else '🔴'} ʀᴄ", "callback_data": "admin_rc", "color": "success" if s.get('rc_enabled',True) else "danger"},
            {"text": f"{ms('rc')} ᴍ", "callback_data": "admin_maint_rc", "color": "info"}
        ]),
        create_styled_row([
            {"text": f"{'🟢' if s.get('gst_enabled',True) else '🔴'} ɢꜱ", "callback_data": "admin_gst", "color": "success" if s.get('gst_enabled',True) else "danger"},
            {"text": f"{ms('gst')} ᴍ", "callback_data": "admin_maint_gst", "color": "info"}
        ]),
        create_styled_row([
            {"text": f"{'🟢' if s.get('pak_enabled',True) else '🔴'} ᴘᴀ", "callback_data": "admin_pak", "color": "success" if s.get('pak_enabled',True) else "danger"},
            {"text": f"{ms('pak')} ᴍ", "callback_data": "admin_maint_pak", "color": "info"}
        ]),
        create_styled_row([
            {"text": f"{'🟢' if s.get('indnum_enabled',True) else '🔴'} ɪɴ2", "callback_data": "admin_indnum", "color": "success" if s.get('indnum_enabled',True) else "danger"},
            {"text": f"{ms('indnum')} ᴍ", "callback_data": "admin_maint_indnum", "color": "info"}
        ]),
        create_styled_row([
            {"text": f"{'🟢' if s.get('indnum3_enabled',True) else '🔴'} ɪɴ3", "callback_data": "admin_indnum3", "color": "success" if s.get('indnum3_enabled',True) else "danger"},
            {"text": f"{ms('indnum3')} ᴍ", "callback_data": "admin_maint_indnum3", "color": "info"}
        ]),
        create_styled_row([
            {"text": "❌ ᴄʟᴏꜱᴇ", "callback_data": "admin_close", "color": "danger"}
        ]),
        create_styled_row([
            {"text": "🔙 ʙᴀᴄᴋ ᴛᴏ ᴍᴇɴᴜ", "callback_data": "admin_back", "color": "primary", "icon_emoji_id": BUTTON_EMOJI_IDS["sparkle"]}
        ])
    ]
    
    flat_kb = []
    for row in kb:
        flat_kb.append(row)
    
    txt = f"{EMOJI_CROWN} ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ {EMOJI_CROWN}\n{EMOJI_INVITE} ᴜꜱᴇʀꜱ: {len(load_json(USERS_FILE))} | {EMOJI_TICKET} ᴄᴏᴅᴇꜱ: {len(load_json(REDEEM_FILE))}"
    
    if hasattr(message, 'edit_text'):
        await message.edit_text(txt, reply_markup=InlineKeyboardMarkup(flat_kb), parse_mode=ParseMode.HTML)
    else:
        await message.reply_text(txt, reply_markup=InlineKeyboardMarkup(flat_kb), parse_mode=ParseMode.HTML)

# --- 🚀 HELP ---

async def show_help_inline(callback_query: CallbackQuery):
    await callback_query.answer()
    text = f"""
<blockquote expandable>
<b>{EMOJI_HELP} 𝐇𝐄𝐋𝐏 & 𝐆𝐔𝐈𝐃𝐄</b>

{EMOJI_STAR} 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄 𝐅𝐄𝐀𝐓𝐔𝐑𝐄𝐒:

{EMOJI_PHONE} 𝐓𝐆 𝐈𝐃 ➜ 𝐍𝐔𝐌𝐁𝐄𝐑
Get phone number from Telegram ID

{EMOJI_BANK} 𝐈𝐅𝐒𝐂 𝐈𝐍𝐅𝐎
Get bank details from IFSC code

{EMOJI_LINK} 𝐋𝐈𝐍𝐊 𝐁𝐘𝐏𝐀𝐒𝐒
Bypass short links

{EMOJI_CARD} 𝐀𝐀𝐃𝐇𝐀𝐑 𝐈𝐍𝐅𝐎
Get details from Aadhaar number

{EMOJI_INDIA} 𝐈𝐍𝐃 𝐍𝐔𝐌𝐁𝐄𝐑 𝐈𝐍𝐅𝐎
Get Indian number details

{EMOJI_CAR} 𝐑𝐂 𝐃𝐄𝐓𝐀𝐈𝐋𝐒
Get vehicle RC details

{EMOJI_CARD} 𝐆𝐒𝐓 𝐋𝐎𝐎𝐊𝐔𝐏
Get business details from GST

{EMOJI_PAK} 𝐏𝐀𝐊 𝐍𝐔𝐌𝐁𝐄𝐑 𝐈𝐍𝐅𝐎
Get Pakistan number details

{EMOJI_GIFT} 𝐃𝐀𝐈𝐋𝐘 𝐅𝐑𝐄𝐄: +{DAILY_FREE_CREDITS} ᴄʀᴇᴅɪᴛꜱ

{EMOJI_INVITE} 𝐈𝐍𝐕𝐈𝐓𝐄: +{INVITE_CREDITS} ᴄʀᴇᴅɪᴛꜱ ᴘᴇʀ ᴜꜱᴇʀ

{EMOJI_CLOCK} 𝐀𝐔𝐓𝐎 𝐃𝐄𝐋𝐄𝐓𝐄: {AUTO_DELETE_TIME}ꜱ
</blockquote>
"""
    await callback_query.message.edit_text(text, parse_mode=ParseMode.HTML)
    await asyncio.sleep(60)
    try: await callback_query.message.delete()
    except: pass

# --- 🚀 COMMAND HANDLERS ---

@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    try:
        uid = message.from_user.id
        
        args = message.text.split()
        if len(args) > 1 and args[1].startswith("HEX-"):
            users = load_json(USERS_FILE)
            for inviter, data in users.items():
                if data.get("invite_code") == args[1] and inviter != str(uid):
                    cr = process_invite(inviter, uid)
                    try: 
                        await app.send_message(
                            chat_id=int(inviter), 
                            text=f"{EMOJI_GIFT} +{cr} ᴄʀᴇᴅɪᴛꜱ! ɴᴇᴡ ᴜꜱᴇʀ ᴊᴏɪɴᴇᴅ!"
                        )
                    except: pass
                    break
        
        user = get_user(uid)
        
        if uid == ADMIN_ID:
            user["verified"] = True
            save_user(uid, user)
            await main_menu(message, 0)
            return
        
        if not user.get("verified"):
            if await check_channel(uid):
                user["verified"] = True
                save_user(uid, user)
                await main_menu(message, 0)
                return
            await show_verification_page(message)
            return
        
        await main_menu(message, 0)
    except Exception as e:
        print(f"Start error: {e}")

# --- 📝 CALLBACK QUERY HANDLER ---

@app.on_callback_query()
async def callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    uid = callback_query.from_user.id
    s = get_settings()
    user = get_user(uid)
    
    # Page navigation
    if data.startswith("page_"):
        page = int(data.split("_")[1])
        await main_menu(callback_query.message, page)
        await callback_query.answer()
        return
    
    # Verification
    if data == "verify":
        if uid == ADMIN_ID:
            user["verified"] = True
            save_user(uid, user)
            await callback_query.answer("✅ Verified as Admin!", show_alert=True)
            try: await callback_query.message.delete()
            except: pass
            await main_menu(callback_query.message, 0)
            return
        
        if await check_channel(uid):
            user["verified"] = True
            save_user(uid, user)
            await callback_query.answer("✅ Verified!", show_alert=True)
            try: await callback_query.message.delete()
            except: pass
            await main_menu(callback_query.message, 0)
        else:
            await callback_query.answer("❌ Please join the channel first!", show_alert=True)
        return
    
    # --- ADMIN CALLBACKS ---
    if data.startswith("admin_"):
        if uid != ADMIN_ID:
            await callback_query.answer("❌ Unauthorized!", show_alert=True)
            return
        
        if data == "admin_close":
            await callback_query.message.delete()
            await callback_query.answer()
            return
        elif data == "admin_back":
            await main_menu(callback_query.message, 0)
            await callback_query.answer()
            return
        elif data == "admin_codes":
            codes = load_json(REDEEM_FILE)
            txt = f"{EMOJI_TICKET} ᴄᴏᴅᴇꜱ: {len(codes)}\n"
            for c, v in list(codes.items())[-15:]:
                txt += f"{'✅' if not v.get('used') else '❌'} <code>{c}</code> | {v.get('credits')}cr\n"
            await callback_query.message.edit_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 ʙᴀᴄᴋ", callback_data="admin_back")]]), parse_mode=ParseMode.HTML)
            await callback_query.answer()
            return
        elif data == "admin_gen":
            ADMIN_STATE[uid] = "gen"
            await callback_query.message.edit_text(f"{EMOJI_TICKET} ᴇɴᴛᴇʀ ᴄʀᴇᴅɪᴛꜱ:\n<i>100</i>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 ʙᴀᴄᴋ", callback_data="admin_back")]]), parse_mode=ParseMode.HTML)
            await callback_query.answer()
            return
        elif data == "admin_credit":
            ADMIN_STATE[uid] = "credit"
            await callback_query.message.edit_text(f"{EMOJI_GIFT} ᴇɴᴛᴇʀ ɪᴅ ᴀᴍᴏᴜɴᴛ:\n<i>123456789 50</i>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 ʙᴀᴄᴋ", callback_data="admin_back")]]), parse_mode=ParseMode.HTML)
            await callback_query.answer()
            return
        elif data == "admin_bcast":
            ADMIN_STATE[uid] = "bcast"
            await callback_query.message.edit_text(f"{EMOJI_BOLT} ᴇɴᴛᴇʀ ᴍᴇꜱꜱᴀɢᴇ:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 ʙᴀᴄᴋ", callback_data="admin_back")]]), parse_mode=ParseMode.HTML)
            await callback_query.answer()
            return
        elif data == "admin_maint":
            s["maintenance_mode"] = not s.get("maintenance_mode", False)
            save_settings(s)
            await callback_query.answer(f"Global: {'ON' if s['maintenance_mode'] else 'OFF'}", show_alert=True)
            await admin_panel(callback_query.message)
            return
        elif data.startswith("admin_maint_"):
            f = data.replace("admin_maint_", "")
            s[f"maint_{f}"] = not s.get(f"maint_{f}", False)
            save_settings(s)
            await callback_query.answer(f"{f}: {'ON' if s[f'maint_{f}'] else 'OFF'}", show_alert=True)
            await admin_panel(callback_query.message)
            return
        elif data in ["admin_tgid", "admin_ifsc", "admin_bypass", "admin_mobile", "admin_aadhaar", "admin_rc", "admin_gst", "admin_pak", "admin_indnum", "admin_indnum3"]:
            toggle_map = {
                "admin_tgid": "tgid_enabled",
                "admin_ifsc": "ifsc_enabled",
                "admin_bypass": "bypass_enabled",
                "admin_mobile": "mobile_enabled",
                "admin_aadhaar": "aadhaar_enabled",
                "admin_rc": "rc_enabled",
                "admin_gst": "gst_enabled",
                "admin_pak": "pak_enabled",
                "admin_indnum": "indnum_enabled",
                "admin_indnum3": "indnum3_enabled"
            }
            if data in toggle_map:
                k = toggle_map[data]
                s[k] = not s.get(k, True)
                save_settings(s)
                await callback_query.answer(f"{k}: {'ON' if s[k] else 'OFF'}", show_alert=True)
                await admin_panel(callback_query.message)
            return
        await callback_query.answer()
        return
    
    # --- MENU CALLBACKS ---
    if data.startswith("menu_"):
        if uid != ADMIN_ID:
            if not user.get("verified"):
                if await check_channel(uid):
                    user["verified"] = True
                    save_user(uid, user)
                    await main_menu(callback_query.message, 0)
                    return
                await show_verification_page(callback_query.message)
                await callback_query.answer()
                return
        
        if data == "menu_tgid":
            if not s.get("tgid_enabled", True):
                await callback_query.message.reply_text(f"{EMOJI_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            maint, msg = check_feature_maintenance("tgid")
            if maint:
                await callback_query.message.reply_text(f"{EMOJI_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            ADMIN_STATE[uid] = 'TG'
            await show_info_quote(callback_query.message, "ᴛɢ ɪᴅ ➜ ɴᴜᴍʙᴇʀ", "ᴇɴᴛᴇʀ ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ:\n<i>7123181749, 6884112825</i>")
            await callback_query.answer()
            return
        
        elif data == "menu_ifsc":
            if not s.get("ifsc_enabled", True):
                await callback_query.message.reply_text(f"{EMOJI_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            maint, msg = check_feature_maintenance("ifsc")
            if maint:
                await callback_query.message.reply_text(f"{EMOJI_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            ADMIN_STATE[uid] = 'IFSC'
            await show_info_quote(callback_query.message, "ɪꜰꜱᴄ ɪɴꜰᴏ", "ᴇɴᴛᴇʀ ʙᴀɴᴋ ɪꜰꜱᴄ ᴄᴏᴅᴇ:\n<i>SBIN0001234, HDFC0001234</i>")
            await callback_query.answer()
            return
        
        elif data == "menu_bypass":
            if not s.get("bypass_enabled", True):
                await callback_query.message.reply_text(f"{EMOJI_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            maint, msg = check_feature_maintenance("bypass")
            if maint:
                await callback_query.message.reply_text(f"{EMOJI_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            ADMIN_STATE[uid] = 'SHORTLINK'
            await show_info_quote(callback_query.message, "ʟɪɴᴋ ʙʏᴘᴀꜱꜱ", "ᴇɴᴛᴇʀ ꜱʜᴏʀᴛ ʟɪɴᴋ:\n<i>https://indianshortner.in/xxxx</i>")
            await callback_query.answer()
            return
        
        elif data == "menu_mobile":
            if not s.get("mobile_enabled", True):
                await callback_query.message.reply_text(f"{EMOJI_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            maint, msg = check_feature_maintenance("mobile")
            if maint:
                await callback_query.message.reply_text(f"{EMOJI_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            ADMIN_STATE[uid] = 'MOBILE'
            await show_info_quote(callback_query.message, "ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ", "ᴇɴᴛᴇʀ ɪɴᴅɪᴀɴ ᴍᴏʙɪʟᴇ ɴᴜᴍʙᴇʀ:\n<i>9876543210, 8123456789</i>")
            await callback_query.answer()
            return
        
        elif data == "menu_aadhaar":
            if not s.get("aadhaar_enabled", True):
                await callback_query.message.reply_text(f"{EMOJI_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            maint, msg = check_feature_maintenance("aadhaar")
            if maint:
                await callback_query.message.reply_text(f"{EMOJI_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            ADMIN_STATE[uid] = 'AADHAAR'
            await show_info_quote(callback_query.message, "ᴀᴀᴅʜᴀʀ ɪɴꜰᴏ", "ᴇɴᴛᴇʀ ᴀᴀᴅʜᴀʀ ɴᴜᴍʙᴇʀ:\n<i>123456789012</i>")
            await callback_query.answer()
            return
        
        elif data == "menu_rc":
            if not s.get("rc_enabled", True):
                await callback_query.message.reply_text(f"{EMOJI_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            maint, msg = check_feature_maintenance("rc")
            if maint:
                await callback_query.message.reply_text(f"{EMOJI_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            ADMIN_STATE[uid] = 'VEHICLE'
            await show_info_quote(callback_query.message, "ʀᴄ ᴅᴇᴛᴀɪʟꜱ", "ᴇɴᴛᴇʀ ᴠᴇʜɪᴄʟᴇ ɴᴜᴍʙᴇʀ:\n<i>KA01AB3256, DL1CX1234</i>")
            await callback_query.answer()
            return
        
        elif data == "menu_gst":
            if not s.get("gst_enabled", True):
                await callback_query.message.reply_text(f"{EMOJI_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            maint, msg = check_feature_maintenance("gst")
            if maint:
                await callback_query.message.reply_text(f"{EMOJI_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            ADMIN_STATE[uid] = 'GST'
            await show_info_quote(callback_query.message, "ɢꜱᴛ ʟᴏᴏᴋᴜᴘ", "ᴇɴᴛᴇʀ ɢꜱᴛ ɴᴜᴍʙᴇʀ:\n<i>19BOKPS7056D1ZI</i>")
            await callback_query.answer()
            return
        
        elif data == "menu_pak":
            if not s.get("pak_enabled", True):
                await callback_query.message.reply_text(f"{EMOJI_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            maint, msg = check_feature_maintenance("pak")
            if maint:
                await callback_query.message.reply_text(f"{EMOJI_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            ADMIN_STATE[uid] = 'PAK'
            await show_info_quote(callback_query.message, "ᴘᴀᴋɪꜱᴛᴀɴ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ", "ᴇɴᴛᴇʀ ᴘᴀᴋɪꜱᴛᴀɴ ɴᴜᴍʙᴇʀ:\n<i>923078750447</i>")
            await callback_query.answer()
            return
        
        elif data == "menu_indnum":
            if not s.get("indnum_enabled", True):
                await callback_query.message.reply_text(f"{EMOJI_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            maint, msg = check_feature_maintenance("indnum")
            if maint:
                await callback_query.message.reply_text(f"{EMOJI_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            ADMIN_STATE[uid] = 'INDNUM'
            await show_info_quote(callback_query.message, "ɪɴᴅ ɴᴜᴍ ɪɴꜰᴏ 𝟸", "ᴇɴᴛᴇʀ ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ:\n<i>6363016966, 9876543210</i>")
            await callback_query.answer()
            return
        
        elif data == "menu_indnum3":
            if not s.get("indnum3_enabled", True):
                await callback_query.message.reply_text(f"{EMOJI_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            maint, msg = check_feature_maintenance("indnum3")
            if maint:
                await callback_query.message.reply_text(f"{EMOJI_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            ADMIN_STATE[uid] = 'INDNUM3'
            await show_info_quote(callback_query.message, "ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ 𝟹", "ᴇɴᴛᴇʀ ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ:\n<i>6363016966, 9876543210</i>")
            await callback_query.answer()
            return
        
        elif data == "menu_invite":
            bot_info = await app.get_me()
            link = f"https://t.me/{bot_info.username}?start={user['invite_code']}"
            await callback_query.message.reply_text(
                f"<blockquote expandable>\n<b>{EMOJI_INVITE} ɪɴᴠɪᴛᴇ (+{INVITE_CREDITS}ᴄʀ)</b>\n\n<code>{link}</code>\n</blockquote>",
                parse_mode=ParseMode.HTML
            )
            await callback_query.answer()
            return
        
        elif data == "menu_redeem":
            ADMIN_STATE[uid] = 'REDEEM'
            await show_info_quote(callback_query.message, "ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ", "ᴇɴᴛᴇʀ ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ:\n<i>HEX-XXXXXXXXXX</i>")
            await callback_query.answer()
            return
        
        elif data == "menu_help":
            await show_help_inline(callback_query)
            return
        
        elif data == "menu_admin":
            if uid == ADMIN_ID:
                await admin_panel(callback_query.message)
                await callback_query.answer()
            else:
                await callback_query.answer("❌ Unauthorized!", show_alert=True)
            return
        
        await callback_query.answer()

# --- 📝 MESSAGE HANDLER ---

@app.on_message(filters.text & ~filters.command("start"))
async def handle_messages(client, message: Message):
    try:
        uid = message.from_user.id
        txt = message.text.strip()
        s = get_settings()
        
        if s.get("maintenance_mode", False) and uid != ADMIN_ID:
            sent = await message.reply_text(f"{EMOJI_TOOLS} Under maintenance", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(sent))
            return
        
        if uid != ADMIN_ID:
            user = get_user(uid)
            if not user.get("verified"):
                if await check_channel(uid):
                    user["verified"] = True
                    save_user(uid, user)
                    await main_menu(message, 0)
                    return
                await show_verification_page(message)
                return
        
        if uid in ADMIN_STATE:
            state = ADMIN_STATE.pop(uid)
            
            if state == "gen":
                try:
                    cr = int(txt)
                    code = generate_redeem_code(cr)
                    sent = await message.reply_text(f"{EMOJI_CHECK} <code>{code}</code> | {EMOJI_CREDIT} {cr}cr", parse_mode=ParseMode.HTML)
                except:
                    sent = await message.reply_text(f"{EMOJI_CROSS} Invalid number", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(sent))
                return
            
            elif state == "credit":
                p = txt.split()
                if len(p) >= 2:
                    bal = add_credits(p[0], int(p[1]))
                    sent = await message.reply_text(f"{EMOJI_CHECK} +{p[1]} | {bal}", parse_mode=ParseMode.HTML)
                else:
                    sent = await message.reply_text(f"{EMOJI_CROSS} Format: ID AMOUNT", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(sent))
                return
            
            elif state == "bcast":
                users = load_json(USERS_FILE)
                cnt = 0
                for u in users:
                    try:
                        await app.send_message(chat_id=int(u), text=f"{EMOJI_BOLT} {txt}")
                        cnt += 1
                    except: pass
                sent = await message.reply_text(f"{EMOJI_CHECK} Sent: {cnt}", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(sent))
                return
            
            elif state == "REDEEM":
                if txt.upper().startswith("HEX-"):
                    success, msg = redeem_code(uid, txt)
                else:
                    msg = f"{EMOJI_CROSS} Invalid code format!"
                sent = await message.reply_text(f"{msg}", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(sent))
                return
            
            elif state in ['TG', 'IFSC', 'SHORTLINK', 'MOBILE', 'AADHAAR', 'VEHICLE', 'GST', 'PAK', 'INDNUM', 'INDNUM3']:
                user = get_user(uid)
                if user.get("credits", 0) <= 0:
                    sent = await message.reply_text(f"{EMOJI_CROSS} No credits! +10 daily | +3 invite", parse_mode=ParseMode.HTML)
                    asyncio.create_task(schedule_delete(sent))
                    return
                
                await run_query(message, state, txt)
                return
        
        if uid in ADMIN_STATE:
            return
        
        await main_menu(message, 0)
        
    except Exception as e:
        print(f"Message handler error: {e}")

async def run_query(message: Message, mode: str, query: str):
    if not await net_ok():
        sent = await message.reply_text(f"{EMOJI_CROSS} No internet", parse_mode=ParseMode.HTML)
        asyncio.create_task(schedule_delete(sent))
        return
    
    st = await message.reply_text(f"{EMOJI_GREEN} ꜱᴇᴀʀᴄʜɪɴɢ...", parse_mode=ParseMode.HTML)
    credit_deducted = False
    
    try:
        if mode in ['AADHAAR', 'MOBILE', 'VEHICLE']:
            raw = run_india_script({'AADHAAR':'2','MOBILE':'1','VEHICLE':'4'}[mode], query)
            if raw:
                records = parse_all_india_records(raw)
                result = format_records_result(records, {'AADHAAR':'aadhaar','MOBILE':'mobile','VEHICLE':'vehicle'}[mode])
                if records and f"{EMOJI_CROSS}" not in str(result):
                    use_credit(message.from_user.id)
                    credit_deducted = True
            else:
                result = f"{EMOJI_CROSS} Script failed"
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
                use_credit(message.from_user.id)
                credit_deducted = True
        
        user = get_user(message.from_user.id)
        final = f"{result}\n{SEP}\n{EMOJI_CREDIT} {'ᴄʀ: '+str(user.get('credits',0)) if credit_deducted else 'ɴᴏ ᴄʀ ᴅᴇᴅᴜᴄᴛᴇᴅ'} | {EMOJI_CLOCK} {AUTO_DELETE_TIME}ꜱ{DISCLAIMER}{FOOTER}"
        sent = await st.edit_text(final, parse_mode=ParseMode.HTML)
        asyncio.create_task(schedule_delete(sent))
    except Exception as e:
        print(f"Query error: {e}")
        try:
            await st.edit_text(f"{EMOJI_WARN} ᴇʀʀᴏʀ{FOOTER}", parse_mode=ParseMode.HTML)
        except: pass

# --- 🚀 MAIN ---

def main():
    print("🔄 Hex Terminal Premium Starting...")
    print("🎨 Colored Inline Buttons with Pagination (8 per page)!")
    print("🤖 Kurigram Version with Full Button Colors!")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4"], capture_output=True, timeout=30)
    except: pass
    
    print(f"✅ {BOT_NAME} Ready!")
    print(f"💎 8 buttons per page with 2-color combination!")
    print(f"⭐ Admin Panel Fixed with proper callbacks!")
    print("🚀 Bot is running...")
    
    app.run()

if __name__ == '__main__':
    main()