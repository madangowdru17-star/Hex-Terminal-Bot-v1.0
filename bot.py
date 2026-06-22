import random
import asyncio
import os
import json
import re
import socket
import aiohttp
import subprocess
import sys
import string
from datetime import datetime, timedelta
from telethon import TelegramClient, events, types, functions
from telethon.tl.types import (
    KeyboardButton, 
    KeyboardButtonStyle, 
    ReplyKeyboardMarkup,
    KeyboardButtonRow
)

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
# PREMIUM EMOJI IDs - For text messages and button icons
# ============================================================

# Premium Emoji IDs for text messages
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

# Premium Emoji IDs for button icons (same as above, used in KeyboardButtonStyle)
BUTTON_ICON_IDS = {
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

# --- PREMIUM EMOJIS FOR TEXT MESSAGES ---
def get_pe(key):
    return f'<tg-emoji emoji-id="{PREMIUM_EMOJI_IDS[key]}"> </tg-emoji>'

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

# --- Initialize Client ---
client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

ADMIN_STATE = {}
USER_STATE = {}
USER_PAGE = {}

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
        member = await client.get_participants(CHANNEL_ID, limit=1)
        return True
    except:
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
# CREATE COLORED KEYBOARD BUTTONS WITH PREMIUM EMOJIS
# ============================================================

def create_colored_button(text: str, icon_id: int = None, style_type: str = "primary"):
    """
    Create a colored keyboard button with premium emoji icon
    style_type: "primary" (blue), "success" (green), "danger" (red)
    """
    if style_type == "primary":
        style = KeyboardButtonStyle(bg_primary=True, icon=icon_id)
    elif style_type == "success":
        style = KeyboardButtonStyle(bg_success=True, icon=icon_id)
    elif style_type == "danger":
        style = KeyboardButtonStyle(bg_danger=True, icon=icon_id)
    else:
        style = KeyboardButtonStyle(icon=icon_id)
    
    return KeyboardButton(text=text, style=style)

def create_button_row(buttons: list) -> KeyboardButtonRow:
    """Create a row of keyboard buttons"""
    return KeyboardButtonRow(buttons=buttons)

def create_keyboard_markup(rows: list, resize: bool = True) -> ReplyKeyboardMarkup:
    """Create reply keyboard markup from rows"""
    return ReplyKeyboardMarkup(
        rows=rows,
        resize=resize
    )

# ============================================================
# KEYBOARD MENU - COLORED BUTTONS WITH PREMIUM EMOJIS
# ============================================================

def get_colored_keyboard(page: int = 1):
    """Get colored keyboard menu with premium emoji icons"""
    
    if page == 1:
        rows = [
            create_button_row([
                create_colored_button("TG ID ➜ NUMBER", BUTTON_ICON_IDS["phone"], "primary"),
                create_colored_button("IFSC INFO", BUTTON_ICON_IDS["bank"], "primary")
            ]),
            create_button_row([
                create_colored_button("LINK BYPASS", BUTTON_ICON_IDS["link"], "warning")
            ]),
            create_button_row([
                create_colored_button("AADHAR INFO", BUTTON_ICON_IDS["card"], "primary"),
                create_colored_button("IND NUMBER INFO", BUTTON_ICON_IDS["india"], "success")
            ]),
            create_button_row([
                create_colored_button("RC DETAILS", BUTTON_ICON_IDS["car"], "info"),
                create_colored_button("GST LOOKUP", BUTTON_ICON_IDS["card"], "warning")
            ]),
            create_button_row([
                create_colored_button("PAK NUMBER INFO", BUTTON_ICON_IDS["pak"], "primary"),
                create_colored_button("IND NUM INFO 2", BUTTON_ICON_IDS["phone2"], "success")
            ]),
            create_button_row([
                create_colored_button("IND NUMBER INFO 3", BUTTON_ICON_IDS["india"], "danger")
            ]),
            create_button_row([
                create_colored_button("INVITE & EARN", BUTTON_ICON_IDS["invite"], "success"),
                create_colored_button("REDEEM CODE", BUTTON_ICON_IDS["ticket"], "warning")
            ]),
            create_button_row([
                create_colored_button("HELP", BUTTON_ICON_IDS["help"], "info"),
                create_colored_button("ABOUT", BUTTON_ICON_IDS["about"], "primary")
            ]),
            create_button_row([
                create_colored_button("STATS", BUTTON_ICON_IDS["stats"], "info"),
                create_colored_button("ADMIN PANEL", BUTTON_ICON_IDS["admin"], "danger") if ADMIN_ID else None
            ]),
            create_button_row([
                create_colored_button("NEXT PAGE", BUTTON_ICON_IDS["next"], "primary")
            ])
        ]
    else:
        rows = [
            create_button_row([
                create_colored_button("IDENTITY TOOLS", BUTTON_ICON_IDS["identity"], "primary"),
                create_colored_button("OSINT TOOLS", BUTTON_ICON_IDS["osint"], "success")
            ]),
            create_button_row([
                create_colored_button("VIP PREMIUM", BUTTON_ICON_IDS["vip"], "danger"),
                create_colored_button("DAILY SPIN", BUTTON_ICON_IDS["spin"], "warning")
            ]),
            create_button_row([
                create_colored_button("DASHBOARD", BUTTON_ICON_IDS["dashboard"], "primary"),
                create_colored_button("LEADERBOARD", BUTTON_ICON_IDS["leaderboard"], "info")
            ]),
            create_button_row([
                create_colored_button("BACK TO MENU", BUTTON_ICON_IDS["back"], "danger")
            ])
        ]
    
    # Filter out None rows
    filtered_rows = []
    for row in rows:
        if row.buttons:
            filtered_rows.append(row)
    
    return create_keyboard_markup(filtered_rows)

# ============================================================
# SEND MESSAGE WITH KEYBOARD
# ============================================================

async def send_message_with_keyboard(chat_id, text, keyboard, parse_mode=None):
    """Send message with reply keyboard markup"""
    return await client.send_message(
        chat_id,
        text,
        reply_markup=keyboard,
        parse_mode=parse_mode
    )

# ============================================================
# MAIN MENU
# ============================================================

async def show_verification_page(event):
    try:
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
        
        # Verification buttons
        rows = [
            create_button_row([
                create_colored_button("JOIN CHANNEL", BUTTON_ICON_IDS["link"], "primary")
            ]),
            create_button_row([
                create_colored_button("I'VE JOINED - VERIFY", BUTTON_ICON_IDS["check"], "success")
            ])
        ]
        keyboard = create_keyboard_markup(rows)
        
        sent = await event.reply(caption, reply_markup=keyboard, parse_mode='html')
        asyncio.create_task(schedule_delete(sent, 120))
    except Exception as e:
        print(f"Verification page error: {e}")

async def main_menu(event, page: int = 1):
    """Main menu with colored keyboard buttons and premium emojis"""
    try:
        uid = event.sender_id
        is_admin = uid == ADMIN_ID
        user = get_user(uid)
        cr = user.get("credits", 0)
        
        keyboard = get_colored_keyboard(page)
        
        txt = (
            f"{PE_DIAMOND} {BOT_NAME} {PE_DIAMOND}\n"
            f"{PE_USER} <b>ᴡᴇʟᴄᴏᴍᴇ ʙᴀᴄᴋ,</b> <code>{event.sender.first_name}</code>\n\n"
            f"{PE_DASHBOARD} <b>ʏᴏᴜʀ ᴅᴀꜱʜʙᴏᴀʀᴅ</b>\n"
            f"┃ {PE_CREDIT} <b>ᴄʀᴇᴅɪᴛꜱ:</b> {cr}\n"
            f"┃ {PE_SPIN} <b>ᴅᴀɪʟʏ ꜱᴘɪɴ:</b> +3 ꜰʀᴇᴇ\n"
            f"┃ {PE_VIP} <b>ᴠɪᴘ ᴘʀᴇᴍɪᴜᴍ:</b> {user.get('total_queries',0)} ꜱᴇᴀʀᴄʜ\n\n"
            f"{PE_STAR} <b>ɴɪᴄʜᴇ ᴅɪʏᴇ ɢʏᴇ ʙᴜᴛᴛᴏɴ ᴜꜱᴇ ᴋʀᴇ</b>\n"
            f"{PE_HELP} <code>/help</code> ᴛᴏ ꜱᴇᴇ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅꜱ\n\n"
            f"{PE_CROWN} <b>ᴅᴇᴠ:</b> @Hexh4ckerOFC\n"
            f"{PE_ROCKET} <b>ᴘᴀɢᴇ:</b> {page}/2"
        )
        
        sent = await event.reply(txt, reply_markup=keyboard, parse_mode='html')
        asyncio.create_task(schedule_delete(sent, AUTO_DELETE_TIME))
        
        USER_PAGE[str(event.sender_id)] = page
    except Exception as e:
        print(f"Main menu error: {e}")

# ============================================================
# BOT COMMAND HANDLERS
# ============================================================

@client.on(events.NewMessage(pattern='/start'))
async def start_command(event):
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
                            f"{PE_GIFT} +{cr} ᴄʀᴇᴅɪᴛꜱ! ɴᴇᴡ ᴜꜱᴇʀ ᴊᴏɪɴᴇᴅ!"
                        )
                    except: pass
                    break
        
        user = get_user(uid)
        
        if uid == ADMIN_ID:
            user["verified"] = True
            save_user(uid, user)
            await main_menu(event)
            return
        
        if not user.get("verified"):
            if await check_channel(uid):
                user["verified"] = True
                save_user(uid, user)
                await main_menu(event)
                return
            await show_verification_page(event)
            return
        
        await main_menu(event)
    except Exception as e:
        print(f"Start error: {e}")

# ============================================================
# MESSAGE HANDLER - HANDLES ALL BUTTON CLICKS
# ============================================================

@client.on(events.NewMessage)
async def handle_messages(event):
    try:
        if event.is_private is False:
            return
        
        uid = event.sender_id
        txt = event.raw_text
        s = get_settings()
        
        # Ignore commands
        if txt.startswith('/'):
            return
        
        if s.get("maintenance_mode", False) and uid != ADMIN_ID:
            sent = await event.reply(f"{PE_TOOLS} Under maintenance", parse_mode='html')
            asyncio.create_task(schedule_delete(sent))
            return
        
        if uid != ADMIN_ID:
            user = get_user(uid)
            if not user.get("verified"):
                if await check_channel(uid):
                    user["verified"] = True
                    save_user(uid, user)
                    await main_menu(event)
                    return
                await show_verification_page(event)
                return
        
        # Handle keyboard navigation
        if txt == "NEXT PAGE":
            await main_menu(event, page=2)
            return
        elif txt == "BACK TO MENU":
            await main_menu(event, page=1)
            return
        
        # Handle admin panel via keyboard
        if txt == "ADMIN PANEL" and uid == ADMIN_ID:
            await admin_panel(event)
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
                asyncio.create_task(schedule_delete(sent))
                return
            
            elif state == "credit":
                p = txt.split()
                if len(p) >= 2:
                    bal = add_credits(p[0], int(p[1]))
                    sent = await event.reply(f"{PE_CHECK} +{p[1]} | {bal}", parse_mode='html')
                else:
                    sent = await event.reply(f"{PE_CROSS} Format: ID AMOUNT", parse_mode='html')
                asyncio.create_task(schedule_delete(sent))
                return
            
            elif state == "bcast":
                users = load_json(USERS_FILE)
                cnt = 0
                for u in users:
                    try:
                        await client.send_message(int(u), f"{PE_BOLT} {txt}")
                        cnt += 1
                    except: pass
                sent = await event.reply(f"{PE_CHECK} Sent: {cnt}", parse_mode='html')
                asyncio.create_task(schedule_delete(sent))
                return
            
            elif state == "REDEEM":
                if txt.upper().startswith("HEX-"):
                    success, msg = redeem_code(uid, txt)
                else:
                    msg = f"{PE_CROSS} Invalid code format!"
                sent = await event.reply(f"{msg}", parse_mode='html')
                asyncio.create_task(schedule_delete(sent))
                return
            
            elif state in ['TG', 'IFSC', 'SHORTLINK', 'MOBILE', 'AADHAAR', 'VEHICLE', 'GST', 'PAK', 'INDNUM', 'INDNUM3']:
                user = get_user(uid)
                if user.get("credits", 0) <= 0:
                    sent = await event.reply(f"{PE_CROSS} No credits! +10 daily | +3 invite", parse_mode='html')
                    asyncio.create_task(schedule_delete(sent))
                    return
                
                await run_query(event, state, txt)
                return
        
        if uid in ADMIN_STATE:
            return
        
        # Handle feature buttons from keyboard
        if txt == "TG ID ➜ NUMBER":
            if not s.get("tgid_enabled", True):
                sent = await event.reply(f"{PE_DISABLED} Disabled", parse_mode='html')
                asyncio.create_task(schedule_delete(sent))
                return
            maint, msg = check_feature_maintenance("tgid")
            if maint:
                sent = await event.reply(f"{PE_TOOLS} {msg}", parse_mode='html')
                asyncio.create_task(schedule_delete(sent))
                return
            ADMIN_STATE[uid] = 'TG'
            sent = await event.reply(f"{PE_PHONE} ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ ᴛᴏ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ\n<i>7123181749, 6884112825</i>", parse_mode='html')
            asyncio.create_task(schedule_delete(sent))
            return
        
        elif txt == "IFSC INFO":
            if not s.get("ifsc_enabled", True):
                sent = await event.reply(f"{PE_DISABLED} Disabled", parse_mode='html')
                asyncio.create_task(schedule_delete(sent))
                return
            maint, msg = check_feature_maintenance("ifsc")
            if maint:
                sent = await event.reply(f"{PE_TOOLS} {msg}", parse_mode='html')
                asyncio.create_task(schedule_delete(sent))
                return
            ADMIN_STATE[uid] = 'IFSC'
            sent = await event.reply(f"{PE_BANK} ʙᴀɴᴋ ɪꜰꜱᴄ ᴄᴏᴅᴇ\n<i>SBIN0001234, HDFC0001234</i>", parse_mode='html')
            asyncio.create_task(schedule_delete(sent))
            return
        
        elif txt == "LINK BYPASS":
            if not s.get("bypass_enabled", True):
                sent = await event.reply(f"{PE_DISABLED} Disabled", parse_mode='html')
                asyncio.create_task(schedule_delete(sent))
                return
            maint, msg = check_feature_maintenance("bypass")
            if maint:
                sent = await event.reply(f"{PE_TOOLS} {msg}", parse_mode='html')
                asyncio.create_task(schedule_delete(sent))
                return
            ADMIN_STATE[uid] = 'SHORTLINK'
            sent = await event.reply(f"{PE_LINK} ʟɪɴᴋ ʙʏᴘᴀꜱꜱ\n<i>https://indianshortner.in/xxxx</i>", parse_mode='html')
            asyncio.create_task(schedule_delete(sent))
            return
        
        elif txt == "IND NUMBER INFO":
            if not s.get("mobile_enabled", True):
                sent = await event.reply(f"{PE_DISABLED} Disabled", parse_mode='html')
                asyncio.create_task(schedule_delete(sent))
                return
            maint, msg = check_feature_maintenance("mobile")
            if maint:
                sent = await event.reply(f"{PE_TOOLS} {msg}", parse_mode='html')
                asyncio.create_task(schedule_delete(sent))
                return
            ADMIN_STATE[uid] = 'MOBILE'
            sent = await event.reply(f"{PE_INDIA} ɪɴᴅɪᴀɴ ᴍᴏʙɪʟᴇ ɴᴜᴍʙᴇʀ\n<i>9876543210, 8123456789</i>", parse_mode='html')
            asyncio.create_task(schedule_delete(sent))
            return
        
        elif txt == "AADHAR INFO":
            if not s.get("aadhaar_enabled", True):
                sent = await event.reply(f"{PE_DISABLED} Disabled", parse_mode='html')
                asyncio.create_task(schedule_delete(sent))
                return
            maint, msg = check_feature_maintenance("aadhaar")
            if maint:
                sent = await event.reply(f"{PE_TOOLS} {msg}", parse_mode='html')
                asyncio.create_task(schedule_delete(sent))
                return
            ADMIN_STATE[uid] = 'AADHAAR'
            sent = await event.reply(f"{PE_CARD} ᴀᴀᴅʜᴀʀ ɴᴜᴍʙᴇʀ\n<i>123456789012</i>", parse_mode='html')
            asyncio.create_task(schedule_delete(sent))
            return
        
        elif txt == "RC DETAILS":
            if not s.get("rc_enabled", True):
                sent = await event.reply(f"{PE_DISABLED} Disabled", parse_mode='html')
                asyncio.create_task(schedule_delete(sent))
                return
            maint, msg = check_feature_maintenance("rc")
            if maint:
                sent = await event.reply(f"{PE_TOOLS} {msg}", parse_mode='html')
                asyncio.create_task(schedule_delete(sent))
                return
            ADMIN_STATE[uid] = 'VEHICLE'
            sent = await event.reply(f"{PE_CAR} ᴠᴇʜɪᴄʟᴇ ɴᴜᴍʙᴇʀ\n<i>KA01AB3256, DL1CX1234</i>", parse_mode='html')
            asyncio.create_task(schedule_delete(sent))
            return
        
        elif txt == "GST LOOKUP":
            if not s.get("gst_enabled", True):
                sent = await event.reply(f"{PE_DISABLED} Disabled", parse_mode='html')
                asyncio.create_task(schedule_delete(sent))
                return
            maint, msg = check_feature_maintenance("gst")
            if maint:
                sent = await event.reply(f"{PE_TOOLS} {msg}", parse_mode='html')
                asyncio.create_task(schedule_delete(sent))
                return
            ADMIN_STATE[uid] = 'GST'
            sent = await event.reply(f"{PE_CARD} ɢꜱᴛ ɴᴜᴍʙᴇʀ\n<i>19BOKPS7056D1ZI</i>", parse_mode='html')
            asyncio.create_task(schedule_delete(sent))
            return
        
        elif txt == "PAK NUMBER INFO":
            if not s.get("pak_enabled", True):
                sent = await event.reply(f"{PE_DISABLED} Disabled", parse_mode='html')
                asyncio.create_task(schedule_delete(sent))
                return
            maint, msg = check_feature_maintenance("pak")
            if maint:
                sent = await event.reply(f"{PE_TOOLS} {msg}", parse_mode='html')
                asyncio.create_task(schedule_delete(sent))
                return
            ADMIN_STATE[uid] = 'PAK'
            sent = await event.reply(f"{PE_PAK} ᴘᴀᴋɪꜱᴛᴀɴ ɴᴜᴍʙᴇʀ\n<i>923078750447</i>", parse_mode='html')
            asyncio.create_task(schedule_delete(sent))
            return
        
        elif txt == "IND NUM INFO 2":
            if not s.get("indnum_enabled", True):
                sent = await event.reply(f"{PE_DISABLED} Disabled", parse_mode='html')
                asyncio.create_task(schedule_delete(sent))
                return
            maint, msg = check_feature_maintenance("indnum")
            if maint:
                sent = await event.reply(f"{PE_TOOLS} {msg}", parse_mode='html')
                asyncio.create_task(schedule_delete(sent))
                return
            ADMIN_STATE[uid] = 'INDNUM'
            sent = await event.reply(f"{PE_PHONE2} ᴀᴅᴠᴀɴᴄᴇᴅ ɴᴜᴍʙᴇʀ\n<i>6363016966, 9876543210</i>", parse_mode='html')
            asyncio.create_task(schedule_delete(sent))
            return
        
        elif txt == "IND NUMBER INFO 3":
            if not s.get("indnum3_enabled", True):
                sent = await event.reply(f"{PE_DISABLED} Disabled", parse_mode='html')
                asyncio.create_task(schedule_delete(sent))
                return
            maint, msg = check_feature_maintenance("indnum3")
            if maint:
                sent = await event.reply(f"{PE_TOOLS} {msg}", parse_mode='html')
                asyncio.create_task(schedule_delete(sent))
                return
            ADMIN_STATE[uid] = 'INDNUM3'
            sent = await event.reply(f"{PE_INDIA} ɪɴᴅɪᴀɴ ɴᴜᴍʙᴇʀ ᴛʀᴀᴄᴋɪɴɢ\n<i>6363016966, 9876543210</i>", parse_mode='html')
            asyncio.create_task(schedule_delete(sent))
            return
        
        elif txt == "INVITE & EARN":
            user = get_user(uid)
            bot_info = await client.get_me()
            link = f"https://t.me/{bot_info.username}?start={user['invite_code']}"
            sent = await event.reply(f"{PE_INVITE} ɪɴᴠɪᴛᴇ (+{INVITE_CREDITS}ᴄʀ)\n<code>{link}</code>", parse_mode='html')
            asyncio.create_task(schedule_delete(sent, 120))
            return
        
        elif txt == "REDEEM CODE":
            ADMIN_STATE[uid] = 'REDEEM'
            sent = await event.reply(f"{PE_TICKET} ᴇɴᴛᴇʀ ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ:\n<i>HEX-XXXXXXXXXX</i>", parse_mode='html')
            asyncio.create_task(schedule_delete(sent, 30))
            return
        
        elif txt == "HELP":
            await show_help(event)
            return
        
        elif txt == "ABOUT":
            await show_about(event)
            return
        
        elif txt == "STATS":
            await show_stats(event)
            return
        
        elif txt == "IDENTITY TOOLS":
            sent = await event.reply(f"{PE_IDENTITY} <b>ɪᴅᴇɴᴛɪᴛʏ ᴛᴏᴏʟꜱ</b>\n\n{PE_CARD} ᴀᴀᴅʜᴀʀ ɪɴꜰᴏ\n{PE_USER} ᴘᴀɴ ᴄᴀʀᴅ ɪɴꜰᴏ\n{PE_PHONE2} ᴍᴏʙɪʟᴇ ɴᴜᴍʙᴇʀ ʟᴏᴏᴋᴜᴘ", parse_mode='html')
            asyncio.create_task(schedule_delete(sent, 30))
            return
        
        elif txt == "OSINT TOOLS":
            sent = await event.reply(f"{PE_OSINT} <b>ᴏꜱɪɴᴛ ᴛᴏᴏʟꜱ</b>\n\n{PE_SEARCH} ᴛɢ ɪᴅ ʟᴏᴏᴋᴜᴘ\n{PE_LINK} ʟɪɴᴋ ʙʏᴘᴀꜱꜱ\n{PE_NETWORK} ɪᴘ ʟᴏᴏᴋᴜᴘ", parse_mode='html')
            asyncio.create_task(schedule_delete(sent, 30))
            return
        
        elif txt == "VIP PREMIUM":
            sent = await event.reply(f"{PE_VIP} <b>ᴠɪᴘ ᴘʀᴇᴍɪᴜᴍ</b>\n\n{PE_CREDIT} ᴇxᴛʀᴀ ᴄʀᴇᴅɪᴛꜱ\n{PE_ROCKET} ᴘʀɪᴏʀɪᴛʏ Qᴜᴇʀɪᴇꜱ\n{PE_STAR} ᴀᴄᴄᴇꜱꜱ ᴛᴏ ᴀʟʟ ꜰᴇᴀᴛᴜʀᴇꜱ", parse_mode='html')
            asyncio.create_task(schedule_delete(sent, 30))
            return
        
        elif txt == "DAILY SPIN":
            rewards = [1, 2, 3, 5, 8, 10]
            reward = random.choice(rewards)
            bal = add_credits(uid, reward)
            sent = await event.reply(f"{PE_SPIN} 🎰 <b>ᴅᴀɪʟʏ ꜱᴘɪɴ</b>\n\n{PE_GIFT} ʏᴏᴜ ᴡᴏɴ <b>+{reward}</b> ᴄʀᴇᴅɪᴛꜱ!\n{PE_CREDIT} ɴᴇᴡ ʙᴀʟᴀɴᴄᴇ: <b>{bal}</b>", parse_mode='html')
            asyncio.create_task(schedule_delete(sent, 30))
            return
        
        elif txt == "DASHBOARD":
            user = get_user(uid)
            txt_msg = f"{PE_DASHBOARD} <b>ʏᴏᴜʀ ᴅᴀꜱʜʙᴏᴀʀᴅ</b>\n\n{PE_USER} <b>ᴜꜱᴇʀ:</b> {event.sender.first_name}\n{PE_CREDIT} <b>ᴄʀᴇᴅɪᴛꜱ:</b> {user.get('credits',0)}\n{PE_SEARCH} <b>Qᴜᴇʀɪᴇꜱ:</b> {user.get('total_queries',0)}\n{PE_INVITE} <b>ɪɴᴠɪᴛᴇꜱ:</b> {user.get('invites',0)}"
            sent = await event.reply(txt_msg, parse_mode='html')
            asyncio.create_task(schedule_delete(sent, 30))
            return
        
        elif txt == "LEADERBOARD":
            users = load_json(USERS_FILE)
            sorted_users = sorted(users.items(), key=lambda x: x[1].get('credits', 0), reverse=True)[:10]
            txt_msg = f"{PE_LEADERBOARD} <b>ᴛᴏᴘ 10 ᴜꜱᴇʀꜱ</b>\n\n"
            for i, (uid_, data) in enumerate(sorted_users, 1):
                try:
                    user = await client.get_entity(int(uid_))
                    name = user.first_name[:15] if user.first_name else f"ᴜꜱᴇʀ {i}"
                except:
                    name = f"ᴜꜱᴇʀ {i}"
                txt_msg += f"{i}. {PE_USER} {name} - {PE_CREDIT} {data.get('credits',0)}\n"
            sent = await event.reply(txt_msg, parse_mode='html')
            asyncio.create_task(schedule_delete(sent, 30))
            return
        
        # If no match, show main menu
        await main_menu(event)
        
    except Exception as e:
        print(f"Message handler error: {e}")
        await main_menu(event)

# ============================================================
# ADMIN PANEL
# ============================================================

async def admin_panel(event):
    if event.sender_id != ADMIN_ID: return
    s = get_settings()
    ms = lambda key: "🔴" if s.get(f"maint_{key}") else "🟢"
    
    rows = [
        create_button_row([
            create_colored_button("GEN CODE", BUTTON_ICON_IDS["ticket"], "success"),
            create_colored_button("CODES", BUTTON_ICON_IDS["ticket"], "info")
        ]),
        create_button_row([
            create_colored_button("ADD CR", BUTTON_ICON_IDS["gift"], "warning"),
            create_colored_button("BCAST", BUTTON_ICON_IDS["bolt"], "primary")
        ]),
        create_button_row([
            create_colored_button(f"{'🔴' if s.get('maintenance_mode') else '🟢'} GLOBAL", BUTTON_ICON_IDS["tools"], "danger" if s.get('maintenance_mode') else "success")
        ]),
        create_button_row([
            create_colored_button(f"{'🟢' if s.get('tgid_enabled',True) else '🔴'} TG", BUTTON_ICON_IDS["phone"], "success" if s.get('tgid_enabled',True) else "danger"),
            create_colored_button(f"{ms('tgid')} M", BUTTON_ICON_IDS["tools"], "info")
        ]),
        create_button_row([
            create_colored_button(f"{'🟢' if s.get('ifsc_enabled',True) else '🔴'} IF", BUTTON_ICON_IDS["bank"], "success" if s.get('ifsc_enabled',True) else "danger"),
            create_colored_button(f"{ms('ifsc')} M", BUTTON_ICON_IDS["tools"], "info")
        ]),
        create_button_row([
            create_colored_button(f"{'🟢' if s.get('bypass_enabled',True) else '🔴'} BY", BUTTON_ICON_IDS["link"], "success" if s.get('bypass_enabled',True) else "danger"),
            create_colored_button(f"{ms('bypass')} M", BUTTON_ICON_IDS["tools"], "info")
        ]),
        create_button_row([
            create_colored_button(f"{'🟢' if s.get('mobile_enabled',True) else '🔴'} MO", BUTTON_ICON_IDS["phone2"], "success" if s.get('mobile_enabled',True) else "danger"),
            create_colored_button(f"{ms('mobile')} M", BUTTON_ICON_IDS["tools"], "info")
        ]),
        create_button_row([
            create_colored_button(f"{'🟢' if s.get('aadhaar_enabled',True) else '🔴'} AA", BUTTON_ICON_IDS["card"], "success" if s.get('aadhaar_enabled',True) else "danger"),
            create_colored_button(f"{ms('aadhaar')} M", BUTTON_ICON_IDS["tools"], "info")
        ]),
        create_button_row([
            create_colored_button(f"{'🟢' if s.get('rc_enabled',True) else '🔴'} RC", BUTTON_ICON_IDS["car"], "success" if s.get('rc_enabled',True) else "danger"),
            create_colored_button(f"{ms('rc')} M", BUTTON_ICON_IDS["tools"], "info")
        ]),
        create_button_row([
            create_colored_button(f"{'🟢' if s.get('gst_enabled',True) else '🔴'} GS", BUTTON_ICON_IDS["card"], "success" if s.get('gst_enabled',True) else "danger"),
            create_colored_button(f"{ms('gst')} M", BUTTON_ICON_IDS["tools"], "info")
        ]),
        create_button_row([
            create_colored_button(f"{'🟢' if s.get('pak_enabled',True) else '🔴'} PA", BUTTON_ICON_IDS["pak"], "success" if s.get('pak_enabled',True) else "danger"),
            create_colored_button(f"{ms('pak')} M", BUTTON_ICON_IDS["tools"], "info")
        ]),
        create_button_row([
            create_colored_button(f"{'🟢' if s.get('indnum_enabled',True) else '🔴'} IN2", BUTTON_ICON_IDS["phone2"], "success" if s.get('indnum_enabled',True) else "danger"),
            create_colored_button(f"{ms('indnum')} M", BUTTON_ICON_IDS["tools"], "info")
        ]),
        create_button_row([
            create_colored_button(f"{'🟢' if s.get('indnum3_enabled',True) else '🔴'} IN3", BUTTON_ICON_IDS["india"], "success" if s.get('indnum3_enabled',True) else "danger"),
            create_colored_button(f"{ms('indnum3')} M", BUTTON_ICON_IDS["tools"], "info")
        ]),
        create_button_row([
            create_colored_button("CLOSE", BUTTON_ICON_IDS["cross"], "danger")
        ])
    ]
    
    keyboard = create_keyboard_markup(rows)
    
    txt = f"{PE_CROWN} ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ {PE_CROWN}\n{PE_INVITE} ᴜꜱᴇʀꜱ: {len(load_json(USERS_FILE))} | {PE_TICKET} ᴄᴏᴅᴇꜱ: {len(load_json(REDEEM_FILE))}"
    
    await event.reply(txt, reply_markup=keyboard, parse_mode='html')

# ============================================================
# HELP, ABOUT, STATS
# ============================================================

async def show_help(event):
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
    sent = await event.reply(text, parse_mode='html')
    asyncio.create_task(schedule_delete(sent, 60))

async def show_about(event):
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
• Colored Keyboard Buttons 🎨

{PE_CROWN} 𝐃𝐄𝐕𝐄𝐋𝐎𝐏𝐄𝐃 𝐁𝐘: @Hexh4ckerOFC

{PE_WARN} 𝐅𝐎𝐑 𝐄𝐃𝐔𝐂𝐀𝐓𝐈𝐎𝐍𝐀𝐋 𝐏𝐔𝐑𝐏𝐎𝐒𝐄𝐒 𝐎𝐍𝐋𝐘
"""
    sent = await event.reply(text, parse_mode='html')
    asyncio.create_task(schedule_delete(sent, 60))

async def show_stats(event):
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
    sent = await event.reply(text, parse_mode='html')
    asyncio.create_task(schedule_delete(sent, 60))

# ============================================================
# API FUNCTIONS
# ============================================================

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

# ============================================================
# RUN QUERY
# ============================================================

async def run_query(event, mode, query):
    if not await net_ok():
        sent = await event.reply(f"{PE_CROSS} No internet", parse_mode='html')
        asyncio.create_task(schedule_delete(sent))
        return
    
    st = await event.reply(f"{PE_GREEN} ꜱᴇᴀʀᴄʜɪɴɢ...", parse_mode='html')
    credit_deducted = False
    
    try:
        if mode in ['AADHAAR', 'MOBILE', 'VEHICLE']:
            raw = run_india_script({'AADHAAR':'2','MOBILE':'1','VEHICLE':'4'}[mode], query)
            if raw:
                records = parse_all_india_records(raw)
                result = format_records_result(records, {'AADHAAR':'aadhaar','MOBILE':'mobile','VEHICLE':'vehicle'}[mode])
                if records and f"{PE_CROSS}" not in str(result):
                    use_credit(event.sender_id)
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
                use_credit(event.sender_id)
                credit_deducted = True
        
        user = get_user(event.sender_id)
        final = f"{result}\n{SEP}\n{PE_CREDIT} {'ᴄʀ: '+str(user.get('credits',0)) if credit_deducted else 'ɴᴏ ᴄʀ ᴅᴇᴅᴜᴄᴛᴇᴅ'} | {PE_CLOCK} {AUTO_DELETE_TIME}ꜱ{DISCLAIMER}{FOOTER}"
        sent = await st.edit(final, parse_mode='html')
        asyncio.create_task(schedule_delete(sent))
    except Exception as e:
        print(f"Query error: {e}")
        try:
            await st.edit(f"{PE_WARN} ᴇʀʀᴏʀ{FOOTER}", parse_mode='html')
        except: pass

# ============================================================
# INDIA SCRIPT FUNCTIONS
# ============================================================

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

def clean_text(text):
    if not text: return ""
    return re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', text)

# ============================================================
# MAIN
# ============================================================

print("🔄 Hex Terminal Premium Starting...")
print("🎨 Colored Keyboard Buttons with Premium Emojis!")
print("🤖 Telethon Version with Full Button Colors!")

try:
    subprocess.run([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4"], capture_output=True, timeout=30)
except: pass

print(f"✅ {BOT_NAME} Ready!")
print(f"💎 All buttons are colored with Premium Emoji Icons!")
print(f"⭐ 2 Page Keyboard Menu with Colored Buttons")
print("🚀 Bot is running...")

client.run_until_disconnected()