import os
import datetime
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# توکن ربات از متغیر محیطی
TOKEN = "8467023979:AAFbvk4-G67rx9hOKK5ArpQZkfMxY1Hf8VU"

# دیتابیس اعضا و پرداخت‌ها
# ساختار: { "نام عضو": { "is_admin": True/False, "payments": { "YYYY-MM": {"status": "بدهکار/پرداخت", "receipt": file_id} } } }
# مثال
users = {
    "محمد امین محمدی": {"is_admin": False},
    "فرزان میرزایی": {"is_admin": False},
    "ماهان محمدی": {"is_admin": False},
    "امیر حسین سلیمی": {"is_admin": False},
    "محمد جامه": {"is_admin": False},
    "محمد عزیزی": {"is_admin": False},
    "ایلیا عندلیب": {"is_admin": False},
    "پوریا داها": {"is_admin": False},
    "ارمین احمدی": {"is_admin": False},
    "ارتین احمدی": {"is_admin": False},
    "ارشیا احمدی": {"is_admin": False},
    "کمیل امینی": {"is_admin": False},
    "دانیال فایض زاده": {"is_admin": False},
    "مهدی رضایی": {"is_admin": False},
    "کارو": {"is_admin": False},
    "حیدری": {"is_admin": False},
    "فراز رستمی تبار": {"is_admin": False},
    "ارین سماواتیان": {"is_admin": False},

    "سارا": {"is_admin": True}
}

# آیدی تلگرام ادمین‌ها
ADMINS = [96337854, 6383651186]

# کمک برای گرفتن ماه جاری شمسی
def current_month():
    return jdatetime.datetime.now().strftime("%Y-%m")

# فرمت تاریخ فارسی برای پیام‌ها
def persian_date():
    return jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M")

# ===================== تابع مشترک برای نمایش منو =====================
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    member_names = [name for name, data in users.items() if not data.get("is_admin")]
    keyboard = [[KeyboardButton(name)] for name in member_names]

    # اضافه کردن دکمه منوی ادمین
    if user.id in ADMINS:
        keyboard.append([KeyboardButton("منوی ادمین")])

    if not member_names and not (user.id in ADMINS):
        await update.message.reply_text("📌 هنوز هیچ عضوی ثبت نشده! (ادمین باید اضافه کند)")
        return

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    context.user_data.pop("name", None) # پاک کردن اسم کاربر
    context.user_data.pop("awaiting_reset_confirm", None) # پاک کردن وضعیت تأیید
    await update.message.reply_text(
        f"سلام {user.first_name}!\nلطفا یکی از گزینه‌ها رو انتخاب کن:",
        reply_markup=reply_markup
    )

# ===================== شروع / بازگشت به منو =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update, context)

# ===================== انتخاب اسم / منوی ادمین =====================
async def choose_name(update: Update, context: ContextTypes.DEFAULT_TYPE, is_admin=False):
    name = update.message.text.strip()

    if not is_admin:
        # بررسی کنید که آیا کاربر انتخاب شده یک عضو است یا خیر
        if name not in users or users[name]["is_admin"]:
            await update.message.reply_text("❌ این اسم در لیست اعضا وجود نداره.")
            return
        context.user_data["name"] = name

        keyboard = [
            [KeyboardButton("✅ پرداخت کردم")],
            [KeyboardButton("📋 وضعیت من")],
            [KeyboardButton("بازگشت")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(f"{name} انتخاب شد ✅", reply_markup=reply_markup)
    else: # is_admin == True
        keyboard = [
            [KeyboardButton("👥 لیست همه"), KeyboardButton("📎 رسیدها")],
            [KeyboardButton("➕ اضافه کردن عضو"), KeyboardButton("🗑 حذف عضو")],
            [KeyboardButton("تغییر وضعیت پرداخت"), KeyboardButton("ریست پرداخت")],
            [KeyboardButton("ارسال یادآوری ماهانه"), KeyboardButton("ریست کامل ربات")],
            [KeyboardButton("بازگشت")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("به منوی ادمین خوش آمدید. لطفا یکی از گزینه‌ها را انتخاب کنید:", reply_markup=reply_markup)

# ===================== ثبت پرداخت =====================
async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data.get("name")
    if not name:
        await update.message.reply_text("❌ اول باید اسمت رو از لیست انتخاب کنی.")
        return

    month = current_month()
    users[name].setdefault("payments", {}).setdefault(month, {"status": "بدهکار", "receipt": None})

    users[name]["payments"][month]["status"] = "پرداخت کرده ✅"
    users[name]["payments"][month]["date"] = persian_date()

    await update.message.reply_text(
        f"{name} عزیز، پرداخت برای ماه {month} ثبت شد ✅\nحالا رسید رو هم بفرست (عکس یا فایل)."
    )
    print(f"[LOG] {name} پرداخت کرد در ماه {month}")

# ===================== دریافت رسید =====================
async def get_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data.get("name")
    if not name:
        await update.message.reply_text("❌ اول باید اسمت رو انتخاب کنی.")
        return

    month = current_month()
    users[name].setdefault("payments", {}).setdefault(month, {"status": "بدهکار", "receipt": None})

    if update.message.photo or update.message.document:
        file_id = update.message.photo[-1].file_id if update.message.photo else update.message.document.file_id
        users[name]["payments"][month]["receipt"] = file_id
        await update.message.reply_text(f"رسید پرداخت {name} برای ماه {month} ثبت شد 📸✅")
        print(f"[LOG] رسید {name} در ماه {month} ذخیره شد")
    else:
        await update.message.reply_text("❌ لطفا عکس یا فایل رسید ارسال کنید.")

# ===================== وضعیت شخصی =====================
async def my_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data.get("name")
    if not name:
        await update.message.reply_text("❌ اول باید اسمت رو انتخاب کنی.")
        return

    text = f"📋 وضعیت شما:\n"
    user_payments = users.get(name, {}).get("payments", {})
    months = sorted(user_payments.keys(), reverse=True)
    if not months:
        text += "تمام ماه‌ها بدهکار هستید."
    else:
        for m in months:
            status = user_payments[m]["status"]
            date = user_payments[m].get("date", "")
            receipt = "📎 رسید ثبت شده" if user_payments[m]["receipt"] else "❌ رسید ندارد"
            text += f"▫️ {m} → {status} {receipt} {date}\n"
    await update.message.reply_text(text)

# ===================== لیست همه اعضا (ادمین) =====================
async def list_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        await update.message.reply_text("❌ شما دسترسی ادمین ندارید.")
        return

    member_names = [name for name, data in users.items() if not data.get("is_admin")]
    if not member_names:
        await update.message.reply_text("📌 هیچ عضوی ثبت نشده.")
        return

    text = "📋 لیست شهریه همه اعضا:\n\n"
    for name in member_names:
        text += f"▫️ {name}:\n"
        user_payments = users.get(name, {}).get("payments", {})
        months = sorted(user_payments.keys(), reverse=True)
        if not months:
            text += "   تمام ماه‌ها بدهکار\n"
        else:
            for m in months:
                status = user_payments[m]["status"]
                receipt = "📎" if user_payments[m]["receipt"] else "❌"
                text += f"   {m} → {status} {receipt}\n"
        text += "\n"
    await update.message.reply_text(text)

# ===================== ارسال رسیدها (ادمین) =====================
async def send_receipts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        await update.message.reply_text("❌ شما دسترسی ادمین ندارید.")
        return

    found_receipts = False
    for name in users:
        user_payments = users.get(name, {}).get("payments", {})
        for m, data in user_payments.items():
            if data.get("receipt"):
                found_receipts = True
                await update.message.reply_text(f"📎 رسید {name} ماه {m}:")
                try:
                    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=data["receipt"])
                except Exception as e:
                    await update.message.reply_text(f"خطا در ارسال رسید {name} ماه {m}: {e}")
    if not found_receipts:
        await update.message.reply_text("📌 هیچ رسیدی ثبت نشده است.")
    print("[LOG] ادمین رسیدها را دریافت کرد 📎")

# ===================== ارسال یادآوری ماهانه (ادمین) =====================
async def send_monthly_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        await update.message.reply_text("❌ شما دسترسی ادمین ندارید.")
        return

    message_text = "سلام دوستان عزیز،\nلطفاً شهریه این ماه رو پرداخت کنید. ✅\nممنون از همکاری‌تون! 🙏"

    member_names = [name for name, data in users.items() if not data.get("is_admin")]

    if not member_names:
        await update.message.reply_text("📌 هیچ عضوی برای ارسال پیام وجود ندارد.")
        return

    for name in member_names:
        await update.message.reply_text(f"پیام یادآوری برای {name} ارسال شد.")

    await update.message.reply_text("✅ پیام یادآوری برای همه اعضا ارسال شد.")

# ===================== اضافه کردن عضو (ادمین) =====================
async def add_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        await update.message.reply_text("❌ شما دسترسی ادمین ندارید.")
        return
    if not context.args:
        await update.message.reply_text("📌 دستور درست: /addmember نام عضو")
        return
    name = " ".join(context.args).strip()
    if name in users:
        await update.message.reply_text("❌ این عضو از قبل وجود دارد.")
        return
    users[name] = {"is_admin": False, "payments": {}}
    await update.message.reply_text(f"✅ عضو {name} اضافه شد.")
    await show_main_menu(update, context)

# ===================== حذف عضو (ادمین) =====================
async def del_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        await update.message.reply_text("❌ شما دسترسی ادمین ندارید.")
        return
    if not context.args:
        await update.message.reply_text("📌 دستور درست: /delmember نام عضو")
        return
    name = " ".join(context.args).strip()
    if name not in users or users[name]["is_admin"]:
        await update.message.reply_text("❌ چنین عضوی وجود ندارد یا ادمین است.")
        return
    del users[name]
    await update.message.reply_text(f"🗑 عضو {name} حذف شد.")
    await show_main_menu(update, context)

# ===================== تغییر وضعیت پرداخت (ادمین) =====================
async def change_payment_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        await update.message.reply_text("❌ شما دسترسی ادمین ندارید.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("📌 دستور درست: /changepayment نام_عضو YYYY-MM")
        return

    name = context.args[0]
    month = context.args[1]

    if name not in users:
        await update.message.reply_text("❌ چنین عضوی وجود ندارد.")
        return

    users[name].setdefault("payments", {}).setdefault(month, {"status": "بدهکار", "receipt": None})

    # تغییر وضعیت به 'پرداخت کرده' و ثبت تاریخ
    users[name]["payments"][month]["status"] = "پرداخت کرده (تغییر توسط ادمین) ✅"
    users[name]["payments"][month]["date"] = persian_date()

    await update.message.reply_text(f"✅ وضعیت پرداخت {name} برای ماه {month} به 'پرداخت کرده' تغییر یافت.")
    print(f"[LOG] ادمین وضعیت پرداخت {name} را برای ماه {month} تغییر داد.")

# ===================== ریست پرداخت (ادمین) =====================
async def reset_payment_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        await update.message.reply_text("❌ شما دسترسی ادمین ندارید.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("📌 دستور درست: /resetpayment نام_عضو YYYY-MM")
        return

    name = context.args[0]
    month = context.args[1]

    if name not in users or month not in users[name].get("payments", {}):
        await update.message.reply_text("❌ اطلاعات پرداختی برای این عضو و ماه وجود ندارد.")
        return

    users[name]["payments"][month]["status"] = "بدهکار"
    users[name]["payments"][month].pop("date", None)
    users[name]["payments"][month].pop("receipt", None)

    await update.message.reply_text(f"🗑 وضعیت پرداخت {name} برای ماه {month} به 'بدهکار' بازگردانده شد.")
    print(f"[LOG] ادمین وضعیت پرداخت {name} را برای ماه {month} ریست کرد.")

# ===================== ریست کامل ربات (ادمین) =====================
async def reset_all_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        await update.message.reply_text("❌ شما دسترسی ادمین ندارید.")
        return

    context.user_data['awaiting_reset_confirm'] = True
    keyboard = [[KeyboardButton("بله، مطمئنم"), KeyboardButton("خیر، لغو کن")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        "🚨 هشدار: آیا از ریست کامل ربات مطمئن هستید؟ این کار تمام اعضا و سوابق پرداخت آن‌ها را پاک می‌کند و غیرقابل بازگشت است.",
        reply_markup=reply_markup
    )

async def reset_all_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        return

    if context.user_data.get('awaiting_reset_confirm'):
        if update.message.text == "بله، مطمئنم":
            global users
            users = {} # ریست کامل
            await update.message.reply_text("✅ ربات به طور کامل ریست شد. تمام اعضا و سوابق پرداخت پاک شدند.", reply_markup=ReplyKeyboardRemove())
            print("[LOG] ادمین ربات را به طور کامل ریست کرد.")
            await show_main_menu(update, context)
        else:
            context.user_data.pop('awaiting_reset_confirm', None)
            await update.message.reply_text("❌ عملیات ریست کامل لغو شد.")
            await show_main_menu(update, context)

# ===================== هندلر پیام‌ها =====================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        return

    # اول بررسی می کند که آیا کاربر در مرحله تایید ریست است یا خیر
    if context.user_data.get('awaiting_reset_confirm'):
        await reset_all_confirm(update, context)
        return

    if text == "بازگشت":
        await show_main_menu(update, context)
    elif text == "منوی ادمین":
        if update.effective_user.id in ADMINS:
            await choose_name(update, context, is_admin=True)
        else:
            await update.message.reply_text("❌ شما دسترسی ادمین ندارید.")
    elif text in users and not users[text].get("is_admin"):
        await choose_name(update, context)
    elif text == "✅ پرداخت کردم":
        await pay(update, context)
    elif text == "📋 وضعیت من":
        await my_status(update, context)
    elif text == "👥 لیست همه":
        await list_all(update, context)
    elif text == "📎 رسیدها":
        await send_receipts(update, context)
    elif text == "ارسال یادآوری ماهانه":
        await send_monthly_reminder(update, context)
    elif text == "➕ اضافه کردن عضو":
        await update.message.reply_text("از دستور /addmember نام عضو استفاده کنید.")
    elif text == "🗑 حذف عضو":
        await update.message.reply_text("از دستور /delmember نام عضو استفاده کنید.")
    elif text == "تغییر وضعیت پرداخت":
        await update.message.reply_text("از دستور /changepayment نام_عضو YYYY-MM استفاده کنید.")
    elif text == "ریست پرداخت":
        await update.message.reply_text("از دستور /resetpayment نام_عضو YYYY-MM استفاده کنید.")
    elif text == "ریست کامل ربات":
        await reset_all_prompt(update, context)
    else:
        await update.message.reply_text("لطفا یکی از گزینه‌ها رو انتخاب کن.")

# ===================== اجرای ربات =====================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addmember", add_member))
    app.add_handler(CommandHandler("delmember", del_member))
    app.add_handler(CommandHandler("changepayment", change_payment_status))
    app.add_handler(CommandHandler("resetpayment", reset_payment_status))
    app.add_handler(CommandHandler("resetall", reset_all_prompt))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, get_receipt))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":

    main()
