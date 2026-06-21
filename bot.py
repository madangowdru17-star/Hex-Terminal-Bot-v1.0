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

CHANNEL_1_ID = int(os.environ.get('CHANNEL_1_ID', '-1003240507339'))
CHANNEL_2_ID = int(os.environ.get('CHANNEL_2_ID', '-1003806004135'))

LINK_1 = os.environ.get('LINK_1', 'https://t.me/+dP7xLb3AoE1jNmRl')
LINK_2 = os.environ.get('LINK_2', 'https://t.me/+9vuPcr9LJ8piODdl')

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
# PREMIUM EMOJI IDs FOR ALL BUTTONS (Colored Inline Buttons)
# ============================================================

# Color Styles with Premium Emoji IDs (Kurigram/Pyrogram style)
BUTTON_STYLES = {
    "primary": {
        "emoji_id": "5258096772776991776",
        "style": ButtonStyle.PRIMARY,
        "color": "🔵"
    },
    "success": {
        "emoji_id": "5258503720928288433",
        "style": ButtonStyle.SUCCESS,
        "color": "🟢"
    },
    "danger": {
        "emoji_id": "5258331647358540449",
        "style": ButtonStyle.DANGER,
        "color": "🔴"
    },
    "warning": {
        "emoji_id": "5258478058097409351",
        "style": None,
        "color": "🟡"
    },
    "info": {
        "emoji_id": "5258024981144066782",
        "style": None,
        "color": "🔵"
    }
}

# Premium Emoji IDs for Button Icons
PREMIUM_EMOJI_IDS = {
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
    "search": "5231012545799666522",
    "magnify": "5258024981144066782",
    "crown": "6267128480601741166",
    "diamond": "6264791387032523779",
    "star": "6266969287638913443",
    "gift": "5203996991054432397",
    "fire": "6264785189394717307",
    "tools": "5462921117423384478",
    "disabled": "5373165973203348165",
    "location": "5391032818111363540",
    "home": "5280955052582785391",
    "state": "5388927107315283144",
    "network": "5321141214735508486",
    "signal": "6147892053796725336",
    "sim": "5800717980266403037",
    "chart": "6093382540784046658",
    "check": "6267008582294705964",
    "cross": "6267000941547885720",
    "lock": "5316522278056399236",
    "warn": "6267039884016358504",
    "rocket": "5195033767969839232",
    "sparkle": "5467683093693354332",
    "help": "5244933196230972438",
    "about": "5285515895534278367",
    "stats": "6093382540784046658",
    "admin": "6267128480601741166",
    "earn": "6267068789146260253",
    "redeem": "5285515895534278367"
}

# --- PREMIUM EMOJIS FOR TEXT MESSAGES ---
def get_pe(eid, fallback):
    return f'<tg-emoji emoji-id="{eid}">{fallback}</tg-emoji>'

EMOJI_WARN = get_pe("6267039884016358504", "⚠️")
EMOJI_CHECK = get_pe("6267008582294705964", "✅")
EMOJI_CROSS = get_pe("6267000941547885720", "❌")
EMOJI_LOCK = get_pe("5316522278056399236", "🔒")
EMOJI_CROWN = get_pe("6267128480601741166", "👑")
EMOJI_DIAMOND = get_pe("6264791387032523779", "💎")
EMOJI_STAR = get_pe("6266969287638913443", "⭐")
EMOJI_GIFT = get_pe("5203996991054432397", "🎁")
EMOJI_FIRE = get_pe("6264785189394717307", "🔥")
EMOJI_SEARCH = get_pe("5231012545799666522", "🔍")
EMOJI_PHONE = get_pe("5947494995798789024", "📞")
EMOJI_BANK = get_pe("5264895611517300926", "🏦")
EMOJI_LINK = get_pe("5271604874419647061", "🔗")
EMOJI_CAR = get_pe("5253752975997803460", "🚘")
EMOJI_CARD = get_pe("5260561650213220533", "🪪")
EMOJI_USER = get_pe("5249053508681883137", "👤")
EMOJI_INDIA = get_pe("6284779941489812433", "🇮🇳")
EMOJI_PAK = get_pe("5913705895375672082", "🇵🇰")
EMOJI_PHONE2 = get_pe("5406809207947142040", "📲")
EMOJI_INVITE = get_pe("5244933196230972438", "👥")
EMOJI_TICKET = get_pe("5285515895534278367", "🎫")
EMOJI_CREDIT = get_pe("6267068789146260253", "💰")
EMOJI_REFRESH = get_pe("5375338737028841420", "🔄")
EMOJI_CLOCK = get_pe("5382194935057372936", "⏱")
EMOJI_BOLT = get_pe("6284971355297290197", "⚡")
EMOJI_GREEN = get_pe("5386367538735104399", "🟩")
EMOJI_SPARKLE = get_pe("5467683093693354332", "✨")
EMOJI_ROCKET = get_pe("5195033767969839232", "🚀")
EMOJI_TOOLS = get_pe("5462921117423384478", "🛠️")
EMOJI_DISABLED = get_pe("5373165973203348165", "📴")
EMOJI_FATHER = get_pe("6147864334077794239", "👨")
EMOJI_LOCATION = get_pe("5391032818111363540", "📍")
EMOJI_HOME = get_pe("5280955052582785391", "🏠")
EMOJI_STATE = get_pe("5388927107315283144", "🏛")
EMOJI_NETWORK = get_pe("5321141214735508486", "📡")
EMOJI_SIGNAL = get_pe("6147892053796725336", "📶")
EMOJI_SIM = get_pe("5800717980266403037", "💳")
EMOJI_CHART = get_pe("6093382540784046658", "📊")
EMOJI_HELP = get_pe("5244933196230972438", "❓")
EMOJI_ABOUT = get_pe("5285515895534278367", "ℹ️")
EMOJI_STATS = get_pe("6093382540784046658", "📊")

DISCLAIMER = f"\n\n{EMOJI_WARN} ᴅɪꜱᴄʟᴀɪᴍᴇʀ:\nᴇᴅᴜᴄᴀᴛɪᴏɴᴀʟ ᴘᴜʀᴘᴏꜱᴇꜱ ᴏɴʟʏ. ᴜꜱᴇ ʀᴇꜱᴘᴏɴꜱɪʙʟʏ."

# --- Initialize Bot ---
app = Client(
    "hex_terminal_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

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

async def check_channels(uid):
    try:
        m1 = await app.get_chat_member(CHANNEL_1_ID, uid)
        m2 = await app.get_chat_member(CHANNEL_2_ID, uid)
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

def check_feature_maintenance(feature_key):
    s = get_settings()
    if s.get(f"maint_{feature_key}", False):
        return True, s.get(f"maint_msg_{feature_key}", f"{EMOJI_TOOLS} Under maintenance.")
    return False, ""

# ============================================================
# CREATE COLORED INLINE BUTTONS WITH PREMIUM EMOJIS
# ============================================================

def create_colored_button(text: str, callback_data: str = None, url: str = None, color: str = "primary", icon_emoji_id: str = None):
    """
    Create a colored inline button with premium emoji icon
    Colors: "primary" (blue), "success" (green), "danger" (red)
    """
    style_info = BUTTON_STYLES.get(color, BUTTON_STYLES["primary"])
    emoji_id = icon_emoji_id or style_info["emoji_id"]
    style = style_info["style"]
    
    # For Kurigram, use icon_custom_emoji_id and style
    try:
        return InlineKeyboardButton(
            text=text,
            callback_data=callback_data,
            url=url,
            icon_custom_emoji_id=emoji_id,
            style=style
        )
    except:
        try:
            return InlineKeyboardButton(
                text=text,
                callback_data=callback_data,
                url=url,
                icon_custom_emoji_id=emoji_id
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
# MAIN MENU WITH COLORED INLINE BUTTONS
# ============================================================

async def show_verification_page(message: Message):
    try:
        bot_info = await app.get_me()
        caption = (
            f"{EMOJI_DIAMOND} {BOT_NAME} {EMOJI_DIAMOND}\n"
            f"@{BOT_USERNAME}\n\n"
            f"{EMOJI_LOCK} ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ʀᴇQᴜɪʀᴇᴅ\n"
            f"ᴊᴏɪɴ ʙᴏᴛʜ ᴄʜᴀɴɴᴇʟꜱ ᴛᴏ ᴜɴʟᴏᴄᴋ\n\n"
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
    
    # Colored verification buttons with premium emojis
    buttons = [
        create_styled_row([
            {"text": "📢 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 𝟷", "url": LINK_1, "color": "primary", "icon_emoji_id": PREMIUM_EMOJI_IDS["link"]}
        ]),
        create_styled_row([
            {"text": "📢 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 𝟸", "url": LINK_2, "color": "primary", "icon_emoji_id": PREMIUM_EMOJI_IDS["link"]}
        ]),
        create_styled_row([
            {"text": "✅ ɪ'ᴠᴇ ᴊᴏɪɴᴇᴅ - ᴠᴇʀɪꜰʏ", "callback_data": "verify", "color": "success", "icon_emoji_id": PREMIUM_EMOJI_IDS["check"]}
        ])
    ]
    
    flat_buttons = []
    for row in buttons:
        flat_buttons.append(row)
    
    sent2 = await message.reply_text(
        f"{EMOJI_LOCK} ᴊᴏɪɴ ʙᴏᴛʜ ᴄʜᴀɴɴᴇʟꜱ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴠᴇʀɪꜰʏ",
        reply_markup=InlineKeyboardMarkup(flat_buttons),
        parse_mode=ParseMode.HTML
    )
    asyncio.create_task(schedule_delete(sent2, 120))

async def main_menu(message: Message):
    """Main menu with colored inline buttons and premium emojis"""
    is_admin = message.from_user.id == ADMIN_ID
    user = get_user(message.from_user.id)
    s = get_settings()
    cr = user.get("credits", 0)
    
    # Build colored inline buttons
    kb = []
    
    # Row 1: TG ID & IFSC
    row1 = []
    if s.get("tgid_enabled", True):
        row1.append({"text": f"{EMOJI_PHONE} ᴛɢ ɪᴅ ➜ {EMOJI_PHONE2} ɴᴜᴍʙᴇʀ {EMOJI_SEARCH}", "callback_data": "menu_tgid", "color": "primary", "icon_emoji_id": PREMIUM_EMOJI_IDS["phone"]})
    if s.get("ifsc_enabled", True):
        row1.append({"text": f"{EMOJI_BANK} ɪꜰꜱᴄ ɪɴꜰᴏ➜{EMOJI_SEARCH}", "callback_data": "menu_ifsc", "color": "info", "icon_emoji_id": PREMIUM_EMOJI_IDS["bank"]})
    if row1:
        kb.append(create_styled_row(row1))
    
    # Row 2: Link Bypass
    if s.get("bypass_enabled", True):
        kb.append(create_styled_row([
            {"text": f"{EMOJI_LINK} ʟɪɴᴋ ʙʏᴘᴀꜱꜱ", "callback_data": "menu_bypass", "color": "warning", "icon_emoji_id": PREMIUM_EMOJI_IDS["link"]}
        ]))
    
    # Row 3: Aadhaar & India Number
    row2 = []
    if s.get("aadhaar_enabled", True):
        row2.append({"text": f"{EMOJI_CARD} ᴀᴀᴅʜᴀʀ ɪɴꜰᴏ➜{EMOJI_USER}", "callback_data": "menu_aadhaar", "color": "primary", "icon_emoji_id": PREMIUM_EMOJI_IDS["card"]})
    if s.get("mobile_enabled", True):
        row2.append({"text": f"{EMOJI_INDIA} ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ➜{EMOJI_USER}", "callback_data": "menu_mobile", "color": "success", "icon_emoji_id": PREMIUM_EMOJI_IDS["india"]})
    if row2:
        kb.append(create_styled_row(row2))
    
    # Row 4: RC & GST
    row3 = []
    if s.get("rc_enabled", True):
        row3.append({"text": f"{EMOJI_CAR} ʀᴄ ᴅᴇᴛᴀɪʟꜱ", "callback_data": "menu_rc", "color": "info", "icon_emoji_id": PREMIUM_EMOJI_IDS["car"]})
    if s.get("gst_enabled", True):
        row3.append({"text": f"{EMOJI_CARD} ɢꜱᴛ ʟᴏᴏᴋᴜᴘ", "callback_data": "menu_gst", "color": "warning", "icon_emoji_id": PREMIUM_EMOJI_IDS["card"]})
    if row3:
        kb.append(create_styled_row(row3))
    
    # Row 5: Pakistan & India Num 2
    row4 = []
    if s.get("pak_enabled", True):
        row4.append({"text": f"{EMOJI_PAK} ᴘᴀᴋ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ", "callback_data": "menu_pak", "color": "primary", "icon_emoji_id": PREMIUM_EMOJI_IDS["pak"]})
    if s.get("indnum_enabled", True):
        row4.append({"text": f"{EMOJI_PHONE2} ɪɴᴅ ɴᴜᴍ ɪɴꜰᴏ 𝟸", "callback_data": "menu_indnum", "color": "success", "icon_emoji_id": PREMIUM_EMOJI_IDS["phone2"]})
    if row4:
        kb.append(create_styled_row(row4))
    
    # Row 6: India Number 3
    if s.get("indnum3_enabled", True):
        kb.append(create_styled_row([
            {"text": f"{EMOJI_INDIA} ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ 𝟹 ➜{EMOJI_USER}", "callback_data": "menu_indnum3", "color": "danger", "icon_emoji_id": PREMIUM_EMOJI_IDS["india"]}
        ]))
    
    # Row 7: Invite & Redeem
    kb.append(create_styled_row([
        {"text": f"{EMOJI_INVITE} ɪɴᴠɪᴛᴇ & ᴇᴀʀɴ", "callback_data": "menu_invite", "color": "success", "icon_emoji_id": PREMIUM_EMOJI_IDS["invite"]},
        {"text": f"{EMOJI_TICKET} ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ", "callback_data": "menu_redeem", "color": "warning", "icon_emoji_id": PREMIUM_EMOJI_IDS["ticket"]}
    ]))
    
    # Row 8: Help & About
    kb.append(create_styled_row([
        {"text": f"{EMOJI_HELP} ʜᴇʟᴘ", "callback_data": "menu_help", "color": "info", "icon_emoji_id": PREMIUM_EMOJI_IDS["help"]},
        {"text": f"{EMOJI_ABOUT} ᴀʙᴏᴜᴛ", "callback_data": "menu_about", "color": "primary", "icon_emoji_id": PREMIUM_EMOJI_IDS["about"]}
    ]))
    
    # Row 9: Stats
    kb.append(create_styled_row([
        {"text": f"{EMOJI_STATS} ꜱᴛᴀᴛꜱ", "callback_data": "menu_stats", "color": "info", "icon_emoji_id": PREMIUM_EMOJI_IDS["stats"]}
    ]))
    
    # Admin buttons
    if is_admin:
        kb.append(create_styled_row([
            {"text": f"{EMOJI_CROWN} ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ", "callback_data": "menu_admin", "color": "danger", "icon_emoji_id": PREMIUM_EMOJI_IDS["admin"]}
        ]))
    
    flat_kb = []
    for row in kb:
        flat_kb.append(row)
    
    markup = InlineKeyboardMarkup(flat_kb)
    
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
        f"{EMOJI_STAR} ꜱᴇʟᴇᴄᴛ ᴀ ꜱᴇʀᴠɪᴄᴇ ʙᴇʟᴏᴡ {EMOJI_STAR}"
    )
    
    sent = await message.reply_text(txt, reply_markup=markup, parse_mode=ParseMode.HTML)
    asyncio.create_task(schedule_delete(sent, AUTO_DELETE_TIME))

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
            result = f"{EMOJI_SPARKLE} {EMOJI_PHONE} ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ ɪɴꜰᴏ {EMOJI_SPARKLE}\n"
            if d.get('chat_id') or d.get('userid'): result += f"{EMOJI_SEARCH} ᴄʜᴀᴛ ɪᴅ: <code>{d.get('chat_id', d.get('userid', query))}</code>\n"
            if d.get('number'): result += f"{EMOJI_PHONE2} ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ: <code>{d['number']}</code>\n"
            if d.get('name'): result += f"{EMOJI_USER} ᴘʀᴏꜰɪʟᴇ ɴᴀᴍᴇ: <code>{d['name']}</code>\n"
            return result
    return f"{EMOJI_CROSS} ɴᴏᴛ ꜰᴏᴜɴᴅ"

async def ifsc_lookup(session, code):
    data = await safe_api_fetch(session, f"{IFSC_API}{code.upper()}")
    if not data or isinstance(data, dict) and data.get("raw_text"): return f"{EMOJI_CROSS} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"
    if isinstance(data, dict):
        return (f"{EMOJI_SPARKLE} {EMOJI_BANK} ʙᴀɴᴋ ɪꜰꜱᴄ ᴅᴇᴛᴀɪʟꜱ {EMOJI_SPARKLE}\n"
                f"{EMOJI_BANK} ʙᴀɴᴋ ɴᴀᴍᴇ: <code>{data.get('BANK','N/A')}</code>\n"
                f"{EMOJI_LOCATION} ʙʀᴀɴᴄʜ: <code>{data.get('BRANCH','N/A')}</code>\n"
                f"{EMOJI_CARD} ɪꜰꜱᴄ ᴄᴏᴅᴇ: <code>{data.get('IFSC',code.upper())}</code>\n"
                f"{EMOJI_LOCATION} ᴀᴅᴅʀᴇꜱꜱ: <code>{data.get('ADDRESS','N/A')}</code>")
    return f"{EMOJI_CROSS} ɪɴᴠᴀʟɪᴅ ᴄᴏᴅᴇ"

async def bypass_lookup(session, link):
    s = get_settings()
    if s.get("bypass_maintenance",False): return f"{EMOJI_TOOLS} ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ"
    data = await safe_api_fetch(session, f"{SHORTLINK_API}{link}", timeout=20)
    if not data or isinstance(data, dict) and data.get("raw_text"): return f"{EMOJI_CROSS} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"
    if isinstance(data, dict):
        r = data.get('bypassed_url') or data.get('url') or str(data)
        return f"{EMOJI_SPARKLE} {EMOJI_LINK} ʟɪɴᴋ ʙʏᴘᴀꜱꜱᴇᴅ {EMOJI_SPARKLE}\n{EMOJI_LINK} ᴏʀɪɢɪɴᴀʟ ᴜʀʟ: <code>{str(r)}</code>"
    return f"{EMOJI_LINK} ʀᴇꜱᴜʟᴛ: <code>{str(data)}</code>"

async def gst_lookup(session, gst_number):
    data = await safe_api_fetch(session, f"{GST_API}{gst_number.upper()}", timeout=20)
    if not data or isinstance(data, dict) and data.get("raw_text"): return f"{EMOJI_CROSS} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"
    if isinstance(data, dict) and data.get("status") == "success" and data.get("data"):
        d = data["data"]
        result = f"{EMOJI_SPARKLE} {EMOJI_CARD} ɢꜱᴛ ʙᴜꜱɪɴᴇꜱꜱ ɪɴꜰᴏ {EMOJI_SPARKLE}\n"
        if d.get('TradeName'): result += f"{EMOJI_BANK} ʙᴜꜱɪɴᴇꜱꜱ ɴᴀᴍᴇ: <code>{d['TradeName']}</code>\n"
        if d.get('Gstin'): result += f"{EMOJI_CARD} ɢꜱᴛ ɴᴜᴍʙᴇʀ: <code>{d['Gstin']}</code>\n"
        return result
    return f"{EMOJI_CROSS} ɪɴᴠᴀʟɪᴅ ɢꜱᴛ"

async def pakistan_lookup(session, number):
    try:
        data = await safe_api_fetch(session, f"{PAK_API}{number}", timeout=20)
        if not data or isinstance(data, dict) and data.get("raw_text"): return f"{EMOJI_CROSS} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"
        if isinstance(data, dict) and data.get("success") and data.get("data"):
            valid = [r for r in data["data"] if isinstance(r, dict) and any(r.get(k) for k in ['name','number','cnic','address'])]
            if not valid: return f"{EMOJI_CROSS} ɴᴏ ᴅᴀᴛᴀ"
            result = f"{EMOJI_SPARKLE} {EMOJI_PAK} ᴘᴀᴋɪꜱᴛᴀɴ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ {EMOJI_SPARKLE}\n"
            for i, r in enumerate(valid[:3], 1):
                if len(valid) > 1: result += f"\n━━ {EMOJI_USER} ʀᴇᴄᴏʀᴅ {i} ━━\n"
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
    result = f"{EMOJI_SPARKLE} {EMOJI_PHONE2} ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴀᴅᴠᴀɴᴄᴇᴅ {EMOJI_SPARKLE}\n{EMOJI_PHONE2} ɴᴜᴍʙᴇʀ: <code>{number}</code>\n"
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
                    result = f"{EMOJI_SPARKLE} {EMOJI_INDIA} ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴛʀᴀᴄᴋɪɴɢ {EMOJI_SPARKLE}\n{EMOJI_PHONE2} ɴᴜᴍʙᴇʀ: <code>{number}</code>\n"
                    for k, v in data.items():
                        if v and str(v).strip():
                            result += f"{EMOJI_SEARCH} {k}: <code>{str(v)[:200]}</code>\n"
                    return result
            except: pass
            clean = re.sub(r'<[^>]+>', '\n', text)
            lines = [l.strip() for l in clean.split('\n') if l.strip() and len(l.strip()) > 1]
            result = f"{EMOJI_SPARKLE} {EMOJI_INDIA} ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴛʀᴀᴄᴋɪɴɢ {EMOJI_SPARKLE}\n{EMOJI_PHONE2} ɴᴜᴍʙᴇʀ: <code>{number}</code>\n"
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
    if not records: return f"{EMOJI_CROSS} ɴᴏ ʀᴇᴄᴏʀᴅꜱ ꜰᴏᴜɴᴅ"
    title = {'aadhaar':f'{EMOJI_CARD} ᴀᴀᴅʜᴀʀ','mobile':f'{EMOJI_INDIA} ɪɴᴅ ɴᴜᴍʙᴇʀ','vehicle':f'{EMOJI_CAR} ᴠᴇʜɪᴄʟᴇ'}.get(search_type, f'{EMOJI_CHART} ʀᴇꜱᴜʟᴛ')
    result = f"{EMOJI_SPARKLE} {title} {EMOJI_SPARKLE}\n{EMOJI_CHART} ᴛᴏᴛᴀʟ ʀᴇᴄᴏʀᴅꜱ: {len(records)}\n"
    for i, record in enumerate(records, 1):
        if len(records) > 1: result += f"\n━━ {EMOJI_USER} ʀᴇᴄᴏʀᴅ {i} ━━\n"
        for key, value in record.items(): result += f"{key}: <code>{value}</code>\n"
    return result

# --- 👑 ADMIN ---

async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID: return
    s = get_settings()
    ms = lambda key: "🔴" if s.get(f"maint_{key}") else "🟢"
    
    kb = [
        create_styled_row([
            {"text": "🎫 ɢᴇɴ ᴄᴏᴅᴇ", "callback_data": "ad_gen", "color": "success", "icon_emoji_id": PREMIUM_EMOJI_IDS["ticket"]},
            {"text": "📋 ᴄᴏᴅᴇꜱ", "callback_data": "ad_codes", "color": "info", "icon_emoji_id": PREMIUM_EMOJI_IDS["ticket"]}
        ]),
        create_styled_row([
            {"text": "🎁 ᴀᴅᴅ ᴄʀ", "callback_data": "ad_credit", "color": "warning", "icon_emoji_id": PREMIUM_EMOJI_IDS["gift"]},
            {"text": "📢 ʙᴄᴀꜱᴛ", "callback_data": "ad_bcast", "color": "primary", "icon_emoji_id": PREMIUM_EMOJI_IDS["bolt"]}
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
    
    flat_kb = []
    for row in kb:
        flat_kb.append(row)
    
    txt = f"{EMOJI_CROWN} ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ {EMOJI_CROWN}\n{EMOJI_INVITE} ᴜꜱᴇʀꜱ: {len(load_json(USERS_FILE))} | {EMOJI_TICKET} ᴄᴏᴅᴇꜱ: {len(load_json(REDEEM_FILE))}"
    
    if hasattr(message, 'edit_text'):
        await message.edit_text(txt, reply_markup=InlineKeyboardMarkup(flat_kb), parse_mode=ParseMode.HTML)
    else:
        await message.reply_text(txt, reply_markup=InlineKeyboardMarkup(flat_kb), parse_mode=ParseMode.HTML)

# --- 🚀 HELP, ABOUT, STATS ---

async def show_help_inline(callback_query: CallbackQuery):
    await callback_query.answer()
    text = f"""
{EMOJI_HELP} 𝐇𝐄𝐋𝐏 & 𝐆𝐔𝐈𝐃𝐄 {EMOJI_HELP}

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
"""
    await callback_query.message.edit_text(text, parse_mode=ParseMode.HTML)
    await asyncio.sleep(60)
    try: await callback_query.message.delete()
    except: pass

async def show_about_inline(callback_query: CallbackQuery):
    await callback_query.answer()
    text = f"""
{EMOJI_ABOUT} 𝐀𝐁𝐎𝐔𝐓 𝐁𝐎𝐓 {EMOJI_ABOUT}

𝐍𝐀𝐌𝐄: {BOT_NAME}
𝐔𝐒𝐄𝐑𝐍𝐀𝐌𝐄: @{BOT_USERNAME}
𝐕𝐄𝐑𝐒𝐈𝐎𝐍: 3.0

{EMOJI_DIAMOND} 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐅𝐄𝐀𝐓𝐔𝐑𝐄𝐒

• Telegram ID Lookup
• IFSC Bank Details
• Link Bypass
• Aadhaar Info
• Mobile Number Tracking
• RC Details
• GST Lookup
• Pakistan Number Info
• Colored Inline Buttons 🎨

{EMOJI_CROWN} 𝐃𝐄𝐕𝐄𝐋𝐎𝐏𝐄𝐃 𝐁𝐘: @Hexh4ckerOFC

{EMOJI_WARN} 𝐅𝐎𝐑 𝐄𝐃𝐔𝐂𝐀𝐓𝐈𝐎𝐍𝐀𝐋 𝐏𝐔𝐑𝐏𝐎𝐒𝐄𝐒 𝐎𝐍𝐋𝐘
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
{EMOJI_STATS} 𝐁𝐎𝐓 𝐒𝐓𝐀𝐓𝐈𝐒𝐓𝐈𝐂𝐒 {EMOJI_STATS}

{EMOJI_USER} 𝐓𝐎𝐓𝐀𝐋 𝐔𝐒𝐄𝐑𝐒: {total_users}
{EMOJI_SEARCH} 𝐓𝐎𝐓𝐀𝐋 𝐐𝐔𝐄𝐑𝐈𝐄𝐒: {total_queries}
{EMOJI_INVITE} 𝐓𝐎𝐓𝐀𝐋 𝐈𝐍𝐕𝐈𝐓𝐄𝐒: {total_invites}
{EMOJI_CREDIT} 𝐓𝐎𝐓𝐀𝐋 𝐂𝐑𝐄𝐃𝐈𝐓𝐒: {total_credits}

{EMOJI_DIAMOND} 𝐁𝐎𝐓 𝐒𝐓𝐀𝐓𝐔𝐒: 🟢 Active
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
                    try: await app.send_message(chat_id=int(inviter), text=f"{EMOJI_GIFT} +{cr} ᴄʀᴇᴅɪᴛꜱ! ɴᴇᴡ ᴜꜱᴇʀ ᴊᴏɪɴᴇᴅ!")
                    except: pass
                    break
        user = get_user(uid)
        if not user.get("verified"):
            if await check_channels(uid):
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
    
    # Verification
    if data == "verify":
        if await check_channels(uid):
            user = get_user(uid)
            user["verified"] = True
            save_user(uid, user)
            await callback_query.answer("✅ Verified!", show_alert=True)
            try: await callback_query.message.delete()
            except: pass
            await main_menu(callback_query.message)
        else:
            await callback_query.answer("❌ Join both channels!", show_alert=True)
        return
    
    # Admin callbacks
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
            txt = f"{EMOJI_TICKET} ᴄᴏᴅᴇꜱ: {len(codes)}\n"
            for c, v in list(codes.items())[-15:]:
                txt += f"{'✅' if not v.get('used') else '❌'} <code>{c}</code> | {v.get('credits')}cr\n"
            await callback_query.message.edit_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
            await callback_query.answer()
            return
        elif data == "ad_gen":
            ADMIN_STATE[uid] = "gen"
            await callback_query.message.edit_text(f"{EMOJI_TICKET} ᴇɴᴛᴇʀ ᴄʀᴇᴅɪᴛꜱ:\n<i>100</i>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
            await callback_query.answer()
            return
        elif data == "ad_credit":
            ADMIN_STATE[uid] = "credit"
            await callback_query.message.edit_text(f"{EMOJI_GIFT} ᴇɴᴛᴇʀ ɪᴅ ᴀᴍᴏᴜɴᴛ:\n<i>123456789 50</i>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
            await callback_query.answer()
            return
        elif data == "ad_bcast":
            ADMIN_STATE[uid] = "bcast"
            await callback_query.message.edit_text(f"{EMOJI_BOLT} ᴇɴᴛᴇʀ ᴍᴇꜱꜱᴀɢᴇ:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
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
    
    # Menu callbacks
    if data.startswith("menu_"):
        # Check verification first
        user = get_user(uid)
        if not user.get("verified"):
            if await check_channels(uid):
                user["verified"] = True
                save_user(uid, user)
                await main_menu(callback_query.message)
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
            await callback_query.message.reply_text(f"{EMOJI_PHONE} ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ ᴛᴏ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ\n<i>7123181749, 6884112825</i>", parse_mode=ParseMode.HTML)
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
            await callback_query.message.reply_text(f"{EMOJI_BANK} ʙᴀɴᴋ ɪꜰꜱᴄ ᴄᴏᴅᴇ\n<i>SBIN0001234, HDFC0001234</i>", parse_mode=ParseMode.HTML)
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
            await callback_query.message.reply_text(f"{EMOJI_LINK} ʟɪɴᴋ ʙʏᴘᴀꜱꜱ\n<i>https://indianshortner.in/xxxx</i>", parse_mode=ParseMode.HTML)
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
            await callback_query.message.reply_text(f"{EMOJI_INDIA} ɪɴᴅɪᴀɴ ᴍᴏʙɪʟᴇ ɴᴜᴍʙᴇʀ\n<i>9876543210, 8123456789</i>", parse_mode=ParseMode.HTML)
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
            await callback_query.message.reply_text(f"{EMOJI_CARD} ᴀᴀᴅʜᴀʀ ɴᴜᴍʙᴇʀ\n<i>123456789012</i>", parse_mode=ParseMode.HTML)
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
            await callback_query.message.reply_text(f"{EMOJI_CAR} ᴠᴇʜɪᴄʟᴇ ɴᴜᴍʙᴇʀ\n<i>KA01AB3256, DL1CX1234</i>", parse_mode=ParseMode.HTML)
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
            await callback_query.message.reply_text(f"{EMOJI_CARD} ɢꜱᴛ ɴᴜᴍʙᴇʀ\n<i>19BOKPS7056D1ZI</i>", parse_mode=ParseMode.HTML)
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
            await callback_query.message.reply_text(f"{EMOJI_PAK} ᴘᴀᴋɪꜱᴛᴀɴ ɴᴜᴍʙᴇʀ\n<i>923078750447</i>", parse_mode=ParseMode.HTML)
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
            await callback_query.message.reply_text(f"{EMOJI_PHONE2} ᴀᴅᴠᴀɴᴄᴇᴅ ɴᴜᴍʙᴇʀ\n<i>6363016966, 9876543210</i>", parse_mode=ParseMode.HTML)
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
            await callback_query.message.reply_text(f"{EMOJI_INDIA} ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴛʀᴀᴄᴋɪɴɢ\n<i>6363016966, 9876543210</i>", parse_mode=ParseMode.HTML)
            await callback_query.answer()
            return
        
        elif data == "menu_invite":
            user = get_user(uid)
            bot_info = await app.get_me()
            link = f"https://t.me/{bot_info.username}?start={user['invite_code']}"
            await callback_query.message.reply_text(f"{EMOJI_INVITE} ɪɴᴠɪᴛᴇ (+{INVITE_CREDITS}ᴄʀ)\n<code>{link}</code>", parse_mode=ParseMode.HTML)
            await callback_query.answer()
            return
        
        elif data == "menu_redeem":
            ADMIN_STATE[uid] = 'REDEEM'
            await callback_query.message.reply_text(f"{EMOJI_TICKET} ᴇɴᴛᴇʀ ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ:\n<i>HEX-XXXXXXXXXX</i>", parse_mode=ParseMode.HTML)
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

@app.on_message(filters.text & ~filters.command)
async def handle_messages(client, message: Message):
    try:
        uid = message.from_user.id
        txt = message.text.strip()
        s = get_settings()
        
        if s.get("maintenance_mode", False) and uid != ADMIN_ID:
            sent = await message.reply_text(f"{EMOJI_TOOLS} Under maintenance", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(sent))
            return
        
        # Check verification
        user = get_user(uid)
        if not user.get("verified"):
            if await check_channels(uid):
                user["verified"] = True
                save_user(uid, user)
                await main_menu(message)
                return
            await show_verification_page(message)
            return
        
        # Admin state handling
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
                # Check credits
                if user.get("credits", 0) <= 0:
                    sent = await message.reply_text(f"{EMOJI_CROSS} No credits! +10 daily | +3 invite", parse_mode=ParseMode.HTML)
                    asyncio.create_task(schedule_delete(sent))
                    return
                
                # Run query
                await run_query(message, state, txt)
                return
        
        # Check if any state is pending
        if uid in ADMIN_STATE:
            return
        
        # If no state, show main menu
        await main_menu(message)
        
    except Exception as e:
        print(f"Message handler error: {e}")

async def run_query(message: Message, mode: str, query: str):
    if not await net_ok():
        sent = await message.reply_text(f"{EMOJI_CROSS} No internet", parse_mode=ParseMode.HTML)
        asyncio.create_task(schedule_delete(sent))
        return
    
    names = {'TG':f'{EMOJI_PHONE}','IFSC':f'{EMOJI_BANK}','SHORTLINK':f'{EMOJI_LINK}','AADHAAR':f'{EMOJI_CARD}','MOBILE':f'{EMOJI_INDIA}','VEHICLE':f'{EMOJI_CAR}','GST':f'{EMOJI_CARD}','PAK':f'{EMOJI_PAK}','INDNUM':f'{EMOJI_PHONE2}','INDNUM3':f'{EMOJI_INDIA}'}
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

async def main():
    print("🔄 Hex Terminal Premium Starting...")
    print("🎨 Colored Inline Buttons with Premium Emojis Enabled!")
    print("🤖 Kurigram Version with Full Button Colors!")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4"], capture_output=True, timeout=30)
    except: pass
    
    print(f"✅ {BOT_NAME} Ready!")
    print(f"💎 All buttons are colored InlineButtons with Premium Emojis!")
    print(f"⭐ Total Menu Buttons: 14 colored inline buttons")
    print("🚀 Bot is running...")
    
    await app.start()
    await app.idle()

if __name__ == '__main__':
    asyncio.run(main())