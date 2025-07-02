import qrcode
import os

def generate_qr_code(username, output_folder='static/uploads/qrcodes'):
    os.makedirs(output_folder, exist_ok=True)
    img = qrcode.make(username)
    path = os.path.join(output_folder, f"{username}.png")
    img.save(path)
    return path
