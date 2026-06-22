import random
import asyncio
import json
import os
import re
import subprocess
import sys
import socket
import aiohttp
from datetime import datetime, timedelta
from telethon import TelegramClient, events, types, functions
from telethon.errors import FloodWaitError

# ============================================================
# CONFIGURATION
# ============================================================
API_ID = int(os.environ.get('API_ID', '37996037'))
API_HASH = os.environ.get('API_HASH', '47ee9fa07b5eeb865edb3d79ada726a5')
TOKEN = os.environ.get('BOT_TOKEN', '8687617595:AAGCa0yJTRM52NLItvLkzt7O1mZEkCaNkn4')
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

USERS_FILE = os.path.join(os.getcwd(), "users.json")
REDEEM_FILE = os.path.join(os.getcwd(), "redeem_codes.json")
SETTINGS_FILE = os.path.join(os.getcwd(), "settings.json")

DAILY_FREE_CREDITS = 10
INVITE_CREDITS = 3
AUTO_DELETE_TIME = 60

BOT_NAME = "𝗛𝗲𝘅 𝗧𝗲𝗿𝗺𝗶𝗻𝗮𝗹"

# ============================================================
# PREMIUM EMOJI IDs
# ============================================================

# Premium Emoji IDs for Button Icons
PREMIUM_EMOJI_IDS = {
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
    "dashboard": 6267128480601741166,
    "spin": 6266969287638913443,
    "vip": 6267068789146260253,
    "osint": 5231012545799666522,
    "identity": 5260561650213220533,
    "leaderboard": 6093382540784046658,
    "menu": 6264791387032523779
}

# Premium Emoji IDs for Text Messages (as strings for tg-emoji tags)
TEXT_EMOJI_IDS = {
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

def get_pe(key):
    return f'<tg-emoji emoji-id="{TEXT_EMOJI_IDS[key]}"> </tg-emoji>'

# Create premium emoji objects
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

# ============================================================
# TELEGRAM CLIENT
# ============================================================

client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=TOKEN)

ADMIN_STATE = {}
USER_STATE = {}

# ============================================================
# DATA FUNCTIONS
# ============================================================

def load_json(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_json(filename, data):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except:
        pass

def get_user(user_id):
    users = load_json(USERS_FILE)
    uid = str(user_id)
    today = datetime.now().strftime("%Y-%m-%d")
    if uid not in users:
        users[uid] = {
            "credits": DAILY_FREE_CREDITS,
            "total_queries": 0,
            "daily_queries": 0,
            "last_reset": today,
            "invite_code": f"HEX-{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))}",
            "invites": 0,
            "verified": False
        }
        save_json(USERS_FILE, users)
    elif users[uid].get("last_reset") != today:
        users[uid]["credits"] = DAILY_FREE_CREDITS
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
        users[uid]["credits"] = users[uid].get("credits", 0) + amount
        save_json(USERS_FILE, users)
        return users[uid]["credits"]
    return 0

def use_credit(uid):
    users = load_json(USERS_FILE)
    uid = str(uid)
    if uid in users and users[uid].get("credits", 0) > 0:
        users[uid]["credits"] -= 1
        users[uid]["total_queries"] = users[uid].get("total_queries", 0) + 1
        users[uid]["daily_queries"] = users[uid].get("daily_queries", 0) + 1
        save_json(USERS_FILE, users)
        return True
    return False

def process_invite(inviter_id, new_id):
    users = load_json(USERS_FILE)
    inviter = str(inviter_id)
    new = str(new_id)
    if inviter in users:
        users[inviter]["credits"] = users[inviter].get("credits", 0) + INVITE_CREDITS
        users[inviter]["invites"] = users[inviter].get("invites", 0) + 1
    if new in users:
        users[new]["credits"] = users[new].get("credits", 0) + INVITE_CREDITS
        users[new]["invited_by"] = inviter
    save_json(USERS_FILE, users)
    return INVITE_CREDITS

def generate_redeem_code(credits):
    code = f"HEX-{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=10))}"
    codes = load_json(REDEEM_FILE)
    codes[code] = {"credits": credits, "used": False, "created": datetime.now().isoformat()}
    save_json(REDEEM_FILE, codes)
    return code

def redeem_code(uid, code):
    codes = load_json(REDEEM_FILE)
    code = code.upper().strip()
    if code not in codes:
        return False, f"{PE_CROSS} ɪɴᴠᴀʟɪᴅ ᴄᴏᴅᴇ"
    if codes[code].get("used"):
        return False, f"{PE_CROSS} ᴀʟʀᴇᴀᴅʏ ᴜꜱᴇᴅ"
    cr = codes[code]["credits"]
    codes[code]["used"] = True
    codes[code]["used_by"] = str(uid)
    save_json(REDEEM_FILE, codes)
    bal = add_credits(uid, cr)
    return True, f"{PE_CHECK} +{cr} ᴄʀᴇᴅɪᴛꜱ ᴀᴅᴅᴇᴅ!\n{PE_CREDIT} ʙᴀʟᴀɴᴄᴇ: {bal}"

def get_settings():
    try:
        return load_json(SETTINGS_FILE)
    except:
        d = {
            "bypass_maintenance": False,
            "tgid_enabled": True,
            "ifsc_enabled": True,
            "bypass_enabled": True,
            "mobile_enabled": True,
            "aadhaar_enabled": True,
            "rc_enabled": True,
            "gst_enabled": True,
            "pak_enabled": True,
            "indnum_enabled": True,
            "indnum3_enabled": True,
            "maintenance_mode": False
        }
        for k in ["tgid", "ifsc", "bypass", "mobile", "aadhaar", "rc", "gst", "pak", "indnum", "indnum3"]:
            d[f"maint_msg_{k}"] = f"{PE_TOOLS} {k} is under maintenance."
            d[f"maint_{k}"] = False
        save_json(SETTINGS_FILE, d)
        return d

def save_settings(data):
    save_json(SETTINGS_FILE, data)

# ============================================================
# COLORED KEYBOARD BUTTON FUNCTIONS (Telethon Style)
# ============================================================

def create_colored_button(text: str, icon_id: int = None, style_type: str = "primary"):
    """Create a colored keyboard button with premium emoji icon"""
    
    # Create button style
    if style_type == "primary":
        style = types.KeyboardButtonStyle(
            bg_primary=True,
            icon=icon_id or PREMIUM_EMOJI_IDS["star"]
        )
    elif style_type == "success":
        style = types.KeyboardButtonStyle(
            bg_success=True,
            icon=icon_id or PREMIUM_EMOJI_IDS["check"]
        )
    elif style_type == "danger":
        style = types.KeyboardButtonStyle(
            bg_danger=True,
            icon=icon_id or PREMIUM_EMOJI_IDS["cross"]
        )
    else:
        style = types.KeyboardButtonStyle(
            bg_primary=True,
            icon=icon_id or PREMIUM_EMOJI_IDS["star"]
        )
    
    return types.KeyboardButton(
        text=text,
        style=style
    )

def create_styled_row(buttons: list) -> types.KeyboardButtonRow:
    """Create a row of colored keyboard buttons"""
    return types.KeyboardButtonRow(buttons=buttons)

def create_keyboard_markup(rows: list) -> types.ReplyKeyboardMarkup:
    """Create reply keyboard markup from rows"""
    return types.ReplyKeyboardMarkup(
        rows=rows,
        resize=True
    )

# ============================================================
# GET KEYBOARD MENU (Colored Buttons with Premium Emojis)
# ============================================================

def get_main_keyboard(page=1, is_admin=False):
    """Create main menu with colored keyboard buttons"""
    
    if page == 1:
        rows = [
            create_styled_row([
                create_colored_button("ᴛɢ ɪᴅ ➜ ɴᴜᴍʙᴇʀ", PREMIUM_EMOJI_IDS["phone"], "primary"),
                create_colored_button("ɪꜰꜱᴄ ɪɴꜰᴏ", PREMIUM_EMOJI_IDS["bank"], "primary")
            ]),
            create_styled_row([
                create_colored_button("ʟɪɴᴋ ʙʏᴘᴀꜱꜱ", PREMIUM_EMOJI_IDS["link"], "warning")
            ]),
            create_styled_row([
                create_colored_button("ᴀᴀᴅʜᴀʀ ɪɴꜰᴏ", PREMIUM_EMOJI_IDS["card"], "primary"),
                create_colored_button("ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ", PREMIUM_EMOJI_IDS["india"], "success")
            ]),
            create_styled_row([
                create_colored_button("ʀᴄ ᴅᴇᴛᴀɪʟꜱ", PREMIUM_EMOJI_IDS["car"], "info"),
                create_colored_button("ɢꜱᴛ ʟᴏᴏᴋᴜᴘ", PREMIUM_EMOJI_IDS["card"], "warning")
            ]),
            create_styled_row([
                create_colored_button("ᴘᴀᴋ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ", PREMIUM_EMOJI_IDS["pak"], "primary"),
                create_colored_button("ɪɴᴅ ɴᴜᴍ ɪɴꜰᴏ 𝟸", PREMIUM_EMOJI_IDS["phone2"], "success")
            ]),
            create_styled_row([
                create_colored_button("ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ 𝟹", PREMIUM_EMOJI_IDS["india"], "danger")
            ]),
            create_styled_row([
                create_colored_button("ɪɴᴠɪᴛᴇ & ᴇᴀʀɴ", PREMIUM_EMOJI_IDS["invite"], "success"),
                create_colored_button("ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ", PREMIUM_EMOJI_IDS["ticket"], "warning")
            ]),
            create_styled_row([
                create_colored_button("ʜᴇʟᴘ", PREMIUM_EMOJI_IDS["help"], "info"),
                create_colored_button("ᴀʙᴏᴜᴛ", PREMIUM_EMOJI_IDS["about"], "primary")
            ]),
            create_styled_row([
                create_colored_button("ꜱᴛᴀᴛꜱ", PREMIUM_EMOJI_IDS["stats"], "info")
            ])
        ]
        
        if is_admin:
            rows.append(create_styled_row([
                create_colored_button("ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ", PREMIUM_EMOJI_IDS["admin"], "danger")
            ]))
        
        rows.append(create_styled_row([
            create_colored_button("ɴᴇxᴛ ᴘᴀɢᴇ ➜", PREMIUM_EMOJI_IDS["next"], "primary")
        ]))
        
    else:
        rows = [
            create_styled_row([
                create_colored_button("ɪᴅᴇɴᴛɪᴛʏ ᴛᴏᴏʟꜱ", PREMIUM_EMOJI_IDS["identity"], "primary"),
                create_colored_button("ᴏꜱɪɴᴛ ᴛᴏᴏʟꜱ", PREMIUM_EMOJI_IDS["osint"], "primary")
            ]),
            create_styled_row([
                create_colored_button("ᴠɪᴘ ᴘʀᴇᴍɪᴜᴍ", PREMIUM_EMOJI_IDS["vip"], "success"),
                create_colored_button("ᴅᴀɪʟʏ ꜱᴘɪɴ", PREMIUM_EMOJI_IDS["spin"], "warning")
            ]),
            create_styled_row([
                create_colored_button("ᴅᴀꜱʜʙᴏᴀʀᴅ", PREMIUM_EMOJI_IDS["dashboard"], "info"),
                create_colored_button("ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ", PREMIUM_EMOJI_IDS["leaderboard"], "primary")
            ]),
            create_styled_row([
                create_colored_button("⬅ ʙᴀᴄᴋ ᴛᴏ ᴍᴇɴᴜ", PREMIUM_EMOJI_IDS["back"], "danger")
            ])
        ]
    
    return create_keyboard_markup(rows)

# ============================================================
# CHECK CHANNEL VERIFICATION
# ============================================================

async def check_channel(uid):
    try:
        member = await client.get_participants(CHANNEL_ID, limit=1, search=f'@{uid}' if uid else None)
        # Simplified check - using get_permissions
        try:
            result = await client(functions.channels.GetParticipantRequest(
                channel=CHANNEL_ID,
                participant=uid
            ))
            return result.participant is not None
        except:
            return False
    except:
        return False

# ============================================================
# SEND MESSAGE WITH PREMIUM EMOJIS
# ============================================================

async def send_message(chat_id, text, reply_markup=None, parse_mode='html'):
    """Send message with premium emoji support"""
    try:
        # Remove HTML tags that might break telethon
        # Telethon supports HTML parsing via parse_mode
        return await client.send_message(
            chat_id,
            text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
    except Exception as e:
        print(f"Send message error: {e}")
        return None

# ============================================================
# VERIFICATION PAGE
# ============================================================

async def show_verification_page(event):
    try:
        caption = (
            f"{PE_DIAMOND} {BOT_NAME} {PE_DIAMOND}\n"
            f"@{client.get_me().username}\n\n"
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
        
        # Create verification buttons (InlineKeyboard for verification)
        inline_buttons = [
            [
                types.InlineKeyboardButton(
                    text="📢 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ",
                    url=CHANNEL_LINK
                )
            ],
            [
                types.InlineKeyboardButton(
                    text="✅ ɪ'ᴠᴇ ᴊᴏɪɴᴇᴅ - ᴠᴇʀɪꜰʏ",
                    callback_data="verify"
                )
            ]
        ]
        
        inline_markup = types.InlineKeyboardMarkup(inline_buttons)
        
        await client.send_message(
            event.chat_id,
            caption,
            reply_markup=inline_markup,
            parse_mode='html'
        )
    except Exception as e:
        print(f"Verification page error: {e}")

# ============================================================
# MAIN MENU
# ============================================================

async def show_main_menu(event, page=1):
    try:
        uid = event.sender_id
        user = get_user(uid)
        is_admin = uid == ADMIN_ID
        cr = user.get("credits", 0)
        
        keyboard = get_main_keyboard(page, is_admin)
        
        txt = (
            f"{PE_DIAMOND} {BOT_NAME} {PE_DIAMOND}\n"
            f"{PE_USER} <b>ᴡᴇʟᴄᴏᴍᴇ ʙᴀᴄᴋ,</b> <code>{event.sender.first_name}</code>\n\n"
            f"{PE_DASHBOARD} <b>ʏᴏᴜʀ ᴅᴀꜱʜʙᴏᴀʀᴅ</b>\n"
            f"┃ {PE_CREDIT} <b>ᴄʀᴇᴅɪᴛꜱ:</b> {cr}\n"
            f"┃ {PE_SEARCH} <b>Qᴜᴇʀɪᴇꜱ:</b> {user.get('total_queries', 0)}\n"
            f"┃ {PE_INVITE} <b>ɪɴᴠɪᴛᴇꜱ:</b> {user.get('invites', 0)}\n\n"
            f"{PE_GIFT} ʀᴇᴡᴀʀᴅꜱ:\n"
            f"{PE_REFRESH} +{DAILY_FREE_CREDITS} ᴅᴀɪʟʏ ꜰʀᴇᴇ\n"
            f"{PE_INVITE} +{INVITE_CREDITS} ᴘᴇʀ ɪɴᴠɪᴛᴇ\n"
            f"{PE_CLOCK} {AUTO_DELETE_TIME}ꜱ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ\n\n"
            f"{PE_STAR} ꜱᴇʟᴇᴄᴛ ᴀ ꜱᴇʀᴠɪᴄᴇ ʙᴇʟᴏᴡ {PE_STAR}"
        )
        
        sent = await client.send_message(
            event.chat_id,
            txt,
            reply_markup=keyboard,
            parse_mode='html'
        )
        
        # Schedule auto-delete
        asyncio.create_task(schedule_delete(sent, AUTO_DELETE_TIME))
        
        USER_STATE[str(uid)] = {"page": page}
    except Exception as e:
        print(f"Main menu error: {e}")

# ============================================================
# AUTO DELETE
# ============================================================

async def schedule_delete(message, delay):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except:
        pass

# ============================================================
# API FUNCTIONS
# ============================================================

async def safe_api_fetch(session, url, timeout=20):
    for attempt in range(3):
        try:
            headers = {'User-Agent': 'Mozilla/5.0', 'Accept': '*/*'}
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout), headers=headers, allow_redirects=True) as r:
                text = await r.text()
                if not text:
                    continue
                try:
                    return json.loads(text)
                except:
                    return {"raw_text": text} if text.strip() else None
        except:
            if attempt == 2:
                return None
            await asyncio.sleep(1)
    return None

async def chatid_lookup(session, query):
    data = await safe_api_fetch(session, f"{LOOKUP_API}{query}")
    if not data:
        return f"{PE_CROSS} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"
    if isinstance(data, dict) and not data.get("raw_text") and data.get("success"):
        d = data.get("data", data)
        if isinstance(d, dict):
            result = f"{PE_SPARKLE} {PE_PHONE} ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ ɪɴꜰᴏ {PE_SPARKLE}\n"
            if d.get('chat_id') or d.get('userid'):
                result += f"{PE_SEARCH} ᴄʜᴀᴛ ɪᴅ: <code>{d.get('chat_id', d.get('userid', query))}</code>\n"
            if d.get('number'):
                result += f"{PE_PHONE2} ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ: <code>{d['number']}</code>\n"
            if d.get('name'):
                result += f"{PE_USER} ᴘʀᴏꜰɪʟᴇ ɴᴀᴍᴇ: <code>{d['name']}</code>\n"
            return result
    return f"{PE_CROSS} ɴᴏᴛ ꜰᴏᴜɴᴅ"

async def ifsc_lookup(session, code):
    data = await safe_api_fetch(session, f"{IFSC_API}{code.upper()}")
    if not data or isinstance(data, dict) and data.get("raw_text"):
        return f"{PE_CROSS} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"
    if isinstance(data, dict):
        return (f"{PE_SPARKLE} {PE_BANK} ʙᴀɴᴋ ɪꜰꜱᴄ ᴅᴇᴛᴀɪʟꜱ {PE_SPARKLE}\n"
                f"{PE_BANK} ʙᴀɴᴋ ɴᴀᴍᴇ: <code>{data.get('BANK', 'N/A')}</code>\n"
                f"{PE_LOCATION} ʙʀᴀɴᴄʜ: <code>{data.get('BRANCH', 'N/A')}</code>\n"
                f"{PE_CARD} ɪꜰꜱᴄ ᴄᴏᴅᴇ: <code>{data.get('IFSC', code.upper())}</code>\n"
                f"{PE_LOCATION} ᴀᴅᴅʀᴇꜱꜱ: <code>{data.get('ADDRESS', 'N/A')}</code>")
    return f"{PE_CROSS} ɪɴᴠᴀʟɪᴅ ᴄᴏᴅᴇ"

async def bypass_lookup(session, link):
    s = get_settings()
    if s.get("bypass_maintenance", False):
        return f"{PE_TOOLS} ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ"
    data = await safe_api_fetch(session, f"{SHORTLINK_API}{link}", timeout=20)
    if not data or isinstance(data, dict) and data.get("raw_text"):
        return f"{PE_CROSS} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"
    if isinstance(data, dict):
        r = data.get('bypassed_url') or data.get('url') or str(data)
        return f"{PE_SPARKLE} {PE_LINK} ʟɪɴᴋ ʙʏᴘᴀꜱꜱᴇᴅ {PE_SPARKLE}\n{PE_LINK} ᴏʀɪɢɪɴᴀʟ ᴜʀʟ: <code>{str(r)}</code>"
    return f"{PE_LINK} ʀᴇꜱᴜʟᴛ: <code>{str(data)}</code>"

async def gst_lookup(session, gst_number):
    data = await safe_api_fetch(session, f"{GST_API}{gst_number.upper()}", timeout=20)
    if not data or isinstance(data, dict) and data.get("raw_text"):
        return f"{PE_CROSS} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"
    if isinstance(data, dict) and data.get("status") == "success" and data.get("data"):
        d = data["data"]
        result = f"{PE_SPARKLE} {PE_CARD} ɢꜱᴛ ʙᴜꜱɪɴᴇꜱꜱ ɪɴꜰᴏ {PE_SPARKLE}\n"
        if d.get('TradeName'):
            result += f"{PE_BANK} ʙᴜꜱɪɴᴇꜱꜱ ɴᴀᴍᴇ: <code>{d['TradeName']}</code>\n"
        if d.get('Gstin'):
            result += f"{PE_CARD} ɢꜱᴛ ɴᴜᴍʙᴇʀ: <code>{d['Gstin']}</code>\n"
        return result
    return f"{PE_CROSS} ɪɴᴠᴀʟɪᴅ ɢꜱᴛ"

async def pakistan_lookup(session, number):
    try:
        data = await safe_api_fetch(session, f"{PAK_API}{number}", timeout=20)
        if not data or isinstance(data, dict) and data.get("raw_text"):
            return f"{PE_CROSS} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"
        if isinstance(data, dict) and data.get("success") and data.get("data"):
            valid = [r for r in data["data"] if isinstance(r, dict) and any(r.get(k) for k in ['name', 'number', 'cnic', 'address'])]
            if not valid:
                return f"{PE_CROSS} ɴᴏ ᴅᴀᴛᴀ"
            result = f"{PE_SPARKLE} {PE_PAK} ᴘᴀᴋɪꜱᴛᴀɴ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ {PE_SPARKLE}\n"
            for i, r in enumerate(valid[:3], 1):
                if len(valid) > 1:
                    result += f"\n━━ {PE_USER} ʀᴇᴄᴏʀᴅ {i} ━━\n"
                if r.get('number'):
                    result += f"{PE_PHONE2} ᴘʜᴏɴᴇ: <code>{r['number']}</code>\n"
                if r.get('name'):
                    result += f"{PE_USER} ɴᴀᴍᴇ: <code>{r['name']}</code>\n"
                if r.get('cnic'):
                    result += f"{PE_CARD} ᴄɴɪᴄ: <code>{r['cnic']}</code>\n"
                if r.get('address'):
                    result += f"{PE_LOCATION} ᴀᴅᴅʀᴇꜱꜱ: <code>{r['address'][:200]}</code>\n"
            return result
        return f"{PE_CROSS} ɴᴏ ᴅᴀᴛᴀ"
    except:
        return f"{PE_CROSS} ᴇʀʀᴏʀ"

async def indnum_lookup(session, number):
    for attempt in range(3):
        data = await safe_api_fetch(session, f"{IND_NUM_API}{number}", timeout=30)
        if data and isinstance(data, dict) and not data.get("raw_text") and data.get("results"):
            break
        if attempt < 2:
            await asyncio.sleep(2)
    if not data or isinstance(data, dict) and data.get("raw_text"):
        return f"{PE_CROSS} ꜱᴇʀᴠɪᴄᴇ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ"
    results = data.get("results", {})
    if not results:
        return f"{PE_CROSS} ɴᴏ ʀᴇꜱᴜʟᴛꜱ"
    result = f"{PE_SPARKLE} {PE_PHONE2} ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴀᴅᴠᴀɴᴄᴇᴅ {PE_SPARKLE}\n{PE_PHONE2} ɴᴜᴍʙᴇʀ: <code>{number}</code>\n"
    found = False
    s3 = results.get("source_3", {}).get("data", {})
    if isinstance(s3, dict):
        for k, e in [("SIM card", PE_SIM), ("Connection", PE_SIGNAL), ("Mobile State", PE_LOCATION), ("Hometown", PE_HOME)]:
            if s3.get(k):
                result += f"{e} {k}: <code>{str(s3[k])[:200]}</code>\n"
                found = True
    s4 = results.get("source_4", {}).get("data", {})
    if isinstance(s4, dict) and s4.get("carrier"):
        result += f"{PE_NETWORK} ᴄᴀʀʀɪᴇʀ: <code>{s4['carrier']}</code>\n"
        found = True
    return result if found else f"{PE_CROSS} ɴᴏ ᴅᴀᴛᴀ"

async def indnum3_lookup(session, number):
    url = f"{IND_NUM_API_3}{number}"
    try:
        headers = {'User-Agent': 'Mozilla/5.0', 'Accept': '*/*'}
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=25), headers=headers, allow_redirects=True) as r:
            text = await r.text()
            if not text or len(text) < 20:
                return f"{PE_CROSS} ᴇᴍᴘᴛʏ ʀᴇꜱᴘᴏɴꜱᴇ"
            try:
                data = json.loads(text)
                if isinstance(data, dict):
                    result = f"{PE_SPARKLE} {PE_INDIA} ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴛʀᴀᴄᴋɪɴɢ {PE_SPARKLE}\n{PE_PHONE2} ɴᴜᴍʙᴇʀ: <code>{number}</code>\n"
                    for k, v in data.items():
                        if v and str(v).strip():
                            result += f"{PE_SEARCH} {k}: <code>{str(v)[:200]}</code>\n"
                    return result
            except:
                pass
            clean = re.sub(r'<[^>]+>', '\n', text)
            lines = [l.strip() for l in clean.split('\n') if l.strip() and len(l.strip()) > 1]
            result = f"{PE_SPARKLE} {PE_INDIA} ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴛʀᴀᴄᴋɪɴɢ {PE_SPARKLE}\n{PE_PHONE2} ɴᴜᴍʙᴇʀ: <code>{number}</code>\n"
            found = 0
            for line in lines[:20]:
                if ':' in line:
                    parts = line.split(':', 1)
                    key, val = parts[0].strip(), parts[1].strip() if len(parts) > 1 else ''
                    if val:
                        e = PE_USER if any(w in key.lower() for w in ['name', 'nama']) else PE_NETWORK if any(w in key.lower() for w in ['carrier', 'operator', 'network', 'sim']) else PE_LOCATION if any(w in key.lower() for w in ['location', 'address', 'city', 'state', 'area']) else PE_PHONE2 if any(w in key.lower() for w in ['phone', 'mobile', 'number', 'no']) else PE_SEARCH
                        result += f"{e} {key}: <code>{val[:200]}</code>\n"
                        found += 1
            if found == 0:
                result += f"{PE_CARD} ʀᴀᴡ ᴅᴀᴛᴀ: <code>{clean[:500]}</code>\n"
            return result
    except:
        return f"{PE_CROSS} ᴛɪᴍᴇᴏᴜᴛ"

# ============================================================
# RUN QUERY
# ============================================================

async def run_query(event, mode, query):
    sent = await event.reply(f"{PE_GREEN} ꜱᴇᴀʀᴄʜɪɴɢ...", parse_mode='html')
    credit_deducted = False
    
    try:
        if mode in ['AADHAAR', 'MOBILE', 'VEHICLE']:
            # Run python script for India data
            script_path = os.path.join(os.getcwd(), "verify_india.py")
            if os.path.exists(script_path):
                try:
                    process = subprocess.Popen(
                        [sys.executable, script_path],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        cwd=os.getcwd()
                    )
                    choice_map = {'AADHAAR': '2', 'MOBILE': '1', 'VEHICLE': '4'}
                    stdout, stderr = process.communicate(f"{choice_map[mode]}\n{query}\n0\n", timeout=45)
                    if stdout and len(stdout) > 20:
                        raw = stdout
                        records = parse_india_records(raw)
                        result = format_india_records(records, mode)
                        if records:
                            use_credit(event.sender_id)
                            credit_deducted = True
                    else:
                        result = f"{PE_CROSS} No data found"
                except:
                    result = f"{PE_CROSS} Script failed"
            else:
                result = f"{PE_CROSS} Script not found"
        else:
            async with aiohttp.ClientSession() as session:
                if mode == 'TG':
                    result = await chatid_lookup(session, query)
                elif mode == 'IFSC':
                    result = await ifsc_lookup(session, query)
                elif mode == 'SHORTLINK':
                    result = await bypass_lookup(session, query)
                elif mode == 'GST':
                    result = await gst_lookup(session, query)
                elif mode == 'PAK':
                    result = await pakistan_lookup(session, query)
                elif mode == 'INDNUM':
                    result = await indnum_lookup(session, query)
                elif mode == 'INDNUM3':
                    result = await indnum3_lookup(session, query)
                else:
                    result = f"{PE_CROSS}"
            
            if result and f"{PE_CROSS}" not in str(result) and "unavailable" not in str(result).lower():
                use_credit(event.sender_id)
                credit_deducted = True
        
        user = get_user(event.sender_id)
        final = f"{result}\n{SEP}\n{PE_CREDIT} {'ᴄʀ: '+str(user.get('credits',0)) if credit_deducted else 'ɴᴏ ᴄʀ ᴅᴇᴅᴜᴄᴛᴇᴅ'} | {PE_CLOCK} {AUTO_DELETE_TIME}ꜱ{DISCLAIMER}{FOOTER}"
        await sent.edit(final, parse_mode='html')
        asyncio.create_task(schedule_delete(sent, AUTO_DELETE_TIME))
    except Exception as e:
        print(f"Query error: {e}")
        try:
            await sent.edit(f"{PE_WARN} ᴇʀʀᴏʀ{FOOTER}", parse_mode='html')
        except:
            pass

def parse_india_records(raw):
    raw = raw if raw else ""
    if not raw:
        return []
    records = []
    sections = re.split(r'={5,}|-{5,}|Record\s*\d+[:\s-]*', raw)
    for section in sections:
        section = section.strip()
        if len(section) < 10:
            continue
        record = {}
        for field, label in {'Name': f'{PE_USER} ɴᴀᴍᴇ', "Father's Name": f'{PE_USER} ꜰᴀᴛʜᴇʀ', 'Mobile': f'{PE_PHONE2} ᴍᴏʙɪʟᴇ', 'Address': f'{PE_LOCATION} ᴀᴅᴅʀᴇꜱꜱ', 'Circle': f'{PE_NETWORK} ᴄɪʀᴄʟᴇ', 'State': f'{PE_STATE} ꜱᴛᴀᴛᴇ'}.items():
            match = re.search(rf'{re.escape(field)}:\s*([^\n]+)', section, re.IGNORECASE)
            if match and match.group(1).strip() not in ['None', '', 'N/A', 'null']:
                record[label] = match.group(1).strip()
        if record:
            seen = set()
            unique = {}
            for k, v in record.items():
                if v not in seen:
                    seen.add(v)
                    unique[k] = v
            if unique:
                records.append(unique)
    final = []
    seen = set()
    for r in records:
        combo = tuple(sorted(r.items()))
        if combo not in seen:
            seen.add(combo)
            final.append(r)
    return final

def format_india_records(records, mode):
    if not records:
        return f"{PE_CROSS} ɴᴏ ʀᴇᴄᴏʀᴅꜱ ꜰᴏᴜɴᴅ"
    title_map = {'AADHAAR': f'{PE_CARD} ᴀᴀᴅʜᴀʀ', 'MOBILE': f'{PE_INDIA} ɪɴᴅ ɴᴜᴍʙᴇʀ', 'VEHICLE': f'{PE_CAR} ᴠᴇʜɪᴄʟᴇ'}
    title = title_map.get(mode, f'{PE_CHART} ʀᴇꜱᴜʟᴛ')
    result = f"{PE_SPARKLE} {title} {PE_SPARKLE}\n{PE_CHART} ᴛᴏᴛᴀʟ ʀᴇᴄᴏʀᴅꜱ: {len(records)}\n"
    for i, record in enumerate(records, 1):
        if len(records) > 1:
            result += f"\n━━ {PE_USER} ʀᴇᴄᴏʀᴅ {i} ━━\n"
        for key, value in record.items():
            result += f"{key}: <code>{value}</code>\n"
    return result

# ============================================================
# ADMIN PANEL
# ============================================================

async def show_admin_panel(event):
    if event.sender_id != ADMIN_ID:
        return
    
    # Create inline admin buttons with colors
    buttons = [
        [
            types.InlineKeyboardButton(
                text="🎫 ɢᴇɴ ᴄᴏᴅᴇ",
                callback_data="ad_gen",
                style=types.ButtonStyle.SUCCESS
            ),
            types.InlineKeyboardButton(
                text="📋 ᴄᴏᴅᴇꜱ",
                callback_data="ad_codes",
                style=types.ButtonStyle.PRIMARY
            )
        ],
        [
            types.InlineKeyboardButton(
                text="🎁 ᴀᴅᴅ ᴄʀ",
                callback_data="ad_credit",
                style=types.ButtonStyle.PRIMARY
            ),
            types.InlineKeyboardButton(
                text="📢 ʙᴄᴀꜱᴛ",
                callback_data="ad_bcast",
                style=types.ButtonStyle.PRIMARY
            )
        ],
        [
            types.InlineKeyboardButton(
                text="🔴 ɢʟᴏʙᴀʟ ᴏꜰꜰ" if get_settings().get("maintenance_mode") else "🟢 ɢʟᴏʙᴀʟ ᴏɴ",
                callback_data="ad_maint",
                style=types.ButtonStyle.DANGER if get_settings().get("maintenance_mode") else types.ButtonStyle.SUCCESS
            )
        ],
        [
            types.InlineKeyboardButton(
                text="❌ ᴄʟᴏꜱᴇ",
                callback_data="ad_close",
                style=types.ButtonStyle.DANGER
            )
        ]
    ]
    
    markup = types.InlineKeyboardMarkup(buttons)
    
    txt = f"{PE_CROWN} ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ {PE_CROWN}\n{PE_INVITE} ᴜꜱᴇʀꜱ: {len(load_json(USERS_FILE))} | {PE_TICKET} ᴄᴏᴅᴇꜱ: {len(load_json(REDEEM_FILE))}"
    
    if hasattr(event, 'edit'):
        await event.edit(txt, reply_markup=markup, parse_mode='html')
    else:
        await client.send_message(event.chat_id, txt, reply_markup=markup, parse_mode='html')

# ============================================================
# HELP, ABOUT, STATS (Inline versions)
# ============================================================

async def show_help_inline(event):
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
    if hasattr(event, 'edit'):
        await event.edit(text, parse_mode='html')
    else:
        await event.reply(text, parse_mode='html')
    await asyncio.sleep(60)
    try:
        await event.delete()
    except:
        pass

async def show_about_inline(event):
    text = f"""
{PE_ABOUT} 𝐀𝐁𝐎𝐔𝐓 𝐁𝐎𝐓 {PE_ABOUT}

𝐍𝐀𝐌𝐄: {BOT_NAME}
𝐔𝐒𝐄𝐑𝐍𝐀𝐌𝐄: @{client.get_me().username}
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
• Colored Keyboard Buttons

{PE_CROWN} 𝐃𝐄𝐕𝐄𝐋𝐎𝐏𝐄𝐃 𝐁𝐘: @Hexh4ckerOFC

{PE_WARN} 𝐅𝐎𝐑 𝐄𝐃𝐔𝐂𝐀𝐓𝐈𝐎𝐍𝐀𝐋 𝐏𝐔𝐑𝐏𝐎𝐒𝐄𝐒 𝐎𝐍𝐋𝐘
"""
    if hasattr(event, 'edit'):
        await event.edit(text, parse_mode='html')
    else:
        await event.reply(text, parse_mode='html')
    await asyncio.sleep(60)
    try:
        await event.delete()
    except:
        pass

async def show_stats_inline(event):
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
    if hasattr(event, 'edit'):
        await event.edit(text, parse_mode='html')
    else:
        await event.reply(text, parse_mode='html')
    await asyncio.sleep(60)
    try:
        await event.delete()
    except:
        pass

# ============================================================
# EVENT HANDLERS
# ============================================================

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    try:
        uid = event.sender_id
        
        # Check invite
        args = event.raw_text.split()
        if len(args) > 1 and args[1].startswith("HEX-"):
            users = load_json(USERS_FILE)
            for inviter, data in users.items():
                if data.get("invite_code") == args[1] and inviter != str(uid):
                    cr = process_invite(inviter, uid)
                    try:
                        await client.send_message(
                            int(inviter),
                            f"{PE_GIFT} +{cr} ᴄʀᴇᴅɪᴛꜱ! ɴᴇᴡ ᴜꜱᴇʀ ᴊᴏɪɴᴇᴅ!",
                            parse_mode='html'
                        )
                    except:
                        pass
                    break
        
        user = get_user(uid)
        
        if uid == ADMIN_ID:
            user["verified"] = True
            save_user(uid, user)
            await show_main_menu(event)
            return
        
        if not user.get("verified"):
            if await check_channel(uid):
                user["verified"] = True
                save_user(uid, user)
                await show_main_menu(event)
                return
            await show_verification_page(event)
            return
        
        await show_main_menu(event)
    except Exception as e:
        print(f"Start error: {e}")

@client.on(events.CallbackQuery)
async def callback_handler(event):
    try:
        data = event.data.decode()
        uid = event.sender_id
        s = get_settings()
        
        if data == "verify":
            if uid == ADMIN_ID:
                user = get_user(uid)
                user["verified"] = True
                save_user(uid, user)
                await event.answer("✅ Verified as Admin!", alert=True)
                await event.message.delete()
                await show_main_menu(event)
                return
            
            if await check_channel(uid):
                user = get_user(uid)
                user["verified"] = True
                save_user(uid, user)
                await event.answer("✅ Verified!", alert=True)
                await event.message.delete()
                await show_main_menu(event)
            else:
                await event.answer("❌ Please join the channel first!", alert=True)
            return
        
        if data.startswith("ad_"):
            if uid != ADMIN_ID:
                await event.answer("❌ Unauthorized!", alert=True)
                return
            
            if data == "ad_close":
                await event.message.delete()
                await event.answer()
                return
            elif data == "ad_codes":
                codes = load_json(REDEEM_FILE)
                txt = f"{PE_TICKET} ᴄᴏᴅᴇꜱ: {len(codes)}\n"
                for c, v in list(codes.items())[-15:]:
                    txt += f"{'✅' if not v.get('used') else '❌'} <code>{c}</code> | {v.get('credits')}cr\n"
                await event.edit(txt, reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton("🔄 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode='html')
                await event.answer()
                return
            elif data == "ad_gen":
                ADMIN_STATE[uid] = "gen"
                await event.edit(f"{PE_TICKET} ᴇɴᴛᴇʀ ᴄʀᴇᴅɪᴛꜱ:\n<i>100</i>", reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton("🔄 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode='html')
                await event.answer()
                return
            elif data == "ad_credit":
                ADMIN_STATE[uid] = "credit"
                await event.edit(f"{PE_GIFT} ᴇɴᴛᴇʀ ɪᴅ ᴀᴍᴏᴜɴᴛ:\n<i>123456789 50</i>", reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton("🔄 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode='html')
                await event.answer()
                return
            elif data == "ad_bcast":
                ADMIN_STATE[uid] = "bcast"
                await event.edit(f"{PE_BOLT} ᴇɴᴛᴇʀ ᴍᴇꜱꜱᴀɢᴇ:", reply_markup=types.InlineKeyboardMarkup([[types.InlineKeyboardButton("🔄 ʙᴀᴄᴋ", callback_data="ad_back")]]), parse_mode='html')
                await event.answer()
                return
            elif data == "ad_maint":
                s["maintenance_mode"] = not s.get("maintenance_mode", False)
                save_settings(s)
                await event.answer(f"Global: {'ON' if s['maintenance_mode'] else 'OFF'}", alert=True)
                await show_admin_panel(event)
                return
            elif data == "ad_back":
                await show_admin_panel(event)
                await event.answer()
                return
            await event.answer()
            return
        
        # Handle menu callbacks
        if data.startswith("menu_"):
            if uid != ADMIN_ID:
                user = get_user(uid)
                if not user.get("verified"):
                    if await check_channel(uid):
                        user["verified"] = True
                        save_user(uid, user)
                        await show_main_menu(event)
                        return
                    await show_verification_page(event)
                    await event.answer()
                    return
            
            if data == "menu_tgid":
                if not s.get("tgid_enabled", True):
                    await event.reply(f"{PE_DISABLED} Disabled", parse_mode='html')
                    await event.answer()
                    return
                maint, msg = check_feature_maintenance("tgid")
                if maint:
                    await event.reply(f"{PE_TOOLS} {msg}", parse_mode='html')
                    await event.answer()
                    return
                ADMIN_STATE[uid] = 'TG'
                await event.reply(f"{PE_PHONE} ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ ᴛᴏ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ\n<i>7123181749, 6884112825</i>", parse_mode='html')
                await event.answer()
                return
            
            elif data == "menu_ifsc":
                if not s.get("ifsc_enabled", True):
                    await event.reply(f"{PE_DISABLED} Disabled", parse_mode='html')
                    await event.answer()
                    return
                maint, msg = check_feature_maintenance("ifsc")
                if maint:
                    await event.reply(f"{PE_TOOLS} {msg}", parse_mode='html')
                    await event.answer()
                    return
                ADMIN_STATE[uid] = 'IFSC'
                await event.reply(f"{PE_BANK} ʙᴀɴᴋ ɪꜰꜱᴄ ᴄᴏᴅᴇ\n<i>SBIN0001234, HDFC0001234</i>", parse_mode='html')
                await event.answer()
                return
            
            elif data == "menu_bypass":
                if not s.get("bypass_enabled", True):
                    await event.reply(f"{PE_DISABLED} Disabled", parse_mode='html')
                    await event.answer()
                    return
                maint, msg = check_feature_maintenance("bypass")
                if maint:
                    await event.reply(f"{PE_TOOLS} {msg}", parse_mode='html')
                    await event.answer()
                    return
                ADMIN_STATE[uid] = 'SHORTLINK'
                await event.reply(f"{PE_LINK} ʟɪɴᴋ ʙʏᴘᴀꜱꜱ\n<i>https://indianshortner.in/xxxx</i>", parse_mode='html')
                await event.answer()
                return
            
            elif data == "menu_mobile":
                if not s.get("mobile_enabled", True):
                    await event.reply(f"{PE_DISABLED} Disabled", parse_mode='html')
                    await event.answer()
                    return
                maint, msg = check_feature_maintenance("mobile")
                if maint:
                    await event.reply(f"{PE_TOOLS} {msg}", parse_mode='html')
                    await event.answer()
                    return
                ADMIN_STATE[uid] = 'MOBILE'
                await event.reply(f"{PE_INDIA} ɪɴᴅɪᴀɴ ᴍᴏʙɪʟᴇ ɴᴜᴍʙᴇʀ\n<i>9876543210, 8123456789</i>", parse_mode='html')
                await event.answer()
                return
            
            elif data == "menu_aadhaar":
                if not s.get("aadhaar_enabled", True):
                    await event.reply(f"{PE_DISABLED} Disabled", parse_mode='html')
                    await event.answer()
                    return
                maint, msg = check_feature_maintenance("aadhaar")
                if maint:
                    await event.reply(f"{PE_TOOLS} {msg}", parse_mode='html')
                    await event.answer()
                    return
                ADMIN_STATE[uid] = 'AADHAAR'
                await event.reply(f"{PE_CARD} ᴀᴀᴅʜᴀʀ ɴᴜᴍʙᴇʀ\n<i>123456789012</i>", parse_mode='html')
                await event.answer()
                return
            
            elif data == "menu_rc":
                if not s.get("rc_enabled", True):
                    await event.reply(f"{PE_DISABLED} Disabled", parse_mode='html')
                    await event.answer()
                    return
                maint, msg = check_feature_maintenance("rc")
                if maint:
                    await event.reply(f"{PE_TOOLS} {msg}", parse_mode='html')
                    await event.answer()
                    return
                ADMIN_STATE[uid] = 'VEHICLE'
                await event.reply(f"{PE_CAR} ᴠᴇʜɪᴄʟᴇ ɴᴜᴍʙᴇʀ\n<i>KA01AB3256, DL1CX1234</i>", parse_mode='html')
                await event.answer()
                return
            
            elif data == "menu_gst":
                if not s.get("gst_enabled", True):
                    await event.reply(f"{PE_DISABLED} Disabled", parse_mode='html')
                    await event.answer()
                    return
                maint, msg = check_feature_maintenance("gst")
                if maint:
                    await event.reply(f"{PE_TOOLS} {msg}", parse_mode='html')
                    await event.answer()
                    return
                ADMIN_STATE[uid] = 'GST'
                await event.reply(f"{PE_CARD} ɢꜱᴛ ɴᴜᴍʙᴇʀ\n<i>19BOKPS7056D1ZI</i>", parse_mode='html')
                await event.answer()
                return
            
            elif data == "menu_pak":
                if not s.get("pak_enabled", True):
                    await event.reply(f"{PE_DISABLED} Disabled", parse_mode='html')
                    await event.answer()
                    return
                maint, msg = check_feature_maintenance("pak")
                if maint:
                    await event.reply(f"{PE_TOOLS} {msg}", parse_mode='html')
                    await event.answer()
                    return
                ADMIN_STATE[uid] = 'PAK'
                await event.reply(f"{PE_PAK} ᴘᴀᴋɪꜱᴛᴀɴ ɴᴜᴍʙᴇʀ\n<i>923078750447</i>", parse_mode='html')
                await event.answer()
                return
            
            elif data == "menu_indnum":
                if not s.get("indnum_enabled", True):
                    await event.reply(f"{PE_DISABLED} Disabled", parse_mode='html')
                    await event.answer()
                    return
                maint, msg = check_feature_maintenance("indnum")
                if maint:
                    await event.reply(f"{PE_TOOLS} {msg}", parse_mode='html')
                    await event.answer()
                    return
                ADMIN_STATE[uid] = 'INDNUM'
                await event.reply(f"{PE_PHONE2} ᴀᴅᴠᴀɴᴄᴇᴅ ɴᴜᴍʙᴇʀ\n<i>6363016966, 9876543210</i>", parse_mode='html')
                await event.answer()
                return
            
            elif data == "menu_indnum3":
                if not s.get("indnum3_enabled", True):
                    await event.reply(f"{PE_DISABLED} Disabled", parse_mode='html')
                    await event.answer()
                    return
                maint, msg = check_feature_maintenance("indnum3")
                if maint:
                    await event.reply(f"{PE_TOOLS} {msg}", parse_mode='html')
                    await event.answer()
                    return
                ADMIN_STATE[uid] = 'INDNUM3'
                await event.reply(f"{PE_INDIA} ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴛʀᴀᴄᴋɪɴɢ\n<i>6363016966, 9876543210</i>", parse_mode='html')
                await event.answer()
                return
            
            elif data == "menu_invite":
                user = get_user(uid)
                me = await client.get_me()
                link = f"https://t.me/{me.username}?start={user['invite_code']}"
                await event.reply(f"{PE_INVITE} ɪɴᴠɪᴛᴇ (+{INVITE_CREDITS}ᴄʀ)\n<code>{link}</code>", parse_mode='html')
                await event.answer()
                return
            
            elif data == "menu_redeem":
                ADMIN_STATE[uid] = 'REDEEM'
                await event.reply(f"{PE_TICKET} ᴇɴᴛᴇʀ ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ:\n<i>HEX-XXXXXXXXXX</i>", parse_mode='html')
                await event.answer()
                return
            
            elif data == "menu_help":
                await show_help_inline(event)
                return
            
            elif data == "menu_about":
                await show_about_inline(event)
                return
            
            elif data == "menu_stats":
                await show_stats_inline(event)
                return
            
            elif data == "menu_admin":
                if uid == ADMIN_ID:
                    await show_admin_panel(event)
                    await event.answer()
                else:
                    await event.answer("❌ Unauthorized!", alert=True)
                return
            
            await event.answer()
    except Exception as e:
        print(f"Callback error: {e}")

@client.on(events.NewMessage)
async def message_handler(event):
    try:
        if event.is_private:
            uid = event.sender_id
            txt = event.raw_text.strip()
            s = get_settings()
            
            # Skip commands
            if txt.startswith('/'):
                return
            
            if s.get("maintenance_mode", False) and uid != ADMIN_ID:
                sent = await event.reply(f"{PE_TOOLS} Under maintenance", parse_mode='html')
                asyncio.create_task(schedule_delete(sent, AUTO_DELETE_TIME))
                return
            
            if uid != ADMIN_ID:
                user = get_user(uid)
                if not user.get("verified"):
                    if await check_channel(uid):
                        user["verified"] = True
                        save_user(uid, user)
                        await show_main_menu(event)
                        return
                    await show_verification_page(event)
                    return
            
            # Handle admin state
            if uid in ADMIN_STATE:
                state = ADMIN_STATE.pop(uid)
                
                if state == "gen":
                    try:
                        cr = int(txt)
                        code = generate_redeem_code(cr)
                        sent = await event.reply(f"{PE_CHECK} <code>{code}</code> | {PE_CREDIT} {cr}cr", parse_mode='html')
                    except:
                        sent = await event.reply(f"{PE_CROSS} Invalid number", parse_mode='html')
                    asyncio.create_task(schedule_delete(sent, AUTO_DELETE_TIME))
                    return
                
                elif state == "credit":
                    p = txt.split()
                    if len(p) >= 2:
                        bal = add_credits(p[0], int(p[1]))
                        sent = await event.reply(f"{PE_CHECK} +{p[1]} | {bal}", parse_mode='html')
                    else:
                        sent = await event.reply(f"{PE_CROSS} Format: ID AMOUNT", parse_mode='html')
                    asyncio.create_task(schedule_delete(sent, AUTO_DELETE_TIME))
                    return
                
                elif state == "bcast":
                    users = load_json(USERS_FILE)
                    cnt = 0
                    for u in users:
                        try:
                            await client.send_message(int(u), f"{PE_BOLT} {txt}", parse_mode='html')
                            cnt += 1
                        except:
                            pass
                    sent = await event.reply(f"{PE_CHECK} Sent: {cnt}", parse_mode='html')
                    asyncio.create_task(schedule_delete(sent, AUTO_DELETE_TIME))
                    return
                
                elif state == "REDEEM":
                    if txt.upper().startswith("HEX-"):
                        success, msg = redeem_code(uid, txt)
                    else:
                        msg = f"{PE_CROSS} Invalid code format!"
                    sent = await event.reply(f"{msg}", parse_mode='html')
                    asyncio.create_task(schedule_delete(sent, AUTO_DELETE_TIME))
                    return
                
                elif state in ['TG', 'IFSC', 'SHORTLINK', 'MOBILE', 'AADHAAR', 'VEHICLE', 'GST', 'PAK', 'INDNUM', 'INDNUM3']:
                    user = get_user(uid)
                    if user.get("credits", 0) <= 0:
                        sent = await event.reply(f"{PE_CROSS} No credits! +10 daily | +3 invite", parse_mode='html')
                        asyncio.create_task(schedule_delete(sent, AUTO_DELETE_TIME))
                        return
                    
                    await run_query(event, state, txt)
                    return
            
            if uid in ADMIN_STATE:
                return
            
            # Handle keyboard navigation - check for exact button text
            if txt == "ɴᴇxᴛ ᴘᴀɢᴇ ➜":
                await show_main_menu(event, page=2)
                return
            elif txt == "⬅ ʙᴀᴄᴋ ᴛᴏ ᴍᴇɴᴜ":
                await show_main_menu(event, page=1)
                return
            
            # Handle admin panel
            if txt == "ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ" and uid == ADMIN_ID:
                await show_admin_panel(event)
                return
            
            # Handle feature buttons
            feature_map = {
                "ᴛɢ ɪᴅ ➜ ɴᴜᴍʙᴇʀ": ("tgid", "TG"),
                "ɪꜰꜱᴄ ɪɴꜰᴏ": ("ifsc", "IFSC"),
                "ʟɪɴᴋ ʙʏᴘᴀꜱꜱ": ("bypass", "SHORTLINK"),
                "ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ": ("mobile", "MOBILE"),
                "ᴀᴀᴅʜᴀʀ ɪɴꜰᴏ": ("aadhaar", "AADHAAR"),
                "ʀᴄ ᴅᴇᴛᴀɪʟꜱ": ("rc", "VEHICLE"),
                "ɢꜱᴛ ʟᴏᴏᴋᴜᴘ": ("gst", "GST"),
                "ᴘᴀᴋ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ": ("pak", "PAK"),
                "ɪɴᴅ ɴᴜᴍ ɪɴꜰᴏ 𝟸": ("indnum", "INDNUM"),
                "ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ 𝟹": ("indnum3", "INDNUM3"),
                "ɪɴᴠɪᴛᴇ & ᴇᴀʀɴ": ("invite", None),
                "ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ": ("redeem", None),
                "ʜᴇʟᴘ": ("help", None),
                "ᴀʙᴏᴜᴛ": ("about", None),
                "ꜱᴛᴀᴛꜱ": ("stats", None),
                "ɪᴅᴇɴᴛɪᴛʏ ᴛᴏᴏʟꜱ": ("identity", None),
                "ᴏꜱɪɴᴛ ᴛᴏᴏʟꜱ": ("osint", None),
                "ᴠɪᴘ ᴘʀᴇᴍɪᴜᴍ": ("vip", None),
                "ᴅᴀɪʟʏ ꜱᴘɪɴ": ("spin", None),
                "ᴅᴀꜱʜʙᴏᴀʀᴅ": ("dashboard", None),
                "ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ": ("leaderboard", None)
            }
            
            if txt in feature_map:
                feature, mode = feature_map[txt]
                
                if feature == "invite":
                    user = get_user(uid)
                    me = await client.get_me()
                    link = f"https://t.me/{me.username}?start={user['invite_code']}"
                    sent = await event.reply(f"{PE_INVITE} ɪɴᴠɪᴛᴇ (+{INVITE_CREDITS}ᴄʀ)\n<code>{link}</code>", parse_mode='html')
                    asyncio.create_task(schedule_delete(sent, 120))
                    return
                
                elif feature == "redeem":
                    ADMIN_STATE[uid] = 'REDEEM'
                    sent = await event.reply(f"{PE_TICKET} ᴇɴᴛᴇʀ ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ:\n<i>HEX-XXXXXXXXXX</i>", parse_mode='html')
                    asyncio.create_task(schedule_delete(sent, 30))
                    return
                
                elif feature == "help":
                    await show_help_inline(event)
                    return
                
                elif feature == "about":
                    await show_about_inline(event)
                    return
                
                elif feature == "stats":
                    await show_stats_inline(event)
                    return
                
                elif feature == "identity":
                    sent = await event.reply(f"{PE_IDENTITY} <b>ɪᴅᴇɴᴛɪᴛʏ ᴛᴏᴏʟꜱ</b>\n\n{PE_CARD} ᴀᴀᴅʜᴀʀ ɪɴꜰᴏ\n{PE_USER} ᴘᴀɴ ᴄᴀʀᴅ ɪɴꜰᴏ\n{PE_PHONE2} ᴍᴏʙɪʟᴇ ɴᴜᴍʙᴇʀ ʟᴏᴏᴋᴜᴘ", parse_mode='html')
                    asyncio.create_task(schedule_delete(sent, 30))
                    return
                
                elif feature == "osint":
                    sent = await event.reply(f"{PE_OSINT} <b>ᴏꜱɪɴᴛ ᴛᴏᴏʟꜱ</b>\n\n{PE_SEARCH} ᴛɢ ɪᴅ ʟᴏᴏᴋᴜᴘ\n{PE_LINK} ʟɪɴᴋ ʙʏᴘᴀꜱꜱ\n{PE_NETWORK} ɪᴘ ʟᴏᴏᴋᴜᴘ", parse_mode='html')
                    asyncio.create_task(schedule_delete(sent, 30))
                    return
                
                elif feature == "vip":
                    sent = await event.reply(f"{PE_VIP} <b>ᴠɪᴘ ᴘʀᴇᴍɪᴜᴍ</b>\n\n{PE_CREDIT} ᴇxᴛʀᴀ ᴄʀᴇᴅɪᴛꜱ\n{PE_ROCKET} ᴘʀɪᴏʀɪᴛʏ Qᴜᴇʀɪᴇꜱ\n{PE_STAR} ᴀᴄᴄᴇꜱꜱ ᴛᴏ ᴀʟʟ ꜰᴇᴀᴛᴜʀᴇꜱ", parse_mode='html')
                    asyncio.create_task(schedule_delete(sent, 30))
                    return
                
                elif feature == "spin":
                    rewards = [1, 2, 3, 5, 8, 10]
                    reward = random.choice(rewards)
                    bal = add_credits(uid, reward)
                    sent = await event.reply(f"{PE_SPIN} 🎰 <b>ᴅᴀɪʟʏ ꜱᴘɪɴ</b>\n\n{PE_GIFT} ʏᴏᴜ ᴡᴏɴ <b>+{reward}</b> ᴄʀᴇᴅɪᴛꜱ!\n{PE_CREDIT} ɴᴇᴡ ʙᴀʟᴀɴᴄᴇ: <b>{bal}</b>", parse_mode='html')
                    asyncio.create_task(schedule_delete(sent, 30))
                    return
                
                elif feature == "dashboard":
                    user = get_user(uid)
                    txt_msg = f"{PE_DASHBOARD} <b>ʏᴏᴜʀ ᴅᴀꜱʜʙᴏᴀʀᴅ</b>\n\n{PE_USER} <b>ᴜꜱᴇʀ:</b> {event.sender.first_name}\n{PE_CREDIT} <b>ᴄʀᴇᴅɪᴛꜱ:</b> {user.get('credits',0)}\n{PE_SEARCH} <b>Qᴜᴇʀɪᴇꜱ:</b> {user.get('total_queries',0)}\n{PE_INVITE} <b>ɪɴᴠɪᴛᴇꜱ:</b> {user.get('invites',0)}"
                    sent = await event.reply(txt_msg, parse_mode='html')
                    asyncio.create_task(schedule_delete(sent, 30))
                    return
                
                elif feature == "leaderboard":
                    users = load_json(USERS_FILE)
                    sorted_users = sorted(users.items(), key=lambda x: x[1].get('credits', 0), reverse=True)[:10]
                    txt_msg = f"{PE_LEADERBOARD} <b>ᴛᴏᴘ 10 ᴜꜱᴇʀꜱ</b>\n\n"
                    for i, (uid_, data) in enumerate(sorted_users, 1):
                        try:
                            user = await client.get_entity(int(uid_))
                            name = user.first_name[:15]
                        except:
                            name = f"ᴜꜱᴇʀ {i}"
                        txt_msg += f"{i}. {PE_USER} {name} - {PE_CREDIT} {data.get('credits',0)}\n"
                    sent = await event.reply(txt_msg, parse_mode='html')
                    asyncio.create_task(schedule_delete(sent, 30))
                    return
                
                elif feature and mode:
                    if not s.get(f"{feature}_enabled", True):
                        sent = await event.reply(f"{PE_DISABLED} Disabled", parse_mode='html')
                        asyncio.create_task(schedule_delete(sent, AUTO_DELETE_TIME))
                        return
                    maint, msg = check_feature_maintenance(feature)
                    if maint:
                        sent = await event.reply(f"{PE_TOOLS} {msg}", parse_mode='html')
                        asyncio.create_task(schedule_delete(sent, AUTO_DELETE_TIME))
                        return
                    ADMIN_STATE[uid] = mode
                    prompts = {
                        "TG": f"{PE_PHONE} ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ ᴛᴏ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ",
                        "IFSC": f"{PE_BANK} ʙᴀɴᴋ ɪꜰꜱᴄ ᴄᴏᴅᴇ",
                        "SHORTLINK": f"{PE_LINK} ʟɪɴᴋ ʙʏᴘᴀꜱꜱ",
                        "MOBILE": f"{PE_INDIA} ɪɴᴅɪᴀɴ ᴍᴏʙɪʟᴇ ɴᴜᴍʙᴇʀ",
                        "AADHAAR": f"{PE_CARD} ᴀᴀᴅʜᴀʀ ɴᴜᴍʙᴇʀ",
                        "VEHICLE": f"{PE_CAR} ᴠᴇʜɪᴄʟᴇ ɴᴜᴍʙᴇʀ",
                        "GST": f"{PE_CARD} ɢꜱᴛ ɴᴜᴍʙᴇʀ",
                        "PAK": f"{PE_PAK} ᴘᴀᴋɪꜱᴛᴀɴ ɴᴜᴍʙᴇʀ",
                        "INDNUM": f"{PE_PHONE2} ᴀᴅᴠᴀɴᴄᴇᴅ ɴᴜᴍʙᴇʀ",
                        "INDNUM3": f"{PE_INDIA} ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴛʀᴀᴄᴋɪɴɢ"
                    }
                    examples = {
                        "TG": "7123181749, 6884112825",
                        "IFSC": "SBIN0001234, HDFC0001234",
                        "SHORTLINK": "https://indianshortner.in/xxxx",
                        "MOBILE": "9876543210, 8123456789",
                        "AADHAAR": "123456789012",
                        "VEHICLE": "KA01AB3256, DL1CX1234",
                        "GST": "19BOKPS7056D1ZI",
                        "PAK": "923078750447",
                        "INDNUM": "6363016966, 9876543210",
                        "INDNUM3": "6363016966, 9876543210"
                    }
                    sent = await event.reply(f"{prompts.get(mode, '')}\n<i>{examples.get(mode, '')}</i>", parse_mode='html')
                    asyncio.create_task(schedule_delete(sent, 30))
                    return
            
            # If no match, show main menu
            await show_main_menu(event)
            
    except Exception as e:
        print(f"Message handler error: {e}")
        try:
            await show_main_menu(event)
        except:
            pass

def check_feature_maintenance(feature_key):
    s = get_settings()
    if s.get(f"maint_{feature_key}", False):
        return True, s.get(f"maint_msg_{feature_key}", f"{PE_TOOLS} Under maintenance.")
    return False, ""

# ============================================================
# MAIN
# ============================================================

print("🔄 Hex Terminal Premium Starting...")
print("🎨 Colored Keyboard Buttons with Premium Emojis!")
print("🤖 Telethon Version with Full Features!")

try:
    subprocess.run([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4"], capture_output=True, timeout=30)
except:
    pass

print(f"✅ {BOT_NAME} Ready!")
print(f"💎 Premium emojis in ALL buttons and text!")
print(f"⭐ Colored Keyboard Buttons with Premium Emoji Icons")
print("🚀 Bot is running...")

client.run_until_disconnected()