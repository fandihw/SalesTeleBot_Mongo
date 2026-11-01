from telegram import Update
from telegram.ext import ContextTypes
from services.mongodb import (
    is_user_allowed, 
    get_user_role, 
    get_all_data_last_30_days, 
    get_user_data_last_30_days
)
from datetime import timezone, timedelta
from html import escape
import asyncio

def fmt(label, value):
    return f"{label:<22}: {escape(str(value) if value else '-')}"

def format_data(entry):
    wib_time = entry["timestamp"].astimezone(timezone(timedelta(hours=7)))
    time_str = wib_time.strftime("%d/%m/%Y %H:%M WIB")

    return (
        "<pre>"
        "📌 Data Kunjungan Sales\n"
        f"{fmt('🗓️ Tanggal/Waktu', time_str)}\n"
        f"{fmt('📁 Kategori', entry.get('kategori'))}\n"
        f"{fmt('👤 Nama Sales', entry.get('nama_sales'))}\n"
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
        f"{fmt('💰 Abonemen', entry.get('cost'))}\n"
        "\n"
        f"{fmt('💬 Feedback', entry.get('feedback'))}\n"
        f"{fmt('💬 Detail Feedback', entry.get('feedback_detail'))}\n"
        f"{fmt('📝 Info Tambahan', entry.get('detail_info'))}\n"
        f"{fmt('🔄 Hasil Follow Up', entry.get('hasil_fu', '-'))}\n"
        f"{fmt('🔢 Visit ke', entry.get('visit_ke', '-'))}\n"
        f"{fmt('👤 User ID', entry.get('user_id', '-'))}\n"
        "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        "</pre>"
    )

# Handler /cekdata
async def handle_cekdata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Cek izin user
    if not is_user_allowed(user_id):
        await update.message.reply_text("❌ Anda tidak memiliki izin untuk melihat data ini")
        return

    # Ambil role user
    user_role = get_user_role(user_id)
    if not user_role:
        await update.message.reply_text("❌ Role user tidak ditemukan")
        return

    # Ambil data berdasarkan role
    if user_role == "superadmin":
        entries = get_all_data_last_30_days()  # Semua data 30 hari terakhir
        info_msg = "📊 Menampilkan SEMUA data kunjungan 30 hari terakhir (Superadmin)"
    else:  # role "sales"
        entries = get_user_data_last_30_days(str(user_id))
        info_msg = "📊 Menampilkan data kunjungan Anda dalam 30 hari terakhir"

    # Cek apakah ada data
    if not entries:
        if user_role == "superadmin":
            await update.message.reply_text("📭 Tidak ada data kunjungan dalam 30 hari terakhir")
        else:
            await update.message.reply_text("📭 Tidak ada data kunjungan Anda dalam 30 hari terakhir")
        return

    # Kirim info jumlah data
    await update.message.reply_text(f"{info_msg}\n\n📈 Total data: {len(entries)} entry")

    # Batasi jumlah data yang ditampilkan untuk menghindari spam
    max_entries = 50 if user_role == "superadmin" else 30
    displayed_entries = entries[:max_entries]

    if len(entries) > max_entries:
        await update.message.reply_text(
            f"⚠️ Terlalu banyak data! Menampilkan {max_entries} data terbaru dari {len(entries)} total data."
        )

    # Kirim data dengan delay untuk menghindari rate limit
    for i, entry in enumerate(displayed_entries, start=1):
        try:
            msg = format_data(entry)
            await update.message.reply_text(msg, parse_mode="HTML")
            
            # Delay setiap 5 pesan untuk superadmin, 10 untuk sales
            delay_interval = 5 if user_role == "superadmin" else 10
            if i % delay_interval == 0:
                await asyncio.sleep(1)
                
        except Exception as e:
            # Jika ada error parsing HTML, kirim sebagai text biasa
            await update.message.reply_text(f"❗ Error menampilkan data ke-{i}: {str(e)}")
            continue

    # Pesan selesai
    total_displayed = len(displayed_entries)
    if user_role == "superadmin" and len(entries) > max_entries:
        await update.message.reply_text(
            f"Selesai menampilkan {total_displayed} dari {len(entries)} data\n"
            f"Gunakan filter atau export untuk melihat semua data"
        )
    else:
        await update.message.reply_text(f"Selesai menampilkan {total_displayed} data")
