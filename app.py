import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import plotly.express as px

# 1. VERİTABANI BAĞLANTISI
def get_db_connection():
    return sqlite3.connect('satislar_bulut.db', check_same_thread=False)

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS satislar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih TEXT,
            satici TEXT,
            departman TEXT,
            tutar REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Personel Listesi
PERSONEL_LISTESI = [
    "Emre YALIMKILINÇ", "Derya DEMİR", "Sevim TEKİN", "Nurdagül MENEKŞE", 
    "Betül Merve GÜNGÖR", "Elif DEMİR", "Onur VARAN", "Özge KEL", 
    "Rabia ÇALHAN", "Merve KARAASLAN", "Bilge TURAN", "Seda SOYDAN", "Şennur ŞAHİN"
]

# 2. MOBİL VE WEB ARAYÜZ TASARIMI
st.set_page_config(page_title="Canlı Satış Portalı", page_icon="📈", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>📱 Web Tabanlı Satış Takip Sistemi</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📝 Yeni Satış Girişi", "🔒 Yönetici Paneli (Admin)"])

# --- SEKME 1: VERİ GİRİŞİ (Herkes Kullanabilir) ---
with tab1:
    st.subheader("Günlük Satış Verisi Girişi")
    with st.form("satis_form", clear_on_submit=True):
        tarih = st.date_input("Satış Tarihi", datetime.now())
        
        satici = st.selectbox("Satıcı Adı Soyadı", PERSONEL_LISTESI)
        dept = st.selectbox("Departman", ["Giriş kat", "Züccaciye", "Kasa", "Mobilya"])
        tutar = st.number_input("Satış Tutarı (₺)", min_value=0.0, step=50.0)
        submit = st.form_submit_button("Sisteme Kaydet")
        
        if submit:
            if tutar > 0:
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("INSERT INTO satislar (tarih, satici, departman, tutar) VALUES (?,?,?,?)",
                          (tarih.strftime('%Y-%m-%d'), satici, dept, tutar))
                conn.commit()
                conn.close()
                st.success(f"Başarılı: {satici} - {dept} departmanı için {tutar} ₺ satış kaydedildi.")
            else:
                st.error("Lütfen tutarın 0'dan büyük olduğundan emin olun.")

# --- SEKME 2: YÖNETİCİ PANELİ (Gelişmiş Filtreli) ---
with tab2:
    st.subheader("Yönetici Girişi")
    
    admin_sifre = st.text_input("Lütfen Admin Şifresini Giriniz:", type="password")
    
    if admin_sifre == "577339":
        st.success("Giriş Başarılı! İstatistikler yükleniyor...")
        st.markdown("---")
        
        conn = get_db_connection()
        df = pd.read_sql_query("SELECT * FROM satislar", conn)
        conn.close()
        
        if not df.empty:
            df['tarih'] = pd.to_datetime(df['tarih'])
            df['Yıl'] = df['tarih'].dt.year
            df['Ay'] = df['tarih'].dt.strftime('%Y-%m')
            df['Gün'] = df['tarih'].dt.strftime('%Y-%m-%d')
            
            # Üst Menü Seçimi
            admin_modu = st.radio("İnceleme Türü Seçin:", ["📅 Tarih Aralıklı Genel Rapor", "👤 Personel Bazlı Özel İnceleme"], horizontal=True)
            st.markdown("---")
            
            # --- MOD 1: TARİH ARALIKLI GENEL RAPOR ---
            if admin_modu == "📅 Tarih Aralıklı Genel Rapor":
                st.markdown("### 📅 Tarih Aralığı Filtresi (Genel Şirket)")
                min_date = df['tarih'].min().to_pydatetime()
                max_date = df['tarih'].max().to_pydatetime()
                
                varsayilan_baslangic = max_date - timedelta(days=7)
                if varsayilan_baslangic < min_date:
                    varsayilan_baslangic = min_date
                    
                tarih_secimi = st.date_input(
                    "Raporlamak istediğiniz başlangıç ve bitiş tarihlerini seçin:",
                    value=(varsayilan_baslangic, max_date),
                    min_value=min_date,
                    max_value=max_date,
                    key="genel_tarih"
                )
                
                if isinstance(tarih_secimi, tuple) and len(tarih_secimi) == 2:
                    baslangic_tarihi, bitis_tarihi = tarih_secimi
                    f_df = df[(df['tarih'] >= pd.to_datetime(baslangic_tarihi)) & 
                              (df['tarih'] <= pd.to_datetime(bitis_tarihi))]
                    st.info(f"📅 **{baslangic_tarihi.strftime('%d.%m.%Y')}** ile **{bitis_tarihi.strftime('%d.%m.%Y')}** arasındaki genel satışlar listeleniyor.")
                else:
                    f_df = df
                    st.warning("Lütfen takvimden hem başlangıç hem de bitiş gününe tıklayarak bir aralık seçin.")
                
                if not f_df.empty:
                    toplam = f_df['tutar'].sum()
                    st.metric(label="Seçilen Tarih Aralığındaki Toplam Ciro", value=f"{toplam:,.2f} ₺")
                    
                    fig = px.bar(f_df, x='satici', y='tutar', color='departman', title="Seçilen Aralıktaki Satıcı Performansları")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.write("📋 Satış Listesi Detayları:")
                    st.dataframe(f_df[['tarih', 'satici', 'departman', 'tutar']].sort_values(by='tarih', ascending=False), use_container_width=True)
                else:
                    st.warning("Seçilen tarih aralığında herhangi bir satış kaydı bulunamadı.")
            
            # --- MOD 2: PERSONEL BAZLI ÖZEL İNCELEME (Tarih Aralıklı) ---
            else:
                st.markdown("### 👤 Personel Bazlı Tarih Aralıklı Gözlem")
                
                secilen_personel = st.selectbox("Satışlarını incelemek istediğiniz kullanıcıyı seçin:", PERSONEL_LISTESI)
                
                # Önce seçilen personelin tüm verilerini bulalım (Tarih sınırını belirlemek için)
                ham_personel_df = df[df['satici'] == secilen_personel]
                
                if not ham_personel_df.empty:
                    # Bu personele özel dinamik takvim sınırları
                    p_min_date = ham_personel_df['tarih'].min().to_pydatetime()
                    p_max_date = ham_personel_df['tarih'].max().to_pydatetime()
                    
                    st.write(f"ℹ️ {secilen_personel} için sistemdeki ilk kayıt: **{p_min_date.strftime('%d.%m.%Y')}**, son kayıt: **{p_max_date.strftime('%d.%m.%Y')}**")
                    
                    # Personel ekranı için özel tarih aralığı kutusu
                    p_tarih_secimi = st.date_input(
                        f"{secilen_personel} için Tarih Aralığı Seçin:",
                        value=(p_min_date, p_max_date),
                        min_value=p_min_date,
                        max_value=p_max_date,
                        key="personel_tarih"
                    )
                    
                    # Seçilen aralığa göre filtrele
                    if isinstance(p_tarih_secimi, tuple) and len(p_tarih_secimi) == 2:
                        p_baslangic, p_bitis = p_tarih_secimi
                        personel_df = ham_personel_df[(ham_personel_df['tarih'] >= pd.to_datetime(p_baslangic)) & 
                                                      (ham_personel_df['tarih'] <= pd.to_datetime(p_bitis))]
                        st.info(f"📅 **{secilen_personel}** isimli personelin **{p_baslangic.strftime('%d.%m.%Y')}** - **{p_bitis.strftime('%d.%m.%Y')}** arasındaki performans verileri:")
                    else:
                        personel_df = ham_personel_df
                        st.warning("Lütfen takvimden hem başlangıç hem de bitiş gününe tıklayarak bir aralık seçin.")
                    
                    # Filtrelenmiş sonuçları göster
                    if not personel_df.empty:
                        p_toplam = personel_df['tutar'].sum()
                        p_adet = len(personel_df)
                        
                        kol1, kol2 = st.columns(2)
                        with kol1:
                            st.metric(label=f"💰 Seçilen Dönem Toplam Cirosu", value=f"{p_toplam:,.2f} ₺")
                        with kol2:
                            st.metric(label="📦 Seçilen Dönem Satış Adedi", value=f"{p_adet} Adet")
                        
                        fig_p = px.pie(personel_df, values='tutar', names='departman', title=f"Seçilen Dönem Departman Dağılımı")
                        st.plotly_chart(fig_p, use_container_width=True)
                        
                        st.write("📋 Dönem Satış Listesi:")
                        st.dataframe(personel_df[['tarih', 'departman', 'tutar']].sort_values(by='tarih', ascending=False), use_container_width=True)
                    else:
                        st.warning("Seçilen tarih aralığında bu personele ait bir satış kaydı bulunamadı.")
                else:
                    st.info(f"Seçilen kullanıcıya ({secilen_personel}) ait sistemde henüz hiçbir satış kaydı bulunmuyor.")
                
        else:
            st.info("Sistemde henüz kayıtlı veri bulunmuyor.")
            
    elif admin_sifre != "":
        st.error("Hatalı Şifre! İstatistikleri görme yetkiniz yoktur.")
