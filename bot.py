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
    return "Bot Cek Rekening Online!"


def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


def keep_alive():
    t = Thread(target=run)
    t.start()


# ------------------------------------------------

# Logging untuk debugging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Masukkan Token dari @BotFather (Pastikan jangan sampai terhapus tanda kutipnya)
TELEGRAM_BOT_TOKEN = "8861657282:AAGUJ0iiZROF5LyfYEHlhYXEZIyJVvF2sy0"


# --- 2. FUNGSI INTEGRASI API CEK REKENING ---
def cek_rekening_api(bank_code: str, account_number: str):
    url = "https://api-rekening.my.id/api/v1/check"

    payload = {
        "accountBank": bank_code.lower().strip(),
        "accountNumber": account_number.strip(),
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            url, json=payload, headers=headers, timeout=12
        )

        if response.status_code == 200:
            res_data = response.json()

            if (
                res_data.get("status") is True
                or str(res_data.get("status")) == "200"
            ):
                data = res_data.get("data", {})
                account_name = (
                    data.get("accountName")
                    or data.get("account_name")
                    or data.get("name")
                )
                bank_name = (
                    data.get("bankName")
                    or data.get("bank_name")
                    or bank_code.upper()
                )

                return True, {
                    "bank": bank_name,
                    "number": account_number,
                    "name": account_name,
                }
            else:
                msg = res_data.get(
                    "message", "Nomor rekening/e-wallet tidak ditemukan."
                )
                return False, msg
        else:
            return (
                False,
                f"Server API sedang sibuk (Status Code: {response.status_code}).",
            )

    except requests.exceptions.Timeout:
        return False, "Waktu koneksi ke server API habis (Timeout)."
    except Exception as e:
        return False, f"Gagal menghubungi API: {str(e)}"


# --- 3. HANDLER COMMAND TELEGRAM BOT ---


# Perintah /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    thread_id = update.message.message_thread_id
    welcome_text = (
        "👋 <b>Selamat Datang di Bot Cek Rekening & E-Wallet!</b>\n\n"
        "Gunakan perintah <code>/cek &lt;KODE_BANK&gt; &lt;NO_REK&gt;</code> untuk mengecek pemilik rekening.\n\n"
        "<b>Contoh Penggunaan:</b>\n"
        "• <code>/cek bca 1234567890</code>\n"
        "• <code>/cek gopay 081234567890</code>\n"
        "• <code>/cek dana 081234567890</code>\n\n"
        "Ketik <code>/bank</code> untuk melihat daftar kode bank/e-wallet."
    )
    await update.message.reply_text(
        welcome_text, parse_mode="HTML", message_thread_id=thread_id
    )


# Perintah /bank
async def bank_list_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    thread_id = update.message.message_thread_id
    text = (
        "📋 <b>Daftar Kode Bank & E-Wallet yang Didukung:</b>\n\n"
        "• <b>Bank Komersial:</b> <code>bca</code>, <code>bri</code>, <code>mandiri</code>, <code>bni</code>, <code>btn</code>\n"
        "• <b>Bank Swasta / Syariah:</b> <code>cimb</code>, <code>permata</code>, <code>bsi</code>, <code>danamon</code>, <code>panin</code>\n"
        "• <b>E-Wallet:</b> <code>gopay</code>, <code>dana</code>, <code>ovo</code>, <code>linkaja</code>, <code>shopeepay</code>"
    )
    await update.message.reply_text(
        text, parse_mode="HTML", message_thread_id=thread_id
    )


# Perintah /cek <KODE_BANK> <NO_REK>
async def cek_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    thread_id = update.message.message_thread_id

    if len(context.args) < 2:
        await update.message.reply_text(
            "⚠️ <b>Format Perintah Salah!</b>\n\n"
            "Gunakan format: <code>/cek &lt;KODE_BANK&gt; &lt;NO_REK&gt;</code>\n"
            "Contoh: <code>/cek bca 1234567890</code>",
            parse_mode="HTML",
            message_thread_id=thread_id,
        )
        return

    bank_code = context.args[0]
    account_number = context.args[1]

    # Kirim pesan sementara
    loading_msg = await update.message.reply_text(
        f"⏳ Memeriksa <b>{bank_code.upper()}</b> nomor <code>{account_number}</code>...",
        parse_mode="HTML",
        message_thread_id=thread_id,
    )

    # Panggil API
    is_success, result = cek_rekening_api(bank_code, account_number)

    if is_success:
        response_text = (
            "✅ <b>REKENING VALID / DITEMUKAN</b>\n\n"
            f"• <b>Bank/E-Wallet:</b> {result['bank']}\n"
            f"• <b>No. Rekening:</b> <code>{result['number']}</code>\n"
            f"• <b>Nama Pemilik:</b> <b>{result['name']}</b>"
        )
    else:
        response_text = (
            "❌ <b>PENGECEKAN GAGAL</b>\n\n" f"• <b>Keterangan:</b> {result}"
        )

    # Edit pesan loading menjadi hasil akhir
    await loading_msg.edit_text(response_text, parse_mode="HTML")


# --- 4. MAIN EXECUTION ---
def main():
    if TELEGRAM_BOT_TOKEN == "ISI_TOKEN_BOT_TELEGRAM_KAMU":
        print("ERROR: Harap isi TELEGRAM_BOT_TOKEN terlebih dahulu!")
        return

    # Jalankan server mini
    keep_alive()

    bot_app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Registrasi Handler Command
    bot_app.add_handler(CommandHandler("start", start_command))
    bot_app.add_handler(CommandHandler("bank", bank_list_command))
    bot_app.add_handler(CommandHandler("cek", cek_command))

    print("🤖 Bot Cek Rekening Siap & Berjalan...")
    bot_app.run_polling()


if __name__ == "__main__":
    main()
