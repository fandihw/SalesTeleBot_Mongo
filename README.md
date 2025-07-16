# 🛎️ Sales Visit Telegram Bot

Bot Telegram untuk mendigitalisasi proses input dan pelaporan kunjungan sales, dengan penyimpanan data otomatis ke **MongoDB**. Mendukung upload foto eviden dan validasi data secara real-time.

---

## 🚀 Fitur Utama

- 🔄 **Input data step-by-step** melalui chat interaktif Telegram (kategori, lokasi, kontak, provider, dll)
- 📸 **Upload foto eviden**, disimpan secara lokal atau via GridFS dan direferensikan dalam database
- 🗃️ **Penyimpanan ke MongoDB** dengan struktur dokumen JSON
- 🔢 **Penomoran otomatis** kunjungan berdasarkan histori sebelumnya (`visit_ke`)
- 🚫 **Deteksi duplikasi** menggunakan kombinasi kunci unik (Sales, POI, STO)
- ✅ **Tombol konfirmasi akhir** sebelum data disimpan (`Konfirmasi` / `Cancel`)
- 📊 Perintah `/cekdata` untuk menampilkan 30 data kunjungan terbaru
- 👥 **Dukungan multi-user**, berdasarkan Telegram ID
- 🔧 Struktur modular dan scalable, mudah diintegrasikan dengan sistem eksternal

---

## 🧰 Teknologi

| [Python](https://www.python.org/)                  | Bahasa pemrograman utama                                                   
| [python-telegram-bot v20+](https://github.com/python-telegram-bot/python-telegram-bot) | Library utama Telegram Bot API               
| [Motor](https://motor.readthedocs.io/)             | Async driver untuk MongoDB                                                 
| [Pymongo](https://pymongo.readthedocs.io/)         | Alternatif driver MongoDB                                                  
| [MongoDB](https://www.mongodb.com/)                | Database NoSQL untuk menyimpan data kunjungan                              
| [GridFS / Local Storage](https://www.mongodb.com/docs/manual/core/gridfs/) | Penyimpanan file foto eviden                         
---
