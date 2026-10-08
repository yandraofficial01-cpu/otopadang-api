import cloudinary.uploader

def upload_to_cloudinary(file, folder="otopadang"):
    result = cloudinary.uploader.upload(file, folder=folder)
    return result.get("secure_url")
