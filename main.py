from config import BOT_TOKEN
from handlers import start, form, cekdata
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start.start_cmd))
    app.add_handler(CommandHandler("help",  start.help_cmd))
    app.add_handler(CommandHandler("cekdata", cekdata.handle_cekdata))

    app.add_handler(CallbackQueryHandler(form.handle_callback, pattern="^(?!confirm_data|cancel_data).*"))
    app.add_handler(CallbackQueryHandler(form.handle_confirmation, pattern="^(confirm_data|cancel_data)$"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, form.handle_text))

    app.add_handler(MessageHandler(filters.PHOTO, form.handle_photo))

    print("Bot is running…")
    app.run_polling()

if __name__ == "__main__":
    main()
