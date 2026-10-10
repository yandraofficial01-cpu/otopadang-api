
import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()

# INI YANG BIKIN KEMAREN ERROR - LU LUPA CONFIG!
cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key = os.getenv("CLOUDINARY_API_KEY"),
    api_secret = os.getenv("CLOUDINARY_API_SECRET"),
    secure = True
)

def upload_to_cloudinary(file, folder="otopadang"):
    try:
        result = cloudinary.uploader.upload(file, folder=folder)
        return result.get("secure_url")
    except Exception as e:
        print(f"CLOUDINARY ERROR: {e}")
        return None

# biar gak error kalau ada yang manggil upload_image juga
def upload_image(file, folder="otopadang"):
    return upload_to_cloudinary(file, folder)
