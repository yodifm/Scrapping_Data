from playwright.sync_api import sync_playwright
import time
import pandas as pd

# ========== CONFIG ==========
KEYWORD = "millwaukee m12 percussion drill"
OUTPUT_FILE = "tokopedia_result.xlsx"
MAX_SCROLL = 10  # jumlah scroll maksimal
SCROLL_WAIT = 2.5

def scrape_tokopedia(keyword):
    # Filter produk terbaru agar hasil relevan (mirip dengan 1 tahun terakhir)
    url = f"https://www.tokopedia.com/search?st=product&q={keyword}&srp_component_id=02.01.00.00&srp_page_id=&source=search&sort=latest"

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir="C:/tokopedia-session",  # agar login/session tersimpan
            headless=False
        )
        page = browser.new_page()
        page.goto(url, timeout=60000)
        time.sleep(5)

        print("Scroll otomatis 10x + klik 'Muat Lebih Banyak' jika ada...")

        for i in range(MAX_SCROLL):
            print(f"🔽 Scroll ke-{i+1}/{MAX_SCROLL}")
            page.mouse.wheel(0, 4000)
            time.sleep(SCROLL_WAIT)

            # Klik tombol 'Muat Lebih Banyak' jika ada
            try:
                load_more_button = page.query_selector("button:has-text('Muat Lebih Banyak')")
                if load_more_button:
                    print("🟢 Klik tombol 'Muat Lebih Banyak'...")
                    load_more_button.click()
                    time.sleep(4)
            except Exception as e:
                print("⚠️ Gagal klik tombol:", e)

        print("✅ Ambil data produk...")

        items = page.query_selector_all("div.css-5wh65g")
        data = []

        for item in items:
            try:
                text = item.inner_text().strip()
                lines = [l.strip() for l in text.splitlines() if l.strip()]

                if not lines or len(lines) < 3:
                    continue

                # --- parsing field utama ---
                title = lines[0]
                price = next((l for l in lines if "Rp" in l), "-")
                sold = next((l for l in lines if "terjual" in l.lower()), "-")
                location = lines[-1] if len(lines) >= 2 else "-"
                store = lines[-2] if len(lines) >= 3 else "-"

                link_el = item.query_selector("a")
                link = link_el.get_attribute("href") if link_el else "-"

                data.append({
                    "Nama Produk": title,
                    "Harga": price,
                    "Terjual": sold,
                    "Toko": store,
                    "Lokasi": location,
                    "Link": link
                })

            except Exception as e:
                print("⚠️ Error parsing produk:", e)

        df = pd.DataFrame(data)
        df.to_excel(OUTPUT_FILE, index=False)

        print(f"✅ Total produk tersimpan: {len(df)}")
        print(f"📁 File tersimpan di: {OUTPUT_FILE}")

        browser.close()

if __name__ == "__main__":
    scrape_tokopedia(KEYWORD)
