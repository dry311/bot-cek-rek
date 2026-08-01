import logging
import os
from threading import Thread
from flask import Flask
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- 1. SERVER MINI UNTUK RENDER & UPTIMEROBOT ---
app = Flask("")


@app.route("/")
def home():
    return "Bot Cek Rekening (CSRF Test) Online!"


def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


def keep_alive():
    t = Thread(target=run)
    t.start()


# ------------------------------------------------

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# === KONFIGURASI BOT & CSRF TOKEN ===
TELEGRAM_BOT_TOKEN = (
    "8834110152:AAFD6orSUPXInEMrlWShPJYL-pkWTCoO1mg"  # Ganti dengan Token dari BotFather
)

# Token CSRF yang kamu dapatkan
CSRF_TOKEN = "iUlVBuZIwXi0cnixhT3g2gA0jQC17RrQ7BL6K4oi"

# Masukkan URL Endpoint API Internal dari situs tempat kamu mengambil CSRF Token
# Contoh: "https://domain-situs.com/api/check-rekening"
TARGET_URL = "PASTE_URL_ENDPOINT_API_DI_SINI"

# Cookie session dari Inspect Element (Penting! CSRF butuh cookie session yang sama)
COOKIE_SESSION = "PASTE_COOKIE_SESSION_DI_SINI"


# --- 2. FUNGSI CEK REKENING DENGAN CSRF TOKEN ---
def cek_rekening_api(bank_code: str, account_number: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "X-CSRF-TOKEN": CSRF_TOKEN,
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Cookie": COOKIE_SESSION,
    }

    payload = {
        "bank": bank_code.lower().strip(),
        "account_number": account_number.strip(),
        "_token": CSRF_TOKEN,  # Beberapa framework Web (seperti Laravel) minta token di dalam body juga
    }

    try:
        response = requests.post(
            TARGET_URL, json=payload, headers=headers, timeout=12
        )

        if response.status_code == 200:
            res_data = response.json()

            # Mengambil data dari respon JSON
            account_name = (
                res_data.get("name")
                or res_data.get("account_name")
                or res_data.get("data", {}).get("name")
            )

            if account_name:
                return True, {
                    "bank": bank_code.upper(),
                    "number": account_number,
                    "name": account_name,
                }
            else:
                msg = res_data.get("message", "Nama rekening tidak ditemukan.")
                return False, msg

        elif response.status_code in [419, 403]:
            return (
                False,
                "CSRF Token / Session Cookie sudah kedaluwarsa (Expired).",
            )
        else:
            return False, f"Server menolak request (Status: {response.status_code})."

    except requests.exceptions.Timeout:
        return False, "Waktu koneksi habis (Timeout)."
    except Exception as e:
        return False, f"Error Request: {str(e)}"


# --- 3. HANDLER COMMAND TELEGRAM BOT ---


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    thread_id = update.message.message_thread_id
    welcome_text = (
        "👋 <b>Selamat Datang di Bot Cek Rekening!</b>\n\n"
        "Gunakan perintah <code>/cek &lt;KODE_BANK&gt; &lt;NO_REK&gt;</code>\n"
        "Contoh: <code>/cek bca 1234567890</code>"
    )
    await update.message.reply_text(
        welcome_text, parse_mode="HTML", message_thread_id=thread_id
    )


async def cek_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    thread_id = update.message.message_thread_id

    if len(context.args) < 2:
        await update.message.reply_text(
            "⚠️ Format salah! Gunakan: <code>/cek bca 1234567890</code>",
            parse_mode="HTML",
            message_thread_id=thread_id,
        )
        return

    bank_code = context.args[0]
    account_number = context.args[1]

    loading_msg = await update.message.reply_text(
        f"⏳ Memeriksa <b>{bank_code.upper()}</b> {account_number}...",
        parse_mode="HTML",
        message_thread_id=thread_id,
    )

    is_success, result = cek_rekening_api(bank_code, account_number)

    if is_success:
        response_text = (
            "✅ <b>REKENING DITEMUKAN</b>\n\n"
            f"• <b>Bank:</b> {result['bank']}\n"
            f"• <b>No. Rek:</b> <code>{result['number']}</code>\n"
            f"• <b>Nama:</b> <b>{result['name']}</b>"
        )
    else:
        response_text = (
            "❌ <b>PENGECEKAN GAGAL</b>\n\n" f"• <b>Keterangan:</b> {result}"
        )

    await loading_msg.edit_text(response_text, parse_mode="HTML")


# --- 4. MAIN EXECUTION ---
def main():
    keep_alive()
    bot_app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    bot_app.add_handler(CommandHandler("start", start_command))
    bot_app.add_handler(CommandHandler("cek", cek_command))

    print("🤖 Bot Siap...")
    bot_app.run_polling()


if __name__ == "__main__":
    main()
