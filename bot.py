import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Logging untuk debugging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Mapping UUID ke Nama Bank (Diambil dari HTML)
BANK_DATA = {
    "01992c0f-d782-7159-93da-3be711e10c79": "Bank BRI",
    "01992c0f-d78e-73f7-9356-f498372d7b59": "Bank Mandiri",
    "01992c0f-d796-738b-8553-97ad0be2e281": "Bank BNI",
    "01992c0f-d7b0-71d0-aa10-aab26a19de5e": "Bank BCA",
    "01992c0f-d7be-72bc-bd30-674ee603f0d0": "Bank Syariah Indonesia (BSI)",
    "01992c0f-d7cc-7299-8d76-e1708eb1a64b": "Bank Muamalat",
    "01992c0f-d7db-72ee-bc96-187e1a384f67": "Bank CIMB Niaga",
    "01992c0f-d7e7-7221-a471-f5b244791e84": "Bank Tabungan Negara (BTN)",
    "01992c0f-d7f8-7359-bbfe-aa22442cd363": "Bank Permata",
    "01992c0f-d80c-738b-944a-eaef8cb82937": "Bank Danamon",
    "01992c0f-d81a-706d-a6aa-a3df65d1d6a3": "Bank Maybank Indonesia",
    "01992c0f-d829-710d-b4b6-eac797a7027d": "Bank Mega",
    "01992c0f-d837-73d8-a159-4ae5a21ff4f6": "Bank Sinarmas",
    "01992c0f-d844-730f-a94a-2197cb5cd8e4": "Bank BSI",
    "01992c0f-d852-736f-b258-294b4e3bd9ae": "Bank OCBC NISP",
    "01992c0f-d861-729f-bfce-e2ea73aef542": "Bank Panin",
    "01992c0f-d86b-7176-98f7-d6c5ed67e5ed": "GOPAY",
    "01992c0f-d87b-7184-a631-e532b12534e3": "DANA",
    "01992c0f-d883-72f4-92c8-220b19e43f58": "OVO",
    "01992c0f-d88f-738d-8fb8-88849b25fb2f": "LinkAja",
    "01992c0f-d899-7128-b80c-26e84db96c56": "Bank BTPN / Jenius",
    "01992c0f-d8a2-710f-8c33-87f5476a88bf": "Bank DBS Indonesia / digibank",
    "01992c0f-d8ae-723a-a114-118dfca6b054": "Bank Neo Commerce (BNC)",
    "01992c0f-d8b7-72eb-a24a-ae9997489bb2": "Bank Jago",
    "01992c0f-d8c0-7117-9c98-4aa4f40f3162": "Bank Aladin Syariah",
    "01992c0f-d8ca-7323-9565-d08bcf7e1c8d": "Bank Commonwealth",
    "01992c0f-d8d5-715a-b68a-b50e395efbb6": "Bank HSBC Indonesia",
    "01992c0f-d8de-73f1-bfa6-b186b51bfbc0": "Bank Standard Chartered",
    "01992c0f-d8e7-73d8-a831-2fb07bc607bf": "Bank UOB Indonesia",
    "01992c0f-d8f0-7058-8686-27bc24c0d380": "Bank Citibank N.A.",
    "01992c0f-d8f9-71c8-88ed-b003c94d0382": "Bank Mayapada",
    "01992c0f-d903-72dd-b883-29437b6dcbe6": "Bank Bukopin / KB Bukopin",
    "01992c0f-d90c-73ca-aa9a-9e12bf24fdf8": "Bank Artha Graha Internasional",
    "01992c0f-d915-71cb-8a4d-ef30713be217": "Bank Bumi Arta",
    "01992c0f-d91f-7232-a54d-17a4c7c8bc7f": "Bank Capital Indonesia",
    "01992c0f-d928-7013-81b3-6c841362fb76": "Bank MNC Internasional",
    "01992c0f-d931-7294-8ef8-cc60b297920a": "Bank India Indonesia",
    "01992c0f-d93a-73d4-bfa2-8cb253c0bf1f": "Bank JTrust Indonesia",
    "01992c0f-d942-70b9-ad7d-d4a0f443833b": "Bank Maspion Indonesia",
    "01992c0f-d94b-70f9-a29d-4340e4e5bd8e": "Bank Ganesha",
    "01992c0f-d954-72bf-8dc7-cecfbc9ff2dc": "Bank ICBC Indonesia",
    "01992c0f-d95e-711e-b83c-138be5a0ef3f": "Bank QNB Indonesia",
    "01992c0f-d967-727c-94cd-64dbd2eb05b7": "Bank WOORI SAUDARA",
    "01992c0f-d971-70bf-bbec-9d9be85a9df6": "Bank China Construction Bank Indonesia (CCBI)",
    "01992c0f-d97b-722a-aef2-d6cb4fb495f5": "Bank DKI",
    "01992c0f-d984-7338-9cb5-bbad9fcdbf09": "Bank BJB (Jawa Barat dan Banten)",
    "01992c0f-d98f-7023-b6c8-f94d93006a88": "Bank Jateng",
    "01992c0f-d998-7359-a5e3-4b684cbceb34": "Bank Jatim",
    "01992c0f-d9a1-71bb-8be8-fbc21d6feec7": "Bank BPD DIY",
    "01992c0f-d9ab-7206-a2a2-8f19ea3fc8eb": "Bank BPD Bali",
    "01992c0f-d9b4-71be-930f-b2e1bfef5fbd": "Bank Sumut",
    "01992c0f-d9bd-71bb-98da-1ed8be114bf5": "Bank Nagari (BPD Sumbar)",
    "01992c0f-d9c6-72bb-8e3d-d1ef1a4cc2a8": "Bank Riau Kepri",
    "01992c0f-d9cf-727a-b9c1-aa5f8d689b9d": "Bank Sumsel Babel",
    "01992c0f-d9d8-71e8-b8bc-25ae147748ca": "Bank Lampung",
    "01992c0f-d9e2-723a-a192-362629b3524d": "Bank Kalsel",
    "01992c0f-d9eb-72fb-87bf-0d04b868a83a": "Bank Kalimantan Barat (Kalbar)",
    "01992c0f-d9f4-71a7-8f5b-3b03657cd3ec": "Bank Kaltimtara (Kaltim Kaltara)",
    "01992c0f-d9fe-7253-ab29-68ea3f2bf83f": "Bank Kalteng",
    "01992c0f-da07-73d8-a8d1-931d8c11efcb": "Bank Sulselbar",
    "01992c0f-da11-7393-a442-70b9ec6ce6e1": "Bank SulutGo",
    "01992c0f-da1a-706f-82ff-3ef99d7990b5": "Bank NTB Syariah",
    "01992c0f-da23-73db-bc1b-05a812dfcfd5": "Bank NTT",
    "01992c0f-da2c-72aa-8b54-94bc7dce2c93": "Bank Maluku Malut",
    "01992c0f-da35-715a-9397-2a4c9ebcd5ca": "Bank Papua",
    "01992c0f-da3e-72cb-b7ff-153a54d6a5f2": "Bank Bengkulu",
    "01992c0f-da48-735a-bd5b-bf4ec6bfcf97": "Bank Sulteng",
    "01992c0f-da51-702b-a0ef-fb80a6b57952": "Bank Sultra",
    "01992c0f-da5a-71db-bbef-e5ff65a0dbd5": "Bank Banten",
    "01992c0f-da63-7182-a39c-2f9cd7469a53": "Bank Syariah Bukopin / KB Bank Syariah",
    "01992c0f-da6c-733d-8e47-e25df5d1bf77": "Bank Victoria Syariah",
    "01992c0f-da75-728b-bda2-540bbef96a2f": "Bank BCA Syariah",
    "01992c0f-da7e-71cb-b39b-e10db5aa21e2": "Bank BTPN Syariah",
    "01992c0f-da87-7323-9cf6-9cc89ebbd38c": "Bank Mega Syariah",
    "01992c0f-da90-705b-a8d4-59eeb6f1e2f3": "Bank Panin Dubai Syariah",
    "01992c0f-da99-736b-9cb6-c3cc17a3a992": "Bank BJB Syariah",
    "01992c0f-daaa-73db-b27b-2401f8087572": "Bank Sahabat Sampoerna",
    "01992c0f-dab8-711e-8eef-12503d6d4564": "Bank KEB Hana Indonesia",
    "01992c0f-dac6-7243-bd32-b7a4214f5263": "Bank Resona Perdania",
    "01992c0f-dad6-73d8-aa4c-ffedbf993425": "Bank Mizuho Indonesia",
    "01992c0f-dae3-722c-96b6-b8db2a3250ef": "Bank Sumitomo Mitsui Indonesia",
    "01992c0f-daf0-7193-9cbf-7013cb47ed5d": "Bank DBS Indonesia",
    "01992c0f-dafd-7377-80da-3fa6676cf4cb": "Bank CTBC Indonesia",
    "01992c0f-db0a-706f-bca1-6cbf2a24fa60": "Bank Shinhan Indonesia",
    "01992c0f-db17-73b3-8c46-f94de9c1f6b1": "Bank China TRUST Indonesia",
    "01992c0f-db25-7287-b031-76f65aa1f134": "Seabank",
    "019bd987-58e1-71b0-920d-e702840bad28": "Shopeepay",
}

# Command /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Membuat tombol inline keyboard (2 kolom)
    keyboard = []
    row = []

    for uuid, name in BANK_DATA.items():
        row.append(InlineKeyboardButton(name, callback_data=f"bank_{uuid}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Halo! Silakan pilih bank atau e-wallet tujuan:",
        reply_markup=reply_markup,
    )


# Handler saat pengguna memilih tombol Bank
async def bank_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Mengambil UUID dari callback_data
    selected_uuid = query.data.replace("bank_", "")
    bank_name = BANK_DATA.get(selected_uuid, "Bank Tidak Diketahui")

    # Menyimpan pilihan bank ke user_data session
    context.user_data["selected_bank_id"] = selected_uuid
    context.user_data["selected_bank_name"] = bank_name

    await query.edit_message_text(
        text=f"Kamu memilih **{bank_name}**.\n\nSekarang, silakan ketik/kirimkan **Nomor Rekening / HP** yang ingin dicek:",
        parse_mode="Markdown",
    )


# Handler saat pengguna mengirimkan nomor rekening (teks)
async def process_account_number(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    account_no = update.message.text.strip()
    bank_id = context.user_data.get("selected_bank_id")
    bank_name = context.user_data.get("selected_bank_name")

    # Jika pengguna belum memilih bank lebih dulu
    if not bank_id:
        await update.message.reply_text(
            "Silakan pilih bank terlebih dahulu dengan mengetik /start"
        )
        return

    await update.message.reply_text(f"Memproses pengecekan untuk...")

    # =========================================================
    # LOGIK CEK REKENING (HTTP POST Request ke backend/API)
    # Kamu bisa menambahkan requests.post() di sini
    # =========================================================

    response_message = (
        f"**Hasil Pengecekan:**\n"
        f"• Bank ID: `{bank_id}` ({bank_name})\n"
        f"• No. Rekening: `{account_no}`\n"
        f"• Status: Data berhasil diproses."
    )

    await update.message.reply_text(response_message, parse_mode="Markdown")

    # Reset data setelah selesai
    context.user_data.clear()


def main():
    # Ganti dengan Token Bot Telegram kamu
    TOKEN = "8834110152:AAFD6orSUPXInEMrlWShPJYL-pkWTCoO1mg"

    app = Application.builder().token(TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(bank_button_click, pattern="^bank_"))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, process_account_number)
    )

    print("Bot Telegram berjalan...")
    app.run_polling()


if __name__ == "__main__":
    main()
