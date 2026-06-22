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
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton
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
# PREMIUM EMOJI IDs - All emojis are premium
# ============================================================

# Premium Emoji IDs as INTEGERS for button icons
BUTTON_EMOJI_IDS = {
    # Main Menu Icons
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
    "fire": 6264785189394717307,
    "earn": 6267068789146260253,
    "redeem": 5285515895534278367,
    "next": 5195033767969839232,
    "back": 5258024981144066782,
    "menu": 6264791387032523779,
    "dashboard": 6267128480601741166,
    "spin": 6266969287638913443,
    "vip": 6267068789146260253,
    "osint": 5231012545799666522,
    "identity": 5260561650213220533,
    "leaderboard": 6093382540784046658
}

# For text messages - Premium emoji tags
PREMIUM_EMOJI_IDS = {
    "warn": "6267039884016358504",
    "check": "6267008582294705964",
    "cross": "6267000941547885720",
    "lock": "5316522278056399236",
    "crown": "6267128480601741166",
    "diamond": "6264791387032523779",
    "star": "6266969287638913443",
    "gift": "5203996991054432397",
    "fire": "6264785189394717307",
    "search": "5231012545799666522",
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
    "magnify": "5258024981144066782",
    "rocket": "5195033767969839232",
    "next": "5195033767969839232",
    "back": "5258024981144066782",
    "dashboard": "6267128480601741166",
    "spin": "6266969287638913443",
    "vip": "6267068789146260253",
    "osint": "5231012545799666522",
    "identity": "5260561650213220533",
    "leaderboard": "6093382540784046658",
    "menu": "6264791387032523779"
}

# --- PREMIUM EMOJIS FOR TEXT MESSAGES ---
def get_pe(key):
    return f'<tg-emoji emoji-id="{PREMIUM_EMOJI_IDS[key]}"> </tg-emoji>'

# Create all premium emoji objects for text
PE_WARN = get_pe("warn")
PE_CHECK = get_pe("check")
PE_CROSS = get_pe("cross")
PE_LOCK = get_pe("lock")
PE_CROWN = get_pe("crown")
PE_DIAMOND = get_pe("diamond")
PE_STAR = get_pe("star")
PE_GIFT = get_pe("gift")
PE_FIRE = get_pe("fire")
PE_SEARCH = get_pe("search")
PE_PHONE = get_pe("phone")
PE_BANK = get_pe("bank")
PE_LINK = get_pe("link")
PE_CAR = get_pe("car")
PE_CARD = get_pe("card")
PE_USER = get_pe("user")
PE_INDIA = get_pe("india")
PE_PAK = get_pe("pak")
PE_PHONE2 = get_pe("phone2")
PE_INVITE = get_pe("invite")
PE_TICKET = get_pe("ticket")
PE_CREDIT = get_pe("credit")
PE_REFRESH = get_pe("refresh")
PE_CLOCK = get_pe("clock")
PE_BOLT = get_pe("bolt")
PE_GREEN = get_pe("green")
PE_SPARKLE = get_pe("sparkle")
PE_TOOLS = get_pe("tools")
PE_DISABLED = get_pe("disabled")
PE_LOCATION = get_pe("location")
PE_HOME = get_pe("home")
PE_STATE = get_pe("state")
PE_NETWORK = get_pe("network")
PE_SIGNAL = get_pe("signal")
PE_SIM = get_pe("sim")
PE_CHART = get_pe("chart")
PE_HELP = get_pe("help")
PE_ABOUT = get_pe("about")
PE_STATS = get_pe("stats")
PE_MAGNIFY = get_pe("magnify")
PE_ROCKET = get_pe("rocket")
PE_NEXT = get_pe("next")
PE_BACK = get_pe("back")
PE_DASHBOARD = get_pe("dashboard")
PE_SPIN = get_pe("spin")
PE_VIP = get_pe("vip")
PE_OSINT = get_pe("osint")
PE_IDENTITY = get_pe("identity")
PE_LEADERBOARD = get_pe("leaderboard")
PE_MENU = get_pe("menu")

DISCLAIMER = f"\n\n{PE_WARN} ᴅɪꜱᴄʟᴀɪᴍᴇʀ:\nᴇᴅᴜᴄᴀᴛɪᴏɴᴀʟ ᴘᴜʀᴘᴏꜱᴇꜱ ᴏɴʟʏ. ᴜꜱᴇ ʀᴇꜱᴘᴏɴꜱɪʙʟʏ."

# --- Initialize Bot ---
app = Client(
    "hex_terminal_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

ADMIN_STATE = {}
USER_STATE = {}

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
    if code not in codes: return False, f"{PE_CROSS} ɪɴᴠᴀʟɪᴅ ᴄᴏᴅᴇ"
    if codes[code].get("used"): return False, f"{PE_CROSS} ᴀʟʀᴇᴀᴅʏ ᴜꜱᴇᴅ"
    cr = codes[code]["credits"]; codes[code]["used"] = True; codes[code]["used_by"] = str(uid)
    save_json(REDEEM_FILE, codes); bal = add_credits(uid, cr)
    return True, f"{PE_CHECK} +{cr} ᴄʀᴇᴅɪᴛꜱ ᴀᴅᴅᴇᴅ!\n{PE_CREDIT} ʙᴀʟᴀɴᴄᴇ: {bal}"

def get_settings():
    try: return load_json(SETTINGS_FILE)
    except:
        d = {"bypass_maintenance":False,"tgid_enabled":True,"ifsc_enabled":True,"bypass_enabled":True,"mobile_enabled":True,"aadhaar_enabled":True,"rc_enabled":True,"gst_enabled":True,"pak_enabled":True,"indnum_enabled":True,"indnum3_enabled":True,"maintenance_mode":False}
        for k in ["tgid","ifsc","bypass","mobile","aadhaar","rc","gst","pak","indnum","indnum3"]: d[f"maint_msg_{k}"] = f"{PE_TOOLS} {k} is under maintenance."; d[f"maint_{k}"] = False
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
        return True, s.get(f"maint_msg_{feature_key}", f"{PE_TOOLS} Under maintenance.")
    return False, ""

# ============================================================
# CREATE COLORED INLINE BUTTONS WITH PREMIUM EMOJIS
# ============================================================

BUTTON_STYLES = {
    "primary": ButtonStyle.PRIMARY,
    "success": ButtonStyle.SUCCESS,
    "danger": ButtonStyle.DANGER,
}

def create_colored_button(text: str, callback_data: str = None, url: str = None, color: str = "primary", icon_emoji_id: int = None):
    """Create a colored inline button with premium emoji icon"""
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
    """Create a row of colored inline buttons with premium emojis"""
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
# KEYBOARD MENU - ONLY PREMIUM EMOJIS
# ============================================================

def get_keyboard_menu(page=1):
    """Create keyboard menu with premium emoji icons only"""
    
    # For ReplyKeyboardMarkup, we need to use text that shows premium emojis
    # Since KeyboardButton doesn't support icon_custom_emoji_id,
    # we use the premium emoji tag in the text - this works in pyrogram
    
    if page == 1:
        keyboard = [
            [
                KeyboardButton(f"{PE_PHONE} ᴛɢ ɪᴅ ➜ ɴᴜᴍʙᴇʀ"),
                KeyboardButton(f"{PE_BANK} ɪꜰꜱᴄ ɪɴꜰᴏ")
            ],
            [
                KeyboardButton(f"{PE_LINK} ʟɪɴᴋ ʙʏᴘᴀꜱꜱ")
            ],
            [
                KeyboardButton(f"{PE_CARD} ᴀᴀᴅʜᴀʀ ɪɴꜰᴏ"),
                KeyboardButton(f"{PE_INDIA} ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ")
            ],
            [
                KeyboardButton(f"{PE_CAR} ʀᴄ ᴅᴇᴛᴀɪʟꜱ"),
                KeyboardButton(f"{PE_CARD} ɢꜱᴛ ʟᴏᴏᴋᴜᴘ")
            ],
            [
                KeyboardButton(f"{PE_PAK} ᴘᴀᴋ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ"),
                KeyboardButton(f"{PE_PHONE2} ɪɴᴅ ɴᴜᴍ ɪɴꜰᴏ 𝟸")
            ],
            [
                KeyboardButton(f"{PE_INDIA} ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ 𝟹")
            ],
            [
                KeyboardButton(f"{PE_INVITE} ɪɴᴠɪᴛᴇ & ᴇᴀʀɴ"),
                KeyboardButton(f"{PE_TICKET} ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ")
            ],
            [
                KeyboardButton(f"{PE_HELP} ʜᴇʟᴘ"),
                KeyboardButton(f"{PE_ABOUT} ᴀʙᴏᴜᴛ")
            ],
            [
                KeyboardButton(f"{PE_STATS} ꜱᴛᴀᴛꜱ"),
                KeyboardButton(f"{PE_CROWN} ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ" if ADMIN_ID else "")
            ],
            [
                KeyboardButton(f"{PE_NEXT} ɴᴇxᴛ ᴘᴀɢᴇ")
            ]
        ]
    else:
        keyboard = [
            [
                KeyboardButton(f"{PE_IDENTITY} ɪᴅᴇɴᴛɪᴛʏ ᴛᴏᴏʟꜱ"),
                KeyboardButton(f"{PE_OSINT} ᴏꜱɪɴᴛ ᴛᴏᴏʟꜱ")
            ],
            [
                KeyboardButton(f"{PE_VIP} ᴠɪᴘ ᴘʀᴇᴍɪᴜᴍ"),
                KeyboardButton(f"{PE_SPIN} ᴅᴀɪʟʏ ꜱᴘɪɴ")
            ],
            [
                KeyboardButton(f"{PE_DASHBOARD} ᴅᴀꜱʜʙᴏᴀʀᴅ"),
                KeyboardButton(f"{PE_LEADERBOARD} ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ")
            ],
            [
                KeyboardButton(f"{PE_BACK} ʙᴀᴄᴋ ᴛᴏ ᴍᴇɴᴜ")
            ]
        ]
    
    # Filter out empty buttons
    filtered_keyboard = []
    for row in keyboard:
        filtered_row = [btn for btn in row if btn.text]
        if filtered_row:
            filtered_keyboard.append(filtered_row)
    
    return ReplyKeyboardMarkup(
        filtered_keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )

# ============================================================
# MAIN MENU WITH KEYBOARD - ALL PREMIUM EMOJIS
# ============================================================

async def show_verification_page(message: Message):
    try:
        bot_info = await app.get_me()
        caption = (
            f"{PE_DIAMOND} {BOT_NAME} {PE_DIAMOND}\n"
            f"@{BOT_USERNAME}\n\n"
            f"{PE_LOCK} ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ʀᴇQᴜɪʀᴇᴅ\n"
            f"ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜɴʟᴏᴄᴋ\n\n"
            f"{PE_WARN} ɢᴜɪᴅᴇʟɪɴᴇꜱ:\n"
            f"• ᴇᴅᴜᴄᴀᴛɪᴏɴᴀʟ ᴘᴜʀᴘᴏꜱᴇꜱ ᴏɴʟʏ\n"
            f"• ᴜꜱᴇ ᴏɴ ʏᴏᴜʀ ᴏᴡɴ ᴅᴀᴛᴀ\n"
            f"• ʀᴇꜱᴘᴇᴄᴛ ᴘʀɪᴠᴀᴄʏ ʟᴀᴡꜱ\n\n"
            f"{PE_GIFT} +{DAILY_FREE_CREDITS} ᴅᴀɪʟʏ {PE_STAR}\n"
            f"{PE_INVITE} +{INVITE_CREDITS} ᴘᴇʀ ɪɴᴠɪᴛᴇ\n"
            f"{PE_CLOCK} {AUTO_DELETE_TIME}ꜱ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ\n\n"
            f"{PE_CROWN} ᴏᴡɴᴇʀ: @Hexh4ckerOFC\n"
            f"{PE_WARN} ᴍɪꜱᴜꜱᴇ ᴍᴀʏ ʟᴇᴀᴅ ᴛᴏ ʟᴇɢᴀʟ ᴀᴄᴛɪᴏɴ"
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
        f"{PE_LOCK} ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴠᴇʀɪꜰʏ",
        reply_markup=InlineKeyboardMarkup(flat_buttons),
        parse_mode=ParseMode.HTML
    )
    asyncio.create_task(schedule_delete(sent2, 120))

async def main_menu(message: Message, page: int = 1):
    """Main menu with keyboard - ALL PREMIUM EMOJIS"""
    is_admin = message.from_user.id == ADMIN_ID
    user = get_user(message.from_user.id)
    cr = user.get("credits", 0)
    
    # Get keyboard menu
    keyboard = get_keyboard_menu(page)
    
    # All premium emojis in header
    txt = (
        f"{PE_DIAMOND} {BOT_NAME} {PE_DIAMOND}\n"
        f"{PE_USER} <b>ᴡᴇʟᴄᴏᴍᴇ ʙᴀᴄᴋ,</b> <code>{message.from_user.first_name}</code>\n\n"
        f"{PE_DASHBOARD} <b>ʏᴏᴜʀ ᴅᴀꜱʜʙᴏᴀʀᴅ</b>\n"
        f"┃ {PE_CREDIT} <b>ᴄʀᴇᴅɪᴛꜱ:</b> {cr}\n"
        f"┃ {PE_SPIN} <b>ᴅᴀɪʟʏ ꜱᴘɪɴ:</b> +3 ꜰʀᴇᴇ\n"
        f"┃ {PE_VIP} <b>ᴠɪᴘ ᴘʀᴇᴍɪᴜᴍ:</b> {user.get('total_queries',0)} ꜱᴇᴀʀᴄʜ\n\n"
        f"{PE_STAR} <b>ɴɪᴄʜᴇ ᴅɪʏᴇ ɢʏᴇ ʙᴜᴛᴛᴏɴ ᴜꜱᴇ ᴋʀᴇ</b>\n"
        f"{PE_HELP} <code>/help</code> ᴛᴏ ꜱᴇᴇ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅꜱ\n\n"
        f"{PE_CROWN} <b>ᴅᴇᴠ:</b> @Hexh4ckerOFC\n"
        f"{PE_ROCKET} <b>ᴘᴀɢᴇ:</b> {page}/2"
    )
    
    sent = await message.reply_text(
        txt,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    asyncio.create_task(schedule_delete(sent, AUTO_DELETE_TIME))
    
    USER_STATE[str(message.from_user.id)] = {"page": page}

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
    if not data: return f"{PE_CROSS} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"
    if isinstance(data, dict) and not data.get("raw_text") and data.get("success"):
        d = data.get("data", data)
        if isinstance(d, dict):
            result = f"{PE_SPARKLE} {PE_PHONE} ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ ɪɴꜰᴏ {PE_SPARKLE}\n"
            if d.get('chat_id') or d.get('userid'): result += f"{PE_SEARCH} ᴄʜᴀᴛ ɪᴅ: <code>{d.get('chat_id', d.get('userid', query))}</code>\n"
            if d.get('number'): result += f"{PE_PHONE2} ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ: <code>{d['number']}</code>\n"
            if d.get('name'): result += f"{PE_USER} ᴘʀᴏꜰɪʟᴇ ɴᴀᴍᴇ: <code>{d['name']}</code>\n"
            return result
    return f"{PE_CROSS} ɴᴏᴛ ꜰᴏᴜɴᴅ"

async def ifsc_lookup(session, code):
    data = await safe_api_fetch(session, f"{IFSC_API}{code.upper()}")
    if not data or isinstance(data, dict) and data.get("raw_text"): return f"{PE_CROSS} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"
    if isinstance(data, dict):
        return (f"{PE_SPARKLE} {PE_BANK} ʙᴀɴᴋ ɪꜰꜱᴄ ᴅᴇᴛᴀɪʟꜱ {PE_SPARKLE}\n"
                f"{PE_BANK} ʙᴀɴᴋ ɴᴀᴍᴇ: <code>{data.get('BANK','N/A')}</code>\n"
                f"{PE_LOCATION} ʙʀᴀɴᴄʜ: <code>{data.get('BRANCH','N/A')}</code>\n"
                f"{PE_CARD} ɪꜰꜱᴄ ᴄᴏᴅᴇ: <code>{data.get('IFSC',code.upper())}</code>\n"
                f"{PE_LOCATION} ᴀᴅᴅʀᴇꜱꜱ: <code>{data.get('ADDRESS','N/A')}</code>")
    return f"{PE_CROSS} ɪɴᴠᴀʟɪᴅ ᴄᴏᴅᴇ"

async def bypass_lookup(session, link):
    s = get_settings()
    if s.get("bypass_maintenance",False): return f"{PE_TOOLS} ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ"
    data = await safe_api_fetch(session, f"{SHORTLINK_API}{link}", timeout=20)
    if not data or isinstance(data, dict) and data.get("raw_text"): return f"{PE_CROSS} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"
    if isinstance(data, dict):
        r = data.get('bypassed_url') or data.get('url') or str(data)
        return f"{PE_SPARKLE} {PE_LINK} ʟɪɴᴋ ʙʏᴘᴀꜱꜱᴇᴅ {PE_SPARKLE}\n{PE_LINK} ᴏʀɪɢɪɴᴀʟ ᴜʀʟ: <code>{str(r)}</code>"
    return f"{PE_LINK} ʀᴇꜱᴜʟᴛ: <code>{str(data)}</code>"

async def gst_lookup(session, gst_number):
    data = await safe_api_fetch(session, f"{GST_API}{gst_number.upper()}", timeout=20)
    if not data or isinstance(data, dict) and data.get("raw_text"): return f"{PE_CROSS} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"
    if isinstance(data, dict) and data.get("status") == "success" and data.get("data"):
        d = data["data"]
        result = f"{PE_SPARKLE} {PE_CARD} ɢꜱᴛ ʙᴜꜱɪɴᴇꜱꜱ ɪɴꜰᴏ {PE_SPARKLE}\n"
        if d.get('TradeName'): result += f"{PE_BANK} ʙᴜꜱɪɴᴇꜱꜱ ɴᴀᴍᴇ: <code>{d['TradeName']}</code>\n"
        if d.get('Gstin'): result += f"{PE_CARD} ɢꜱᴛ ɴᴜᴍʙᴇʀ: <code>{d['Gstin']}</code>\n"
        return result
    return f"{PE_CROSS} ɪɴᴠᴀʟɪᴅ ɢꜱᴛ"

async def pakistan_lookup(session, number):
    try:
        data = await safe_api_fetch(session, f"{PAK_API}{number}", timeout=20)
        if not data or isinstance(data, dict) and data.get("raw_text"): return f"{PE_CROSS} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"
        if isinstance(data, dict) and data.get("success") and data.get("data"):
            valid = [r for r in data["data"] if isinstance(r, dict) and any(r.get(k) for k in ['name','number','cnic','address'])]
            if not valid: return f"{PE_CROSS} ɴᴏ ᴅᴀᴛᴀ"
            result = f"{PE_SPARKLE} {PE_PAK} ᴘᴀᴋɪꜱᴛᴀɴ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ {PE_SPARKLE}\n"
            for i, r in enumerate(valid[:3], 1):
                if len(valid) > 1: result += f"\n━━ {PE_USER} ʀᴇᴄᴏʀᴅ {i} ━━\n"
                if r.get('number'): result += f"{PE_PHONE2} ᴘʜᴏɴᴇ: <code>{r['number']}</code>\n"
                if r.get('name'): result += f"{PE_USER} ɴᴀᴍᴇ: <code>{r['name']}</code>\n"
                if r.get('cnic'): result += f"{PE_CARD} ᴄɴɪᴄ: <code>{r['cnic']}</code>\n"
                if r.get('address'): result += f"{PE_LOCATION} ᴀᴅᴅʀᴇꜱꜱ: <code>{r['address'][:200]}</code>\n"
            return result
        return f"{PE_CROSS} ɴᴏ ᴅᴀᴛᴀ"
    except: return f"{PE_CROSS} ᴇʀʀᴏʀ"

async def indnum_lookup(session, number):
    for attempt in range(3):
        data = await safe_api_fetch(session, f"{IND_NUM_API}{number}", timeout=30)
        if data and isinstance(data, dict) and not data.get("raw_text") and data.get("results"): break
        if attempt < 2: await asyncio.sleep(2)
    if not data or isinstance(data, dict) and data.get("raw_text"): return f"{PE_CROSS} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"
    results = data.get("results", {})
    if not results: return f"{PE_CROSS} ɴᴏ ʀᴇꜱᴜʟᴛꜱ"
    result = f"{PE_SPARKLE} {PE_PHONE2} ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴀᴅᴠᴀɴᴄᴇᴅ {PE_SPARKLE}\n{PE_PHONE2} ɴᴜᴍʙᴇʀ: <code>{number}</code>\n"
    found = False
    s3 = results.get("source_3", {}).get("data", {})
    if isinstance(s3, dict):
        for k, e in [("SIM card",PE_SIM),("Connection",PE_SIGNAL),("Mobile State",PE_LOCATION),("Hometown",PE_HOME)]:
            if s3.get(k): result += f"{e} {k}: <code>{str(s3[k])[:200]}</code>\n"; found = True
    s4 = results.get("source_4", {}).get("data", {})
    if isinstance(s4, dict) and s4.get("carrier"): result += f"{PE_NETWORK} ᴄᴀʀʀɪᴇʀ: <code>{s4['carrier']}</code>\n"; found = True
    return result if found else f"{PE_CROSS} ɴᴏ ᴅᴀᴛᴀ"

async def indnum3_lookup(session, number):
    url = f"{IND_NUM_API_3}{number}"
    try:
        headers = {'User-Agent': 'Mozilla/5.0','Accept': '*/*'}
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=25), headers=headers, allow_redirects=True) as r:
            text = await r.text()
            if not text or len(text) < 20: return f"{PE_CROSS} ᴇᴍᴘᴛʏ ʀᴇꜱᴘᴏɴꜱᴇ"
            try:
                data = json.loads(text)
                if isinstance(data, dict):
                    result = f"{PE_SPARKLE} {PE_INDIA} ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴛʀᴀᴄᴋɪɴɢ {PE_SPARKLE}\n{PE_PHONE2} ɴᴜᴍʙᴇʀ: <code>{number}</code>\n"
                    for k, v in data.items():
                        if v and str(v).strip():
                            result += f"{PE_SEARCH} {k}: <code>{str(v)[:200]}</code>\n"
                    return result
            except: pass
            clean = re.sub(r'<[^>]+>', '\n', text)
            lines = [l.strip() for l in clean.split('\n') if l.strip() and len(l.strip()) > 1]
            result = f"{PE_SPARKLE} {PE_INDIA} ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴛʀᴀᴄᴋɪɴɢ {PE_SPARKLE}\n{PE_PHONE2} ɴᴜᴍʙᴇʀ: <code>{number}</code>\n"
            found = 0
            for line in lines[:20]:
                if ':' in line:
                    parts = line.split(':', 1)
                    key, val = parts[0].strip(), parts[1].strip() if len(parts) > 1 else ''
                    if val:
                        e = PE_USER if any(w in key.lower() for w in ['name','nama']) else PE_NETWORK if any(w in key.lower() for w in ['carrier','operator','network','sim']) else PE_LOCATION if any(w in key.lower() for w in ['location','address','city','state','area']) else PE_PHONE2 if any(w in key.lower() for w in ['phone','mobile','number','no']) else PE_SEARCH
                        result += f"{e} {key}: <code>{val[:200]}</code>\n"; found += 1
            if found == 0: result += f"{PE_CARD} ʀᴀᴡ ᴅᴀᴛᴀ: <code>{clean[:500]}</code>\n"
            return result
    except: return f"{PE_CROSS} ᴛɪᴍᴇᴏᴜᴛ"

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
        for field, label in {'Name':f'{PE_USER} ɴᴀᴍᴇ',"Father's Name":f'{PE_USER} ꜰᴀᴛʜᴇʀ','Mobile':f'{PE_PHONE2} ᴍᴏʙɪʟᴇ','Address':f'{PE_LOCATION} ᴀᴅᴅʀᴇꜱꜱ','Circle':f'{PE_NETWORK} ᴄɪʀᴄʟᴇ','State':f'{PE_STATE} ꜱᴛᴀᴛᴇ'}.items():
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
    if not records: return f"{PE_CROSS} ɴᴏ ʀᴇᴄᴏʀᴅꜱ ꜰᴏᴜɴᴅ"
    title = {'aadhaar':f'{PE_CARD} ᴀᴀᴅʜᴀʀ','mobile':f'{PE_INDIA} ɪɴᴅ ɴᴜᴍʙᴇʀ','vehicle':f'{PE_CAR} ᴠᴇʜɪᴄʟᴇ'}.get(search_type, f'{PE_CHART} ʀᴇꜱᴜʟᴛ')
    result = f"{PE_SPARKLE} {title} {PE_SPARKLE}\n{PE_CHART} ᴛᴏᴛᴀʟ ʀᴇᴄᴏʀᴅꜱ: {len(records)}\n"
    for i, record in enumerate(records, 1):
        if len(records) > 1: result += f"\n━━ {PE_USER} ʀᴇᴄᴏʀᴅ {i} ━━\n"
        for key, value in record.items(): result += f"{key}: <code>{value}</code>\n"
    return result

# --- 👑 ADMIN ---

async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID: return
    s = get_settings()
    ms = lambda key: "🔴" if s.get(f"maint_{key}") else "🟢"
    
    kb = [
        create_styled_row([
            {"text": "ɢᴇɴ ᴄᴏᴅᴇ", "callback_data": "ad_gen", "color": "success", "icon_emoji_id": BUTTON_EMOJI_IDS["ticket"]},
            {"text": "ᴄᴏᴅᴇꜱ", "callback_data": "ad_codes", "color": "info", "icon_emoji_id": BUTTON_EMOJI_IDS["ticket"]}
        ]),
        create_styled_row([
            {"text": "ᴀᴅᴅ ᴄʀ", "callback_data": "ad_credit", "color": "warning", "icon_emoji_id": BUTTON_EMOJI_IDS["gift"]},
            {"text": "ʙᴄᴀꜱᴛ", "callback_data": "ad_bcast", "color": "primary", "icon_emoji_id": BUTTON_EMOJI_IDS["bolt"]}
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
            {"text": "ᴄʟᴏꜱᴇ", "callback_data": "ad_close", "color": "danger"}
        ])
    ]
    
    flat_kb = []
    for row in kb:
        flat_kb.append(row)
    
    txt = f"{PE_CROWN} ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ {PE_CROWN}\n{PE_INVITE} ᴜꜱᴇʀꜱ: {len(load_json(USERS_FILE))} | {PE_TICKET} ᴄᴏᴅᴇꜱ: {len(load_json(REDEEM_FILE))}"
    
    if hasattr(message, 'edit_text'):
        await message.edit_text(txt, reply_markup=InlineKeyboardMarkup(flat_kb), parse_mode=ParseMode.HTML)
    else:
        await message.reply_text(txt, reply_markup=InlineKeyboardMarkup(flat_kb), parse_mode=ParseMode.HTML)

# --- 🚀 HELP, ABOUT, STATS ---

async def show_help_inline(callback_query: CallbackQuery):
    await callback_query.answer()
    text = f"""
{PE_HELP} 𝐇𝐄𝐋𝐏 & 𝐆𝐔𝐈𝐃𝐄 {PE_HELP}

{PE_STAR} 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄 𝐅𝐄𝐀𝐓𝐔𝐑𝐄𝐒:

{PE_PHONE} 𝐓𝐆 𝐈𝐃 ➜ 𝐍𝐔𝐌𝐁𝐄𝐑
Get phone number from Telegram ID

{PE_BANK} 𝐈𝐅𝐒𝐂 𝐈𝐍𝐅𝐎
Get bank details from IFSC code

{PE_LINK} 𝐋𝐈𝐍𝐊 𝐁𝐘𝐏𝐀𝐒𝐒
Bypass short links

{PE_CARD} 𝐀𝐀𝐃𝐇𝐀𝐑 𝐈𝐍𝐅𝐎
Get details from Aadhaar number

{PE_INDIA} 𝐈𝐍𝐃 𝐍𝐔𝐌𝐁𝐄𝐑 𝐈𝐍𝐅𝐎
Get Indian number details

{PE_CAR} 𝐑𝐂 𝐃𝐄𝐓𝐀𝐈𝐋𝐒
Get vehicle RC details

{PE_CARD} 𝐆𝐒𝐓 𝐋𝐎𝐎𝐊𝐔𝐏
Get business details from GST

{PE_PAK} 𝐏𝐀𝐊 𝐍𝐔𝐌𝐁𝐄𝐑 𝐈𝐍𝐅𝐎
Get Pakistan number details

{PE_GIFT} 𝐃𝐀𝐈𝐋𝐘 𝐅𝐑𝐄𝐄: +{DAILY_FREE_CREDITS} ᴄʀᴇᴅɪᴛꜱ

{PE_INVITE} 𝐈𝐍𝐕𝐈𝐓𝐄: +{INVITE_CREDITS} ᴄʀᴇᴅɪᴛꜱ ᴘᴇʀ ᴜꜱᴇʀ

{PE_CLOCK} 𝐀𝐔𝐓𝐎 𝐃𝐄𝐋𝐄𝐓𝐄: {AUTO_DELETE_TIME}ꜱ
"""
    await callback_query.message.edit_text(text, parse_mode=ParseMode.HTML)
    await asyncio.sleep(60)
    try: await callback_query.message.delete()
    except: pass

async def show_about_inline(callback_query: CallbackQuery):
    await callback_query.answer()
    text = f"""
{PE_ABOUT} 𝐀𝐁𝐎𝐔𝐓 𝐁𝐎𝐓 {PE_ABOUT}

𝐍𝐀𝐌𝐄: {BOT_NAME}
𝐔𝐒𝐄𝐑𝐍𝐀𝐌𝐄: @{BOT_USERNAME}
𝐕𝐄𝐑𝐒𝐈𝐎𝐍: 3.0

{PE_DIAMOND} 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐅𝐄𝐀𝐓𝐔𝐑𝐄𝐒

• Telegram ID Lookup
• IFSC Bank Details
• Link Bypass
• Aadhaar Info
• Mobile Number Tracking
• RC Details
• GST Lookup
• Pakistan Number Info
• Colored Inline Buttons

{PE_CROWN} 𝐃𝐄𝐕𝐄𝐋𝐎𝐏𝐄𝐃 𝐁𝐘: @Hexh4ckerOFC

{PE_WARN} 𝐅𝐎𝐑 𝐄𝐃𝐔𝐂𝐀𝐓𝐈𝐎𝐍𝐀𝐋 𝐏𝐔𝐑𝐏𝐎𝐒𝐄𝐒 𝐎𝐍𝐋𝐘
"""
    await callback_query.message.edit_text(text, parse_mode=ParseMode.HTML)
    await asyncio.sleep(60)
    try: await callback_query.message.delete()
    except: pass

async def show_stats_inline(callback_query: CallbackQuery):
    await callback_query.answer()
    users = load_json(USERS_FILE)
    total_users = len(users)
    total_queries = sum(u.get('total_queries', 0) for u in users.values())
    total_invites = sum(u.get('invites', 0) for u in users.values())
    total_credits = sum(u.get('credits', 0) for u in users.values())
    
    text = f"""
{PE_STATS} 𝐁𝐎𝐓 𝐒𝐓𝐀𝐓𝐈𝐒𝐓𝐈𝐂𝐒 {PE_STATS}

{PE_USER} 𝐓𝐎𝐓𝐀𝐋 𝐔𝐒𝐄𝐑𝐒: {total_users}
{PE_SEARCH} 𝐓𝐎𝐓𝐀𝐋 𝐐𝐔𝐄𝐑𝐈𝐄𝐒: {total_queries}
{PE_INVITE} 𝐓𝐎𝐓𝐀𝐋 𝐈𝐍𝐕𝐈𝐓𝐄𝐒: {total_invites}
{PE_CREDIT} 𝐓𝐎𝐓𝐀𝐋 𝐂𝐑𝐄𝐃𝐈𝐓𝐒: {total_credits}

{PE_DIAMOND} 𝐁𝐎𝐓 𝐒𝐓𝐀𝐓𝐔𝐒: 🟢 Active
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
                            text=f"{PE_GIFT} +{cr} ᴄʀᴇᴅɪᴛꜱ! ɴᴇᴡ ᴜꜱᴇʀ ᴊᴏɪɴᴇᴅ!"
                        )
                    except: pass
                    break
        
        user = get_user(uid)
        
        if uid == ADMIN_ID:
            user["verified"] = True
            save_user(uid, user)
            await main_menu(message)
            return
        
        if not user.get("verified"):
            if await check_channel(uid):
                user["verified"] = True
                save_user(uid, user)
                await main_menu(message)
                return
            await show_verification_page(message)
            return
        
        await main_menu(message)
    except Exception as e:
        print(f"Start error: {e}")

# --- 📝 CALLBACK QUERY HANDLER ---

@app.on_callback_query()
async def callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    uid = callback_query.from_user.id
    s = get_settings()
    
    if data == "verify":
        if uid == ADMIN_ID:
            user = get_user(uid)
            user["verified"] = True
            save_user(uid, user)
            await callback_query.answer("✅ Verified as Admin!", show_alert=True)
            try: await callback_query.message.delete()
            except: pass
            await main_menu(callback_query.message)
            return
        
        if await check_channel(uid):
            user = get_user(uid)
            user["verified"] = True
            save_user(uid, user)
            await callback_query.answer("✅ Verified!", show_alert=True)
            try: await callback_query.message.delete()
            except: pass
            await main_menu(callback_query.message)
        else:
            await callback_query.answer("❌ Please join the channel first!", show_alert=True)
        return
    
    if data.startswith("ad_"):
        if uid != ADMIN_ID:
            await callback_query.answer("❌ Unauthorized!", show_alert=True)
            return
        
        if data == "ad_close":
            await callback_query.message.delete()
            await callback_query.answer()
            return
        elif data == "ad_codes":
            codes = load_json(REDEEM_FILE)
            txt = f"{PE_TICKET} ᴄᴏᴅᴇꜱ: {len(codes)}\n"
            for c, v in list(codes.items())[-15:]:
                txt += f"{'✅' if not v.get('used') else '❌'} <code>{c}</code> | {v.get('credits')}cr\n"
            await callback_query.message.edit_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
            await callback_query.answer()
            return
        elif data == "ad_gen":
            ADMIN_STATE[uid] = "gen"
            await callback_query.message.edit_text(f"{PE_TICKET} ᴇɴᴛᴇʀ ᴄʀᴇᴅɪᴛꜱ:\n<i>100</i>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
            await callback_query.answer()
            return
        elif data == "ad_credit":
            ADMIN_STATE[uid] = "credit"
            await callback_query.message.edit_text(f"{PE_GIFT} ᴇɴᴛᴇʀ ɪᴅ ᴀᴍᴏᴜɴᴛ:\n<i>123456789 50</i>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
            await callback_query.answer()
            return
        elif data == "ad_bcast":
            ADMIN_STATE[uid] = "bcast"
            await callback_query.message.edit_text(f"{PE_BOLT} ᴇɴᴛᴇʀ ᴍᴇꜱꜱᴀɢᴇ:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
            await callback_query.answer()
            return
        elif data == "ad_maint":
            s["maintenance_mode"] = not s.get("maintenance_mode", False)
            save_settings(s)
            await callback_query.answer(f"Global: {'ON' if s['maintenance_mode'] else 'OFF'}", show_alert=True)
            await admin_panel(callback_query.message)
            return
        elif data.startswith("ad_maint_"):
            f = data.replace("ad_maint_", "")
            s[f"maint_{f}"] = not s.get(f"maint_{f}", False)
            save_settings(s)
            await callback_query.answer(f"{f}: {'ON' if s[f'maint_{f}'] else 'OFF'}", show_alert=True)
            await admin_panel(callback_query.message)
            return
        elif data.startswith("ad_"):
            toggle_map = {"ad_tgid":"tgid_enabled","ad_ifsc":"ifsc_enabled","ad_bypass_toggle":"bypass_enabled","ad_mobile":"mobile_enabled","ad_aadhaar":"aadhaar_enabled","ad_rc":"rc_enabled","ad_gst":"gst_enabled","ad_pak":"pak_enabled","ad_indnum":"indnum_enabled","ad_indnum3":"indnum3_enabled"}
            if data in toggle_map:
                k = toggle_map[data]
                s[k] = not s.get(k, True)
                save_settings(s)
                await callback_query.answer(f"{k}: {'ON' if s[k] else 'OFF'}", show_alert=True)
                await admin_panel(callback_query.message)
            return
        elif data == "ad_back":
            await admin_panel(callback_query.message)
            await callback_query.answer()
            return
        await callback_query.answer()
        return
    
    if data.startswith("menu_"):
        if uid != ADMIN_ID:
            user = get_user(uid)
            if not user.get("verified"):
                if await check_channel(uid):
                    user["verified"] = True
                    save_user(uid, user)
                    await main_menu(callback_query.message)
                    return
                await show_verification_page(callback_query.message)
                await callback_query.answer()
                return
        
        if data == "menu_tgid":
            if not s.get("tgid_enabled", True):
                await callback_query.message.reply_text(f"{PE_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            maint, msg = check_feature_maintenance("tgid")
            if maint:
                await callback_query.message.reply_text(f"{PE_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            ADMIN_STATE[uid] = 'TG'
            await callback_query.message.reply_text(f"{PE_PHONE} ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ ᴛᴏ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ\n<i>7123181749, 6884112825</i>", parse_mode=ParseMode.HTML)
            await callback_query.answer()
            return
        
        elif data == "menu_ifsc":
            if not s.get("ifsc_enabled", True):
                await callback_query.message.reply_text(f"{PE_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            maint, msg = check_feature_maintenance("ifsc")
            if maint:
                await callback_query.message.reply_text(f"{PE_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            ADMIN_STATE[uid] = 'IFSC'
            await callback_query.message.reply_text(f"{PE_BANK} ʙᴀɴᴋ ɪꜰꜱᴄ ᴄᴏᴅᴇ\n<i>SBIN0001234, HDFC0001234</i>", parse_mode=ParseMode.HTML)
            await callback_query.answer()
            return
        
        elif data == "menu_bypass":
            if not s.get("bypass_enabled", True):
                await callback_query.message.reply_text(f"{PE_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            maint, msg = check_feature_maintenance("bypass")
            if maint:
                await callback_query.message.reply_text(f"{PE_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            ADMIN_STATE[uid] = 'SHORTLINK'
            await callback_query.message.reply_text(f"{PE_LINK} ʟɪɴᴋ ʙʏᴘᴀꜱꜱ\n<i>https://indianshortner.in/xxxx</i>", parse_mode=ParseMode.HTML)
            await callback_query.answer()
            return
        
        elif data == "menu_mobile":
            if not s.get("mobile_enabled", True):
                await callback_query.message.reply_text(f"{PE_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            maint, msg = check_feature_maintenance("mobile")
            if maint:
                await callback_query.message.reply_text(f"{PE_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            ADMIN_STATE[uid] = 'MOBILE'
            await callback_query.message.reply_text(f"{PE_INDIA} ɪɴᴅɪᴀɴ ᴍᴏʙɪʟᴇ ɴᴜᴍʙᴇʀ\n<i>9876543210, 8123456789</i>", parse_mode=ParseMode.HTML)
            await callback_query.answer()
            return
        
        elif data == "menu_aadhaar":
            if not s.get("aadhaar_enabled", True):
                await callback_query.message.reply_text(f"{PE_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            maint, msg = check_feature_maintenance("aadhaar")
            if maint:
                await callback_query.message.reply_text(f"{PE_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            ADMIN_STATE[uid] = 'AADHAAR'
            await callback_query.message.reply_text(f"{PE_CARD} ᴀᴀᴅʜᴀʀ ɴᴜᴍʙᴇʀ\n<i>123456789012</i>", parse_mode=ParseMode.HTML)
            await callback_query.answer()
            return
        
        elif data == "menu_rc":
            if not s.get("rc_enabled", True):
                await callback_query.message.reply_text(f"{PE_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            maint, msg = check_feature_maintenance("rc")
            if maint:
                await callback_query.message.reply_text(f"{PE_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            ADMIN_STATE[uid] = 'VEHICLE'
            await callback_query.message.reply_text(f"{PE_CAR} ᴠᴇʜɪᴄʟᴇ ɴᴜᴍʙᴇʀ\n<i>KA01AB3256, DL1CX1234</i>", parse_mode=ParseMode.HTML)
            await callback_query.answer()
            return
        
        elif data == "menu_gst":
            if not s.get("gst_enabled", True):
                await callback_query.message.reply_text(f"{PE_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            maint, msg = check_feature_maintenance("gst")
            if maint:
                await callback_query.message.reply_text(f"{PE_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            ADMIN_STATE[uid] = 'GST'
            await callback_query.message.reply_text(f"{PE_CARD} ɢꜱᴛ ɴᴜᴍʙᴇʀ\n<i>19BOKPS7056D1ZI</i>", parse_mode=ParseMode.HTML)
            await callback_query.answer()
            return
        
        elif data == "menu_pak":
            if not s.get("pak_enabled", True):
                await callback_query.message.reply_text(f"{PE_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            maint, msg = check_feature_maintenance("pak")
            if maint:
                await callback_query.message.reply_text(f"{PE_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            ADMIN_STATE[uid] = 'PAK'
            await callback_query.message.reply_text(f"{PE_PAK} ᴘᴀᴋɪꜱᴛᴀɴ ɴᴜᴍʙᴇʀ\n<i>923078750447</i>", parse_mode=ParseMode.HTML)
            await callback_query.answer()
            return
        
        elif data == "menu_indnum":
            if not s.get("indnum_enabled", True):
                await callback_query.message.reply_text(f"{PE_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            maint, msg = check_feature_maintenance("indnum")
            if maint:
                await callback_query.message.reply_text(f"{PE_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            ADMIN_STATE[uid] = 'INDNUM'
            await callback_query.message.reply_text(f"{PE_PHONE2} ᴀᴅᴠᴀɴᴄᴇᴅ ɴᴜᴍʙᴇʀ\n<i>6363016966, 9876543210</i>", parse_mode=ParseMode.HTML)
            await callback_query.answer()
            return
        
        elif data == "menu_indnum3":
            if not s.get("indnum3_enabled", True):
                await callback_query.message.reply_text(f"{PE_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            maint, msg = check_feature_maintenance("indnum3")
            if maint:
                await callback_query.message.reply_text(f"{PE_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                await callback_query.answer()
                return
            ADMIN_STATE[uid] = 'INDNUM3'
            await callback_query.message.reply_text(f"{PE_INDIA} ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴛʀᴀᴄᴋɪɴɢ\n<i>6363016966, 9876543210</i>", parse_mode=ParseMode.HTML)
            await callback_query.answer()
            return
        
        elif data == "menu_invite":
            user = get_user(uid)
            bot_info = await app.get_me()
            link = f"https://t.me/{bot_info.username}?start={user['invite_code']}"
            await callback_query.message.reply_text(f"{PE_INVITE} ɪɴᴠɪᴛᴇ (+{INVITE_CREDITS}ᴄʀ)\n<code>{link}</code>", parse_mode=ParseMode.HTML)
            await callback_query.answer()
            return
        
        elif data == "menu_redeem":
            ADMIN_STATE[uid] = 'REDEEM'
            await callback_query.message.reply_text(f"{PE_TICKET} ᴇɴᴛᴇʀ ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ:\n<i>HEX-XXXXXXXXXX</i>", parse_mode=ParseMode.HTML)
            await callback_query.answer()
            return
        
        elif data == "menu_help":
            await show_help_inline(callback_query)
            return
        
        elif data == "menu_about":
            await show_about_inline(callback_query)
            return
        
        elif data == "menu_stats":
            await show_stats_inline(callback_query)
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

@app.on_message(filters.text & ~filters.command("start") & ~filters.command("help"))
async def handle_messages(client, message: Message):
    try:
        uid = message.from_user.id
        txt = message.text.strip()
        s = get_settings()
        
        if s.get("maintenance_mode", False) and uid != ADMIN_ID:
            sent = await message.reply_text(f"{PE_TOOLS} Under maintenance", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(sent))
            return
        
        if uid != ADMIN_ID:
            user = get_user(uid)
            if not user.get("verified"):
                if await check_channel(uid):
                    user["verified"] = True
                    save_user(uid, user)
                    await main_menu(message)
                    return
                await show_verification_page(message)
                return
        
        # Handle keyboard navigation
        if txt == f"{PE_NEXT} ɴᴇxᴛ ᴘᴀɢᴇ":
            await main_menu(message, page=2)
            return
        elif txt == f"{PE_BACK} ʙᴀᴄᴋ ᴛᴏ ᴍᴇɴᴜ":
            await main_menu(message, page=1)
            return
        
        # Handle admin panel via keyboard
        if txt == f"{PE_CROWN} ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ" and uid == ADMIN_ID:
            await admin_panel(message)
            return
        
        # Handle admin state
        if uid in ADMIN_STATE:
            state = ADMIN_STATE.pop(uid)
            
            if state == "gen":
                try:
                    cr = int(txt)
                    code = generate_redeem_code(cr)
                    sent = await message.reply_text(f"{PE_CHECK} <code>{code}</code> | {PE_CREDIT} {cr}cr", parse_mode=ParseMode.HTML)
                except:
                    sent = await message.reply_text(f"{PE_CROSS} Invalid number", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(sent))
                return
            
            elif state == "credit":
                p = txt.split()
                if len(p) >= 2:
                    bal = add_credits(p[0], int(p[1]))
                    sent = await message.reply_text(f"{PE_CHECK} +{p[1]} | {bal}", parse_mode=ParseMode.HTML)
                else:
                    sent = await message.reply_text(f"{PE_CROSS} Format: ID AMOUNT", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(sent))
                return
            
            elif state == "bcast":
                users = load_json(USERS_FILE)
                cnt = 0
                for u in users:
                    try:
                        await app.send_message(chat_id=int(u), text=f"{PE_BOLT} {txt}")
                        cnt += 1
                    except: pass
                sent = await message.reply_text(f"{PE_CHECK} Sent: {cnt}", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(sent))
                return
            
            elif state == "REDEEM":
                if txt.upper().startswith("HEX-"):
                    success, msg = redeem_code(uid, txt)
                else:
                    msg = f"{PE_CROSS} Invalid code format!"
                sent = await message.reply_text(f"{msg}", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(sent))
                return
            
            elif state in ['TG', 'IFSC', 'SHORTLINK', 'MOBILE', 'AADHAAR', 'VEHICLE', 'GST', 'PAK', 'INDNUM', 'INDNUM3']:
                user = get_user(uid)
                if user.get("credits", 0) <= 0:
                    sent = await message.reply_text(f"{PE_CROSS} No credits! +10 daily | +3 invite", parse_mode=ParseMode.HTML)
                    asyncio.create_task(schedule_delete(sent))
                    return
                
                await run_query(message, state, txt)
                return
        
        if uid in ADMIN_STATE:
            return
        
        # Handle feature buttons from keyboard
        if txt == f"{PE_PHONE} ᴛɢ ɪᴅ ➜ ɴᴜᴍʙᴇʀ":
            if not s.get("tgid_enabled", True):
                sent = await message.reply_text(f"{PE_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(sent))
                return
            maint, msg = check_feature_maintenance("tgid")
            if maint:
                sent = await message.reply_text(f"{PE_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(sent))
                return
            ADMIN_STATE[uid] = 'TG'
            sent = await message.reply_text(f"{PE_PHONE} ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ ᴛᴏ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ\n<i>7123181749, 6884112825</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(sent))
            return
        
        elif txt == f"{PE_BANK} ɪꜰꜱᴄ ɪɴꜰᴏ":
            if not s.get("ifsc_enabled", True):
                sent = await message.reply_text(f"{PE_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(sent))
                return
            maint, msg = check_feature_maintenance("ifsc")
            if maint:
                sent = await message.reply_text(f"{PE_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(sent))
                return
            ADMIN_STATE[uid] = 'IFSC'
            sent = await message.reply_text(f"{PE_BANK} ʙᴀɴᴋ ɪꜰꜱᴄ ᴄᴏᴅᴇ\n<i>SBIN0001234, HDFC0001234</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(sent))
            return
        
        elif txt == f"{PE_LINK} ʟɪɴᴋ ʙʏᴘᴀꜱꜱ":
            if not s.get("bypass_enabled", True):
                sent = await message.reply_text(f"{PE_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(sent))
                return
            maint, msg = check_feature_maintenance("bypass")
            if maint:
                sent = await message.reply_text(f"{PE_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(sent))
                return
            ADMIN_STATE[uid] = 'SHORTLINK'
            sent = await message.reply_text(f"{PE_LINK} ʟɪɴᴋ ʙʏᴘᴀꜱꜱ\n<i>https://indianshortner.in/xxxx</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(sent))
            return
        
        elif txt == f"{PE_INDIA} ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ":
            if not s.get("mobile_enabled", True):
                sent = await message.reply_text(f"{PE_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(sent))
                return
            maint, msg = check_feature_maintenance("mobile")
            if maint:
                sent = await message.reply_text(f"{PE_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(sent))
                return
            ADMIN_STATE[uid] = 'MOBILE'
            sent = await message.reply_text(f"{PE_INDIA} ɪɴᴅɪᴀɴ ᴍᴏʙɪʟᴇ ɴᴜᴍʙᴇʀ\n<i>9876543210, 8123456789</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(sent))
            return
        
        elif txt == f"{PE_CARD} ᴀᴀᴅʜᴀʀ ɪɴꜰᴏ":
            if not s.get("aadhaar_enabled", True):
                sent = await message.reply_text(f"{PE_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(sent))
                return
            maint, msg = check_feature_maintenance("aadhaar")
            if maint:
                sent = await message.reply_text(f"{PE_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(sent))
                return
            ADMIN_STATE[uid] = 'AADHAAR'
            sent = await message.reply_text(f"{PE_CARD} ᴀᴀᴅʜᴀʀ ɴᴜᴍʙᴇʀ\n<i>123456789012</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(sent))
            return
        
        elif txt == f"{PE_CAR} ʀᴄ ᴅᴇᴛᴀɪʟꜱ":
            if not s.get("rc_enabled", True):
                sent = await message.reply_text(f"{PE_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(sent))
                return
            maint, msg = check_feature_maintenance("rc")
            if maint:
                sent = await message.reply_text(f"{PE_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(sent))
                return
            ADMIN_STATE[uid] = 'VEHICLE'
            sent = await message.reply_text(f"{PE_CAR} ᴠᴇʜɪᴄʟᴇ ɴᴜᴍʙᴇʀ\n<i>KA01AB3256, DL1CX1234</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(sent))
            return
        
        elif txt == f"{PE_CARD} ɢꜱᴛ ʟᴏᴏᴋᴜᴘ":
            if not s.get("gst_enabled", True):
                sent = await message.reply_text(f"{PE_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(sent))
                return
            maint, msg = check_feature_maintenance("gst")
            if maint:
                sent = await message.reply_text(f"{PE_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(sent))
                return
            ADMIN_STATE[uid] = 'GST'
            sent = await message.reply_text(f"{PE_CARD} ɢꜱᴛ ɴᴜᴍʙᴇʀ\n<i>19BOKPS7056D1ZI</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(sent))
            return
        
        elif txt == f"{PE_PAK} ᴘᴀᴋ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ":
            if not s.get("pak_enabled", True):
                sent = await message.reply_text(f"{PE_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(sent))
                return
            maint, msg = check_feature_maintenance("pak")
            if maint:
                sent = await message.reply_text(f"{PE_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(sent))
                return
            ADMIN_STATE[uid] = 'PAK'
            sent = await message.reply_text(f"{PE_PAK} ᴘᴀᴋɪꜱᴛᴀɴ ɴᴜᴍʙᴇʀ\n<i>923078750447</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(sent))
            return
        
        elif txt == f"{PE_PHONE2} ɪɴᴅ ɴᴜᴍ ɪɴꜰᴏ 𝟸":
            if not s.get("indnum_enabled", True):
                sent = await message.reply_text(f"{PE_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(sent))
                return
            maint, msg = check_feature_maintenance("indnum")
            if maint:
                sent = await message.reply_text(f"{PE_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(sent))
                return
            ADMIN_STATE[uid] = 'INDNUM'
            sent = await message.reply_text(f"{PE_PHONE2} ᴀᴅᴠᴀɴᴄᴇᴅ ɴᴜᴍʙᴇʀ\n<i>6363016966, 9876543210</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(sent))
            return
        
        elif txt == f"{PE_INDIA} ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ 𝟹":
            if not s.get("indnum3_enabled", True):
                sent = await message.reply_text(f"{PE_DISABLED} Disabled", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(sent))
                return
            maint, msg = check_feature_maintenance("indnum3")
            if maint:
                sent = await message.reply_text(f"{PE_TOOLS} {msg}", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(sent))
                return
            ADMIN_STATE[uid] = 'INDNUM3'
            sent = await message.reply_text(f"{PE_INDIA} ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴛʀᴀᴄᴋɪɴɢ\n<i>6363016966, 9876543210</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(sent))
            return
        
        elif txt == f"{PE_INVITE} ɪɴᴠɪᴛᴇ & ᴇᴀʀɴ":
            user = get_user(uid)
            bot_info = await app.get_me()
            link = f"https://t.me/{bot_info.username}?start={user['invite_code']}"
            sent = await message.reply_text(f"{PE_INVITE} ɪɴᴠɪᴛᴇ (+{INVITE_CREDITS}ᴄʀ)\n<code>{link}</code>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(sent, 120))
            return
        
        elif txt == f"{PE_TICKET} ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ":
            ADMIN_STATE[uid] = 'REDEEM'
            sent = await message.reply_text(f"{PE_TICKET} ᴇɴᴛᴇʀ ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ:\n<i>HEX-XXXXXXXXXX</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(sent, 30))
            return
        
        elif txt == f"{PE_HELP} ʜᴇʟᴘ":
            await show_help_inline(message)
            return
        
        elif txt == f"{PE_ABOUT} ᴀʙᴏᴜᴛ":
            await show_about_inline(message)
            return
        
        elif txt == f"{PE_STATS} ꜱᴛᴀᴛꜱ":
            await show_stats_inline(message)
            return
        
        elif txt == f"{PE_IDENTITY} ɪᴅᴇɴᴛɪᴛʏ ᴛᴏᴏʟꜱ":
            sent = await message.reply_text(f"{PE_IDENTITY} <b>ɪᴅᴇɴᴛɪᴛʏ ᴛᴏᴏʟꜱ</b>\n\n{PE_CARD} ᴀᴀᴅʜᴀʀ ɪɴꜰᴏ\n{PE_USER} ᴘᴀɴ ᴄᴀʀᴅ ɪɴꜰᴏ\n{PE_PHONE2} ᴍᴏʙɪʟᴇ ɴᴜᴍʙᴇʀ ʟᴏᴏᴋᴜᴘ", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(sent, 30))
            return
        
        elif txt == f"{PE_OSINT} ᴏꜱɪɴᴛ ᴛᴏᴏʟꜱ":
            sent = await message.reply_text(f"{PE_OSINT} <b>ᴏꜱɪɴᴛ ᴛᴏᴏʟꜱ</b>\n\n{PE_SEARCH} ᴛɢ ɪᴅ ʟᴏᴏᴋᴜᴘ\n{PE_LINK} ʟɪɴᴋ ʙʏᴘᴀꜱꜱ\n{PE_NETWORK} ɪᴘ ʟᴏᴏᴋᴜᴘ", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(sent, 30))
            return
        
        elif txt == f"{PE_VIP} ᴠɪᴘ ᴘʀᴇᴍɪᴜᴍ":
            sent = await message.reply_text(f"{PE_VIP} <b>ᴠɪᴘ ᴘʀᴇᴍɪᴜᴍ</b>\n\n{PE_CREDIT} ᴇxᴛʀᴀ ᴄʀᴇᴅɪᴛꜱ\n{PE_ROCKET} ᴘʀɪᴏʀɪᴛʏ Qᴜᴇʀɪᴇꜱ\n{PE_STAR} ᴀᴄᴄᴇꜱꜱ ᴛᴏ ᴀʟʟ ꜰᴇᴀᴛᴜʀᴇꜱ", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(sent, 30))
            return
        
        elif txt == f"{PE_SPIN} ᴅᴀɪʟʏ ꜱᴘɪɴ":
            # Random spin reward
            rewards = [1, 2, 3, 5, 8, 10]
            reward = random.choice(rewards)
            bal = add_credits(uid, reward)
            sent = await message.reply_text(f"{PE_SPIN} 🎰 <b>ᴅᴀɪʟʏ ꜱᴘɪɴ</b>\n\n{PE_GIFT} ʏᴏᴜ ᴡᴏɴ <b>+{reward}</b> ᴄʀᴇᴅɪᴛꜱ!\n{PE_CREDIT} ɴᴇᴡ ʙᴀʟᴀɴᴄᴇ: <b>{bal}</b>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(sent, 30))
            return
        
        elif txt == f"{PE_DASHBOARD} ᴅᴀꜱʜʙᴏᴀʀᴅ":
            user = get_user(uid)
            txt = f"{PE_DASHBOARD} <b>ʏᴏᴜʀ ᴅᴀꜱʜʙᴏᴀʀᴅ</b>\n\n{PE_USER} <b>ᴜꜱᴇʀ:</b> {message.from_user.first_name}\n{PE_CREDIT} <b>ᴄʀᴇᴅɪᴛꜱ:</b> {user.get('credits',0)}\n{PE_SEARCH} <b>Qᴜᴇʀɪᴇꜱ:</b> {user.get('total_queries',0)}\n{PE_INVITE} <b>ɪɴᴠɪᴛᴇꜱ:</b> {user.get('invites',0)}"
            sent = await message.reply_text(txt, parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(sent, 30))
            return
        
        elif txt == f"{PE_LEADERBOARD} ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ":
            users = load_json(USERS_FILE)
            sorted_users = sorted(users.items(), key=lambda x: x[1].get('credits', 0), reverse=True)[:10]
            txt = f"{PE_LEADERBOARD} <b>ᴛᴏᴘ 10 ᴜꜱᴇʀꜱ</b>\n\n"
            for i, (uid, data) in enumerate(sorted_users, 1):
                try:
                    user = await app.get_users(int(uid))
                    name = user.first_name[:15]
                except:
                    name = f"ᴜꜱᴇʀ {i}"
                txt += f"{i}. {PE_USER} {name} - {PE_CREDIT} {data.get('credits',0)}\n"
            sent = await message.reply_text(txt, parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(sent, 30))
            return
        
        # If no match, show main menu
        await main_menu(message)
        
    except Exception as e:
        print(f"Message handler error: {e}")
        await main_menu(message)

async def show_help_inline(message: Message):
    text = f"""
{PE_HELP} 𝐇𝐄𝐋𝐏 & 𝐆𝐔𝐈𝐃𝐄 {PE_HELP}

{PE_STAR} 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄 𝐅𝐄𝐀𝐓𝐔𝐑𝐄𝐒:

{PE_PHONE} 𝐓𝐆 𝐈𝐃 ➜ 𝐍𝐔𝐌𝐁𝐄𝐑
Get phone number from Telegram ID

{PE_BANK} 𝐈𝐅𝐒𝐂 𝐈𝐍𝐅𝐎
Get bank details from IFSC code

{PE_LINK} 𝐋𝐈𝐍𝐊 𝐁𝐘𝐏𝐀𝐒𝐒
Bypass short links

{PE_CARD} 𝐀𝐀𝐃𝐇𝐀𝐑 𝐈𝐍𝐅𝐎
Get details from Aadhaar number

{PE_INDIA} 𝐈𝐍𝐃 𝐍𝐔𝐌𝐁𝐄𝐑 𝐈𝐍𝐅𝐎
Get Indian number details

{PE_CAR} 𝐑𝐂 𝐃𝐄𝐓𝐀𝐈𝐋𝐒
Get vehicle RC details

{PE_CARD} 𝐆𝐒𝐓 𝐋𝐎𝐎𝐊𝐔𝐏
Get business details from GST

{PE_PAK} 𝐏𝐀𝐊 𝐍𝐔𝐌𝐁𝐄𝐑 𝐈𝐍𝐅𝐎
Get Pakistan number details

{PE_GIFT} 𝐃𝐀𝐈𝐋𝐘 𝐅𝐑𝐄𝐄: +{DAILY_FREE_CREDITS} ᴄʀᴇᴅɪᴛꜱ

{PE_INVITE} 𝐈𝐍𝐕𝐈𝐓𝐄: +{INVITE_CREDITS} ᴄʀᴇᴅɪᴛꜱ ᴘᴇʀ ᴜꜱᴇʀ

{PE_CLOCK} 𝐀𝐔𝐓𝐎 𝐃𝐄𝐋𝐄𝐓𝐄: {AUTO_DELETE_TIME}ꜱ
"""
    sent = await message.reply_text(text, parse_mode=ParseMode.HTML)
    asyncio.create_task(schedule_delete(sent, 60))

async def show_about_inline(message: Message):
    text = f"""
{PE_ABOUT} 𝐀𝐁𝐎𝐔𝐓 𝐁𝐎𝐓 {PE_ABOUT}

𝐍𝐀𝐌𝐄: {BOT_NAME}
𝐔𝐒𝐄𝐑𝐍𝐀𝐌𝐄: @{BOT_USERNAME}
𝐕𝐄𝐑𝐒𝐈𝐎𝐍: 3.0

{PE_DIAMOND} 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐅𝐄𝐀𝐓𝐔𝐑𝐄𝐒

• Telegram ID Lookup
• IFSC Bank Details
• Link Bypass
• Aadhaar Info
• Mobile Number Tracking
• RC Details
• GST Lookup
• Pakistan Number Info
• Colored Inline Buttons

{PE_CROWN} 𝐃𝐄𝐕𝐄𝐋𝐎𝐏𝐄𝐃 𝐁𝐘: @Hexh4ckerOFC

{PE_WARN} 𝐅𝐎𝐑 𝐄𝐃𝐔𝐂𝐀𝐓𝐈𝐎𝐍𝐀𝐋 𝐏𝐔𝐑𝐏𝐎𝐒𝐄𝐒 𝐎𝐍𝐋𝐘
"""
    sent = await message.reply_text(text, parse_mode=ParseMode.HTML)
    asyncio.create_task(schedule_delete(sent, 60))

async def show_stats_inline(message: Message):
    users = load_json(USERS_FILE)
    total_users = len(users)
    total_queries = sum(u.get('total_queries', 0) for u in users.values())
    total_invites = sum(u.get('invites', 0) for u in users.values())
    total_credits = sum(u.get('credits', 0) for u in users.values())
    
    text = f"""
{PE_STATS} 𝐁𝐎𝐓 𝐒𝐓𝐀𝐓𝐈𝐒𝐓𝐈𝐂𝐒 {PE_STATS}

{PE_USER} 𝐓𝐎𝐓𝐀𝐋 𝐔𝐒𝐄𝐑𝐒: {total_users}
{PE_SEARCH} 𝐓𝐎𝐓𝐀𝐋 𝐐𝐔𝐄𝐑𝐈𝐄𝐒: {total_queries}
{PE_INVITE} 𝐓𝐎𝐓𝐀𝐋 𝐈𝐍𝐕𝐈𝐓𝐄𝐒: {total_invites}
{PE_CREDIT} 𝐓𝐎𝐓𝐀𝐋 𝐂𝐑𝐄𝐃𝐈𝐓𝐒: {total_credits}

{PE_DIAMOND} 𝐁𝐎𝐓 𝐒𝐓𝐀𝐓𝐔𝐒: 🟢 Active
"""
    sent = await message.reply_text(text, parse_mode=ParseMode.HTML)
    asyncio.create_task(schedule_delete(sent, 60))

async def run_query(message: Message, mode: str, query: str):
    if not await net_ok():
        sent = await message.reply_text(f"{PE_CROSS} No internet", parse_mode=ParseMode.HTML)
        asyncio.create_task(schedule_delete(sent))
        return
    
    st = await message.reply_text(f"{PE_GREEN} ꜱᴇᴀʀᴄʜɪɴɢ...", parse_mode=ParseMode.HTML)
    credit_deducted = False
    
    try:
        if mode in ['AADHAAR', 'MOBILE', 'VEHICLE']:
            raw = run_india_script({'AADHAAR':'2','MOBILE':'1','VEHICLE':'4'}[mode], query)
            if raw:
                records = parse_all_india_records(raw)
                result = format_records_result(records, {'AADHAAR':'aadhaar','MOBILE':'mobile','VEHICLE':'vehicle'}[mode])
                if records and f"{PE_CROSS}" not in str(result):
                    use_credit(message.from_user.id)
                    credit_deducted = True
            else:
                result = f"{PE_CROSS} Script failed"
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
                    result = f"{PE_CROSS}"
            
            if result and f"{PE_CROSS}" not in str(result) and "unavailable" not in str(result).lower():
                use_credit(message.from_user.id)
                credit_deducted = True
        
        user = get_user(message.from_user.id)
        final = f"{result}\n{SEP}\n{PE_CREDIT} {'ᴄʀ: '+str(user.get('credits',0)) if credit_deducted else 'ɴᴏ ᴄʀ ᴅᴇᴅᴜᴄᴛᴇᴅ'} | {PE_CLOCK} {AUTO_DELETE_TIME}ꜱ{DISCLAIMER}{FOOTER}"
        sent = await st.edit_text(final, parse_mode=ParseMode.HTML)
        asyncio.create_task(schedule_delete(sent))
    except Exception as e:
        print(f"Query error: {e}")
        try:
            await st.edit_text(f"{PE_WARN} ᴇʀʀᴏʀ{FOOTER}", parse_mode=ParseMode.HTML)
        except: pass

# --- 🚀 MAIN ---

def main():
    print("🔄 Hex Terminal Premium Starting...")
    print("🎨 100% Premium Emojis Only - No Normal Emojis!")
    print("🤖 Kurigram Version with Full Keyboard + Colored Buttons!")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4"], capture_output=True, timeout=30)
    except: pass
    
    print(f"✅ {BOT_NAME} Ready!")
    print(f"💎 All emojis are PREMIUM only!")
    print(f"⭐ 2 Page Keyboard Menu with Premium Emojis")
    print("🚀 Bot is running...")
    
    app.run()

if __name__ == '__main__':
    main()