import os
from datetime import datetime, timedelta, timezone
from telegram import Update
from telegram.ext import ContextTypes
from services.mongodb import save_data_to_mongo

# Zona waktu WIB (GMT+7)
WIB = timezone(timedelta(hours=7))

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Validasi: pastikan ada foto
    if not update.message.photo:
        await update.message.reply_text("❗ Silakan kirim foto sebagai eviden kunjungan.")
        return

    # Ambil file foto resolusi tertinggi
    photo_file = await update.message.photo[-1].get_file()

    # Simpan foto secara lokal sementara
    os.makedirs("photos", exist_ok=True)
    file_path = f"photos/{user_id}_{photo_file.file_unique_id}.jpg"
    await photo_file.download_to_drive(file_path)

    # Ambil data form dari user_data
    form_data = context.user_data.copy()
    form_data.update({
        "user_id": str(user_id),
        "timestamp": datetime.now(WIB)
    })
    context.user_data["form_data"] = form_data

    # Simpan ke MongoDB (termasuk path lokal ke foto)
    msg = save_data_to_mongo(form_data, file_path)

    # Respons akhir ke user
    await update.message.reply_text(msg)
    await update.message.reply_text("✅ Data dan eviden berhasil dikirim. Terima kasih!")