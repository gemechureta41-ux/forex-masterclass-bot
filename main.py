import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler
)

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Conversation states
NAME, PHONE, PAYMENT_METHOD, TRANSACTION_ID, SCREENSHOT = range(5)

# Token fi Admin ID kallattiidhaan asitti galchameera
TOKEN = "8961524303:AAHhrvbJQsegAdqtGy6AeuPZZb4Z-QM8aUQ"
ADMIN_CHAT_ID = "5558713786"
VIP_CHANNEL_LINK = "https://t.me/+p8VcsdP-k2FmMjk0"

# Payment Configuration
VIP_PRICE = "3599 ETB"
TELEBIRR_NO = "0917091612"
MPESA_NO = "0717120607"
ACCOUNT_NAME = "Gemechu Reta"

# Temporary Database (In-memory storage)
user_data_db = {}

# STEP 1: /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "WELCOME TO PRICEACTION_SMC FX!\n"
        "Welcome to our VIP Forex Master Class!\n\n"
        f"Price: {VIP_PRICE}\n\n"
        "Learn:\n"
        "• Price Action\n"
        "• Smart Money Concepts (SMC)\n"
        "• Risk Management\n"
        "• Trading Psychology\n"
        "• Live Trading Sessions\n\n"
        "To register for our VIP Master Class, click the button below."
    )
    keyboard = [[InlineKeyboardButton("REGISTER NOW", callback_data="register")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    return ConversationHandler.END

# STEP 2: Start Registration Flow
async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    await query.message.reply_text("Please enter your Full Name:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['full_name'] = update.message.text
    context.user_data['username'] = update.message.from_user.username or "No Username"
    
    await update.message.reply_text("Please enter your Phone Number:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    
    keyboard = [
        [InlineKeyboardButton("Telebirr", callback_data="Telebirr")],
        [InlineKeyboardButton("M-Pesa", callback_data="M-Pesa")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("Please select your payment method:", reply_markup=reply_markup)
    return PAYMENT_METHOD

# STEP 3: Payment Method Details
async def select_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    method = query.data
    context.user_data['payment_method'] = method
    
    number = TELEBIRR_NO if method == "Telebirr" else MPESA_NO
    
    payment_info = (
        f"You selected {method}!\n\n"
        f"Amount to Pay: {VIP_PRICE}\n"
        f"Account Name: {ACCOUNT_NAME}\n"
        f"Account Number: {number}\n\n"
        f"Please make the payment of {VIP_PRICE} to the above account, and then send your Transaction ID:"
    )
    
    await query.message.reply_text(payment_info)
    return TRANSACTION_ID

async def get_transaction_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['transaction_id'] = update.message.text
    
    await update.message.reply_text("Please send the payment screenshot (Photo):")
    return SCREENSHOT

# STEP 4: Receive Screenshot & Send to Admin
async def get_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['photo_id'] = update.message.photo[-1].file_id
    user_id = update.message.from_user.id
    
    user_data_db[user_id] = {
        'full_name': context.user_data['full_name'],
        'username': context.user_data['username'],
        'phone': context.user_data['phone'],
        'payment_method': context.user_data['payment_method'],
        'transaction_id': context.user_data['transaction_id'],
        'status': 'PENDING'
    }
    
    await update.message.reply_text(
        "⏳ PAYMENT PENDING!\n\n"
        "Your payment is under verification. Once approved by the admin, you will automatically receive your VIP channel invite link!"
    )
    
    admin_msg = (
        f"🔔 NEW PAYMENT PENDING VERIFICATION!\n\n"
        f"👤 Full Name: {context.user_data['full_name']}\n"
        f"💬 Telegram: @{context.user_data['username']}\n"
        f"📞 Phone: {context.user_data['phone']}\n"
        f"💳 Method: {context.user_data['payment_method']}\n"
        f"💰 Amount: {VIP_PRICE}\n"
        f"🆔 Transaction ID: {context.user_data['transaction_id']}\n\n"
        f"Please verify and choose an option:"
    )
    
    admin_keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
        ]
    ]
    
    if ADMIN_CHAT_ID:
        await context.bot.send_photo(
            chat_id=int(ADMIN_CHAT_ID),
            photo=context.user_data['photo_id'],
            caption=admin_msg,
            reply_markup=InlineKeyboardMarkup(admin_keyboard)
        )
    
    return ConversationHandler.END

# STEP 5: Admin Decision (Approve / Reject) & Auto Invite Link Dispatch
async def admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data_parts = query.data.split("_")
    action = data_parts[0]
    user_id = int(data_parts[1])
    
    if action == "approve":
        if user_id in user_data_db:
            user_data_db[user_id]['status'] = 'CONFIRMED'
        
        success_msg = (
            "🎉 PAYMENT SUCCESSFUL!\n\n"
            "Congratulations!\n"
            "Your payment has been verified successfully.\n"
            "Welcome to PriceAction_SMC VIP Master Class!\n\n"
            f"🔗 Your VIP Invite Link: {VIP_CHANNEL_LINK}\n\n"
            "✅ Registration Completed | 💳 Payment Verified | 🚀 VIP Access Ready\n"
            "Learn. Analyze. Trade."
        )
        
        await context.bot.send_message(chat_id=user_id, text=success_msg)
        await query.edit_message_caption(caption=query.message.caption + "\n\n✅ **STATUS: CONFIRMED & LINK SENT**")
        
    elif action == "reject":
        if user_id in user_data_db:
            user_data_db[user_id]['status'] = 'REJECTED'
        
        reject_msg = (
            "❌ PAYMENT VERIFICATION FAILED!\n\n"
            "Your payment could not be verified. "
            "Please check your transaction details or contact support/admin to resolve this."
        )
        
        await context.bot.send_message(chat_id=user_id, text=reject_msg)
        await query.edit_message_caption(caption=query.message.caption + "\n\n❌ **STATUS: REJECTED**")

def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN environment variable is missing!")
        
    app = ApplicationBuilder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_registration, pattern="^register$")],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            PAYMENT_METHOD: [CallbackQueryHandler(select_payment, pattern="^(Telebirr|M-Pesa)$")],
            TRANSACTION_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_transaction_id)],
            SCREENSHOT: [MessageHandler(filters.PHOTO, get_screenshot)]
        },
        fallbacks=[CommandHandler("start", start)]
    )
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(admin_decision, pattern="^(approve|reject)_"))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
