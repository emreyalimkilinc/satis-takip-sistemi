import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import plotly.express as px

# 1. VERİTABANI BAĞLANTISI VE YAPILANDIRMASI
def get_db_connection():
    return sqlite3.connect('satislar_bulut.db', check_same_thread=False)

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # Satışlar Tablosu
    c.execute('''
        CREATE TABLE IF NOT EXISTS satislar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih TEXT,
            satici TEXT,
            departman TEXT,
            tutar REAL
        )
    ''')
    # Bireysel Personel Hedefleri Tablosu
    c.execute('''
        CREATE TABLE IF NOT EXISTS hedefler (
            tur TEXT PRIMARY KEY,
            hedef_tutar REAL
        )
    ''')
    # Kullanıcılar ve Şifreler Tablosu
    c.execute('''
        CREATE TABLE IF NOT EXISTS kullanicilar (
            kod TEXT PRIMARY KEY,
            isim TEXT,
            sifre TEXT
        )
    ''')
    
    # Tüm personelleri ve varsayılan kotaları veritabanına ilk kez ekleme
    for kod, p_isim in PERSONEL_KODLARI.items():
        c.execute("INSERT OR IGNORE INTO hedefler (tur, hedef_tutar) VALUES (?, 1500000.0)", (p_isim,))
        c.execute("INSERT OR IGNORE INTO kullanicilar (kod, isim, sifre) VALUES (?, ?, '123456')", (kod, p_isim))
        
    conn.commit()
    conn.close()

# SABİT PERSONEL LİSTESİ (İlk kurulum ve eşleşmeler için)
PERSONEL_KODLARI = {
    "2646": "Emre YALIMKILINÇ",
    "1303": "Derya DEMİR",
    "3253": "Onur VARAN",
    "3267": "Sevim TEKİN",
    "2079": "Seda SOYDAN",
    "3111": "Betül Merve GÜNGÖR",
    "3313": "Merve KARAASLAN",
    "2497": "Rabia ÇALHAN",
    "3310": "Nurdagül MENEKŞE",
    "2993": "Elif DEMİR",
    "3123": "Özge KEL",
    "3271": "Bilge TURAN",
    "2288": "Fatih",
    "3103": "Şennur ŞAHİN"
}

DEPARTMAN_LISTESI = ["Giriş kat", "Züccaciye", "Kasa", "Mobilya"]

# --- GLOBAL PREMIUM DARK MOD MOBİL CSS ---
st.set_page_config(page_title="Sales Portal", page_icon="📈", layout="centered")

st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #0F172A !important;
        color: #F1F5F9 !important;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }
    div[data-testid="stForm"], div.stAlert {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3) !important;
    }
    label, p, span, div[data-testid="stMarkdownContainer"] p, h1, h2, h3, h4 {
        color: #F1F5F9 !important;
        font-weight: 500 !important;
    }
    div[data-baseweb="select"], div[data-baseweb="input"], input, div[data-baseweb="popover"] {
        background-color: #0F172A !important;
        color: #F1F5F9 !important;
        border: 1px solid #475569 !important;
        border-radius: 10px !important;
    }
    div[data-testid="stForm"] div.stButton > button {
        width: 100% !important;
        height: 52px !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }
    button[kind="primaryFormSubmit"] {
        background-color: #3B82F6 !important;
        color: white !important;
    }
    div[data-testid="stHorizontalBlock"] div.stButton > button {
        width: 100% !important;
        height: 40px !important;
        border-radius: 10px !important;
        background-color: #334155 !important;
        color: #F1F5F9 !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        border: 1px solid #475569 !important;
    }
    #MainMenu, footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Veritabanını başlat
init_db()

# --- OTURUM DURUMU KONTROLLERİ ---
if 'admin_modu_aktif' not in st.session_state:
    st.session_state.admin_modu_aktif = False

if 'admin_sifre_dogrulandi' not in st.session_state:
    st.session_state.admin_sifre_dogrulandi = False

if 'user_oturum_aktif' not in st.session_state:
    st.session_state.user_oturum_aktif = False

if 'aktif_satici_adi' not in st.session_state:
    st.session_state.aktif_satici_adi = None

if 'aktif_satici_kodu' not in st.session_state:
    st.session_state.aktif_satici_kodu = None

# --- İPTAL SATIRLARINI KIRMIZI YAPMA FONKSİYONU ---
def renkli_satirlar(row):
    if row['Tutar (₺)'] < 0:
        return ['background-color: #7f1d1d; color: #fca5a5; font-weight: bold;'] * len(row)
    return [''] * len(row)

# --- ÜST BAŞLIK VE SAĞ BUTON ALANI ---
hdr_col1, hdr_col2 = st.columns([2, 1])

with hdr_col1:
    st.markdown(f"""
        <div style='text-align: left; padding: 5px 0px;'>
            <h1 style='color: #F8FAFC; font-size: 24px; font-weight: 700; letter-spacing: -0.5px; margin: 0;'>Sales Portal</h1>
            <p style='color: #94A3B8; font-size: 12px; margin: 2px 0 0 0;'>
                {f"Aktif Kullanıcı: {st.session_state.aktif_satici_adi}" if st.session_state.user_oturum_aktif else "Lütfen Giriş Yapın"}
            </p>
        </div>
    """, unsafe_allow_html=True)

with hdr_col2:
    st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
    if not st.session_state.admin_modu_aktif:
        if st.button("🔒 Admin Panel"):
            st.session_state.admin_modu_aktif = True
            st.rerun()
    else:
        if st.button("📝 Satış Ekranı"):
            st.session_state.admin_modu_aktif = False
            st.rerun()

st.markdown("---")

# --- GÖRÜNÜM 1: KULLANICI MODU ---
if not st.session_state.admin_modu_aktif:
    
    if not st.session_state.user_oturum_aktif:
        st.markdown("### 🔑 Personel Girişi")
        with st.form("personel_giris_formu"):
            girilen_kod = st.text_input("Satış Personel Kodunuz:", placeholder="Örn: 2646", type="password")
            girilen_sifre = st.text_input("Şifre:", value="", placeholder="••••••", type="password")
            giris_butonu = st.form_submit_button("GİRİŞ YAP")
            
            if giris_butonu:
                conn = get_db_connection()
                c = conn.cursor()
                # Şifreyi DB'den dinamik sorguluyoruz
                c.execute("SELECT isim, sifre FROM kullanicilar WHERE kod = ?", (girilen_kod,))
                user_data = c.fetchone()
                conn.close()
                
                if user_data and girilen_sifre == user_data[1]:
                    st.session_state.user_oturum_aktif = True
                    st.session_state.aktif_satici_adi = user_data[0]
                    st.session_state.aktif_satici_kodu = girilen_kod
                    st.success(f"Hoş geldiniz, {st.session_state.aktif_satici_adi}!")
                    st.rerun()
                else:
                    st.error("Hatalı Personel Kodu veya Şifre!")
                    
    else:
        col_cikis1, col_cikis2 = st.columns([3, 1])
        with col_cikis2:
            if st.button("🚪 Oturumu Kapat"):
                st.session_state.user_oturum_aktif = False
                st.session_state.aktif_satici_adi = None
                st.session_state.aktif_satici_kodu = None
                st.rerun()
        
        # Bireysel Kota İlerleme Şeması
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT SUM(tutar) FROM satislar WHERE satici = ?", (st.session_state.aktif_satici_adi,))
        user_toplam_ciro = c.fetchone()[0] or 0.0
        c.execute("SELECT hedef_tutar FROM hedefler WHERE tur = ?", (st.session_state.aktif_satici_adi,))
        user_kota = c.fetchone()[0] or 1500000.0
        conn.close()
        
        kalan_kota = user_kota - user_toplam_ciro
        user_yuzde = min(max(user_toplam_ciro / user_kota, 0.0), 1.0)
        
        st.markdown(f"""
            <div style='background-color: #1E293B; border: 1px solid #334155; border-radius: 12px; padding: 15px; margin-bottom: 5px;'>
                <p style='margin:0; color:#94A3B8; font-size:13px; font-weight:600;'>🎯 BİREYSEL SATIŞ KOTANIZ VE DURUMUNUZ</p>
                <h3 style='margin:5px 0; color:#10B981; font-size:20px;'>Toplam Cironuz: {user_toplam_ciro:,.2f} ₺ / Hedef: {user_kota:,.2f} ₺</h3>
                <p style='margin:0; color:#3B82F6; font-size:13px;'>
                    {f"Kotalarınızı Tamamlamaya Kalan: <b>{kalan_kota:,.2f} ₺</b>" if kalan_kota > 0 else "🎉 Tebrikler! Satış Kotanızı Başarıyla Tamamladınız!"}
                </p>
            </div>
        """, unsafe_allow_html=True)
        st.progress(user_yuzde)
        st.markdown("<br>", unsafe_allow_html=True)

        # Satış Giriş Formu
        with st.form("satis_form", clear_on_submit=True):
            tarih = st.date_input("Satış Tarihi", datetime.now().date())
            dept = st.selectbox("Departman", DEPARTMAN_LISTESI)
            tutar = st.number_input("Satış/İptal Tutarı (₺)", min_value=None, step=50.0, value=0.0)
            submit = st.form_submit_button("KAYDET")
            
            if submit:
                if tutar != 0:
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute("INSERT INTO satislar (tarih, satici, departman, tutar) VALUES (?,?,?,?)",
                              (tarih.strftime('%Y-%m-%d'), st.session_state.aktif_satici_adi, dept, tutar))
                    conn.commit()
                    conn.close()
                    st.success("İşlem başarıyla kaydedildi!")
                    st.rerun()
                else:
                    st.error("Lütfen 0 dışında geçerli bir tutar girin.")

        # Alt Geçmiş Tablosu
        st.markdown("---")
        st.markdown("#### 📋 Son İşlemleriniz")
        conn = get_db_connection()
        df_personel = pd.read_sql_query("SELECT * FROM satislar WHERE satici = ?", conn, params=(st.session_state.aktif_satici_adi,))
        conn.close()
        
        if not df_personel.empty:
            df_personel = df_personel.sort_values(by='id', ascending=False).reset_index(drop=True)
            df_personel.index = df_personel.index + 1
            goster_kullanici = df_personel.reset_index().rename(columns={'index': 'No'})
            goster_kullanici['tarih'] = pd.to_datetime(goster_kullanici['tarih']).dt.strftime('%d.%m.%Y')
            
            final_user_df = goster_kullanici[['No', 'tarih', 'departman', 'tutar']].rename(columns={'tarih':'Tarih','departman':'Departman','tutar':'Tutar (₺)'})
            st.dataframe(final_user_df.style.apply(renkli_satirlar, axis=1), use_container_width=True)
            
        # --- PERSONEL İÇİN ŞİFRE DEĞİŞTİRME BÖLÜMÜ ---
        st.markdown("---")
        with st.expander("🔐 Şifremi Değiştir"):
            with st.form("sifre_degis_form", clear_on_submit=True):
                p_eski = st.text_input("Mevcut Şifre:", type="password")
                p_yeni = st.text_input("Yeni Şifre:", type="password")
                p_yeni_onay = st.text_input("Yeni Şifre (Tekrar):", type="password")
                degis_submit = st.form_submit_button("🔑 ŞİFREMİ GÜNCELLE")
                
                if degis_submit:
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute("SELECT sifre FROM kullanicilar WHERE kod = ?", (st.session_state.aktif_satici_kodu,))
                    guncel_sifre = c.fetchone()[0]
                    
                    if p_eski != guncel_sifre:
                        st.error("Mevcut şifrenizi hatalı girdiniz.")
                    elif p_yeni != p_yeni_onay:
                        st.error("Yeni şifreler birbiriyle uyuşmuyor.")
                    elif len(p_yeni) < 4:
                        st.error("Yeni şifre en az 4 karakter olmalıdır.")
                    else:
                        c.execute("UPDATE kullanicilar SET sifre = ? WHERE kod = ?", (p_yeni, st.session_state.aktif_satici_kodu))
                        conn.commit()
                        st.success("Şifreniz başarıyla değiştirildi! Bir sonraki girişte yeni şifrenizi kullanın.")
                    conn.close()

# --- GÖRÜNÜM 2: YÖNETİCİ PANELİ ---
else:
    if not st.session_state.admin_sifre_dogrulandi:
        st.markdown("### 🔒 Yönetici Kimlik Doğrulama")
        admin_sifre = st.text_input("Admin Şifresini Girin:", type="password", placeholder="•••••")
        
        if admin_sifre == "577339":
            st.session_state.admin_sifre_dogrulandi = True
            st.success("Giriş Başarılı!")
            st.rerun()
        elif admin_sifre != "":
            st.error("Hatalı Şifre!")
            
    if st.session_state.admin_sifre_dogrulandi:
        conn = get_db_connection()
        df = pd.read_sql_query("SELECT * FROM satislar", conn)
        
        # Kotaları Çek
        c = conn.cursor()
        kotalar = {}
        for p_isim in PERSONEL_KODLARI.values():
            c.execute("SELECT hedef_tutar FROM hedefler WHERE tur=?", (p_isim,))
            res = c.fetchone()
            kotalar[p_isim] = res[0] if res else 1500000.0
        conn.close()

        admin_modu = st.radio("İnceleme Türü:", ["📊 Genel Rapor & Kotalar", "👤 Personel", "🏆 Şampiyonlar", "⚙️ Düzenle/Sil", "👤 Personel & Şifre Yönetimi"], horizontal=True)
        st.markdown("---")
        
        if not df.empty:
            df['tarih_formatli'] = pd.to_datetime(df['tarih'])
            min_date, max_date = df['tarih_formatli'].min().date(), df['tarih_formatli'].max().date()
            varsayilan_baslangic = max_date - timedelta(days=7)
            if varsayilan_baslangic < min_date: varsayilan_baslangic = min_date
        else:
            min_date, max_date, varsayilan_baslangic = datetime.now().date(), datetime.now().date(), datetime.now().date()
        
        # --- MOD 1: GENEL RAPOR VE BİREYSEL KOTA DÜZENLEME ---
        if admin_modu == "📊 Genel Rapor & Kotalar":
            tarih_secimi = st.date_input("Filtre Aralığı:", value=(varsayilan_baslangic, max_date), min_value=min_date, max_value=max_date)
            if isinstance(tarih_secimi, tuple) and len(tarih_secimi) == 2: baslangic_tarihi, bitis_tarihi = tarih_secimi
            else: baslangic_tarihi = tarih_secimi if not isinstance(tarih_secimi, (tuple, list)) else tarih_secimi[0]; bitis_tarihi = baslangic_tarihi
            
            try: f_df = df[(df['tarih_formatli'].dt.date >= baslangic_tarihi) & (df['tarih_formatli'].dt.date <= bitis_tarihi)].copy()
            except: f_df = pd.DataFrame()
            
            toplam_ciro = f_df['tutar'].sum() if not f_df.empty else 0.0
            st.metric("MAĞAZA TOPLAM NET DÖNEM CİROSU", f"{toplam_ciro:,.2f} ₺")
            
            st.markdown("### ⚙️ Personel Bazlı Bireysel Kota Yönetimi")
            kota_duzenleme_listesi = []
            for p_isim in PERSONEL_KODLARI.values():
                p_satis_toplam = f_df[f_df['satici'] == p_isim]['tutar'].sum() if not f_df.empty else 0.0
                p_hedef = kotalar.get(p_isim, 1500000.0)
                kalan = p_hedef - p_satis_toplam
                
                kota_duzenleme_listesi.append({
                    "Personel Adı Soyadı": p_isim,
                    "Mevcut Dönem Cirosu (₺)": round(p_satis_toplam, 2),
                    "Bireysel Kota (₺)": float(p_hedef),
                    "Kotaya Kalan Tutar": f"{kalan:,.2f} ₺" if kalan > 0 else "0.00 ₺ (Kotayı Tamamladı 🎉)",
                    "Başarı Oranı": f"% {(p_satis_toplam / p_hedef) * 100:.1f}" if p_hedef > 0 else "% 0.0"
                })
            
            girdi_df = pd.DataFrame(kota_duzenleme_listesi)
            duzenlenmis_durum = st.data_editor(
                girdi_df,
                column_config={
                    "Personel Adı Soyadı": st.column_config.TextColumn(disabled=True),
                    "Mevcut Dönem Cirosu (₺)": st.column_config.NumberColumn(format="%.2f ₺", disabled=True),
                    "Bireysel Kota (₺)": st.column_config.NumberColumn(format="%.2f ₺", min_value=0.0, step=50000.0),
                    "Kotaya Kalan Tutar": st.column_config.TextColumn(disabled=True),
                    "Başarı Oranı": st.column_config.TextColumn(disabled=True)
                },
                disabled=["Personel Adı Soyadı", "Mevcut Dönem Cirosu (₺)", "Kotaya Kalan Tutar", "Başarı Oranı"],
                use_container_width=True,
                key="bireysel_kota_editor"
            )
            
            if st.button("💾 Tüm Bireysel Kotaları Kaydet", type="primary"):
                conn = get_db_connection()
                c = conn.cursor()
                for index, row in duzenlenmis_durum.iterrows():
                    c.execute("UPDATE hedefler SET hedef_tutar = ? WHERE tur = ?", (float(row["Bireysel Kota (₺)"]), row["Personel Adı Soyadı"]))
                conn.commit()
                conn.close()
                st.success("Bireysel kotalar başarıyla güncellendi!")
                st.rerun()
                
            if not f_df.empty:
                st.markdown("---")
                fig = px.bar(f_df, x='satici', y='tutar', color='departman', template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
                
                goster_df = f_df.sort_values(by='id', ascending=False).reset_index(drop=True)
                goster_df.index = goster_df.index + 1
                goster_df = goster_df.reset_index().rename(columns={'index': 'No'})
                goster_df['tarih'] = pd.to_datetime(goster_df['tarih']).dt.strftime('%d.%m.%Y')
                
                final_table_df = goster_df[['No', 'tarih', 'satici', 'departman', 'tutar']].rename(columns={'tarih':'Tarih','satici':'Satıcı','departman':'Departman','tutar':'Tutar (₺)'})
                st.dataframe(final_table_df.style.apply(renkli_satirlar, axis=1), use_container_width=True)

        # --- MOD 2: PERSONEL BAZLI İNCELEME ---
        elif admin_modu == "👤 Personel":
            secilen_personel = st.selectbox("Personel Seçin:", ["Seçiniz..."] + list(PERSONEL_KODLARI.values()))
            if secilen_personel != "Seçiniz..." and not df.empty:
                ham_personel_df = df[df['satici'] == secilen_personel].copy()
                if not ham_personel_df.empty:
                    p_min, p_max = ham_personel_df['tarih_formatli'].min().date(), ham_personel_df['tarih_formatli'].max().date()
                    p_tarih = st.date_input("Dönem Filtresi:", value=(p_min, p_max), min_value=p_min, max_value=p_max)
                    if isinstance(p_tarih, tuple) and len(p_tarih) == 2: p_b, p_bit = p_tarih
                    else: p_b = p_tarih if not isinstance(p_tarih, (tuple, list)) else p_tarih[0]; p_bit = p_b
                    
                    personel_df = ham_personel_df[(ham_personel_df['tarih_formatli'].dt.date >= p_b) & (ham_personel_df['tarih_formatli'].dt.date <= p_bit)].sort_values(by='id', ascending=False).reset_index(drop=True)
                    if not personel_df.empty:
                        p_kota_degeri = kotalar.get(secilen_personel, 1500000.0)
                        st.markdown(f"**💰 Toplam Satışı:** {personel_df['tutar'].sum():,.2f} ₺ | **🎯 Bireysel Kotası:** {p_kota_degeri:,.2f} ₺")
                        personel_df.index = personel_df.index + 1
                        goster_p = personel_df.reset_index().rename(columns={'index': 'No'})
                        goster_p['tarih'] = pd.to_datetime(goster_p['tarih']).dt.strftime('%d.%m.%Y')
                        
                        final_p_df = goster_p[['No', 'tarih', 'departman', 'tutar']].rename(columns={'tarih':'Tarih','departman':'Departman','tutar':'Tutar (₺)'})
                        st.dataframe(final_p_df.style.apply(renkli_satirlar, axis=1), use_container_width=True)

        # --- MOD 3: LİDERLİK TABLOSU ---
        elif admin_modu == "🏆 Şampiyonlar":
            if not df.empty:
                liderlik = df.groupby('satici')['tutar'].sum().reset_index().sort_values(by='tutar', ascending=False).reset_index(drop=True)
                liderlik.index = liderlik.index + 1
                st.dataframe(liderlik.reset_index().rename(columns={'index':'Sıra','satici':'Personel Adı','tutar':'Net Ciro (₺)'}), use_container_width=True)

        # --- MOD 4: GÜNCELLEME VE SİLME ---
        elif admin_modu == "⚙️ Düzenle/Sil":
            if not df.empty:
                islem_df = df.sort_values(by='id', ascending=False).reset_index(drop=True)
                islem_df.index = islem_df.index + 1
                islem_df = islem_df.reset_index().rename(columns={'index': 'No'})
                
                gosterilecek_df = islem_df.copy()
                gosterilecek_df['tarih'] = pd.to_datetime(gosterilecek_df['tarih']).dt.strftime('%d.%m.%Y')
                
                final_action_df = gosterilecek_df[['No', 'tarih', 'satici', 'departman', 'tutar']].rename(columns={'tarih':'Tarih','satici':'Satıcı','departman':'Departman','tutar':'Tutar (₺)'})
                st.dataframe(final_action_df.style.apply(renkli_satirlar, axis=1), use_container_width=True)
                
                st.markdown("---")
                islem_tipi = st.radio("Yapılacak İşlem:", ["✏️ Sıra No Seç ve Güncelle", "🚨 Sıra No Seç ve Sil"], horizontal=True)
                mevcut_no_listesi = islem_df['No'].tolist()
                
                if mevcut_no_listesi:
                    if islem_tipi == "✏️ Sıra No Seç ve Güncelle":
                        secilen_no = st.selectbox("Düzenlemek istediğiniz işlemin 'No' değerini seçin:", mevcut_no_listesi)
                        secilen_satir = islem_df[islem_df['No'] == secilen_no].iloc[0]
                        gercek_db_id = int(secilen_satir['id'])
                        
                        eski_tarih = datetime.strptime(secilen_satir['tarih'], '%Y-%m-%d').date()
                        personel_listesi_full = list(PERSONEL_KODLARI.values())
                        try: s_idx = personel_listesi_full.index(secilen_satir['satici'])
                        except: s_idx = 0
                        try: d_idx = DEPARTMAN_LISTESI.index(secilen_satir['departman'])
                        except: d_idx = 0
                        
                        with st.form("canli_duzenleme_formu"):
                            yeni_tarih = st.date_input("Tarih", eski_tarih)
                            yeni_satici = st.selectbox("Satıcı", personel_listesi_full, index=s_idx)
                            yeni_dept = st.selectbox("Departman", DEPARTMAN_LISTESI, index=d_idx)
                            yeni_tutar = st.number_input("Tutar (₺)", min_value=None, value=float(secilen_satir['tutar']), step=50.0)
                            
                            edit_onayi = st.form_submit_button("🔁 DEĞİŞİKLİKLERİ KAYDET")
                            if edit_onayi:
                                conn = get_db_connection()
                                c = conn.cursor()
                                c.execute("UPDATE satislar SET tarih=?, satici=?, departman=?, tutar=? WHERE id=?", 
                                          (yeni_tarih.strftime('%Y-%m-%d'), yeni_satici, yeni_dept, yeni_tutar, gercek_db_id))
                                conn.commit()
                                conn.close()
                                st.success("İşlem başarıyla güncellendi!")
                                st.rerun()
                                
                    elif islem_tipi == "🚨 Sıra No Seç ve Sil":
                        with st.form("silme_formu"):
                            silinecek_no = st.selectbox("Silmek istediğiniz işlemin 'No' değerini seçin:", mevcut_no_listesi)
                            silinecek_satir = islem_df[islem_df['No'] == silinecek_no].iloc[0]
                            gercek_db_id = int(silinecek_satir['id'])
                            
                            silme_onayi = st.form_submit_button("🚨 SEÇİLİ İŞLEMİ KALICI OLARAK SİL")
                            if silme_onayi:
                                conn = get_db_connection()
                                c = conn.cursor()
                                c.execute("DELETE FROM satislar WHERE id = ?", (gercek_db_id,))
                                conn.commit()
                                conn.close()
                                st.success("İşlem başarıyla silindi.")
                                st.rerun()

        # --- MOD 5: ADMIN İÇİN PERSONEL & ŞİFRE YÖNETİMİ ---
        elif admin_modu == "👤 Personel & Şifre Yönetimi":
            st.markdown("### 🔑 Tüm Personel Kodları ve Güncel Şifreleri")
            st.info("Unutulan şifreleri buradan görebilir ya da personelin şifresini doğrudan güncelleyebilirsiniz.")
            
            conn = get_db_connection()
            df_kullanicilar = pd.read_sql_query("SELECT kod as 'Personel Kodu', isim as 'Personel Adı Soyadı', sifre as 'Güncel Şifre' FROM kullanicilar", conn)
            conn.close()
            
            st.dataframe(df_kullanicilar, use_container_width=True)
            
            st.markdown("---")
            st.markdown("#### ✏️ Personel Şifresini Yönetici Olarak Değiştir/Sıfırla")
            with st.form("admin_sifre_sifirla_form"):
                secilen_kod = st.selectbox("Şifresi Değişecek Personel:", df_kullanicilar['Personel Kodu'].tolist(), 
                                           format_func=lambda x: f"{x} - {PERSONEL_KODLARI.get(x)}")
                yeni_gecici_sifre = st.text_input("Yeni Şifre:", value="123456")
                sifre_sifirla_submit = st.form_submit_button("🔁 PERSONEL ŞİFRESİNİ GÜNCELLE")
                
                if sifre_sifirla_submit:
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute("UPDATE kullanicilar SET sifre = ? WHERE kod = ?", (yeni_gecici_sifre, secilen_kod))
                    conn.commit()
                    conn.close()
                    st.success(f"{secilen_kod} kodlu personelin şifresi başarıyla '{yeni_gecici_sifre}' olarak güncellendi!")
                    st.rerun()
