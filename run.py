"""
╔══════════════════════════════════════════════════════════════════════════════╗
║         🖥  UNIVERSAL SERVER BOSHQARUV TIZIMI  —  run.py  (v2.2)            ║
║         Python + Flask + SQLite  |  Modular tuzilma                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Ishlatish: python run.py                                                   ║
║                                                                             ║
║  Majburiy: pip install flask                                                ║
║  Ixtiyoriy: pip install pyngrok colorama psutil qrcode[pil]                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import threading
import time
import platform
import subprocess

# ── App va konfiguratsiyani yuklash ────────────────────────────────────────
from app.config import (app as flask_app, CFG, NGROK_OK, PSUTIL_OK, QRCODE_OK,
                         _active_mode, _c, R, G, Y, C, M, W)
from app.database import setup_db

# ── Middleware va routelarni yuklash (import qilinganda ro'yxatdan o'tadi) ──
import app.routes.middleware
import app.routes.auth_routes
import app.routes.dashboard
import app.routes.modes
import app.routes.links
import app.routes.files
import app.routes.projects
import app.routes.admin
import app.routes.api
import app.routes.features
import app.routes.advanced

# ── Yordamchi funksiyalar ──────────────────────────────────────────────────
from app.utils import local_ip, get_ssid, expiry_checker, uptime_checker


def print_banner():
    print(_c("""
╔══════════════════════════════════════════════════════════════════════╗
║      ⬡  UNIVERSAL SERVER BOSHQARUV TIZIMI  v2.2  (SQLite)          ║
║      Python + Flask  |  Modular tuzilma                             ║
╚══════════════════════════════════════════════════════════════════════╝""", C))


def print_menu():
    print(f"""
  {_c('Rejimni tanlang:', W)}

  {_c('1', Y)}  🔒  Shaxsiy (localhost)   — faqat siz
  {_c('2', G)}  📡  LAN / WiFi            — bir xil tarmoqdagilar
  {_c('3', M)}  🌍  Global (Internet)     — ngrok orqali butun dunyo
  {_c('0', R)}  ❌  Chiqish
""")


def run_srv(host):
    import logging
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    flask_app.run(host=host, port=CFG["PORT"], debug=False, use_reloader=False, threaded=True)


def show_info(mode):
    port = CFG["PORT"]
    ip = local_ip()
    ssid = get_ssid()
    pub = _active_mode.get("url", "")
    print("\n" + _c("─" * 66, C))
    if mode == "private":
        url = f"http://127.0.0.1:{port}"
        print(_c("  🔒  SHAXSIY REJIM", Y))
        print(_c("─" * 66, C))
        print(f"\n  {_c('Sayt:', G)}      {_c(url, W)}")
        print(f"  {_c('Dashboard:', G)} {_c(url + '/dashboard', W)}")
        print(f"  {_c('Login:', Y)}     {CFG['ADMIN_USER']}  |  {_c('Parol:', Y)} {CFG['ADMIN_PASS']}")
        print(f"\n  {_c('Faqat bu kompyuterdan kirish mumkin.', Y)}")
    elif mode == "lan":
        url = f"http://{ip}:{port}"
        print(_c("  📡  LAN REJIM", G))
        print(_c("─" * 66, C))
        print(f"\n  {_c('WiFi SSID:', G)}   {_c(ssid, W)}")
        print(f"  {_c('Manzil:', G)}      {_c(url, W)}")
        print(f"\n  {_c('Boshqa qurilmadan:', C)}")
        print(f"  1. {_c(ssid, W)} WiFi ga ulaning")
        print(f"  2. Brauzerda oching: {_c(url, W)}")
    elif mode == "global":
        print(_c("  🌍  GLOBAL REJIM (ngrok)", M))
        print(_c("─" * 66, C))
        if pub:
            print(f"\n  {_c('✓ Ngrok faol!', G)}")
            print(f"  {_c('Ommaviy URL:', G)}  {_c(pub, W)}")
        else:
            print(f"\n  {_c('✗ Ngrok ishlamadi.', R)}")
    print(_c("─" * 66, C))
    print(f"\n  {_c('Toxtatish uchun: Ctrl+C', Y)}\n")


def main():
    print_banner()
    print(_c("\n  🗄  SQLite baza tayyorlanmoqda...", C))
    setup_db()
    print(_c("  ✓ Tayyor! Ma'lumotlar: server_data.db", G))

    if not PSUTIL_OK:
        print(_c("  ⚠  Monitoring uchun: pip install psutil", Y))
    if not QRCODE_OK:
        print(_c("  ⚠  QR-kod uchun: pip install qrcode[pil]", Y))

    # Fon threadlarni ishga tushirish
    threading.Thread(target=expiry_checker, daemon=True).start()
    threading.Thread(target=uptime_checker, daemon=True).start()

    while True:
        print_menu()
        try:
            ch = input(f"  {_c('Tanlov (0-3):', W)} ").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n  {_c('Xayr!', Y)}\n")
            break

        if ch == "1":
            t = threading.Thread(target=run_srv, args=("127.0.0.1",), daemon=True)
            t.start()
            time.sleep(0.8)
            show_info("private")
            try:
                while t.is_alive():
                    time.sleep(1)
            except KeyboardInterrupt:
                print(f"\n  {_c('Server toxtatildi.', Y)}")

        elif ch == "2":
            t = threading.Thread(target=run_srv, args=("0.0.0.0",), daemon=True)
            t.start()
            time.sleep(0.8)
            show_info("lan")
            try:
                while t.is_alive():
                    time.sleep(1)
            except KeyboardInterrupt:
                print(f"\n  {_c('Server toxtatildi.', Y)}")

        elif ch == "3":
            if NGROK_OK:
                print(_c("\n  🚀 Ngrok tunnel ochilmoqda...", C))
                try:
                    from pyngrok import ngrok as _ngrok
                    if CFG["NGROK_TOKEN"]:
                        _ngrok.set_auth_token(CFG["NGROK_TOKEN"])
                    import app.config as cfg
                    cfg._ngrok_tunnel = _ngrok.connect(CFG["PORT"], "http")
                    cfg._active_mode["url"] = cfg._ngrok_tunnel.public_url
                except Exception as e:
                    print(_c(f"  [ngrok xato] {e}", R))
            else:
                print(_c("  ⚠  pyngrok yo'q: pip install pyngrok", Y))
            t = threading.Thread(target=run_srv, args=("0.0.0.0",), daemon=True)
            t.start()
            time.sleep(1)
            show_info("global")
            try:
                while t.is_alive():
                    time.sleep(1)
            except KeyboardInterrupt:
                print(f"\n  {_c('Server toxtatildi.', Y)}")
                if NGROK_OK:
                    try:
                        from pyngrok import ngrok as _ngrok
                        _ngrok.kill()
                    except:
                        pass
                _active_mode["url"] = None

        elif ch == "0":
            print(f"\n  {_c('Xayr!', Y)}\n")
            break
        else:
            print(_c("  Noto'g'ri tanlov!", R))


if __name__ == "__main__":
    main()
