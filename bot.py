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

FOOTER = "\n\n<b>⚠️ ᴇᴅᴜᴄᴀᴛɪᴏɴᴀʟ ᴘᴜʀᴘᴏꜱᴇ ᴏɴʟʏ | ᴅᴏ ɴᴏᴛ ᴍɪꜱᴜꜱᴇ</b>"
SEP = "━━━━━━━━━━━━━━━━━━━"

# APIs
LOOKUP_API = "https://toxic-tg.vercel.app/?userid="
IFSC_API = "https://ifsc.razorpay.com/"
SHORTLINK_API = "https://link-btpass.onrender.com/bypass?key=9c44ad66b95cef8aecd7a99cfb362ce0&link="
GST_API = "https://gst-0y-vishal.vercel.app/api/gst.js?gstNumber="
PAK_API = "https://api-server-virid-two.vercel.app/number="
IND_NUM_API = "https://all-number-info-rajan-eta.vercel.app/api?number="

VERIFY_SCRIPT = "verify_india.py"

USERS_FILE = "users.json"
REDEEM_FILE = "redeem_codes.json"
SETTINGS_FILE = "settings.json"

DAILY_FREE_CREDITS = 10
INVITE_CREDITS = 3
AUTO_DELETE_TIME = 60

BOT_NAME = "Hex Terminal"
BOT_USERNAME = "Hex_Terminal_bot"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

ADMIN_STATE = {}

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
    return True, f"✅ +{cr} credits added!\n💰 Balance: {bal}"

def get_settings():
    try: return json.load(open(SETTINGS_FILE, 'r'))
    except:
        d = {"bypass_maintenance":False,"tgid_enabled":True,"ifsc_enabled":True,"bypass_enabled":True,"mobile_enabled":True,"aadhaar_enabled":True,"rc_enabled":True,"gst_enabled":True,"pak_enabled":True,"indnum_enabled":True,"maintenance_mode":False}
        for k in ["tgid","ifsc","bypass","mobile","aadhaar","rc","gst","pak","indnum"]: d[f"maint_{k}"] = False; d[f"maint_msg_{k}"] = "Under maintenance."
        save_settings(d); return d

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

async def schedule_delete(msg, delay=AUTO_DELETE_TIME):
    await asyncio.sleep(delay)
    try: await msg.delete()
    except: pass

async def loading_animation(msg, name):
    bars = ["🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛","🟩🟩⬛⬛⬛⬛⬛⬛⬛⬛","🟩🟩🟩⬛⬛⬛⬛⬛⬛⬛","🟩🟩🟩🟩⬛⬛⬛⬛⬛⬛","🟩🟩🟩🟩🟩⬛⬛⬛⬛⬛","🟩🟩🟩🟩🟩🟩⬛⬛⬛⬛","🟩🟩🟩🟩🟩🟩🟩⬛⬛⬛","🟩🟩🟩🟩🟩🟩🟩🟩⬛⬛","🟩🟩🟩🟩🟩🟩🟩🟩🟩⬛","🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩"]
    for i, bar in enumerate(bars):
        try: await msg.edit_text(f"<b>⚡ {name}</b>\n<code>{bar} {i*10}%</code>", parse_mode=ParseMode.HTML); await asyncio.sleep(0.2)
        except: break

def check_feature_maintenance(feature_key):
    s = get_settings()
    if s.get(f"maint_{feature_key}", False):
        return True, s.get(f"maint_msg_{feature_key}", "Under maintenance.")
    return False, ""

async def show_verification_page(update, context):
    try:
        bot = await context.bot.get_me()
        photos = await context.bot.get_user_profile_photos(bot.id, limit=1)
        caption = (
            f"<b>🤖 {BOT_NAME}</b>\n"
            f"<b>@{BOT_USERNAME}</b>\n\n"
            f"<b>🔒 Verification Required</b>\n"
            f"<b>Join both channels to unlock all features</b>\n\n"
            f"<b>📌 Features:</b>\n"
            f"<b>• Telegram ID to Number</b>\n"
            f"<b>• IFSC Bank Information</b>\n"
            f"<b>• Short Link Bypass</b>\n"
            f"<b>• Indian Number Lookup</b>\n"
            f"<b>• Aadhaar Information</b>\n"
            f"<b>• Vehicle RC Details</b>\n"
            f"<b>• GST Number Lookup</b>\n"
            f"<b>• Pakistan Number Info</b>\n"
            f"<b>• Premium Number Info</b>\n\n"
            f"<b>🎁 +{DAILY_FREE_CREDITS} Daily Free Credits</b>\n"
            f"<b>👥 +{INVITE_CREDITS} Credits per Invite</b>\n"
            f"<b>⏱ {AUTO_DELETE_TIME}s Auto Delete</b>\n\n"
            f"<b>⚠️ For educational purposes only</b>\n"
            f"<b>Do not misuse any information</b>"
        )
        if photos and photos.photos: sent = await update.message.reply_photo(photo=photos.photos[0][-1].file_id, caption=caption, parse_mode=ParseMode.HTML)
        else: sent = await update.message.reply_text(caption, parse_mode=ParseMode.HTML)
        asyncio.create_task(schedule_delete(sent, 120))
    except: pass
    buttons = [[InlineKeyboardButton("📢 Join Channel 1", url=LINK_1)],[InlineKeyboardButton("📢 Join Channel 2", url=LINK_2)],[InlineKeyboardButton("✅ I've Joined - Verify Now", callback_data="verify")]]
    sent2 = await update.message.reply_text("<b>🔒 Join both channels then click verify to unlock</b>", reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)
    asyncio.create_task(schedule_delete(sent2, 120))

async def main_menu(update, context):
    is_admin = update.effective_user.id == ADMIN_ID
    user = get_user(update.effective_user.id); s = get_settings()
    kb = []; row = []
    if s.get("tgid_enabled",True): row.append(KeyboardButton("📱 TG ID to Number"))
    if s.get("ifsc_enabled",True): row.append(KeyboardButton("🏦 IFSC Bank Info"))
    if row: kb.append(row)
    if s.get("bypass_enabled",True): kb.append([KeyboardButton("🔗 Link Bypass")])
    row2 = []
    if s.get("aadhaar_enabled",True): row2.append(KeyboardButton("🪪 Aadhaar Info"))
    if s.get("mobile_enabled",True): row2.append(KeyboardButton("🇮🇳 Indian Number"))
    if row2: kb.append(row2)
    row3 = []
    if s.get("rc_enabled",True): row3.append(KeyboardButton("🚘 Vehicle RC"))
    if s.get("gst_enabled",True): row3.append(KeyboardButton("📋 GST Lookup"))
    if row3: kb.append(row3)
    row4 = []
    if s.get("pak_enabled",True): row4.append(KeyboardButton("🇵🇰 Pakistan Number"))
    if s.get("indnum_enabled",True): row4.append(KeyboardButton("📲 Premium Info"))
    if row4: kb.append(row4)
    kb.append([KeyboardButton("👥 Invite & Earn"), KeyboardButton("🎫 Redeem Code")])
    if is_admin: kb.append([KeyboardButton("👑 Admin Panel")])
    markup = ReplyKeyboardMarkup(kb, resize_keyboard=True)
    cr = user.get("credits",0); total = user.get("total_queries",0); invites = user.get("invites",0)
    txt = (
        f"<b>🤖 {BOT_NAME} | @{BOT_USERNAME}</b>\n\n"
        f"<b>Welcome,</b> <code>{update.effective_user.first_name}</code>\n\n"
        f"<b>📊 Your Statistics:</b>\n"
        f"<b>💰 Credits:</b> {cr}\n"
        f"<b>📊 Total Queries:</b> {total}\n"
        f"<b>👥 Invites:</b> {invites}\n\n"
        f"<b>🔄 +{DAILY_FREE_CREDITS} Daily Free | 👥 +{INVITE_CREDITS} per Invite</b>\n"
        f"<b>⏱ Messages auto-delete in {AUTO_DELETE_TIME}s</b>\n\n"
        f"<b>⚠️ Educational Purpose Only | Do Not Misuse</b>"
    )
    msg = await update.message.reply_text(txt, reply_markup=markup, parse_mode=ParseMode.HTML)
    asyncio.create_task(schedule_delete(msg, AUTO_DELETE_TIME))

# --- 🔗 API ---

async def safe_api_fetch(session, url, timeout=20):
    for attempt in range(3):
        try:
            headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout), headers=headers) as r:
                text = await r.text()
                if not text: continue
                try: return json.loads(text)
                except:
                    if attempt == 2: return None
                    await asyncio.sleep(1)
        except:
            if attempt == 2: return None
            await asyncio.sleep(1)
    return None

async def chatid_lookup(session, query):
    data = await safe_api_fetch(session, f"{LOOKUP_API}{query}")
    if not data: return "<b>❌ Service unavailable</b>"
    if isinstance(data, dict):
        if data.get("success"):
            d = data.get("data", data)
            if isinstance(d, dict):
                result = "<b>📱 Telegram ID to Number</b>\n"
                if d.get('chat_id') or d.get('userid'): result += f"<b>🆔 Chat ID:</b> <code>{d.get('chat_id', d.get('userid', query))}</code>\n"
                if d.get('number'): result += f"<b>📞 Number:</b> <code>{d['number']}</code>\n"
                if d.get('name'): result += f"<b>👤 Name:</b> <code>{d['name']}</code>\n"
                return result
        if data.get("message"): return f"<b>❌ {data['message']}</b>"
    return "<b>❌ Not found - Use @ChatIdInfoBot first</b>"

async def ifsc_lookup(session, code):
    data = await safe_api_fetch(session, f"{IFSC_API}{code.upper()}")
    if not data: return "<b>❌ Service unavailable</b>"
    if isinstance(data, dict):
        return (f"<b>🏦 IFSC Bank Information</b>\n"
                f"<b>🏛 Bank:</b> <code>{data.get('BANK','N/A')}</code>\n"
                f"<b>📍 Branch:</b> <code>{data.get('BRANCH','N/A')}</code>\n"
                f"<b>🔑 IFSC:</b> <code>{data.get('IFSC',code.upper())}</code>\n"
                f"<b>📫 Address:</b> <code>{data.get('ADDRESS','N/A')}</code>")
    return "<b>❌ Invalid IFSC code</b>"

async def bypass_lookup(session, link):
    s = get_settings()
    if s.get("bypass_maintenance",False): return "<b>🛠️ Under maintenance</b>"
    data = await safe_api_fetch(session, f"{SHORTLINK_API}{link}", timeout=20)
    if not data: return "<b>❌ Service unavailable</b>"
    if isinstance(data, dict):
        r = data.get('bypassed_url') or data.get('url') or str(data)
        return f"<b>🔗 Link Bypassed</b>\n<b>🔗 Original:</b> <code>{str(r)}</code>"
    return f"<b>🔗 Result:</b> <code>{str(data)}</code>"

async def gst_lookup(session, gst_number):
    data = await safe_api_fetch(session, f"{GST_API}{gst_number.upper()}", timeout=20)
    if not data: return "<b>❌ Service unavailable</b>"
    if isinstance(data, dict) and data.get("status") == "success" and data.get("data"):
        d = data["data"]
        result = "<b>📋 GST Number Information</b>\n"
        if d.get('TradeName'): result += f"<b>🏢 Trade Name:</b> <code>{d['TradeName']}</code>\n"
        if d.get('Gstin'): result += f"<b>🔑 GST Number:</b> <code>{d['Gstin']}</code>\n"
        if d.get('Status'):
            status_map = {'ACT': 'Active', 'SUS': 'Suspended', 'CAN': 'Cancelled'}
            result += f"<b>📊 Status:</b> {status_map.get(d['Status'], d['Status'])}\n"
        if d.get('DtReg'): result += f"<b>📅 Registered:</b> <code>{d['DtReg']}</code>\n"
        return result
    return "<b>❌ Invalid GST number</b>"

async def pakistan_lookup(session, number):
    try:
        data = await safe_api_fetch(session, f"{PAK_API}{number}", timeout=20)
        if not data: return "<b>❌ Service unavailable</b>"
        if isinstance(data, dict) and data.get("success") and data.get("data"):
            records = data["data"]
            valid = [r for r in records if isinstance(r, dict) and any(r.get(k) for k in ['name','number','cnic','address'])]
            if not valid: return "<b>❌ No data found</b>"
            result = "<b>🇵🇰 Pakistan Number Info</b>\n"
            for i, r in enumerate(valid[:3], 1):
                if len(valid) > 1: result += f"\n<b>Record {i}:</b>\n"
                if r.get('number'): result += f"<b>📞 Number:</b> <code>{r['number']}</code>\n"
                if r.get('name'): result += f"<b>👤 Name:</b> <code>{r['name']}</code>\n"
                if r.get('cnic'): result += f"<b>🪪 CNIC:</b> <code>{r['cnic']}</code>\n"
                if r.get('address'): result += f"<b>📍 Address:</b> <code>{r['address'][:200]}</code>\n"
            return result
        return "<b>❌ No data found</b>"
    except: return "<b>❌ Error</b>"

async def indnum_lookup(session, number):
    """Premium Indian Number Info"""
    for attempt in range(3):
        data = await safe_api_fetch(session, f"{IND_NUM_API}{number}", timeout=30)
        if data and isinstance(data, dict) and data.get("results"): break
        if attempt < 2: await asyncio.sleep(2)
    if not data: return "<b>❌ Service unavailable - try again</b>"
    if not isinstance(data, dict): return "<b>❌ Invalid response</b>"
    results = data.get("results", {})
    if not results: return "<b>❌ No results found</b>"
    result = f"<b>📲 Premium Number Information</b>\n<b>📞 Number:</b> <code>{number}</code>\n"
    found_any = False
    s3 = results.get("source_3", {}).get("data", {})
    if isinstance(s3, dict):
        for key, emoji in [("SIM card","💳"),("Connection","📶"),("Mobile State","📍"),("Hometown","🏠"),("Language","🗣"),("Owner Name","👤"),("Owner Address","📍"),("Complaints","⚠️"),("Tracker Id","🪪")]:
            if s3.get(key): result += f"<b>{emoji} {key}:</b> <code>{str(s3[key])[:200]}</code>\n"; found_any = True
    s4 = results.get("source_4", {}).get("data", {})
    if isinstance(s4, dict):
        if s4.get("carrier"): result += f"<b>📡 Carrier:</b> <code>{s4['carrier']}</code>\n"; found_any = True
    s8 = results.get("source_8", {}).get("data", {})
    if isinstance(s8, dict) and s8.get("success"):
        tc = s8.get("data", {}).get("results", {})
        if isinstance(tc, dict):
            if tc.get("name"): result += f"<b>👤 Truecaller:</b> <code>{tc['name']}</code>\n"; found_any = True
    s9 = results.get("source_9", {}).get("data", {})
    if isinstance(s9, dict) and s9.get("success"):
        s9r = s9.get("result", {}).get("results", [])
        if s9r:
            seen = set(); unique = []
            for r in s9r:
                if isinstance(r, dict):
                    k = (r.get('NAME',''), r.get('ADDRESS',''))
                    if k not in seen: seen.add(k); unique.append(r)
            if unique:
                result += f"\n<b>📊 Database Records: {len(unique)}</b>\n"
                for i, rec in enumerate(unique[:3], 1):
                    result += f"\n<b>Record {i}:</b>\n"
                    if rec.get('NAME'): result += f"<b>👤 Name:</b> <code>{rec['NAME']}</code>\n"
                    if rec.get('fname'): result += f"<b>👨 Father:</b> <code>{rec['fname']}</code>\n"
                    if rec.get('ADDRESS'): result += f"<b>📍 Address:</b> <code>{rec['ADDRESS'][:150]}</code>\n"
                found_any = True
    if not found_any: return "<b>❌ No detailed information found</b>"
    return result

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
        fields = {'Name': '👤 Name', "Father's Name": '👨 Father', 'Mobile': '📱 Mobile', 'Address': '📍 Address', 'Circle': '📡 Circle', 'State': '🏛 State', 'RC Number': '🔖 RC', 'Owner Name': '👤 Owner', 'Vehicle Class': '🚗 Class', 'Fuel Type': '⛽ Fuel', 'Insurance Company': '🛡️ Insurance', 'Phone': '📞 Phone'}
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
    if not records: return "<b>❌ No records found</b>"
    title_map = {'aadhaar':'🪪 Aadhaar Info','mobile':'🇮🇳 Indian Number','vehicle':'🚘 Vehicle RC'}
    title = title_map.get(search_type, '📊 Result')
    result = f"<b>{title}</b>\n<b>📊 Records: {len(records)}</b>\n"
    for i, record in enumerate(records, 1):
        if len(records) > 1: result += f"\n<b>Record {i}:</b>\n"
        for key, value in record.items(): result += f"<b>{key}:</b> <code>{value}</code>\n"
    return result

# --- 👑 ADMIN ---

async def admin_panel(update, context):
    if update.effective_user.id != ADMIN_ID: return
    s = get_settings()
    ms = lambda key: "🔴" if s.get(f"maint_{key}") else "🟢"
    kb = [
        [InlineKeyboardButton("🎫 Gen Code", callback_data="ad_gen"), InlineKeyboardButton("📋 Codes", callback_data="ad_codes")],
        [InlineKeyboardButton("🎁 Add Credits", callback_data="ad_credit"), InlineKeyboardButton("📢 Broadcast", callback_data="ad_bcast")],
        [InlineKeyboardButton(f"{'🔴' if s.get('maintenance_mode') else '🟢'} Global Maint", callback_data="ad_maint")],
        [InlineKeyboardButton(f"{'🟢' if s.get('tgid_enabled',True) else '🔴'} TG ID", callback_data="ad_tgid"), InlineKeyboardButton(f"{ms('tgid')} MTG", callback_data="ad_maint_tgid")],
        [InlineKeyboardButton(f"{'🟢' if s.get('ifsc_enabled',True) else '🔴'} IFSC", callback_data="ad_ifsc"), InlineKeyboardButton(f"{ms('ifsc')} MIF", callback_data="ad_maint_ifsc")],
        [InlineKeyboardButton(f"{'🟢' if s.get('bypass_enabled',True) else '🔴'} Bypass", callback_data="ad_bypass_toggle"), InlineKeyboardButton(f"{ms('bypass')} MBY", callback_data="ad_maint_bypass")],
        [InlineKeyboardButton(f"{'🟢' if s.get('mobile_enabled',True) else '🔴'} Mobile", callback_data="ad_mobile"), InlineKeyboardButton(f"{ms('mobile')} MMO", callback_data="ad_maint_mobile")],
        [InlineKeyboardButton(f"{'🟢' if s.get('aadhaar_enabled',True) else '🔴'} Aadhaar", callback_data="ad_aadhaar"), InlineKeyboardButton(f"{ms('aadhaar')} MAA", callback_data="ad_maint_aadhaar")],
        [InlineKeyboardButton(f"{'🟢' if s.get('rc_enabled',True) else '🔴'} RC", callback_data="ad_rc"), InlineKeyboardButton(f"{ms('rc')} MRC", callback_data="ad_maint_rc")],
        [InlineKeyboardButton(f"{'🟢' if s.get('gst_enabled',True) else '🔴'} GST", callback_data="ad_gst"), InlineKeyboardButton(f"{ms('gst')} MGS", callback_data="ad_maint_gst")],
        [InlineKeyboardButton(f"{'🟢' if s.get('pak_enabled',True) else '🔴'} Pak", callback_data="ad_pak"), InlineKeyboardButton(f"{ms('pak')} MPA", callback_data="ad_maint_pak")],
        [InlineKeyboardButton(f"{'🟢' if s.get('indnum_enabled',True) else '🔴'} IndNum", callback_data="ad_indnum"), InlineKeyboardButton(f"{ms('indnum')} MIN", callback_data="ad_maint_indnum")],
        [InlineKeyboardButton("🛠️ Bypass Maint", callback_data="ad_bypass_maint"), InlineKeyboardButton("❌ Close", callback_data="ad_close")]
    ]
    txt = f"<b>👑 Admin Panel</b>\n<b>👥 Users: {len(load_json(USERS_FILE))} | 🎫 Codes: {len(load_json(REDEEM_FILE))}</b>"
    if update.callback_query: await update.callback_query.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
    else: await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)

async def admin_callback(update, context):
    q = update.callback_query
    if q.from_user.id != ADMIN_ID: await q.answer("❌"); return
    d = q.data; s = get_settings()
    if d == "ad_close": await q.message.delete()
    elif d == "ad_codes":
        codes = load_json(REDEEM_FILE); txt = f"<b>🎫 {len(codes)} Codes</b>\n"
        for c, v in list(codes.items())[-15:]: txt += f"<b>{'✅' if not v.get('used') else '❌'}</b> <code>{c}</code> | {v.get('credits')}cr\n"
        await q.message.edit_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d == "ad_gen": ADMIN_STATE[q.from_user.id] = "gen"; await q.message.edit_text("<b>🎫 Enter credit amount:</b>\n<i>100</i>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d == "ad_credit": ADMIN_STATE[q.from_user.id] = "credit"; await q.message.edit_text("<b>🎁 Enter: ID AMOUNT</b>\n<i>123456789 50</i>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d == "ad_bcast": ADMIN_STATE[q.from_user.id] = "bcast"; await q.message.edit_text("<b>📢 Enter message:</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="ad_back")]]), parse_mode=ParseMode.HTML)
    elif d == "ad_maint": s["maintenance_mode"] = not s.get("maintenance_mode", False); save_settings(s); await q.answer(f"Global: {'ON' if s['maintenance_mode'] else 'OFF'}", show_alert=True); await admin_panel(update, context)
    elif d.startswith("ad_maint_"):
        f = d.replace("ad_maint_", ""); s[f"maint_{f}"] = not s.get(f"maint_{f}", False); save_settings(s); await q.answer(f"{f}: {'🔴 ON' if s[f'maint_{f}'] else '🟢 OFF'}", show_alert=True); await admin_panel(update, context)
    elif d.startswith("ad_"):
        toggle_map = {"ad_tgid":"tgid_enabled","ad_ifsc":"ifsc_enabled","ad_bypass_toggle":"bypass_enabled","ad_mobile":"mobile_enabled","ad_aadhaar":"aadhaar_enabled","ad_rc":"rc_enabled","ad_gst":"gst_enabled","ad_pak":"pak_enabled","ad_indnum":"indnum_enabled"}
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
                    try: await context.bot.send_message(chat_id=int(inviter), text=f"<b>🎉 +{cr} credits! New user joined via your link!</b>", parse_mode=ParseMode.HTML)
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
    else: await q.answer("❌ Join both channels first!", show_alert=True)

async def msg_handler(update, context):
    try:
        uid = update.effective_user.id; txt = update.message.text.strip()
        asyncio.create_task(schedule_delete(update.message, AUTO_DELETE_TIME))
        s = get_settings()
        if s.get("maintenance_mode", False) and uid != ADMIN_ID:
            m = await update.message.reply_text(f"<b>🛠️ Bot is under maintenance. Please try later.</b>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m)); return
        if uid == ADMIN_ID and uid in ADMIN_STATE:
            state = ADMIN_STATE.pop(uid)
            if state == "gen":
                try: cr = int(txt); code = generate_redeem_code(cr); msg = await update.message.reply_text(f"<b>✅ Code:</b> <code>{code}</code> | <b>💰 {cr}cr</b>", parse_mode=ParseMode.HTML)
                except: msg = await update.message.reply_text("<b>❌ Enter a number</b>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(msg)); return
            elif state == "credit":
                p = txt.split()
                if len(p) >= 2: bal = add_credits(p[0], int(p[1])); msg = await update.message.reply_text(f"<b>✅ +{p[1]} credits | Balance: {bal}</b>", parse_mode=ParseMode.HTML)
                else: msg = await update.message.reply_text("<b>❌ Format: ID AMOUNT</b>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(msg)); return
            elif state == "bcast":
                users = load_json(USERS_FILE); cnt = 0
                for u in users:
                    try: await context.bot.send_message(chat_id=int(u), text=f"📢 {txt}"); cnt += 1
                    except: pass
                msg = await update.message.reply_text(f"<b>✅ Sent to {cnt} users</b>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(msg)); return
        user = get_user(uid)
        if not user.get("verified"):
            if await check_channels(uid, context): user["verified"] = True; save_user(uid, user); await main_menu(update, context)
            else: await show_verification_page(update, context)
            return
        if txt in ["👑 Admin Panel", "👑 ᴀᴅᴍɪɴ"]: await admin_panel(update, context)
        elif txt in ["📱 TG ID to Number", "ᴛɢ ɪᴅ ➜ 📞 ɴᴜᴍʙᴇʀ 🔍"]:
            if not s.get("tgid_enabled",True): m=await update.message.reply_text("<b>📴 Feature disabled</b>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("tgid")
            if maint: m=await update.message.reply_text(f"<b>🛠️ {msg}</b>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'TG'
            btn = [[InlineKeyboardButton("🤖 Open @ChatIdInfoBot", url="https://t.me/ChatIdInfoBot")]]
            m = await update.message.reply_text("<b>📱 Send Chat ID to get number</b>\n<i>Example: 7123181749</i>", reply_markup=InlineKeyboardMarkup(btn), parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        elif txt in ["🏦 IFSC Bank Info", "🏦 ɪꜰꜱᴄ ɪɴꜰᴏ➜🔎"]:
            if not s.get("ifsc_enabled",True): m=await update.message.reply_text("<b>📴 Feature disabled</b>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("ifsc")
            if maint: m=await update.message.reply_text(f"<b>🛠️ {msg}</b>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'IFSC'
            m = await update.message.reply_text("<b>🏦 Send IFSC code</b>\n<i>Example: SBIN0001234</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        elif txt in ["🔗 Link Bypass", "🔗 ʟɪɴᴋ ʙʏᴘᴀꜱꜱ"]:
            if not s.get("bypass_enabled",True): m=await update.message.reply_text("<b>📴 Feature disabled</b>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("bypass")
            if maint: m=await update.message.reply_text(f"<b>🛠️ {msg}</b>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'SHORTLINK'
            m = await update.message.reply_text("<b>🔗 Send short link to bypass</b>\n<i>Example: https://indianshortner.in/xxxx</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        elif txt in ["🇮🇳 Indian Number", "🇮🇳 ɪɴᴅ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ➜👤"]:
            if not s.get("mobile_enabled",True): m=await update.message.reply_text("<b>📴 Feature disabled</b>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("mobile")
            if maint: m=await update.message.reply_text(f"<b>🛠️ {msg}</b>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'MOBILE'
            m = await update.message.reply_text("<b>🇮🇳 Send 10-digit Indian mobile number</b>\n<i>Example: 9876543210</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        elif txt in ["🪪 Aadhaar Info", "🪪 ᴀᴀᴅʜᴀʀ ɪɴꜰᴏ➜👤"]:
            if not s.get("aadhaar_enabled",True): m=await update.message.reply_text("<b>📴 Feature disabled</b>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("aadhaar")
            if maint: m=await update.message.reply_text(f"<b>🛠️ {msg}</b>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'AADHAAR'
            m = await update.message.reply_text("<b>🪪 Send 12-digit Aadhaar number</b>\n<i>Example: 123456789012</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        elif txt in ["🚘 Vehicle RC", "🚘 ʀᴄ ᴅᴇᴛᴀɪʟꜱ"]:
            if not s.get("rc_enabled",True): m=await update.message.reply_text("<b>📴 Feature disabled</b>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("rc")
            if maint: m=await update.message.reply_text(f"<b>🛠️ {msg}</b>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'VEHICLE'
            m = await update.message.reply_text("<b>🚘 Send vehicle number</b>\n<i>Example: KA01AB3256</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        elif txt in ["📋 GST Lookup", "📋 ɢꜱᴛ ʟᴏᴏᴋᴜᴘ"]:
            if not s.get("gst_enabled",True): m=await update.message.reply_text("<b>📴 Feature disabled</b>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("gst")
            if maint: m=await update.message.reply_text(f"<b>🛠️ {msg}</b>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'GST'
            m = await update.message.reply_text("<b>📋 Send GST number</b>\n<i>Example: 19BOKPS7056D1ZI</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        elif txt in ["🇵🇰 Pakistan Number", "🇵🇰 ᴘᴀᴋ ɴᴜᴍʙᴇʀ ɪɴꜰᴏ"]:
            if not s.get("pak_enabled",True): m=await update.message.reply_text("<b>📴 Feature disabled</b>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("pak")
            if maint: m=await update.message.reply_text(f"<b>🛠️ {msg}</b>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'PAK'
            m = await update.message.reply_text("<b>🇵🇰 Send Pakistan phone number</b>\n<i>Example: 923078750447</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        elif txt in ["📲 Premium Info", "📲 ɪɴᴅ ɴᴜᴍ ɪɴꜰᴏ 𝟸"]:
            if not s.get("indnum_enabled",True): m=await update.message.reply_text("<b>📴 Feature disabled</b>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            maint, msg = check_feature_maintenance("indnum")
            if maint: m=await update.message.reply_text(f"<b>🛠️ {msg}</b>", parse_mode=ParseMode.HTML); asyncio.create_task(schedule_delete(m)); return
            context.user_data['mode'] = 'INDNUM'
            m = await update.message.reply_text("<b>📲 Send any 10-digit Indian number</b>\n<i>Example: 6363016966</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m))
        elif txt in ["👥 Invite & Earn", "👥 ɪɴᴠɪᴛᴇ", "👥 ɪɴᴠɪᴛᴇ & ᴇᴀʀɴ"]:
            user = get_user(uid); bot_username = context.bot.username or BOT_USERNAME
            link = f"https://t.me/{bot_username}?start={user['invite_code']}"
            m = await update.message.reply_text(f"<b>👥 Invite & Earn</b>\n<b>🎁 +{INVITE_CREDITS} credits per invite</b>\n<b>🔗 Your link:</b>\n<code>{link}</code>\n<b>👥 Invites: {user.get('invites',0)} | 💰 Balance: {user.get('credits',0)}</b>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m, 120))
        elif txt in ["🎫 Redeem Code", "🎫 ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ"]:
            context.user_data['redeem_mode'] = True
            m = await update.message.reply_text("<b>🎫 Enter your redeem code:</b>\n<i>HEX-XXXXXXXXXX</i>", parse_mode=ParseMode.HTML)
            asyncio.create_task(schedule_delete(m, 30))
        else:
            if context.user_data.get('redeem_mode'):
                context.user_data['redeem_mode'] = False
                msg = redeem_code(uid, txt)[1] if txt.upper().startswith("HEX-") and len(txt) > 10 else "❌ Invalid format!"
                m = await update.message.reply_text(f"<b>{msg}</b>", parse_mode=ParseMode.HTML)
                asyncio.create_task(schedule_delete(m)); return
            mode = context.user_data.get('mode')
            if mode:
                if txt.upper().startswith("HEX-") and len(txt) > 10:
                    success, msg = redeem_code(uid, txt)
                    m = await update.message.reply_text(f"<b>{msg}</b>", parse_mode=ParseMode.HTML)
                    asyncio.create_task(schedule_delete(m)); context.user_data['mode'] = None; return
                user = get_user(uid)
                if user.get("credits", 0) <= 0:
                    m = await update.message.reply_text("<b>❌ No credits! +10 daily | +3 invite</b>", parse_mode=ParseMode.HTML)
                    asyncio.create_task(schedule_delete(m)); context.user_data['mode'] = None; return
                await run_query(update, context, mode, txt); context.user_data['mode'] = None
    except Exception as e: logger.error(f"Msg: {e}")

async def run_query(update, context, mode, query):
    if not await net_ok():
        m = await update.message.reply_text("<b>🔴 No internet connection</b>", parse_mode=ParseMode.HTML)
        asyncio.create_task(schedule_delete(m)); return
    await update.message.reply_chat_action(ChatAction.TYPING)
    names = {'TG':'📱','IFSC':'🏦','SHORTLINK':'🔗','AADHAAR':'🪪','MOBILE':'🇮🇳','VEHICLE':'🚘','GST':'📋','PAK':'🇵🇰','INDNUM':'📲'}
    st = await update.message.reply_text("<b>🟩 Searching...</b>", parse_mode=ParseMode.HTML)
    lt = asyncio.create_task(loading_animation(st, names.get(mode, '')))
    credit_deducted = False
    try:
        if mode in ['AADHAAR', 'MOBILE', 'VEHICLE']:
            raw = run_india_script({'AADHAAR':'2','MOBILE':'1','VEHICLE':'4'}[mode], query)
            if raw:
                records = parse_all_india_records(raw)
                result = format_records_result(records, {'AADHAAR':'aadhaar','MOBILE':'mobile','VEHICLE':'vehicle'}[mode])
                if records and "❌" not in str(result): use_credit(update.effective_user.id); credit_deducted = True
            else: result = "<b>❌ Script failed</b>"
        else:
            async with aiohttp.ClientSession() as s:
                if mode == 'TG': result = await chatid_lookup(s, query)
                elif mode == 'IFSC': result = await ifsc_lookup(s, query)
                elif mode == 'SHORTLINK': result = await bypass_lookup(s, query)
                elif mode == 'GST': result = await gst_lookup(s, query)
                elif mode == 'PAK': result = await pakistan_lookup(s, query)
                elif mode == 'INDNUM': result = await indnum_lookup(s, query)
                else: result = "❌"
            if result and "❌" not in str(result) and "unavailable" not in str(result).lower(): use_credit(update.effective_user.id); credit_deducted = True
        lt.cancel()
        try: await lt
        except asyncio.CancelledError: pass
        user = get_user(update.effective_user.id)
        final = f"{result}\n{SEP}\n<b>💰 {'Credits: '+str(user.get('credits',0)) if credit_deducted else 'No credit deducted'} | ⏱ {AUTO_DELETE_TIME}s</b>{FOOTER}"
        sent = await st.edit_text(final, parse_mode=ParseMode.HTML)
        asyncio.create_task(schedule_delete(sent))
    except Exception as e:
        lt.cancel(); logger.error(f"Query: {e}")
        try: await st.edit_text(f"<b>⚠️ Error - No credit deducted</b>{FOOTER}", parse_mode=ParseMode.HTML)
        except: pass

def main():
    print("Starting Hex Terminal...")
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