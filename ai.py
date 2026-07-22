import os
from dotenv import load_dotenv
from google import genai # <-- GANTI INI

# 1. Baca file .env biar bisa ambil API KEY
load_dotenv()

# 2. Konekin ke Google Gemini versi baru
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY")) # <-- GANTI INI

# 3. Fungsi Anti Gravity kita
def generate_deskripsi(merek, tahun, km, harga):
    prompt = f"""
    Kamu adalah sales mobil terbaik di Padang. Buatkan deskripsi iklan jual mobil yang menarik.

    Data Mobil:
    - Merek: {merek}
    - Tahun: {tahun}
    - KM: {km:,}
    - Harga: Rp{harga:,}

    Aturan:
    1. Buat 3 paragraf. Paragraf 1: Hook. Paragraf 2: Keunggulan 3 poin. Paragraf 3: CTA
    2. Bahasa santai, gaul, tapi profesional
    3. Sebutkan 3 keunggulan utama: Irit, Terawat, Surat Lengkap
    4. Ajak calon pembeli untuk WA di akhir
    5. Maksimal 200 kata
    """
    response = client.models.generate_content( # <-- GANTI INI
        model="gemini-2.0-flash", # <-- Pake model paling cepet
        contents=prompt
    )
    return response.text