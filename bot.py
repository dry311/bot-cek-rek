{}
```MD
Kendalanya terjadi karena mayoritas API gratisan (seperti `viki.id` atau `heirro`) sering tutup/ganti endpoint tanpa pemberitahuan.

Biar gak gonta-ganti API lagi, kita langsung ganti kodenya memakai **`api-rekening.my.id`** (atau `cekrekening.bank`) yang saat ini masih aktif dan menggunakan metode `POST`.

---

### Solusi Cepat: Ganti Fungsi `cek_rekening_api` di GitHub

Buka file `bot.py` kamu di GitHub, lalu ganti **seluruh fungsi `cek_rekening_api`** (mulai dari baris `# --- FUNGSI INTEGRASI...` sampai `except` paling bawah) dengan kode di bawah ini:

```python
# --- FUNGSI INTEGRASI API CEK REKENING (STABIL) ---
def cek_rekening_api(bank_code: str, account_number: str):
    # Menggunakan API terbuka publik
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

            # Pengecekan hasil dari API
            if (
                res_data.get("status") == True
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
