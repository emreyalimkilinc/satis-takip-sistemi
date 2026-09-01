import os
import sqlite3
import sys
import tkinter as tk
from tkinter import messagebox, ttk

# Başlangıç Verileri (Ürün Listesi)
BASLANGIC_VERILERI = [
    ("202402001", "i3 | 8GB | 500GB | 8 GB RX550 | FREEDOS"),
    (
        "202402296",
        (
            "Intel Core i5-12400F İşlemci, 16GB, 500GB NVMe SSD, 8GB NVIDIA RTX"
            " 3050 128 BIT, İşlemci fanı, RGB Klavye ve Mouse, 500W"
            " (2.50Ghz-4.40Ghz'e kadar, 18MB Akıllı Bellek)"
        ),
    ),
    (
        "202401997",
        (
            "Quantum Gaming Chaser SNT7 Q5516560 Amd Ryzen 5 5500, 16Gb 3200Mhz,"
            " 512Gb ssd, 8gb 4060, Freedos"
        ),
    ),
    (
        "202402295",
        (
            "Intel Core i3-12100F İşlemci, 8GB, 500GB NVMe SSD, 8GB AMD RX 550 128"
            " BIT, İşlemci fanı, RGB Klavye ve Mouse, 500W"
            " (3.30Ghz-4.30Ghz'e kadar, 12MB Akıllı Bellek)"
        ),
    ),
    ("202402003", "i7 | 8 GB | 1 TB | 8 GB RX550 | FREEDOS"),
    (
        "202502080",
        (
            "Lenovo LOQ 15IRH8 82XV00WYTX i5-12450H, 8GB, 512GB SSD, RTX3050,"
            ' 15,6" Full HD Gaming NB'
        ),
    ),
    (
        "202602778",
        (
            'Acer Al15-32P N45000 İntel Celeron, 4Gb Ram, 128 Ssd, 15,6 Fhd W11H'
            ' Notebook'
        ),
    ),
    (
        "202500824",
        (
            "AMD Ryzen™ 5-7430U İşlemci 4.3 GHz, 16GB, 500GB NVMe SSD, AMD"
            ' Radeon™ Graphics, 15.6" FHD IPS, FREEDOS, Gri'
        ),
    ),
    (
        "202303764",
        (
            "Intel Core i5-12450H İşlemci (3.30 GHz - 4.40 GHz’e kadar, 24MB"
            " Akıllı Bellek) - 16GB - 1TB NVMe SSD - 4 GB GDDR6 Nvidia Geforce"
            ' RTX 3050 Ekran Kartı - 15.6" FHD IPS 144HZ - RGB Klavye - FREEDOS'
            " - Siyah"
        ),
    ),
    (
        "202501954",
        (
            'Quantum Ultra TN1501 AMD R7-6800H, 16Gb, 512Gb Ssd, HDMI+WiFi, 15.6"'
            ' FullHD IPS, Freedos Notebook QNNTB10B060684'
        ),
    ),
    (
        "202505539",
        (
            "Casper G880.1342-CE50X-C i5 Excalibur Notebook - İşlemci: 13. Nesil"
            " Intel® Core™ i5 13420H, Ekran Kartı: NVIDIA® GeForce® RTX5050"
            ' 8GB, RAM: 24GB DDR5, Depolama: 500GB M.2 SSD, Ekran: 15.6" FHD'
            " IPS 165HZ"
        ),
    ),
    (
        "202506405",
        (
            "Intel Core i7-13620H İşlemci (3.60 GHz-4.90 GHz'e kadar, 24MB"
            " Akıllı Bellek), 24GB DDR5, 1TB NVMe SSD, Nvidia Geforce RTX5060"
            " 8GB GDDR7, FREEDOS"
        ),
    ),
    (
        "202307459",
        (
            "Intel Core i5-12450H İşlemci (3.30 GHz - 4.40 GHz'e kadar, 24MB"
            " Akıllı Bellek), 16GB, 500GB NVMe SSD, 6GB Nvidia Geforce RTX 4050"
            ' Ekran Kartı, 15.6" FHD IPS 144HZ, RGB Klavye, FREEDOS, Gri'
        ),
    ),
    (
        "202500825",
        (
            "Intel Core i7-12700H İşlemci (3.50 GHz-4.70 GHz'e kadar, 24MB"
            " Akıllı Bellek), 16GB, 1TB NVMe SSD, 4 GB GDDR6 Nvidia Geforce RTX"
            ' 3050 Ekran Kartı, 15.6" FHD IPS 144HZ, RGB Klavye, FREEDOS, Siyah'
        ),
    ),
    (
        "202506227",
        (
            "Intel Core i7-13620H İşlemci (3.60 GHz-4.90 GHz'e kadar, 24MB"
            " Akıllı Bellek), 16GB, 500GB NVMe SSD, Nvidia Geforce RTX3050 6GB,"
            ' 15.6" FHD IPS 165HZ, Gri'
        ),
    ),
    (
        "202303418",
        (
            "Quantum Magic CWE15IAR Intel i7-11800H, 16GB DDR4, 512GB SSD, RTX"
            " 3050 4GB, 15.6'' FreeDos"
        ),
    ),
    (
        "202506403",
        (
            "AMD Ryzen™ 7 5825U işlemci, FreeDOS, Entegre AMD Radeon™ Grafikler,"
            ' 16GB Soldered DDR4-3200, 512GB SSD M.2, 15.6" FHD IPS, Buzul Grisi'
        ),
    ),
    (
        "202303763",
        (
            "Intel Core i7-12650H İşlemci (3.50 GHz-4.70 GHz'e kadar, 24MB"
            " Akıllı Bellek) - 16GB - 1TB NVMe SSD - 4 GB GDDR6 Nvidia Geforce"
            ' RTX 3050 Ekran Kartı - 15.6" FHD IPS 144HZ - RGB Klavye - FREEDOS'
            " - Siyah"
        ),
    ),
]


class BilgisayarTakipApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Senetsepet.com - Donanım Takip Paneli")
    self.root.geometry("1050x700")
    self.root.config(bg="#f8f9fa")

    # Modern Renk Paleti
    self.bg_color = "#f8f9fa"
    self.card_bg = "#ffffff"
    self.primary_color = "#4338ca"  # Modern Indigo
    self.accent_color = "#059669"  # Emerald Green
    self.text_color = "#1f2937"
    self.border_color = "#e5e7eb"

    try:
      self.baglanti_kur()
    except Exception as e:
      messagebox.showerror(
          "Veritabanı Hatası", f"Veritabanı oluşturulamadı: {e}"
      )
      sys.exit(1)

    self.arayuz_olustur()
    self.verileri_listele()

  def baglanti_kur(self):
    db_yolu = os.path.join(
        os.path.expanduser("~"), "bilgisayar_takip_modern.db"
    )
    self.conn = sqlite3.connect(db_yolu)
    self.cursor = self.conn.cursor()
    self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS pc (
                barkod TEXT PRIMARY KEY,
                ozellikler TEXT
            )
        """)
    self.conn.commit()

    self.cursor.execute("SELECT COUNT(*) FROM pc")
    if self.cursor.fetchone()[0] == 0:
      self.cursor.executemany(
          "INSERT OR IGNORE INTO pc (barkod, ozellikler) VALUES (?, ?)",
          BASLANGIC_VERILERI,
      )
      self.conn.commit()

  def arayuz_olustur(self):
    # Ana Konteyner
    main_container = tk.Frame(self.root, bg=self.bg_color)
    main_container.pack(fill="both", expand=True, padx=20, pady=20)

    # Başlık Bölümü
    header_frame = tk.Frame(main_container, bg=self.bg_color)
    header_frame.pack(fill="x", pady=(0, 15))

    tk.Label(
        header_frame,
        text="Donanım Envanter Yönetimi",
        font=("Segoe UI", 18, "bold"),
        bg=self.bg_color,
        fg=self.text_color,
    ).pack(side="left")

    # Arama Paneli (Kart Yapısı)
    search_card = tk.Frame(
        main_container,
        bg=self.card_bg,
        highlightbackground=self.border_color,
        highlightthickness=1,
    )
    search_card.pack(fill="x", pady=(0, 15), ipady=8, ipadx=10)

    search_inner = tk.Frame(search_card, bg=self.card_bg)
    search_inner.pack(fill="x", padx=10, pady=5)

    tk.Label(
        search_inner,
        text="🔍",
        font=("Segoe UI", 12),
        bg=self.card_bg,
        fg="#6b7280",
    ).pack(side="left", padx=(0, 5))

    tk.Label(
        search_inner,
        text="Arama:",
        font=("Segoe UI", 10, "bold"),
        bg=self.card_bg,
        fg=self.text_color,
    ).pack(side="left", padx=(0, 10))

    self.arama_entry = tk.Entry(
        search_inner,
        font=("Segoe UI", 11),
        bg="#f3f4f6",
        fg=self.text_color,
        relief="flat",
        width=35,
    )
    self.arama_entry.pack(side="left", padx=5, ipady=5)
    self.arama_entry.bind("<KeyRelease>", self.arama_yap)

    tk.Button(
        search_inner,
        text="Tümünü Listele",
        command=self.verileri_listele,
        bg=self.primary_color,
        fg="white",
        font=("Segoe UI", 9, "bold"),
        relief="flat",
        cursor="hand2",
        padx=15,
        pady=5,
    ).pack(side="right", padx=5)

    # Tablo Alanı (Kart Yapısı İçinde)
    table_card = tk.Frame(
        main_container,
        bg=self.card_bg,
        highlightbackground=self.border_color,
        highlightthickness=1,
    )
    table_card.pack(fill="both", expand=True, pady=(0, 15), ipady=5, ipadx=5)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Treeview",
        background=self.card_bg,
        foreground=self.text_color,
        fieldbackground=self.card_bg,
        rowheight=32,
        font=("Segoe UI", 9),
    )
    style.configure(
        "Treeview.Heading",
        background="#f1f5f9",
        foreground="#334155",
        font=("Segoe UI", 10, "bold"),
        relief="flat",
    )
    style.map(
        "Treeview",
        background=[("selected", "#e0e7ff")],
        foreground=[("selected", "#1e1b4b")],
    )

    columns = ("barkod", "ozellikler")
    self.tree = ttk.Treeview(table_card, columns=columns, show="headings")
    self.tree.heading("barkod", text="Barkod No")
    self.tree.heading("ozellikler", text="Bilgisayarın Teknik Özellikleri")
    self.tree.column("barkod", width=140, anchor="center")
    self.tree.column("ozellikler", width=720, anchor="w")

    scrollbar = ttk.Scrollbar(
        table_card, orient="vertical", command=self.tree.yview
    )
    self.tree.configure(yscrollcommand=scrollbar.set)

    self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    scrollbar.pack(side="right", fill="y", pady=5)

    # Ürün Ekleme Paneli (Kart Yapısı)
    add_card = tk.Frame(
        main_container,
        bg=self.card_bg,
        highlightbackground=self.border_color,
        highlightthickness=1,
    )
    add_card.pack(fill="x", ipady=12, ipadx=10)

    add_inner = tk.Frame(add_card, bg=self.card_bg)
    add_inner.pack(fill="x", padx=15)

    tk.Label(
        add_inner,
        text="Yeni Ürün Ekle / Güncelle",
        font=("Segoe UI", 10, "bold"),
        bg=self.card_bg,
        fg=self.primary_color,
    ).pack(anchor="w", pady=(0, 10))

    form_grid = tk.Frame(add_inner, bg=self.card_bg)
    form_grid.pack(fill="x")

    tk.Label(
        form_grid,
        text="Barkod No:",
        font=("Segoe UI", 9),
        bg=self.card_bg,
        fg=self.text_color,
    ).grid(row=0, column=0, sticky="w", padx=(0, 5))
    self.yeni_barkod = tk.Entry(
        form_grid,
        font=("Segoe UI", 10),
        bg="#f3f4f6",
        fg=self.text_color,
        relief="flat",
        width=18,
    )
    self.yeni_barkod.grid(row=0, column=1, padx=(0, 20), ipady=4)

    tk.Label(
        form_grid,
        text="Teknik Özellikler:",
        font=("Segoe UI", 9),
        bg=self.card_bg,
        fg=self.text_color,
    ).grid(row=0, column=2, sticky="w", padx=(0, 5))
    self.yeni_ozellik = tk.Entry(
        form_grid,
        font=("Segoe UI", 10),
        bg="#f3f4f6",
        fg=self.text_color,
        relief="flat",
        width=45,
    )
    self.yeni_ozellik.grid(row=0, column=3, padx=(0, 20), ipady=4)

    tk.Button(
        form_grid,
        text="+ Kaydet",
        command=self.urun_ekle,
        bg=self.accent_color,
        fg="white",
        font=("Segoe UI", 9, "bold"),
        relief="flat",
        cursor="hand2",
        padx=15,
        pady=5,
    ).grid(row=0, column=4)

  def verileri_listele(self):
    for item in self.tree.get_children():
      self.tree.delete(item)

    self.cursor.execute("SELECT barkod, ozellikler FROM pc ORDER BY barkod DESC")
    for row in self.cursor.fetchall():
      self.tree.insert("", "end", values=row)

  def arama_yap(self, event):
    aranan = self.arama_entry.get().strip()
    for item in self.tree.get_children():
      self.tree.delete(item)

    self.cursor.execute(
        "SELECT barkod, ozellikler FROM pc WHERE barkod LIKE ? OR ozellikler"
        " LIKE ?",
        (f"%{aranan}%", f"%{aranan}%"),
    )
    for row in self.cursor.fetchall():
      self.tree.insert("", "end", values=row)

  def urun_ekle(self):
    barkod = self.yeni_barkod.get().strip()
    ozellikler = self.yeni_ozellik.get().strip()

    if not barkod:
      messagebox.showerror("Hata", "Lütfen barkod numarasını boş bırakmayın!")
      return

    try:
      self.cursor.execute(
          "INSERT OR REPLACE INTO pc (barkod, ozellikler) VALUES (?, ?)",
          (barkod, ozellikler),
      )
      self.conn.commit()
      messagebox.showinfo(
          "Başarılı", "Ürün sisteme başarıyla kaydedildi/güncellendi."
      )

      self.yeni_barkod.delete(0, tk.END)
      self.yeni_ozellik.delete(0, tk.END)
      self.arama_entry.delete(0, tk.END)
      self.verileri_listele()
    except Exception as e:
      messagebox.showerror("Hata", f"Bir hata oluştu: {e}")


if __name__ == "__main__":
  root = tk.Tk()
  app = BilgisayarTakipApp(root)
  root.mainloop()
