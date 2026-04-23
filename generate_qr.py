"""
Run: python generate_qr.py https://your-app.onrender.com/form
Outputs: qrcode.png in this directory
"""
import sys
import qrcode

def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "https://your-app.onrender.com/form"
    img = qrcode.make(url)
    img.save("qrcode.png")
    print(f"QR code saved to qrcode.png → {url}")

if __name__ == "__main__":
    main()
