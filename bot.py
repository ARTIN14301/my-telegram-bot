import json
import os
import threading
from random import randint, sample
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ========== تنظیمات ==========
DATA_FILE = "game_data.json"
ADMIN_ID = 5596656149
FIGHT_COOLDOWN_MINUTES = 5
FIGHT_BLOCK_MINUTES = 10
ARMY_COOLDOWN_HOURS = 48
ATTACK_COOLDOWN_SECONDS = 10800  # 3 ساعت
data_lock = threading.Lock()

# ========== ارتش‌ها ==========
ARMIES_CONFIG = {
    "byzantine": {"name": "امپراتوری بیزانس", "bonus": 8, "emoji": "🛡️"},
    "holy_roman": {"name": "امپراتوری مقدس روم", "bonus": 7, "emoji": "⚔️"},
    "persian": {"name": "شاهنشاهی ایران", "bonus": 5, "emoji": "🦁"},
    "mongol": {"name": "ایلخانان مغول", "bonus": 10, "emoji": "🏹"}
}

# ========== آیتم‌های شاپ ==========



# ========== آیتم‌های شاپ ==========
ITEMS = {
    # ========== سلاح‌ها (20 عدد) ==========
    # سطح پایین (قیمت 1000-5000)
    "dagger": {"name": "خنجر کهنه", "type": "weapon", "price": 1000, "effect": 2},
    "short_sword": {"name": "شمشیر کوتاه", "type": "weapon", "price": 2000, "effect": 3},
    "iron_sword": {"name": "شمشیر آهنی", "type": "weapon", "price": 3500, "effect": 4},
    "steel_sword": {"name": "شمشیر فولادی", "type": "weapon", "price": 5000, "effect": 5},
    
    # سطح متوسط (قیمت 10000-30000)
    "crimson_blade": {"name": "تیغ زرشکی", "type": "weapon", "price": 10000, "effect": 7},
    "shadow_fang": {"name": "نیش سایه", "type": "weapon", "price": 15000, "effect": 9},
    "dragon_claw": {"name": "چنگال اژدها", "type": "weapon", "price": 20000, "effect": 11},
    "thunder_bringer": {"name": "آورنده رعد", "type": "weapon", "price": 30000, "effect": 13},
    
    # سطح بالا (قیمت 50000-100000)
    "frost_mourne": {"name": "سوگ یخبندان", "type": "weapon", "price": 50000, "effect": 16},
    "hell_fire": {"name": "آتش دوزخی", "type": "weapon", "price": 65000, "effect": 19},
    "star_breaker": {"name": "ستاره‌شکن", "type": "weapon", "price": 80000, "effect": 22},
    "void_edge": {"name": "لبه خلأ", "type": "weapon", "price": 100000, "effect": 25},
    
    # سطح افسانه‌ای (قیمت 150000-300000)
    "soul_reaper": {"name": "دروگر ارواح", "type": "weapon", "price": 150000, "effect": 30},
    "god_slayer": {"name": "خداکش", "type": "weapon", "price": 200000, "effect": 35},
    "world_ender": {"name": "پایان جهان", "type": "weapon", "price": 300000, "effect": 40},
    
    # سطح اسطوره‌ای (قیمت 500000-1000000)
    "apocalypse": {"name": "آخرالزمان", "type": "weapon", "price": 500000, "effect": 46},
    "eternity": {"name": "جاودانگی", "type": "weapon", "price": 700000, "effect": 52},
    "primordial": {"name": "نخستین", "type": "weapon", "price": 850000, "effect": 58},
    "infinity": {"name": "بی‌نهایت", "type": "weapon", "price": 1000000, "effect": 65},
    
    # ========== زره‌ها (20 عدد) ==========
    # سطح پایین (قیمت 1000-5000)
    "leather_armor": {"name": "زره چرمی", "type": "armor", "price": 1000, "effect": 2},
    "studded_armor": {"name": "زره میخی", "type": "armor", "price": 2000, "effect": 3},
    "chainmail": {"name": "زره زنجیری", "type": "armor", "price": 3500, "effect": 4},
    "iron_armor": {"name": "زره آهنی", "type": "armor", "price": 5000, "effect": 5},
    
    # سطح متوسط (قیمت 10000-30000)
    "steel_armor": {"name": "زره فولادی", "type": "armor", "price": 10000, "effect": 7},
    "golden_armor": {"name": "زره طلایی", "type": "armor", "price": 15000, "effect": 9},
    "dragon_scale": {"name": "پولک اژدها", "type": "armor", "price": 20000, "effect": 11},
    "dark_armor": {"name": "زره تاریکی", "type": "armor", "price": 30000, "effect": 13},
    
    # سطح بالا (قیمت 50000-100000)
    "phoenix_armor": {"name": "زره ققنوس", "type": "armor", "price": 50000, "effect": 16},
    "titan_armor": {"name": "زره تیتان", "type": "armor", "price": 65000, "effect": 19},
    "thunder_armor": {"name": "زره رعد", "type": "armor", "price": 80000, "effect": 22},
    "holy_armor": {"name": "زره مقدس", "type": "armor", "price": 100000, "effect": 25},
    
    # سطح افسانه‌ای (قیمت 150000-300000)
    "eternal_armor": {"name": "زره جاویدان", "type": "armor", "price": 150000, "effect": 30},
    "god_armor": {"name": "زره خدایان", "type": "armor", "price": 200000, "effect": 35},
    "celestial_armor": {"name": "زره آسمانی", "type": "armor", "price": 300000, "effect": 40},
    
    # سطح اسطوره‌ای (قیمت 500000-1000000)
    "immortal": {"name": "جاودانگی", "type": "armor", "price": 500000, "effect": 46},
    "void_armor": {"name": "زره خلأ", "type": "armor", "price": 700000, "effect": 52},
    "creation": {"name": "آفرینش", "type": "armor", "price": 850000, "effect": 58},
    "absolute": {"name": "مطلق", "type": "armor", "price": 1000000, "effect": 65},
    
    # ========== اسب‌ها (6 عدد) ==========
    "pony": {"name": "کره اسب", "type": "horse", "price": 10000, "effect": 5},
    "war_horse": {"name": "اسب جنگی", "type": "horse", "price": 30000, "effect": 10},
    "nightmare": {"name": "کابوس", "type": "horse", "price": 80000, "effect": 18},
    "pegasus": {"name": "پگاسوس", "type": "horse", "price": 150000, "effect": 28},
    "shadow_stallion": {"name": "اسب نریان سایه", "type": "horse", "price": 300000, "effect": 40},
    "celestial_horse": {"name": "اسب آسمانی", "type": "horse", "price": 500000, "effect": 55},
}




TITLES = ["رعیت", "سرباز", "پاسدار", "شمشیرزن", "نجیب‌زاده", "فئودال", "بارون", "ویسکونت", "کنت", "مارکیز", "دوک", "ارل", "شاهزاده", "ژنرال", "فرمانده", "پادشاه"]

# ========== کوئست‌ها ==========
QUESTS_LIST = [
    {"name": "جنگجو", "desc": "۲ بار در جنگ پیروز شو", "type": "win_fight", "target": 2, "gold": 2000, "exp": 100},
    {"name": "سرباز حرفه‌ای", "desc": "۳ بار در جنگ پیروز شو", "type": "win_fight", "target": 3, "gold": 2500, "exp": 160},
    {"name": "قاتل", "desc": "۵ بار در جنگ پیروز شو", "type": "win_fight", "target": 5, "gold": 3000, "exp": 200},
    {"name": "حمله‌کننده", "desc": "۱ بار حمله کن", "type": "attack", "target": 1, "gold": 2100, "exp": 200},
    {"name": "غارتگر", "desc": "۲ بار حمله کن", "type": "attack", "target": 2, "gold": 1200, "exp": 170},
    {"name": "بازرگان", "desc": "۱ آیتم بخر", "type": "buy", "target": 1, "gold": 1000, "exp": 110},
]

# ========== توابع کمکی ==========
def load_data():
    with data_lock:
        if not os.path.exists(DATA_FILE):
            return {}
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except:
            return {}

def save_data(data):
    with data_lock:
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except:
            pass

def get_title(level):
    if level < 1: return TITLES[0]
    if level > len(TITLES): return TITLES[-1]
    return TITLES[level-1]

def get_total_effect(user):
    effect = 0
    if user.get("current_weapon"):
        effect += ITEMS.get(user["current_weapon"], {}).get("effect", 0)
    if user.get("current_armor"):
        effect += ITEMS.get(user["current_armor"], {}).get("effect", 0)
    if user.get("current_horse"):
        effect += ITEMS.get(user["current_horse"], {}).get("effect", 0)
    return effect

def get_army_bonus(user):
    return ARMIES_CONFIG.get(user.get("army"), {}).get("bonus", 0)

def check_army_cooldown(user):
    if not user.get("army"): return True, 0
    join = datetime.fromisoformat(user["army_join_time"])
    passed = (datetime.now() - join).total_seconds()
    if passed >= ARMY_COOLDOWN_HOURS * 3600: return True, 0
    return False, (ARMY_COOLDOWN_HOURS * 3600 - passed) / 3600

def paginate(items, page, per_page=5):
    start = page * per_page
    return items[start:start+per_page], (len(items) + per_page - 1) // per_page

def init_user(user):
    """اطمینان از وجود همه فیلدهای مورد نیاز"""
    defaults = {
        "inventory": [], 
        "current_weapon": None, 
        "current_armor": None, 
        "current_horse": None,
        "wins": 0, 
        "losses": 0, 
        "daily_quests": [], 
        "last_daily": None, 
        "last_attack": None
    }
    for key, val in defaults.items():
        if key not in user:
            user[key] = val
    return user


def get_user_by_username(username):
    data = load_data()
    for uid, info in data.items():
        if info.get("username", "").lower() == username.lower():
            return uid, info
    return None, None

# ========== استارت و ثبت‌نام ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚔️ به دنیای قرون وسطی خوش آمدی ⚔️\n\n"
        "📋 کامندها:\n"
        "/register - ثبت‌نام\n/profile - پروفایل\n/chosearmy - انتخاب ارتش\n"
        "/solofight - جنگ\n/inventory - اینونتوری\n/shop - فروشگاه\n"
        "/attack - حمله به بازیکن\n/top - رنکینگ\n/daily - کوئست روزانه\n"
        "/claim - دریافت پاداش کوئست\n/admin - پنل ادمین"
    )

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    data = load_data()
    if str(uid) in data:
        await update.message.reply_text("❌ قبلاً ثبت‌نام کردی!")
        return
    waiting_for_name[uid] = True
    await update.message.reply_text("✨ یه اسم برای شخصیتت انتخاب کن:\n• حداکثر ۱۵ حرف\n• فقط حروف انگلیسی و اعداد")

async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in waiting_for_name:
        return
    text = update.message.text.strip()
    if len(text) > 15 or " " in text or not text.replace("_", "").isalnum():
        await update.message.reply_text("❌ اسم نامعتبر. دوباره تلاش کن:")
        return
    existing_id, _ = get_user_by_username(text)
    if existing_id:
        await update.message.reply_text("❌ این اسم قبلاً ثبت شده!")
        return
    data = load_data()
    data[str(uid)] = init_user({
        "username": text, "level": 1, "title": "رعیت", "gold": 500,
        "exp": 0, "exp_needed": 100, "army": None, "army_join_time": None
    })
    save_data(data)
    del waiting_for_name[uid]
    await update.message.reply_text(f"✅ ثبت‌نام موفق!\n🎭 نام: {text}\n💰 طلا: 500\n🌟 لول: 1")

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    data = load_data()
    if uid not in data:
        await update.message.reply_text("❌ اول ثبت‌نام کن!")
        return
    user = init_user(data[uid])
    army = ARMIES_CONFIG.get(user.get("army"), {}).get("name", "ندارد")
    weapon = ITEMS.get(user.get("current_weapon"), {}).get("name", "ندارد")
    armor = ITEMS.get(user.get("current_armor"), {}).get("name", "ندارد")
    horse = ITEMS.get(user.get("current_horse"), {}).get("name", "ندارد")
    await update.message.reply_text(
        f"⚔️ پروفایل {user['username']} ⚔️\n\n"
        f"🏅 لقب: {user['title']}\n🌟 لول: {user['level']}\n💰 طلا: {user['gold']}\n"
        f"🏆 برد: {user['wins']} | 💀 باخت: {user['losses']}\n"
        f"✨ تجربه: {user['exp']}/{user['exp_needed']}\n⚔️ ارتش: {army}\n"
        f"🗡️ سلاح: {weapon}\n🛡️ زره: {armor}\n🐎 اسب: {horse}"
    )

# ========== ارتش ==========
async def chosearmy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    data = load_data()
    if uid not in data:
        await update.message.reply_text("❌ اول ثبت‌نام کن!")
        return
    user = init_user(data[uid])
    can, rem = check_army_cooldown(user)
    if not can:
        await update.message.reply_text(f"⏳ {rem:.1f} ساعت دیگه می‌تونی عوض کنی.")
        return
    keyboard = [[InlineKeyboardButton(f"{v['emoji']} {v['name']}", callback_data=f"army_{k}")] for k, v in ARMIES_CONFIG.items()]
    await update.message.reply_text("⚔️ انتخاب ارتش:", reply_markup=InlineKeyboardMarkup(keyboard))

async def army_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    army_key = q.data.replace("army_", "")
    if army_key not in ARMIES_CONFIG:
        await q.edit_message_text("❌ ارتش نامعتبر!")
        return
    data = load_data()
    if uid not in data:
        await q.edit_message_text("❌ اول ثبت‌نام کن!")
        return
    user = init_user(data[uid])
    can, _ = check_army_cooldown(user)
    if not can:
        await q.edit_message_text("⏳ هنوز نمی‌تونی عوض کنی!")
        return
    army = ARMIES_CONFIG[army_key]
    user["army"] = army_key
    user["army_join_time"] = datetime.now().isoformat()
    save_data(data)
    await q.edit_message_text(f"✅ به ارتش {army['name']} پیوستی!\n{army['emoji']} +{army['bonus']}% قدرت")

async def leavearmy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    data = load_data()
    if uid not in data:
        await update.message.reply_text("❌ اول ثبت‌نام کن!")
        return
    user = init_user(data[uid])
    if not user.get("army"):
        await update.message.reply_text("❌ عضو ارتشی نیستی!")
        return
    can, rem = check_army_cooldown(user)
    if not can:
        await update.message.reply_text(f"⏳ {rem:.1f} ساعت دیگه می‌تونی خارج بشی.")
        return
    user["army"] = None
    user["army_join_time"] = None
    save_data(data)
    await update.message.reply_text("✅ از ارتش خارج شدی.")

# ========== شاپ ==========
async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    data = load_data()
    if uid not in data:
        await update.message.reply_text("❌ اول ثبت‌نام کن!")
        return
    keyboard = [
        [InlineKeyboardButton("🗡️ سلاح‌ها", callback_data="shop_weapon")],
        [InlineKeyboardButton("🛡️ زره‌ها", callback_data="shop_armor")],
        [InlineKeyboardButton("🐎 اسب‌ها", callback_data="shop_horse")],
        [InlineKeyboardButton("💰 فروش", callback_data="shop_sell")],
        [InlineKeyboardButton("❌ بستن", callback_data="shop_close")]
    ]
    await update.message.reply_text("🛒 فروشگاه:", reply_markup=InlineKeyboardMarkup(keyboard))

async def shop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    if uid not in data:
        await q.edit_message_text("❌ خطا!")
        return
    action = q.data
    if action == "shop_close":
        await q.edit_message_text("🚪 بسته شد.")
    elif action == "shop_weapon":
        await show_shop_items(q, uid, data, "weapon", 0)
    elif action == "shop_armor":
        await show_shop_items(q, uid, data, "armor", 0)
    elif action == "shop_horse":
        await show_shop_items(q, uid, data, "horse", 0)
    elif action == "shop_sell":
        await show_sell_items(q, uid, data, 0)
    elif action.startswith("buy_"):
        await buy_item(q, uid, action[4:], data)
    elif action.startswith("sell_"):
        await sell_item(q, uid, action[5:], data)
    elif action.startswith("spage_"):
        parts = action.split("_")
        await show_shop_items(q, uid, data, parts[1], int(parts[2]))
    elif action.startswith("spage_sell_"):
        await show_sell_items(q, uid, data, int(action[11:]))

async def show_shop_items(q, uid, data, item_type, page):
    items = {k: v for k, v in ITEMS.items() if v["type"] == item_type}
    items_list = list(items.keys())
    page_items, total = paginate(items_list, page)
    type_name = {"weapon": "سلاح", "armor": "زره", "horse": "اسب"}
    text = f"🛒 {type_name[item_type]}ها - صفحه {page+1}/{total}\n\n"
    keyboard = []
    for key in page_items:
        item = items[key]
        text += f"• {item['name']} | {item['price']}💰 | +{item['effect']}%\n"
        keyboard.append([InlineKeyboardButton(f"خرید {item['name']}", callback_data=f"buy_{key}")])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️", callback_data=f"spage_{item_type}_{page-1}"))
    if page < total-1:
        nav.append(InlineKeyboardButton("▶️", callback_data=f"spage_{item_type}_{page+1}"))
    if nav:
        keyboard.append(nav)
    keyboard.append([InlineKeyboardButton("🔙", callback_data="shop_back")])
    await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def buy_item(q, uid, item_key, data):
    user = init_user(data[uid])
    item = ITEMS.get(item_key)
    if not item:
        await q.edit_message_text("❌ نامعتبر!")
        return
    if user["gold"] < item["price"]:
        await q.edit_message_text(f"❌ نیاز به {item['price']}💰 داری!")
        return
    user["gold"] -= item["price"]
    user["inventory"].append(item_key)
    
    # آپدیت کوئست خرید
    today = datetime.now().date().isoformat()
    if user.get("last_daily") == today:
        for quest in user.get("daily_quests", []):
            if not quest.get("completed") and quest["type"] == "buy":
                quest["progress"] = quest.get("progress", 0) + 1
                if quest["progress"] >= quest["target"]:
                    quest["completed"] = True
    
    save_data(data)
    await q.edit_message_text(f"✅ {item['name']} خریداری شد! -{item['price']}💰")

async def show_sell_items(q, uid, data, page):
    user = init_user(data[uid])
    inv = user.get("inventory", [])
    if not inv:
        await q.edit_message_text("🎒 خالی است!")
        return
    page_items, total = paginate(inv, page)
    text = f"💰 فروش - صفحه {page+1}/{total}\n\n"
    keyboard = []
    for key in page_items:
        item = ITEMS.get(key, {"name": key, "price": 0})
        sell_price = item["price"] // 2
        text += f"• {item['name']} | فروش: {sell_price}💰\n"
        keyboard.append([InlineKeyboardButton(f"فروش {item['name']}", callback_data=f"sell_{key}")])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️", callback_data=f"spage_sell_{page-1}"))
    if page < total-1:
        nav.append(InlineKeyboardButton("▶️", callback_data=f"spage_sell_{page+1}"))
    if nav:
        keyboard.append(nav)
    keyboard.append([InlineKeyboardButton("🔙", callback_data="shop_back")])
    await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def sell_item(q, uid, item_key, data):
    user = init_user(data[uid])
    if item_key not in user["inventory"]:
        await q.edit_message_text("❌ در اینونتوری نیست!")
        return
    item = ITEMS.get(item_key, {"name": item_key, "price": 0})
    sell_price = item["price"] // 2
    user["inventory"].remove(item_key)
    user["gold"] += sell_price
    if user.get("current_weapon") == item_key:
        user["current_weapon"] = None
    if user.get("current_armor") == item_key:
        user["current_armor"] = None
    if user.get("current_horse") == item_key:
        user["current_horse"] = None
    save_data(data)
    await q.edit_message_text(f"💰 {item['name']} فروخته شد! +{sell_price}💰")

# ========== اینونتوری ==========
async def inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    data = load_data()
    if uid not in data:
        await update.message.reply_text("❌ اول ثبت‌نام کن!")
        return
    user = init_user(data[uid])
    inv = user.get("inventory", [])
    weapons = [i for i in inv if ITEMS.get(i, {}).get("type") == "weapon"]
    armors = [i for i in inv if ITEMS.get(i, {}).get("type") == "armor"]
    horses = [i for i in inv if ITEMS.get(i, {}).get("type") == "horse"]
    keyboard = []
    if weapons:
        keyboard.append([InlineKeyboardButton(f"🗡️ سلاح‌ها ({len(weapons)})", callback_data="inv_weapon")])
    if armors:
        keyboard.append([InlineKeyboardButton(f"🛡️ زره‌ها ({len(armors)})", callback_data="inv_armor")])
    if horses:
        keyboard.append([InlineKeyboardButton(f"🐎 اسب‌ها ({len(horses)})", callback_data="inv_horse")])
    if not keyboard:
        keyboard.append([InlineKeyboardButton("🎒 خالی", callback_data="noop")])
    keyboard.append([InlineKeyboardButton("❌ بستن", callback_data="inv_close")])
    await update.message.reply_text(
        f"🎒 اینونتوری {user['username']}\n\n"
        f"🗡️ سلاح: {ITEMS.get(user.get('current_weapon'), {}).get('name', 'ندارد')}\n"
        f"🛡️ زره: {ITEMS.get(user.get('current_armor'), {}).get('name', 'ندارد')}\n"
        f"🐎 اسب: {ITEMS.get(user.get('current_horse'), {}).get('name', 'ندارد')}\n\n"
        f"📦 {len(inv)} آیتم",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def inv_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    if uid not in data:
        await q.edit_message_text("❌ خطا!")
        return
    action = q.data
    if action == "inv_close":
        await q.edit_message_text("🚪 بسته شد.")
    elif action == "inv_weapon":
        await show_inv_items(q, uid, data, "weapon", 0)
    elif action == "inv_armor":
        await show_inv_items(q, uid, data, "armor", 0)
    elif action == "inv_horse":
        await show_inv_items(q, uid, data, "horse", 0)
    elif action.startswith("inv_page_"):
        parts = action.split("_")
        await show_inv_items(q, uid, data, parts[2], int(parts[3]))
    elif action.startswith("equip_"):
        await equip_item(q, uid, action[6:], data)

async def show_inv_items(q, uid, data, item_type, page):
    user = init_user(data[uid])
    inv = user.get("inventory", [])
    items = [i for i in inv if ITEMS.get(i, {}).get("type") == item_type]
    if not items:
        await q.edit_message_text("❌ خالی است!")
        return
    page_items, total = paginate(items, page)
    type_name = {"weapon": "سلاح", "armor": "زره", "horse": "اسب"}
    text = f"🎒 {type_name[item_type]}ها - صفحه {page+1}/{total}\n\n"
    keyboard = []
    for key in page_items:
        item = ITEMS[key]
        equipped = (item_type == "weapon" and user.get("current_weapon") == key) or \
                   (item_type == "armor" and user.get("current_armor") == key) or \
                   (item_type == "horse" and user.get("current_horse") == key)
        mark = " ✅" if equipped else ""
        text += f"• {item['name']}{mark} | +{item['effect']}%\n"
        if not equipped:
            keyboard.append([InlineKeyboardButton(f"🔧 تجهیز", callback_data=f"equip_{key}")])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️", callback_data=f"inv_page_{item_type}_{page-1}"))
    if page < total-1:
        nav.append(InlineKeyboardButton("▶️", callback_data=f"inv_page_{item_type}_{page+1}"))
    if nav:
        keyboard.append(nav)
    keyboard.append([InlineKeyboardButton("🔙", callback_data="inv_back")])
    await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))



async def equip_item(q, uid, item_key, data):
    user = init_user(data[uid])
    if item_key not in user["inventory"]:
        await q.edit_message_text("❌ این آیتم در اینونتوری نیست!")
        return
    
    item = ITEMS[item_key]
    item_type = item["type"]
    
    if item_type == "weapon":
        if user.get("current_weapon") == item_key:
            await q.edit_message_text("❌ این سلاح قبلاً تجهیز شده!")
            return
        user["current_weapon"] = item_key
        
    elif item_type == "armor":
        if user.get("current_armor") == item_key:
            await q.edit_message_text("❌ این زره قبلاً تجهیز شده!")
            return
        user["current_armor"] = item_key
        
    elif item_type == "horse":
        if user.get("current_horse") == item_key:
            await q.edit_message_text("❌ این اسب قبلاً تجهیز شده!")
            return
        user["current_horse"] = item_key
        
    save_data(data)
    await q.edit_message_text(f"✅ {item['name']} تجهیز شد!")


async def inv_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await inventory(update, context)


# ========== جنگ ==========
fight_lock = {}  # جلوگیری از درخواست‌های همزمان جنگ
user_fight_menu = {}  # ذخیره آخرین پیام جنگ هر کاربر

async def solofight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع جنگ با ربات - با قفل جلوگیری از درخواست همزمان"""
    uid = str(update.effective_user.id)
    
    # چک کردن قفل جنگ
    if uid in fight_lock and fight_lock[uid]:
        await update.message.reply_text("⏳ درخواست جنگ قبلی هنوز در حال پردازش است! لطفاً صبر کن.")
        return
    
    # قفل کردن جنگ برای این کاربر
    fight_lock[uid] = True
    
    try:
        data = load_data()
        if uid not in data:
            await update.message.reply_text("❌ اول ثبت‌نام کن!")
            return
        
        user = init_user(data[uid])
        
        if not user.get("army"):
            await update.message.reply_text("⚠️ اول با /chosearmy به ارتش بپیوند!")
            return
        
        # چک کردن بلاک بعد از شکست
        if user.get("fight_blocked_until"):
            blocked = datetime.fromisoformat(user["fight_blocked_until"])
            if datetime.now() < blocked:
                rem = (blocked - datetime.now()).seconds // 60
                await update.message.reply_text(f"❌ {rem} دقیقه دیگه می‌تونی بجنگی.")
                return
        
        # چک کردن کول‌داون
        if user.get("last_fight"):
            last = datetime.fromisoformat(user["last_fight"])
            passed = (datetime.now() - last).seconds
            if passed < FIGHT_COOLDOWN_MINUTES * 60:
                rem = FIGHT_COOLDOWN_MINUTES * 60 - passed
                await update.message.reply_text(f"⏳ {rem//60} دقیقه {rem%60} ثانیه دیگه.")
                return
        
        keyboard = [
            [InlineKeyboardButton("1️⃣ کمک کارگری (500💰 - 0%)", callback_data="fight_1")],
            [InlineKeyboardButton("2️⃣ فتح روستا (1200💰 - 25%)", callback_data="fight_2")],
            [InlineKeyboardButton("3️⃣ جبهه فرعی (1700💰 - 50%)", callback_data="fight_3")],
            [InlineKeyboardButton("4️⃣ جبهه اصلی (2300💰 - 80%)", callback_data="fight_4")]
        ]
        
        # ذخیره message_id پیام جنگ برای بستن خودکار
        msg = await update.message.reply_text(
            "⚔️ **نوع جنگ رو انتخاب کن:** ⚔️",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        user_fight_menu[uid] = msg.message_id
        
        # تنظیم تایمر برای بستن خودکار منو بعد از 30 ثانیه
        context.job_queue.run_once(
            auto_close_fight_menu,
            30,
            data={"chat_id": update.effective_chat.id, "user_id": uid, "message_id": msg.message_id}
        )
    
    except Exception as e:
        print(f"خطا در solofight: {e}")
    
    finally:
        # باز کردن قفل بعد از اتمام
        fight_lock[uid] = False

async def auto_close_fight_menu(context: ContextTypes.DEFAULT_TYPE):
    """بستن خودکار منوی جنگ بعد از ۳۰ ثانیه"""
    job_data = context.job.data
    chat_id = job_data["chat_id"]
    user_id = job_data["user_id"]
    message_id = job_data["message_id"]
    
    try:
        # چک کردن اینکه منو هنوز بسته نشده
        if user_fight_menu.get(user_id) == message_id:
            # حذف دکمه‌ها با ویرایش پیام
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="⏳ زمان انتخاب جنگ به پایان رسید! دوباره /solofight بزن."
            )
            # پاک کردن از لیست
            if user_id in user_fight_menu:
                del user_fight_menu[user_id]
    except Exception as e:
        print(f"خطا در auto_close_fight_menu: {e}")

async def fight_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش نتیجه جنگ با قفل"""
    q = update.callback_query
    await q.answer()
    
    uid = str(q.from_user.id)
    
    # چک کردن اینکه این منو هنوز فعال هست
    if uid in user_fight_menu:
        if q.message.message_id != user_fight_menu[uid]:
            await q.edit_message_text("⏳ این منو منقضی شده! لطفاً دوباره /solofight بزن.")
            return
        # پاک کردن منو از لیست تا دوباره استفاده نشه
        del user_fight_menu[uid]
    
    # چک کردن قفل جنگ
    if uid in fight_lock and fight_lock[uid]:
        await q.edit_message_text("⏳ درخواست جنگ قبلی هنوز در حال پردازش است!")
        return
    
    # قفل کردن جنگ برای این کاربر
    fight_lock[uid] = True
    
    try:
        ft = int(q.data[6:])  # استخراج عدد از "fight_1" → 1
        
        fights = {
            1: {"name": "کمک کارگری", "reward": 500, "base_risk": 0},
            2: {"name": "فتح روستا", "reward": 1200, "base_risk": 25},
            3: {"name": "جبهه فرعی", "reward": 1700, "base_risk": 50},
            4: {"name": "جبهه اصلی", "reward": 2300, "base_risk": 80}
        }
        
        fight = fights[ft]
        
        data = load_data()
        if uid not in data:
            await q.edit_message_text("❌ خطا! کاربر پیدا نشد.")
            return
        
        user = init_user(data[uid])
        
        # محاسبه قدرت کل
        total_bonus = get_total_effect(user) + get_army_bonus(user)
        final_risk = max(5, min(95, fight["base_risk"] - total_bonus))
        
        # تاس انداختن
        roll = randint(1, 100)
        win = roll > final_risk
        
        # ثبت زمان آخرین جنگ
        user["last_fight"] = datetime.now().isoformat()
        
        if win:
            # ====== پیروزی ======
            reward = fight["reward"]
            exp_gain = randint(10, 30)
            
            user["gold"] += reward
            user["exp"] += exp_gain
            user["wins"] += 1
            user["fight_blocked_until"] = None
            
            # چک کردن لول آپ
            leveled = False
            while user["exp"] >= user["exp_needed"]:
                user["exp"] -= user["exp_needed"]
                user["level"] += 1
                user["exp_needed"] = int(user["exp_needed"] * 1.2)
                user["title"] = get_title(user["level"])
                leveled = True
            
            # آپدیت کوئست روزانه
            today = datetime.now().date().isoformat()
            if user.get("last_daily") == today:
                for quest in user.get("daily_quests", []):
                    if not quest.get("completed") and quest["type"] == "win_fight":
                        quest["progress"] = quest.get("progress", 0) + 1
                        if quest["progress"] >= quest["target"]:
                            quest["completed"] = True
            
            save_data(data)
            
            # ساخت پیام نتیجه
            msg = f"🎉 **پیروزی در {fight['name']}!** 🎉\n\n"
            msg += f"💰 +{reward} سکه\n"
            msg += f"✨ +{exp_gain} تجربه\n"
            msg += f"🎲 شانس شکست: {final_risk}%\n"
            
            if leveled:
                msg += f"\n🌟 **لول آپ!**\n"
                msg += f"🏅 لول: {user['level']}\n"
                msg += f"🎭 لقب جدید: {user['title']}"
            
            await q.edit_message_text(msg)
            
        else:
            # ====== شکست ======
            user["fight_blocked_until"] = (datetime.now() + timedelta(minutes=FIGHT_BLOCK_MINUTES)).isoformat()
            save_data(data)
            
            await q.edit_message_text(
                f"💀 **شکست در {fight['name']}!** 💀\n\n"
                f"⏳ تا {FIGHT_BLOCK_MINUTES} دقیقه نمی‌تونی بجنگی.\n"
                f"🎲 شانس شکست: {final_risk}%\n"
                f"🎲 عدد تاس: {roll}\n\n"
                "بعد از بهبودی دوباره /solofight بزن."
            )
    
    except ValueError:
        await q.edit_message_text("❌ خطا در پردازش درخواست!")
    
    except Exception as e:
        print(f"خطا در fight_callback: {e}")
        await q.edit_message_text("❌ خطایی رخ داد! دوباره تلاش کن.")
    
    finally:
        # باز کردن قفل (حتماً اجرا می‌شه)
        fight_lock[uid] = False



# ========== حمله ==========
attack_cooldown = {}

async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attacker_id = str(update.effective_user.id)
    data = load_data()
    if attacker_id not in data:
        await update.message.reply_text("❌ اول ثبت‌نام کن!")
        return
    attacker = init_user(data[attacker_id])
    if not attacker.get("army"):
        await update.message.reply_text("⚠️ اول به ارتش بپیوند!")
        return
    last = attack_cooldown.get(attacker_id)
    if last and (datetime.now() - last).seconds < ATTACK_COOLDOWN_SECONDS:
        remaining = ATTACK_COOLDOWN_SECONDS - (datetime.now() - last).seconds
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        await update.message.reply_text(f"⏳ {hours} ساعت {minutes} دقیقه دیگه.")
        return
    args = context.args
    if not args:
        await update.message.reply_text("⚔️ نحوه حمله:\n/attack @username\n/attack آیدی")
        return
    target_input = args[0]
    target_id = None
    if target_input.startswith("@"):
        username = target_input[1:]
        for uid, u in data.items():
            if u.get("username", "").lower() == username.lower():
                target_id = uid
                break
    else:
        target_id = target_input
    if not target_id or target_id not in data:
        await update.message.reply_text("❌ کاربر پیدا نشد!")
        return
    if attacker_id == target_id:
        await update.message.reply_text("❌ نمی‌تونی به خودت حمله کنی!")
        return
    target = init_user(data[target_id])
    if not target.get("army"):
        await update.message.reply_text("❌ هدف هنوز به ارتشی نپیوسته!")
        return
    attack_cooldown[attacker_id] = datetime.now()
    a_power = get_total_effect(attacker) + get_army_bonus(attacker)
    t_power = get_total_effect(target) + get_army_bonus(target)
    total = a_power + t_power
    chance = max(20, min(80, int((a_power / total) * 100))) if total > 0 else 50
    roll = randint(1, 100)
    win = roll <= chance
    loot = max(50, int(target["gold"] * randint(15, 25) / 100))
    if win:
        if target["gold"] >= loot:
            attacker["gold"] += loot
            target["gold"] -= loot
        else:
            loot = target["gold"]
            attacker["gold"] += loot
            target["gold"] = 0
        exp = randint(10, 25)
        attacker["exp"] += exp
        attacker["wins"] += 1
        target["losses"] += 1
        leveled = False
        while attacker["exp"] >= attacker["exp_needed"]:
            attacker["exp"] -= attacker["exp_needed"]
            attacker["level"] += 1
            attacker["exp_needed"] = int(attacker["exp_needed"] * 1.2)
            attacker["title"] = get_title(attacker["level"])
            leveled = True
        
        # آپدیت کوئست حمله
        today = datetime.now().date().isoformat()
        if attacker.get("last_daily") == today:
            for quest in attacker.get("daily_quests", []):
                if not quest.get("completed") and quest["type"] == "attack":
                    quest["progress"] = quest.get("progress", 0) + 1
                    if quest["progress"] >= quest["target"]:
                        quest["completed"] = True
        
        save_data(data)
        msg = f"⚔️ حمله موفق!\n💰 {loot} سکه گرفتی!\n✨ +{exp} تجربه\n🎲 شانس: {chance}%"
        if leveled:
            msg += f"\n🌟 لول {attacker['level']} | لقب: {attacker['title']}"
        await update.message.reply_text(msg)
    else:
        counter = max(30, int(attacker["gold"] * randint(5, 10) / 100))
        if attacker["gold"] >= counter:
            target["gold"] += counter
            attacker["gold"] -= counter
        else:
            counter = attacker["gold"]
            target["gold"] += counter
            attacker["gold"] = 0
        exp = randint(5, 15)
        target["exp"] += exp
        target["wins"] += 1
        attacker["losses"] += 1
        leveled = False
        while target["exp"] >= target["exp_needed"]:
            target["exp"] -= target["exp_needed"]
            target["level"] += 1
            target["exp_needed"] = int(target["exp_needed"] * 1.2)
            target["title"] = get_title(target["level"])
            leveled = True
        save_data(data)
        await update.message.reply_text(f"🛡️ حمله ناموفق!\n💰 {counter} سکه از دست دادی!\n🎲 شانس: {chance}%")

# ========== رنکینگ ==========
async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 ثروتمند", callback_data="top_gold")],
        [InlineKeyboardButton("⚔️ قدرتمند", callback_data="top_level")],
        [InlineKeyboardButton("🏆 پرافتخار", callback_data="top_win")],
        [InlineKeyboardButton("❌ بستن", callback_data="top_close")]
    ]
    await update.message.reply_text("🏆 رنکینگ:", reply_markup=InlineKeyboardMarkup(keyboard))

async def top_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    action = q.data
    if action == "top_close":
        await q.edit_message_text("🚪 بسته شد.")
        return
    cat = action[4:]
    data = load_data()
    users = []
    for uid, u in data.items():
        u = init_user(u)
        users.append({"name": u["username"], "gold": u["gold"], "level": u["level"], "wins": u["wins"]})
    if cat == "gold":
        users.sort(key=lambda x: x["gold"], reverse=True)
        title = "💰 ثروتمندترین‌ها"
        val_key = "gold"
        val_name = "سکه"
    elif cat == "level":
        users.sort(key=lambda x: x["level"], reverse=True)
        title = "⚔️ قدرتمندترین‌ها"
        val_key = "level"
        val_name = "لول"
    else:
        users.sort(key=lambda x: x["wins"], reverse=True)
        title = "🏆 پرافتخارترین‌ها"
        val_key = "wins"
        val_name = "برد"
    text = f"{title}\n\n"
    for i, u in enumerate(users[:10], 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        text += f"{medal} {u['name']} | {u[val_key]} {val_name}\n"
    await q.edit_message_text(text)

# ========== کوئست روزانه ==========
async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    data = load_data()
    if uid not in data:
        await update.message.reply_text("❌ اول ثبت‌نام کن!")
        return
    user = init_user(data[uid])
    today = datetime.now().date().isoformat()
    if user.get("last_daily") != today:
        user["daily_quests"] = []
        for q in sample(QUESTS_LIST, min(3, len(QUESTS_LIST))):
            user["daily_quests"].append({
                "name": q["name"], "desc": q["desc"], "type": q["type"],
                "target": q["target"], "progress": 0, "completed": False,
                "gold": q["gold"], "exp": q["exp"]
            })
        user["last_daily"] = today
        save_data(data)
    quests = user.get("daily_quests", [])
    if not quests:
        await update.message.reply_text("🎯 امروز کوئستی ندارم!")
        return
    text = f"🎯 کوئست‌های روزانه - {today}\n\n"
    for i, q in enumerate(quests, 1):
        status = "✅" if q["completed"] else "⏳"
        text += f"{status} {i}. {q['name']}\n   {q['desc']}\n   پیشرفت: {q['progress']}/{q['target']}\n"
        if not q["completed"]:
            text += f"   🎁 {q['gold']}💰 + {q['exp']}✨\n"
        text += "\n"
    await update.message.reply_text(text)

async def claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    data = load_data()
    if uid not in data:
        await update.message.reply_text("❌ اول ثبت‌نام کن!")
        return
    user = init_user(data[uid])
    for quest in user.get("daily_quests", []):
        if quest.get("completed") and not quest.get("claimed"):
            quest["claimed"] = True
            user["gold"] += quest["gold"]
            user["exp"] += quest["exp"]
            leveled = False
            while user["exp"] >= user["exp_needed"]:
                user["exp"] -= user["exp_needed"]
                user["level"] += 1
                user["exp_needed"] = int(user["exp_needed"] * 1.2)
                user["title"] = get_title(user["level"])
                leveled = True
            save_data(data)
            msg = f"🎉 پاداش {quest['name']} دریافت شد!\n💰 +{quest['gold']} سکه\n✨ +{quest['exp']} تجربه"
            if leveled:
                msg += f"\n🌟 لول {user['level']} | لقب: {user['title']}"
            await update.message.reply_text(msg)
            return
    await update.message.reply_text("❌ هیچ کوئست تکمیل شده‌ای برای دریافت نداری!")



# ========== ادمین ==========
admin_temp_data = {}  # ذخیره موقت اطلاعات ادمین

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ دسترسی ندارید!")
        return
    keyboard = [
        [InlineKeyboardButton("💰 افزودن سکه", callback_data="admin_add")],
        [InlineKeyboardButton("💸 حذف سکه", callback_data="admin_remove")],
        [InlineKeyboardButton("🔄 ریست", callback_data="admin_reset")],
        [InlineKeyboardButton("❌ بستن", callback_data="admin_close")]
    ]
    await update.message.reply_text("👑 پنل ادمین:", reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.from_user.id != ADMIN_ID:
        await q.edit_message_text("❌ دسترسی ندارید!")
        return
    action = q.data
    if action == "admin_close":
        await q.edit_message_text("🚪 بسته شد.")
    elif action == "admin_add":
        admin_temp_data[q.from_user.id] = {"action": "add"}
        await q.edit_message_text("💰 لطفاً آیدی کاربر و مقدار سکه رو به فرمت زیر بفرست:\n\n`آیدی مقدار`\n\nمثال: `5596656149 1000`", parse_mode="Markdown")
    elif action == "admin_remove":
        admin_temp_data[q.from_user.id] = {"action": "remove"}
        await q.edit_message_text("💸 لطفاً آیدی کاربر و مقدار سکه رو به فرمت زیر بفرست:\n\n`آیدی مقدار`\n\nمثال: `5596656149 500`", parse_mode="Markdown")
    elif action == "admin_reset":
        admin_temp_data[q.from_user.id] = {"action": "reset"}
        await q.edit_message_text("🔄 لطفاً آیدی کاربر رو بفرست:\n\nمثال: `5596656149`", parse_mode="Markdown")

async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return
    
    # چک کردن اینکه کاربر در حالت ادمین هست یا نه
    if user_id not in admin_temp_data:
        return
    
    temp = admin_temp_data[user_id]
    action = temp["action"]
    text = update.message.text.strip()
    data = load_data()
    
    if action == "add":
        parts = text.split()
        if len(parts) != 2:
            await update.message.reply_text("❌ فرمت اشتباه! مثال: `5596656149 1000`")
            return
        try:
            target_id, amount = parts[0], int(parts[1])
            if amount <= 0:
                await update.message.reply_text("❌ مقدار باید بیشتر از 0 باشه!")
                return
            if target_id not in data:
                await update.message.reply_text(f"❌ کاربر با آیدی {target_id} پیدا نشد!")
                return
            data[target_id]["gold"] += amount
            save_data(data)
            await update.message.reply_text(f"✅ {amount} سکه به {data[target_id]['username']} اضافه شد!\nطلای فعلی: {data[target_id]['gold']}")
        except:
            await update.message.reply_text("❌ عدد معتبر وارد کن!")
        finally:
            del admin_temp_data[user_id]
            
    elif action == "remove":
        parts = text.split()
        if len(parts) != 2:
            await update.message.reply_text("❌ فرمت اشتباه! مثال: `5596656149 500`")
            return
        try:
            target_id, amount = parts[0], int(parts[1])
            if amount <= 0:
                await update.message.reply_text("❌ مقدار باید بیشتر از 0 باشه!")
                return
            if target_id not in data:
                await update.message.reply_text(f"❌ کاربر با آیدی {target_id} پیدا نشد!")
                return
            if data[target_id]["gold"] < amount:
                await update.message.reply_text(f"❌ کاربر طلای کافی نداره! طلای فعلی: {data[target_id]['gold']}")
                return
            data[target_id]["gold"] -= amount
            save_data(data)
            await update.message.reply_text(f"✅ {amount} سکه از {data[target_id]['username']} کم شد!\nطلای فعلی: {data[target_id]['gold']}")
        except:
            await update.message.reply_text("❌ عدد معتبر وارد کن!")
        finally:
            del admin_temp_data[user_id]
            
    elif action == "reset":
        target_id = text.strip()
        if target_id not in data:
            await update.message.reply_text(f"❌ کاربر با آیدی {target_id} پیدا نشد!")
            del admin_temp_data[user_id]
            return
        username = data[target_id]["username"]
        data[target_id] = {
            "username": username, "level": 1, "title": "رعیت", "gold": 100,
            "exp": 0, "exp_needed": 100, "army": None, "army_join_time": None,
            "inventory": [], "current_weapon": None, "current_armor": None,
            "current_horse": None, "last_fight": None, "fight_blocked_until": None,
            "wins": 0, "losses": 0, "last_attack": None
        }
        save_data(data)
        await update.message.reply_text(f"✅ کاربر {username} با موفقیت ریست شد!")
        del admin_temp_data[user_id]






# ====================================================================
# ============================== دوئل ===============================
# ====================================================================

# ذخیره دوئل‌های فعال
active_duels = {}

async def duel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع یک دوئل با شرط‌بندی"""
    user_id = str(update.effective_user.id)
    data = load_data()
    
    if user_id not in data:
        await update.message.reply_text("❌ اول با /register ثبت‌نام کن!")
        return
    
    user = init_user(data[user_id])
    
    # چک کردن اینکه کاربر در دوئل فعال نیست
    for duel_id, duel_info in active_duels.items():
        if duel_info["creator_id"] == user_id:
            await update.message.reply_text("❌ تو قبلاً یک دوئل ایجاد کرده‌ای! اول اون رو لغو کن یا منتظر بمان.")
            return
        if duel_info["joiner_id"] == user_id:
            await update.message.reply_text("❌ تو قبلاً به یک دوئل پیوسته‌ای! اول اون رو تمام کن.")
            return
    
    # درخواست مقدار شرط
    admin_temp_data[user_id] = {"action": "duel_bet"}
    await update.message.reply_text(
        "⚔️ **دوئل با شرط‌بندی** ⚔️\n\n"
        "💰 چقدر می‌خوای شرط ببندی؟\n"
        f"💰 طلای فعلی تو: {user['gold']} سکه\n\n"
        "لطفاً مقدار رو به عدد وارد کن (حداقل ۱۰۰ سکه):",
        parse_mode="Markdown"
    )

async def handle_duel_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش مقدار شرط دوئل"""
    user_id = str(update.effective_user.id)
    text = update.message.text.strip()
    
    # چک کردن اینکه کاربر در حالت شرط‌بندی هست
    temp = admin_temp_data.get(user_id)
    if not temp or temp.get("action") != "duel_bet":
        return
    
    data = load_data()
    if user_id not in data:
        await update.message.reply_text("❌ خطا! لطفاً دوباره /duel بزن.")
        del admin_temp_data[user_id]
        return
    
    user = init_user(data[user_id])
    
    try:
        bet_amount = int(text)
        if bet_amount < 100:
            await update.message.reply_text("❌ حداقل شرط ۱۰۰ سکه است!")
            return
        if bet_amount > user["gold"]:
            await update.message.reply_text(f"❌ طلای کافی نداری! طلای فعلی تو: {user['gold']} سکه")
            return
        
        # ایجاد دوئل جدید
        duel_id = str(datetime.now().timestamp())
        active_duels[duel_id] = {
            "creator_id": user_id,
            "creator_name": user["username"],
            "bet_amount": bet_amount,
            "joiner_id": None,
            "joiner_name": None,
            "status": "waiting",  # waiting, started, finished
            "created_at": datetime.now()
        }
        
        # ذخیره در دیتای موقت
        admin_temp_data[user_id] = {"action": "duel_creator", "duel_id": duel_id}
        
        # دکمه‌های پیوستن و لغو
        keyboard = [
            [
                InlineKeyboardButton("⚔️ پیوستن به دوئل", callback_data=f"duel_join_{duel_id}"),
                InlineKeyboardButton("❌ لغو دوئل", callback_data=f"duel_cancel_{duel_id}")
            ]
        ]
        
        # ریپلای به پیام کاربر
        await update.message.reply_text(
            f"⚔️ **دوئل ایجاد شد!** ⚔️\n\n"
            f"🎭 {user['username']} یک دوئل با شرط {bet_amount}💰 ایجاد کرد!\n\n"
            f"هر کسی می‌تونه با زدن دکمه **پیوستن** وارد دوئل بشه.\n"
            f"برنده کل مبلغ ({bet_amount * 2}💰) رو می‌بره!\n\n"
            f"⏳ زمان باقی‌مانده: ۲ دقیقه",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        # تنظیم تایمر ۲ دقیقه‌ای برای انقضای دوئل
        context.job_queue.run_once(
            expire_duel,
            120,  # 2 دقیقه
            data={"duel_id": duel_id, "chat_id": update.effective_chat.id}
        )
        
    except ValueError:
        await update.message.reply_text("❌ لطفاً یک عدد معتبر وارد کن!")
        del admin_temp_data[user_id]

async def duel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش دکمه‌های پیوستن و لغو دوئل"""
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    data = load_data()
    
    if user_id not in data:
        await query.edit_message_text("❌ اول با /register ثبت‌نام کن!")
        return
    
    user = init_user(data[user_id])
    action = query.data
    
    if action.startswith("duel_join_"):
        duel_id = action.replace("duel_join_", "")
        
        if duel_id not in active_duels:
            await query.edit_message_text("❌ این دوئل منقضی شده یا وجود ندارد!")
            return
        
        duel = active_duels[duel_id]
        
        if duel["status"] != "waiting":
            await query.edit_message_text("❌ این دوئل قبلاً شروع شده یا تمام شده!")
            return
        
        if duel["creator_id"] == user_id:
            await query.edit_message_text("❌ نمی‌تونی با خودت دوئل کنی!")
            return
        
        # چک کردن طلای کاربر برای شرط
        if user["gold"] < duel["bet_amount"]:
            await query.edit_message_text(f"❌ طلای کافی نداری! نیاز به {duel['bet_amount']} سکه داری!")
            return
        
        # پیوستن به دوئل
        duel["joiner_id"] = user_id
        duel["joiner_name"] = user["username"]
        duel["status"] = "started"
        
        # کم کردن طلا از هر دو طرف
        creator = init_user(data[duel["creator_id"]])
        creator["gold"] -= duel["bet_amount"]
        user["gold"] -= duel["bet_amount"]
        
        save_data(data)
        
        # شروع دوئل (شانس ۵۰-۵۰)
        import random
        winner_id = random.choice([duel["creator_id"], duel["joiner_id"]])
        
        total_prize = duel["bet_amount"] * 2
        
        if winner_id == duel["creator_id"]:
            winner_name = duel["creator_name"]
            creator["gold"] += total_prize
        else:
            winner_name = duel["joiner_name"]
            user["gold"] += total_prize
        
        save_data(data)
        
        duel["status"] = "finished"
        
        # حذف دوئل از لیست فعال
        del active_duels[duel_id]
        
        # اعلام نتیجه
        result_text = (
            f"⚔️ **نتیجه دوئل!** ⚔️\n\n"
            f"🎭 {duel['creator_name']} vs {duel['joiner_name']}\n"
            f"💰 شرط هرکدام: {duel['bet_amount']} سکه\n"
            f"🏆 جایزه نهایی: {total_prize} سکه\n\n"
            f"🎉 **برنده: {winner_name}** 🎉\n\n"
            f"💰 {winner_name} {total_prize} سکه برنده شد!"
        )
        
        await query.edit_message_text(result_text, parse_mode="Markdown")
        
    elif action.startswith("duel_cancel_"):
        duel_id = action.replace("duel_cancel_", "")
        
        if duel_id not in active_duels:
            await query.edit_message_text("❌ این دوئل منقضی شده یا وجود ندارد!")
            return
        
        duel = active_duels[duel_id]
        
        # فقط سازنده دوئل می‌تونه لغو کنه
        if duel["creator_id"] != user_id:
            await query.edit_message_text("❌ فقط کسی که دوئل رو ساخته می‌تونه لغوش کنه!")
            return
        
        if duel["status"] != "waiting":
            await query.edit_message_text("❌ این دوئل قبلاً شروع شده و قابل لغو نیست!")
            return
        
        del active_duels[duel_id]
        
        # پاک کردن حالت از admin_temp_data
        if user_id in admin_temp_data:
            del admin_temp_data[user_id]
        
        await query.edit_message_text(f"❌ دوئل توسط {duel['creator_name']} لغو شد!")

async def expire_duel(context: ContextTypes.DEFAULT_TYPE):
    """انقضای دوئل بعد از ۲ دقیقه"""
    job_data = context.job.data
    duel_id = job_data["duel_id"]
    chat_id = job_data["chat_id"]
    
    if duel_id in active_duels:
        duel = active_duels[duel_id]
        
        if duel["status"] == "waiting":
            # لغو خودکار دوئل
            del active_duels[duel_id]
            
            # پاک کردن حالت از admin_temp_data
            if duel["creator_id"] in admin_temp_data:
                del admin_temp_data[duel["creator_id"]]
            
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"⏳ دوئل {duel['creator_name']} به دلیل عدم حضور حریف لغو شد!"
                )
            except:
                pass




# ========== تغییر اسم ==========
async def rename(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تغییر اسم کاربر (فقط ادمین)"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ فقط ادمین می‌تونه اسم پلیرا رو تغییر بده!")
        return
    
    try:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text(
                "❌ نحوه استفاده:\n/rename `آیدی عددی` `اسم جدید`\n\n"
                "مثال: `/rename 5596656149 ArashNew`",
                parse_mode="Markdown"
            )
            return
        
        target_id = args[0]
        new_name = " ".join(args[1:])
        
        if len(new_name) > 15 or " " in new_name or not new_name.replace("_", "").isalnum():
            await update.message.reply_text("❌ اسم نامعتبر! (حداکثر ۱۵ حرف، فقط حروف انگلیسی و اعداد)")
            return
        
        data = load_data()
        if target_id not in data:
            await update.message.reply_text(f"❌ کاربر با آیدی {target_id} پیدا نشد!")
            return
        
        # چک تکراری نبودن اسم
        for uid, user in data.items():
            if user.get("username", "").lower() == new_name.lower() and uid != target_id:
                await update.message.reply_text(f"❌ اسم {new_name} قبلاً استفاده شده!")
                return
        
        old_name = data[target_id]["username"]
        data[target_id]["username"] = new_name
        save_data(data)
        
        await update.message.reply_text(
            f"✅ اسم کاربر با موفقیت تغییر کرد!\n\n"
            f"👤 از: {old_name}\n"
            f"👤 به: {new_name}"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {str(e)}")




# ========== کامندهای فارسی ==========
async def handle_farsi_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تشخیص کامندهای فارسی بدون نیاز به /"""
    user_id = str(update.effective_user.id)
    text = update.message.text.strip()
    
    # فقط اگه پیام با / شروع نشده باشه
    if text.startswith("/"):
        return
    
    # تشخیص کامندهای فارسی
    farsi_commands = {
        "دوئل": "duel",
        "پروفایل": "profile",
        "ثبت نام": "register",
        "ثبت‌نام": "register",
        "جنگ": "solofight",
        "حمله": "attack",
        "خرید": "shop",
        "اینونتوری": "inventory",
        "رنکینگ": "top",
        "کوئست": "daily",
        "گرفتن": "claim"
    }
    
    for farsi, english in farsi_commands.items():
        if text == farsi:
            if english == "duel":
                await duel(update, context)
            elif english == "profile":
                await profile(update, context)
            elif english == "register":
                await register(update, context)
            elif english == "solofight":
                await solofight(update, context)
            elif english == "attack":
                await attack(update, context)
            elif english == "shop":
                await shop(update, context)
            elif english == "inventory":
                await inventory(update, context)
            elif english == "top":
                await top(update, context)
            elif english == "daily":
                await daily(update, context)
            elif english == "claim":
                await claim(update, context)
            return




# ========== اجرا ==========


def main():
    app = Application.builder().token("8919439033:AAHYQlNGEJpdag_5-fl-LWxm6Er8N30kd64").build()
    
    # ========== 1. کامندها (CommandHandler) ==========
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("register", register))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("chosearmy", chosearmy))
    app.add_handler(CommandHandler("leavearmy", leavearmy))
    app.add_handler(CommandHandler("solofight", solofight))
    app.add_handler(CommandHandler("inventory", inventory))
    app.add_handler(CommandHandler("shop", shop))
    app.add_handler(CommandHandler("attack", attack))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(CommandHandler("daily", daily))
    app.add_handler(CommandHandler("claim", claim))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("duel", duel))
    app.add_handler(CommandHandler("rename", rename))
    
    # ========== 2. کالبک‌ها (CallbackQueryHandler) ==========
    app.add_handler(CallbackQueryHandler(army_callback, pattern="^army_"))
    app.add_handler(CallbackQueryHandler(fight_callback, pattern="^fight_"))
    app.add_handler(CallbackQueryHandler(shop_callback, pattern="^shop_|buy_|sell_|spage_"))
    app.add_handler(CallbackQueryHandler(inv_callback, pattern="^inv_|equip_|inv_back"))
    app.add_handler(CallbackQueryHandler(top_callback, pattern="^top_"))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^admin_"))
    app.add_handler(CallbackQueryHandler(duel_callback, pattern="^duel_"))

       
    # ========== هندلر کامندهای فارسی (بدون /) ==========
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_farsi_commands))
    
    # ========== 3. هندلرهای متنی (MessageHandler) با اولویت ==========
    # اولویت 1: دوئل (عدد شرط)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_duel_bet), group=1)
    
    # اولویت 2: ادمین (عملیات مدیریتی)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_text), group=2)
    
    # اولویت 3: ثبت‌نام (انتخاب اسم)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name), group=3)
    
    # ========== 4. اجرا ==========
    print("✅ Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()

