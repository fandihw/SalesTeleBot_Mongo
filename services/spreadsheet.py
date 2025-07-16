'''
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from config import SPREADSHEET_ID, SHEET_NAME

# Setup
scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scopes)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

# Kolom yang disimpan (tidak termasuk id dan timestamp yang dibuat otomatis)
fields = [
        "kategori", "sales_name", "channel", "poi_name", "address",
        "contact_name", "contact_position", "contact_phone", "sto",
        "berlangganan", "provider", "cost", "kegiatan", "feedback",
        "detail_info", "image_url"
]

def save_data(user_id, data):
# Hitung ID dari jumlah baris eksisting
        existing_rows = len(sheet.get_all_values())
        new_id = existing_rows if existing_rows > 1 else 1  # Baris pertama biasanya header

# Waktu sekarang dalam format string
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Siapkan data lengkap untuk ditulis ke baris baru
        row = [new_id, timestamp, user_id] + [data.get(field, '') for field in fields]
        sheet.append_row(row)
'''