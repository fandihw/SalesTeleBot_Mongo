'''
from telegram import Update
from telegram.ext import ContextTypes
from services.mongodb import get_last_30_days_data
from datetime import timezone, timedelta
from html import escape

# Fungsi bantu untuk padding label
def fmt(label, value):
    return f"{label:<22}: {escape(str(value) if value else '-')}"

# Fungsi format data
def format_data(entry):
    wib_time = entry["timestamp"].astimezone(timezone(timedelta(hours=7)))
    time_str = wib_time.strftime("%d/%m/%Y %H:%M WIB")

    return (
        "<pre>\n"
        "📌 Data Kunjungan Sales\n"
        f"{fmt('🗓️ Tanggal/Waktu', time_str)}\n"
        f"{fmt('📁 Kategori', entry.get('kategori'))}\n"
        f"{fmt('👤 Nama Sales', entry.get('kkontak'))}\n"
        f"{fmt('🌏 Wilayah Telda', entry.get('telda'))}\n"
        f"{fmt('🏬 STO', entry.get('sto'))}\n"
        f"{fmt('🎯 Jenis Kegiatan', entry.get('kegiatan'))}\n"
        "\n"
        f"{fmt('🏢 Nama POI', entry.get('poi_name'))}\n"
        f"{fmt('📍 Alamat', entry.get('address'))}\n"
        f"{fmt('🌐 Ekosistem', entry.get('ekosistem'))}\n"
        "\n"
        f"{fmt('👥 Nama PIC', entry.get('contact_name'))}\n"
        f"{fmt('🧑‍💼 Jabatan PIC', entry.get('contact_position'))}\n"
        f"{fmt('📞 No.hp PIC', entry.get('contact_phone'))}\n"
        "\n"
        f"{fmt('💡 Provider', entry.get('provider'))}\n"
        f"{fmt('🔌 Nama Provider', entry.get('provider_detail'))}\n"
        f"{fmt('💰 Abonemen Berlangganan', entry.get('cost'))}\n"
        "\n"
        f"{fmt('💬 Feedback', entry.get('feedback'))}\n\n"              
        f"{fmt('💬 Detail Feedback', entry.get('feedback_detail'))}\n\n"
        f"{fmt('📝 Info Tambahan', entry.get('detail_info'))}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "</pre>"
    )

# Handler /cekdata
# Handler untuk /cekdata
async def handle_cekdata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = get_last_30_days_data()

    if not data:
        await update.message.reply_text("📭 Tidak ada data dalam 30 hari terakhir.")
        return

    # Kirim masing-masing entry sebagai pesan terpisah (maks 30)
    for i, entry in enumerate(data[:30], start=1):
        message = format_data(entry)
        await update.message.reply_text(message, parse_mode="HTML")
'''
from telegram import Update
from telegram.ext import ContextTypes
from services.mongodb import get_last_30_days_data
from services import is_user_allowed, is_admin
from datetime import timezone, timedelta
from html import escape

# Fungsi bantu untuk padding label
def fmt(label, value):
    return f"{label:<22}: {escape(str(value) if value else '-')}"

# Format pesan tiap entry
def format_data(entry):
    wib_time = entry["timestamp"].astimezone(timezone(timedelta(hours=7)))
    time_str = wib_time.strftime("%d/%m/%Y %H:%M WIB")

    return (
        "<pre>\n"
        "📌 Data Kunjungan Sales\n"
        f"{fmt('🗓️ Tanggal/Waktu', time_str)}\n"
        f"{fmt('📁 Kategori', entry.get('Kategori'))}\n"
        f"{fmt('👤 Nama Sales', entry.get('Nama Sales'))}\n"
        f"{fmt('🌏 Wilayah Telda', entry.get('Telda'))}\n"
        f"{fmt('🏬 STO', entry.get('STO'))}\n"
        f"{fmt('🎯 Jenis Kegiatan', entry.get('Kegiatan'))}\n"
        "\n"
        f"{fmt('🏢 Nama POI', entry.get('POI Name'))}\n"
        f"{fmt('📍 Alamat', entry.get('Alamat'))}\n"
        f"{fmt('🌐 Ekosistem', entry.get('Ekosistem'))}\n"
        "\n"
        f"{fmt('👥 Nama PIC', entry.get('Nama PIC'))}\n"
        f"{fmt('🧑‍💼 Jabatan PIC', entry.get('Jabatan PIC'))}\n"
        f"{fmt('📞 No.hp PIC', entry.get('HP'))}\n"
        "\n"
        f"{fmt('💡 Provider', entry.get('Provider'))}\n"
        f"{fmt('🔌 Nama Provider', entry.get('Provider Detail'))}\n"
        f"{fmt('💰 Abonemen Berlangganan', entry.get('Abonemen'))}\n"
        "\n"
        f"{fmt('💬 Feedback', entry.get('Feedback'))}\n\n"              
        f"{fmt('💬 Detail Feedback', entry.get('Feedback Detail'))}\n\n"
        f"{fmt('📝 Info Tambahan', entry.get('Info Tambahan'))}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "</pre>"
    )

# Handler /cekdata
async def handle_cekdata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not is_user_allowed(user_id):
        await update.message.reply_text("❌ Anda tidak memiliki izin untuk melihat data ini")
        return

    entries = get_last_30_days_data()
    if not entries:
        await update.message.reply_text("📭 Tidak ada data dalam 30 hari terakhir")
        return

    # Filter data untuk user biasa
    if not is_admin(user_id):
        entries = [e for e in entries if str(e.get("User ID")) == str(user_id)]

    if not entries:
        await update.message.reply_text("📭 Tidak ada data kunjungan milik Anda dalam 30 hari terakhir")
        return

    # Kirim maksimal 30 entry
    for i, entry in enumerate(entries[:30], start=1):
        msg = format_data(entry)
        await update.message.reply_text(msg, parse_mode="HTML")