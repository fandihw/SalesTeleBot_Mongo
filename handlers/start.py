from telegram import Update
from telegram.ext import ContextTypes
from services.mongodb import is_user_allowed

WELCOME = (
    "👋 Selamat datang di *Sales Visit Bot*.\n\n"
    "❗❗❗ *CATATAN PENTING :* ❗❗❗\n"
    "MASUKKAN *NAMA DAN NAMA POI YANG SAMA* PERSIS SEPERTI YANG PERTAMA KALI ANDA GUNAKAN SAAT MENGISI DATA SEBELUMNYA\n\n"
    "NAMA INI DIGUNAKAN UNTUK MENCATAT KUNJUNGAN ANDA\n\n"
    "Gunakan /start untuk input baru\n"
    "Gunakan /cekdata untuk melihat 30 data terakhir"
)

HELP = (
    "🛠 *Bantuan*\n"
    "• /start – memulai input kunjungan\n"
    "• /cekdata – menampilkan 30 data terakhir\n"
)

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_user_allowed(user_id):
        await update.message.reply_text("❌ Maaf, Anda tidak terdaftar sebagai user yang diizinkan.")
        return

    context.user_data.clear()
    context.user_data["step"] = "kategori"
    from handlers.form import ask_next
    await update.message.reply_text(WELCOME, parse_mode="Markdown")
    await ask_next(update, context)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP, parse_mode="Markdown")

