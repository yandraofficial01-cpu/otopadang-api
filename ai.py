import os
from dotenv import load_dotenv
import google.generativeai as genai # <-- PENTING GANTI INI

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY tidak ditemukan")

genai.configure(api_key=API_KEY)

def generate_deskripsi(merek, tahun, km, harga):
    model = genai.GenerativeModel('gemini-1.5-flash')
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
    response = model.generate_content(prompt)
    return response.text
