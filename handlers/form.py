'''
import os
from datetime import datetime, timezone, timedelta
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from services.mongodb import save_data

# ─────────────────────────────────────────────────────────────
# Mapping dinamis TELDA ke opsi STO
# ─────────────────────────────────────────────────────────────
telda_sto_map = {
    "Bangkalan": ["SPG", "KML", "ARB", "KPP", "BKL", "OMB", "BEA", "TBU"],
    "Gresik": ["CRM", "POG", "BPG", "DDS", "SDY", "KDE", "BWN", "GSK"],
    "Lamongan": ["SDD", "LMG", "BBA", "BDG"],
    "Pamekasan": ["BAB", "ABT", "SPK", "PRG", "AJA", "WRP", "SMP", "PME", "SPD", "MSL"],
    "Tandes": ["BAB", "ABT", "SPK", "PRG", "AJA", "WRP", "SMP", "PME", "SPD", "MSL"],
    "Ketintang": ["WRU", "IJK", "RKT", "TPO"],
    "Manyar": ["GBG", "MYR", "JGR", "MGO"],
    "Kanjeran": ["KPS", "PRK", "KBL", "KJR"]
}

# ─────────────────────────────────────────────────────────────
# Langkah-langkah pengisian form
# ─────────────────────────────────────────────────────────────
steps = [
    "kategori", "kkontak", "telda", "sto", "kegiatan", "poi_name", "address",
    "ekosistem", "contact_name", "contact_position", "contact_phone",
    "provider", "provider_detail", "cost", "feedback", "feedback_detail",
    "detail_info"
]

# ─────────────────────────────────────────────────────────────
# Pilihan tombol per step
# ─────────────────────────────────────────────────────────────
options = {
    "kategori": ["Visit Baru", "Follow Up"],
    "telda": list(telda_sto_map.keys()),
    "kegiatan": ["Door to Door", "Out Bond Call"],
    "ekosistem": ["Ruko", "Sekolah", "Hotel", "Multifinance", "Health", "Ekspedisi",
                  "Energi", "Agriculture", "Properti", "Manufaktur", "Media & Communication"],
    "provider": ["Telkom Group", "Kompetitor", "Belum Berlangganan Internet"],
    "provider_detail_telkom": ["Indihome", "Indibiz", "Wifi.id", "Astinet", "Other"],
    "provider_detail_kompetitor": ["MyRep", "Biznet", "FirtsMedia", "Iconnet", "XL Smart",
                                   "Indosat MNCPlay", "IFORTE", "Hypernet", "CBN", "Fibernet", "Fiberstar", "Other"],
    "feedback": ["Bertemu dengan PIC/Owner/Manajemen", "Tidak bertemu dengan PIC"],
    "feedback_detail_ya": ["Tertarik Berlangganan Indibiz", "Tidak Tertarik Berlangganan Indibiz",
                           "Ragu-ragu atau masih dipertimbangkan"],
    "feedback_detail_tidak": ["Mendapatkan Kontak Owner/PIC/Manajemen", "Tidak Mendapatkan Kontak Owner/PIC/Manajemen"]
}

# ─────────────────────────────────────────────────────────────
# Label untuk setiap input
# ─────────────────────────────────────────────────────────────
labels = {
    "kategori": "Kategori",
    "kkontak": "KKONTAK",
    "telda": "TELDA",
    "sto": "STO",
    "kegiatan": "Jenis Kegiatan",
    "poi_name": "Nama POI",
    "address": "Alamat",
    "ekosistem": "Ekosistem",
    "contact_name": "Nama PIC",
    "contact_position": "Jabatan PIC",
    "contact_phone": "Telepon PIC",
    "provider": "Provider",
    "provider_detail": "Jenis Provider",
    "cost": "Abonemen Berlangganan",
    "feedback": "Feedback",
    "feedback_detail": "Detail Feedback",
    "detail_info": "Informasi Tambahan"
}


# ─────────────────────────────────────────────────────────────
# Handler untuk input tombol (inline keyboard)
# ─────────────────────────────────────────────────────────────
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    step = context.user_data.get("step")
    selected_value = query.data
    context.user_data[step] = selected_value

    await query.edit_message_text(f"✅ Anda memilih: *{selected_value}*", parse_mode="Markdown")

    if step == "telda":
        context.user_data["step"] = "sto"
        keyboard = [[InlineKeyboardButton(sto, callback_data=sto)] for sto in telda_sto_map[selected_value]]
        await query.message.reply_text(
            f"Anda memilih {selected_value.title()}, pilih STO:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    elif step == "provider":
        if selected_value == "Belum Berlangganan Internet":
            context.user_data["provider_detail"] = "-"
            context.user_data["cost"] = "-"
            context.user_data["step"] = "feedback"
            await query.message.reply_text("ℹ️ Karena belum berlangganan, data provider & biaya dilewati.")
            await ask_next(update, context)
            return
        else:
            context.user_data["step"] = "provider_detail"
            detail_key = "provider_detail_telkom" if selected_value == "Telkom Group" else "provider_detail_kompetitor"
            keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in options[detail_key]]
            await query.message.reply_text("Pilih jenis provider:", reply_markup=InlineKeyboardMarkup(keyboard))
            return

    elif step == "provider_detail" and selected_value == "Other":
        await query.message.reply_text("Masukkan nama provider lainnya:")
        return

    elif step == "feedback":
        context.user_data["step"] = "feedback_detail"
        detail_key = "feedback_detail_ya" if selected_value.startswith("Bertemu") else "feedback_detail_tidak"
        keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in options[detail_key]]
        await query.message.reply_text("Pilih detail feedback:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    next_index = steps.index(step) + 1
    if next_index < len(steps):
        context.user_data["step"] = steps[next_index]
        await ask_next(update, context)
    else:
        await query.message.reply_text("📸 Silakan kirim foto eviden kegiatan:")


# ─────────────────────────────────────────────────────────────
# Handler untuk input teks
# ─────────────────────────────────────────────────────────────
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")
    if step not in steps:
        await update.message.reply_text("Terjadi kesalahan. /start untuk ulang.")
        return

    context.user_data[step] = update.message.text
    await update.message.reply_text(f"✅ Anda mengisi: *{update.message.text}*", parse_mode="Markdown")

    next_index = steps.index(step) + 1
    if next_index < len(steps):
        context.user_data["step"] = steps[next_index]
        await ask_next(update, context)
    else:
        await update.message.reply_text("📸 Silakan kirim foto eviden kegiatan:")


# ─────────────────────────────────────────────────────────────
# Menampilkan pertanyaan berikutnya
# ─────────────────────────────────────────────────────────────
async def ask_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")
    label = labels.get(step, step.replace("_", " ").title())
    msg = update.effective_message

    if step in options:
        keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in options[step]]
        await msg.reply_text(f"Pilih {label}:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await msg.reply_text(f"Masukkan {label}:")


# ─────────────────────────────────────────────────────────────
# Handler foto (eviden) & simpan ke database + upload GDrive
# ─────────────────────────────────────────────────────────────
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from services.drive import upload_photo  # Import lokal agar aman

    user_id = update.effective_user.id
    photo_file = await update.message.photo[-1].get_file()
    os.makedirs("photos", exist_ok=True)
    file_path = f"photos/{user_id}_{photo_file.file_unique_id}.jpg"
    await photo_file.download_to_drive(file_path)

    drive_url = upload_photo(file_path)

    # Gunakan timezone WIB
    wib = timezone(timedelta(hours=7))
    data = context.user_data.copy()
    data["photo_url"] = drive_url
    data["timestamp"] = datetime.now(wib)

    save_data(data)
    await update.message.reply_text("✅ Data dan eviden berhasil dikirim. Terima kasih!")
'''
import os
import asyncio
from datetime import datetime, timezone, timedelta
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from telegram.helpers import escape_markdown
from services import is_user_allowed
from services.mongodb import collection
from pymongo import MongoClient
from bson.objectid import ObjectId


# ────────────── Konstanta dan Konfigurasi ──────────────
WIB = timezone(timedelta(hours=7))

TELDA_STO_MAP = {
    "Bangkalan": ["SPG", "KML", "ARB", "KPP", "BKL", "OMB", "BEA", "TBU"],
    "Gresik": ["CRM", "POG", "BPG", "DDS", "SDY", "KDE", "BWN", "GSK"],
    "Lamongan": ["SDD", "LMG", "BBA", "BDG"],
    "Pamekasan": ["BAB", "ABT", "SPK", "PRG", "AJA", "WRP", "SMP", "PME", "SPD", "MSL"],
    "Tandes": ["DMO", "TNS", "KNN", "BBE", "KLN", "LKI", "KRP"],
    "Ketintang": ["WRU", "IJK", "RKT", "TPO"],
    "Manyar": ["GBG", "MYR", "JGR", "MGO"],
    "Kanjeran": ["KPS", "PRK", "KBL", "KJR"],
}

STEPS = [
    "kategori", "nama_sales", "telda", "sto", "kegiatan", "poi_name", "address",
    "ekosistem", "contact_name", "contact_position", "contact_phone",
    "provider", "provider_detail", "cost", "feedback", "feedback_detail",
    "detail_info", "hasil_fu"
]

OPTIONS = {
    "kategori": ["Visit Baru", "Follow Up"],
    "telda": list(TELDA_STO_MAP.keys()),
    "kegiatan": ["Door to Door", "Out Bond Call"],
    "ekosistem": [
        "Ruko", "Sekolah", "Hotel", "Multifinance", "Health", "Ekspedisi",
        "Energi", "Agriculture", "Properti", "Manufaktur", "Media & Communication"
    ],
    "provider": ["Telkom Group", "Kompetitor", "Belum Berlangganan Internet"],
    "provider_detail_telkom": ["Indihome", "Indibiz", "Wifi.id", "Astinet", "Other"],
    "provider_detail_kompetitor": [
        "MyRep", "Biznet", "FirtsMedia", "Iconnet", "XL Smart",
        "Indosat MNCPlay", "IFORTE", "Hypernet", "CBN", "Fibernet", "Fiberstar", "Other"
    ],
    "feedback": [
        "Bertemu dengan PIC/Owner/Manajemen", "Tidak bertemu dengan PIC"
    ],
    "feedback_detail_ya": [
        "Tertarik Berlangganan Indibiz", "Tidak Tertarik Berlangganan Indibiz",
        "Ragu-ragu atau masih dipertimbangkan"
    ],
    "feedback_detail_tidak": [
        "Mendapatkan Kontak Owner/PIC/Manajemen", "Tidak Mendapatkan Kontak Owner/PIC/Manajemen"
    ],
}

LABELS = {
    "kategori": "Kategori",
    "nama_sales": "Nama Sales",
    "telda": "Telda",
    "sto": "STO",
    "poi_name": "Nama POI",
    "address": "Alamat",
    "ekosistem": "Ekosistem",
    "kegiatan": "Jenis Kegiatan",
    "contact_name": "Nama PIC",
    "contact_position": "Jabatan PIC",
    "contact_phone": "HP",
    "provider": "Provider",
    "provider_detail": "Jenis Provider",
    "cost": "Abonemen",
    "feedback": "Feedback",
    "feedback_detail": "Detail Feedback",
    "detail_info": "Informasi Detail",
    "hasil_fu": "Hasil Follow Up",
}

# ────────────── Handler Callback ──────────────
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    if not is_user_allowed(user_id):
        await query.message.reply_text("❌ Anda tidak diizinkan mengisi form ini.")
        return
    await query.answer()
    selected = query.data

    if selected in ["confirm_data", "cancel_data"]:
        await handle_confirmation(update, context)
        return

    step = context.user_data.get("step")
    context.user_data[step] = selected
    await query.edit_message_text(f"✅ Anda memilih: *{escape_markdown(selected, version=2)}*", parse_mode=ParseMode.MARKDOWN_V2)

    if step == "telda":
        context.user_data["step"] = "sto"
        keyboard = [[InlineKeyboardButton(sto, callback_data=sto)] for sto in TELDA_STO_MAP[selected]]
        await query.message.reply_text(f"Anda memilih {selected}, pilih STO:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if step == "provider":
        if selected == "Belum Berlangganan Internet":
            context.user_data.update({"provider_detail": "-", "cost": "-", "step": "feedback"})
            await query.message.reply_text("ℹ️ Provider & abonemen dilewati")
            await ask_next(update, context)
            return
        context.user_data["step"] = "provider_detail"
        dkey = "provider_detail_telkom" if selected == "Telkom Group" else "provider_detail_kompetitor"
        keyboard = [[InlineKeyboardButton(x, callback_data=x)] for x in OPTIONS[dkey]]
        await query.message.reply_text("Pilih jenis provider:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if step == "provider_detail" and selected == "Other":
        await query.message.reply_text("Masukkan nama provider lainnya:")
        return

    if step == "feedback":
        context.user_data["step"] = "feedback_detail"
        dkey = "feedback_detail_ya" if selected.startswith("Bertemu") else "feedback_detail_tidak"
        keyboard = [[InlineKeyboardButton(x, callback_data=x)] for x in OPTIONS[dkey]]
        await query.message.reply_text("Pilih detail feedback:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    next_idx = STEPS.index(step) + 1
    if next_idx < len(STEPS):
        context.user_data["step"] = STEPS[next_idx]
        await ask_next(update, context)
    else:
        await query.message.reply_text("📸 Silakan kirim foto eviden kegiatan:")

# ────────────── Handler Input Text ──────────────
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")

    user_id = update.effective_user.id
    if not is_user_allowed(user_id):
        await update.message.reply_text("❌ Anda tidak diizinkan mengisi form ini.")
        return


    if not step or step not in STEPS:
        await update.message.reply_text("Terjadi kesalahan. Ketik /start untuk memulai ulang.")
        return

    if not update.message.text.strip():
        await update.message.reply_text("❗ Input tidak boleh kosong. Silakan masukkan kembali.")
        return

    context.user_data[step] = update.message.text
    await update.message.reply_text(
        f"✅ Anda mengisi: *{escape_markdown(update.message.text.strip(), version=2)}*",
        parse_mode=ParseMode.MARKDOWN_V2
    )

    next_idx = STEPS.index(step) + 1
    if next_idx < len(STEPS):
        context.user_data["step"] = STEPS[next_idx]
        await ask_next(update, context)
    else:
        await update.message.reply_text("📸 Silakan kirim foto eviden kegiatan:")

# ────────────── Pertanyaan Selanjutnya ──────────────
async def ask_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")
    kategori = context.user_data.get("kategori")
    
    # 🔒 Skip "hasil_fu" jika kategori bukan Follow Up
    if step == "hasil_fu" and kategori != "Follow Up":
        next_idx = STEPS.index(step) + 1
        if next_idx < len(STEPS):
            context.user_data["step"] = STEPS[next_idx]
            await ask_next(update, context)
        else:
            await update.message.reply_text("📸 Silakan kirim foto eviden kegiatan:")
        return

    label = LABELS.get(step, step)
    msg = update.effective_message

    if step in OPTIONS:
        keyboard = [[InlineKeyboardButton(val, callback_data=val)] for val in OPTIONS[step]]
        await msg.reply_text(f"Pilih {label}:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await msg.reply_text(f"Masukkan {label}:")
# ────────────── Save to MongoDB ──────────────
async def save_data_to_mongo(data: dict) -> str:
    loop = asyncio.get_running_loop()

    key = (
        data.get("user_id"),
        data.get("telda"),
        data.get("sto"),
        data.get("poi_name")
    )

    query = {
        "user_id": key[0],
        "telda": key[1],
        "sto": key[2],
        "poi_name": key[3]
    }

    existing_visits = await loop.run_in_executor(None, lambda: list(collection.find(query)))
    visit_ke = len(existing_visits) + 1

    data["visit_ke"] = visit_ke
    now_wib = datetime.now(WIB)
    data["timestamp"] = now_wib

    await loop.run_in_executor(None, lambda: collection.insert_one(data))

    return f"✅ Data berhasil disimpan, (Visit ke-{visit_ke})"

# ────────────── Upload Foto dan Simpan ──────────────
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    photo_file = await update.message.photo[-1].get_file()

    os.makedirs("photos", exist_ok=True)
    file_path = f"photos/{user_id}_{photo_file.file_unique_id}.jpg"
    await photo_file.download_to_drive(file_path)

    form_data = context.user_data.copy()
    form_data.update({
        "photo_url": file_path,
        "user_id": user_id
    })
    context.user_data["form_data"] = form_data

    await show_confirmation(update, context)

# ────────────── Konfirmasi dan Simpan ──────────────
async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "confirm_data":
        data = context.user_data.get("form_data")
        if data:
            msg = save_data_to_mongo(data)
            context.user_data.clear()
            await query.edit_message_text(escape_markdown(msg, version=2), parse_mode=ParseMode.MARKDOWN_V2)
        else:
            await query.edit_message_text("❗ Data tidak ditemukan. Silakan ulangi", parse_mode=ParseMode.MARKDOWN_V2)

    elif query.data == "cancel_data":
        context.user_data.clear()
        await query.edit_message_text("❌ Input dibatalkan. Silakan mulai ulang dengan /start", parse_mode=ParseMode.MARKDOWN_V2)

# ────────────── Konfirmasi Visual ──────────────
async def show_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    form_data = context.user_data.get("form_data", {})
    kategori = form_data.get("kategori", "Visit Baru")
    lines = ["📋 Berikut ringkasan data yang Anda input:"]

    for key in STEPS:
        if key == "hasil_fu" and kategori != "Follow Up":
            continue
        label = LABELS.get(key, key)
        value = form_data.get(key, "-")
        lines.append(f"*{escape_markdown(label, version=2)}*: {escape_markdown(str(value), version=2)}")

    lines.append(f"*Visit ke*: {form_data.get('visit_ke', '?')}")

    keyboard = [[
        InlineKeyboardButton("✅ Konfirmasi", callback_data="confirm_data"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel_data")
    ]]

    await update.effective_message.reply_text(
        "\n".join(lines) +
        "\n\n❗❗*PASTIKAN DATA YANG ANDA INPUTKAN SUDAH BENAR*❗❗\n" +
        "• Klik ✅ *Konfirmasi* kalau sudah benar\n" +
        "• Klik ❌ *Cancel* untuk mengulang dari awal",
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ────────────── Simpan atau Batalkan ──────────────
async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "confirm_data":
        data = context.user_data.get("form_data")
        if data:
            msg = await save_data_to_mongo(data)  # ← sekarang pakai await
            context.user_data.clear()
            await query.edit_message_text(escape_markdown(msg, version=2), parse_mode=ParseMode.MARKDOWN_V2)

            await query.message.reply_text(
                "👋 Selamat datang di *Sales Visit Bot*\n\n"
                "❗❗❗ *CATATAN PENTING :* ❗❗❗\n"
                "GUNAKAN *NAMA DAN NAMA POI YANG SAMA* PERSIS SEPERTI YANG PERTAMA KALI ANDA GUNAKAN SAAT MENGISI DATA SEBELUMNYA\n\n"
                "Gunakan /start untuk input baru\n"
                "Gunakan /cekdata untuk lihat 30 data terakhir",
                parse_mode=ParseMode.MARKDOWN_V2
            )
        else:
            await query.edit_message_text(
                escape_markdown("❗ Data tidak ditemukan. Silakan ulangi", version=2),
                parse_mode=ParseMode.MARKDOWN_V2
            )

    elif query.data == "cancel_data":
        context.user_data.clear()
        await query.edit_message_text(
            escape_markdown("❌ Input dibatalkan. Mohon lebih teliti lagi. Silakan mulai ulang dengan /start", version=2),
            parse_mode=ParseMode.MARKDOWN_V2
        )
