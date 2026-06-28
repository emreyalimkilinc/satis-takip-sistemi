import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import plotly.express as px
import io

# 1. VERİTABANI BAĞLANTISI VE YAPILANDIRMASI
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
    c.execute('''
        CREATE TABLE IF NOT EXISTS hedefler (
            tur TEXT PRIMARY KEY,
            hedef_tutar REAL
        )
    ''')
    c.execute("INSERT OR IGNORE INTO hedefler (tur, hedef_tutar) VALUES ('aylik_genel', 500000.0)")
    conn.commit()
    conn.close()

init_db()

PERSONEL_LISTESI = [
    "Emre YALIMKILINÇ", "Derya DEMİR", "Sevim TEKİN", "Nurdagül MENEKŞE", 
    "Betül Merve GÜNGÖR", "Elif DEMİR", "Onur VARAN", "Özge KEL", 
    "Rabia ÇALHAN", "Merve KARAASLAN", "Bilge TURAN", "Seda SOYDAN", "Şennur ŞAHİN"
]
DEPARTMAN_LISTESI = ["Giriş kat", "Züccaciye", "Kasa", "Mobilya"]

# --- GLOBAL MODERN MOBİL TASARIM AYARLARI (CSS) ---
st.set_page_config(page_title="Sales Portal", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    /* Global Arka Plan ve Temiz Font */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #F8FAFC;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Mobil Sekme (Tabs) Tasarımı */
    button[data-testid="stMarkdownContainer"] p {
        font-size: 16px !important;
        font-weight: 600 !important;
    }
    div[data-testid="stTabs"] button {
        padding: 10px 20px !important;
    }
    
    /* Dokunmatik Ekranlar İçin Büyük ve Şık Butonlar */
    div.stButton > button {
        width: 100% !important;
        height: 50px !important;
        border-radius: 12px !important;
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 16px !important;
        border: none !important;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:active {
        transform: scale(0.98) !important;
    }
    
    /* Form Alanlarının Kart (Card) Mimarisine Dönüştürülmesi */
    div[data-testid="stForm"] {
        background-color: white !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
    }
    
    /* Mobil input alanları yükseklik ayarı */
    div[data-baseweb="select"], div[data-baseweb="input"] {
        border-radius: 8px !important;
    }
    
    /* Mobil İndirme Butonu */
    a[data-testid="stDownloadButton"] {
        width: 100% !important;
    }
    div[data-testid="stDownloadButton"] button {
        width: 100% !important;
        height: 44px !important;
        border-radius: 10px !important;
        background-color: #10B981 !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# Başlık Kısmı - Küresel ve Sade Tasarım
st.markdown("""
    <div style='text-align: center; padding: 10px 0px;'>
        <h1 style='color: #0F172A; font-size: 28px; font-weight: 800; margin-bottom: 4px;'>📈 Sales Portal</h1>
        <p style='color: #64748B; font-size: 14px;'>Canlı Satış Takip ve Yönetim Paneli</p>
    </div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📝 Satış Girişi", "🔒 Yönetici Paneli"])

# --- SEKME 1: VERİ GİRİŞİ ---
with tab1:
    st.markdown("<p style='color:#334155; font-weight:600; margin-bottom:15px;'>Yeni Satış Kaydı Gürün</p>", unsafe_allow_html=True)
    with st.form("satis_form", clear_on_submit=True):
        tarih = st.date_input("Satış Tarihi", datetime.now().date())
        satici = st.selectbox("Satıcı Adı Soyadı", PERSONEL_LISTESI)
        dept = st.selectbox("Departman", DEPARTMAN_LISTESI)
        tutar = st.number_input("Satış Tutarı (₺)", min_value=0.0, step=50.0, value=0.0)
        
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        submit = st.form_submit_button("Sisteme Kaydet")
        
        if submit:
            if tutar > 0:
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("INSERT INTO satislar (tarih, satici, departman, tutar) VALUES (?,?,?,?)",
                          (tarih.strftime('%Y-%m-%d'), satici, dept, tutar))
                conn.commit()
                conn.close()
                st.success(f"Başarılı: {satici} için {tutar:,.2f} ₺ satış kaydedildi.")
                st.rerun()
            else:
                st.error("Lütfen tutarın 0'dan büyük olduğundan emin olun.")

# --- SEKME 2: YÖNETİCİ PANELİ ---
with tab2:
    admin_sifre = st.text_input("Admin Şifresi:", type="password", placeholder="••••••")
    
    if admin_sifre == "577339":
        st.success("Giriş Başarılı!")
        st.markdown("---")
        
        conn = get_db_connection()
        df = pd.read_sql_query("SELECT * FROM satislar", conn)
        c = conn.cursor()
        c.execute("SELECT hedef_tutar FROM hedefler WHERE tur='aylik_genel'")
        mevcut_hedef = c.fetchone()[0]
        conn.close()
        
        # Mobil uyumlu kenar çubuğu hedef ayarı
        st.sidebar.markdown("### 🎯 Aylık Hedef Ayarı")
        yeni_hedef = st.sidebar.number_input("Hedef Ciro (₺):", min_value=0.0, value=float(mevcut_hedef), step=10000.0)
        if yeni_hedef != mevcut_hedef:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("UPDATE hedefler SET hedef_tutar = ? WHERE tur='aylik_genel'", (yeni_hedef,))
            conn.commit()
            conn.close()
            st.sidebar.success("Hedef güncellendi!")
            st.rerun()

        if not df.empty:
            try:
                df['tarih_formatli'] = pd.to_datetime(df['tarih'])
            except Exception:
                pass
            
            # Mobilde yan yana sığması için sadeleştirilmiş buton menüsü
            admin_modu = st.radio("Menü:", [
                "📊 Genel Rapor", 
                "👤 Personel", 
                "🏆 Şampiyonlar", 
                "🗑️ Düzenle/Sil"
            ], horizontal=True)
            st.markdown("---")
            
            # --- MOD 1: GENEL RAPOR ---
            if admin_modu == "📊 Genel Rapor":
                try:
                    min_date = df['tarih_formatli'].min().date()
                    max_date = df['tarih_formatli'].max().date()
                    varsayilan_baslangic = max_date - timedelta(days=7)
                    if varsayilan_baslangic < min_date:
                        varsayilan_baslangic = min_date
                except Exception:
                    min_date, max_date, varsayilan_baslangic = datetime.now().date(), datetime.now().date(), datetime.now().date()
                    
                tarih_secimi = st.date_input("Filtre Aralığı:", value=(varsayilan_baslangic, max_date), min_value=min_date, max_value=max_date, key="genel_t")
                
                if isinstance(tarih_secimi, tuple) and len(tarih_secimi) == 2:
                    baslangic_tarihi, bitis_tarihi = tarih_secimi
                else:
                    baslangic_tarihi = tarih_secimi if not isinstance(tarih_secimi, (tuple, list)) else tarih_secimi[0]
                    bitis_tarihi = baslangic_tarihi
                
                try:
                    f_df = df[(df['tarih_formatli'].dt.date >= baslangic_tarihi) & (df['tarih_formatli'].dt.date <= bitis_tarihi)].copy()
                except Exception:
                    f_df = pd.DataFrame()
                
                if not f_df.empty:
                    toplam_ciro = f_df['tutar'].sum()
                    
                    # Mobil Uyumlu İlerleme Göstergesi (Card Tasarımı)
                    yuzde = min(toplam_ciro / mevcut_hedef, 1.0)
                    st.markdown(f"""
                        <div style='background-color: white; border: 1px solid #E2E8F0; border-radius: 12px; padding: 15px; margin-bottom: 15px;'>
                            <p style='margin:0; color:#64748B; font-size:13px; font-weight:600;'>TOPLAM DÖNEM CİROSU</p>
                            <h2 style='margin:5px 0; color:#1E3A8A; font-size:24px;'>{toplam_ciro:,.2f} ₺</h2>
                            <p style='margin:0; color:#059669; font-size:12px; font-weight:600;'>Hedef İlerlemesi: %{yuzde*100:.1f} (Hedef: {mevcut_hedef:,.0f} ₺)</p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.progress(yuzde)
                    
                    # Küresel ve Premium Renk Paletli Grafik
                    try:
                        fig = px.bar(f_df, x='satici', y='tutar', color='departman', 
                                     title="Personel Performansı",
                                     color_discrete_sequence=px.colors.qualitative.Safe)
                        fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        st.info("Grafik hazırlanıyor...")
                    
                    st.markdown("#### 📋 Satış Listesi Detayları")
                    
                    try:
                        output = io.BytesIO()
                        excel_df = f_df[['tarih', 'satici', 'departman', 'tutar']].copy()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            excel_df.to_excel(writer, index=False, sheet_name='Satis_Raporu')
                        processed_data = output.getvalue()
                        
                        st.download_button(
                            label="📥 Excel Raporu İndir",
                            data=processed_data,
                            file_name=f"Rapor_{baslangic_tarihi}_{bitis_tarihi}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    except Exception:
                        pass
                    
                    # Mobilde Kusursuz Kaydırılabilen Hata Korumalı Tablo
                    try:
                        goster_df = f_df[['id', 'tarih', 'satici', 'departman', 'tutar']].copy()
                        goster_df['tarih'] = pd.to_datetime(goster_df['tarih']).dt.strftime('%d.%m.%Y')
                        goster_df.columns = ['ID', 'Tarih', 'Satıcı', 'Departman', 'Tutar (₺)']
                        st.dataframe(goster_df.sort_values(by='ID', ascending=False), use_container_width=True)
                    except Exception:
                        st.error("Tablo yüklenirken bir hata oluştu.")
                else:
                    st.warning("Bu tarih aralığında satış kaydı bulunamadı.")
            
            # --- MOD 2: PERSONEL BAZLI ÖZEL İNCELEME ---
            elif admin_modu == "👤 Personel":
                secilen_personel = st.selectbox("Personel Seçin:", ["Seçiniz..."] + PERSONEL_LISTESI, key="admin_personel_sec")
                
                if secilen_personel != "Seçiniz...":
                    ham_personel_df = df[df['satici'] == secilen_personel].copy()
                    
                    if not ham_personel_df.empty:
                        try:
                            p_min, p_max = ham_personel_df['tarih_formatli'].min().date(), ham_personel_df['tarih_formatli'].max().date()
                        except Exception:
                            p_min, p_max = datetime.now().date(), datetime.now().date()
                            
                        p_tarih = st.date_input("Dönem Filtresi:", value=(p_min, p_max), min_value=p_min, max_value=p_max, key="p_t")
                        
                        if isinstance(p_tarih, tuple) and len(p_tarih) == 2:
                            p_b, p_bit = p_tarih
                        else:
                            p_b = p_tarih if not isinstance(p_tarih, (tuple, list)) else p_tarih[0]
                            p_bit = p_b
                            
                        try:
                            personel_df = ham_personel_df[(ham_personel_df['tarih_formatli'].dt.date >= p_b) & (ham_personel_df['tarih_formatli'].dt.date <= p_bit)].copy()
                        except Exception:
                            personel_df = pd.DataFrame()
                            
                        if not personel_df.empty:
                            st.markdown(f"""
                                <div style='background-color: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 10px; padding: 12px; margin-bottom:15px;'>
                                    <p style='margin:0; color:#1E40AF; font-size:14px;'><b>💰 Toplam Ciro:</b> {personel_df['tutar'].sum():,.2f} ₺</p>
                                    <p style='margin:5px 0 0 0; color:#1E40AF; font-size:14px;'><b>📦 Satış Adedi:</b> {len(personel_df)} Adet</p>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            try:
                                fig_p = px.pie(personel_df, values='tutar', names='departman', title="Departman Dağılımı", color_discrete_sequence=px.colors.qualitative.Pastel)
                                fig_p.update_layout(margin=dict(l=10, r=10, t=30, b=10))
                                st.plotly_chart(fig_p, use_container_width=True)
                            except Exception:
                                pass
                            
                            try:
                                goster_p_df = personel_df[['id', 'tarih', 'departman', 'tutar']].copy()
                                goster_p_df['tarih'] = pd.to_datetime(goster_p_df['tarih']).dt.strftime('%d.%m.%Y')
                                goster_p_df.columns = ['ID', 'Tarih', 'Departman', 'Tutar (₺)']
                                st.dataframe(goster_p_df.sort_values(by='ID', ascending=False), use_container_width=True)
                            except Exception:
                                pass
                        else:
                            st.warning("Seçilen aralıkta veri yok.")
                    else:
                        st.info("Bu personele ait henüz kayıt yok.")

            # --- MOD 3: LİDERLİK TABLOSU ---
            elif admin_modu == "🏆 Şampiyonlar":
                try:
                    l_min, l_max = df['tarih_formatli'].min().date(), df['tarih_formatli'].max().date()
                except Exception:
                    l_min, l_max = datetime.now().date(), datetime.now().date()
                    
                l_tarih = st.date_input("Sıralama Aralığı:", value=(l_min, l_max), key="l_t")
                
                if isinstance(l_tarih, tuple) and len(l_tarih) == 2:
                    l_b, l_bit = l_tarih
                else:
                    l_b = l_tarih if not isinstance(l_tarih, (tuple, list)) else l_tarih[0]
                    l_bit = l_b
                    
                try:
                    l_df = df[(df['tarih_formatli'].dt.date >= l_b) & (df['tarih_formatli'].dt.date <= l_bit)].copy()
                except Exception:
                    l_df = pd.DataFrame()
                
                if not l_df.empty:
                    liderlik = l_df.groupby('satici')['tutar'].sum().reset_index()
                    liderlik = liderlik.sort_values(by='tutar', ascending=False).reset_index(drop=True)
                    liderlik.index = liderlik.index + 1
                    liderlik.columns = ['Personel Adı', 'Toplam Ciro (₺)']
                    
                    st.markdown("#### 🥇 TOP 3 ŞAMPİYON")
                    if len(liderlik) >= 1:
                        st.success(f"🥇 **1. {liderlik.iloc[0]['Personel Adı']}:** {liderlik.iloc[0]['Toplam Ciro (₺)']:,.2f} ₺")
                    if len(liderlik) >= 2:
                        st.info(f"🥈 **2. {liderlik.iloc[1]['Personel Adı']}:** {liderlik.iloc[1]['Toplam Ciro (₺)']:,.2f} ₺")
                    if len(liderlik) >= 3:
                        st.warning(f"🥉 **3. {liderlik.iloc[2]['Personel Adı']}:** {liderlik.iloc[2]['Toplam Ciro (₺)']:,.2f} ₺")
                    
                    st.markdown("---")
                    st.dataframe(liderlik.style.format({'Toplam Ciro (₺)': '{:,.2f} ₺'}), use_container_width=True)
                else:
                    st.warning("Veri bulunamadı.")

            # --- MOD 4: KAYIT SİLME ---
            elif admin_modu == "🗑️ Düzenle/Sil":
                st.markdown("### 🗑️ Kayıt Temizleme")
                
                try:
                    gosterilecek_df = df[['id', 'tarih', 'satici', 'departman', 'tutar']].copy()
                    gosterilecek_df['tarih'] = pd.to_datetime(gosterilecek_df['tarih']).dt.strftime('%d.%m.%Y')
                    gosterilecek_df.columns = ['ID', 'Tarih', 'Satıcı', 'Departman', 'Tutar (₺)']
                    st.dataframe(gosterilecek_df.sort_values(by='ID', ascending=False).head(25), use_container_width=True)
                except Exception:
                    pass
                
                with st.form("silme_formu"):
                    silinecek_id = st.number_input("Silinecek Satış ID:", min_value=1, step=1)
                    silme_onayi = st.form_submit_button("🚨 SEÇİLİ KAYDI SİL")
                    
                    if silme_onayi:
                        if int(silinecek_id) in df['id'].values:
                            conn = get_db_connection()
                            c = conn.cursor()
                            c.execute("DELETE FROM satislar WHERE id = ?", (int(silinecek_id),))
                            conn.commit()
                            conn.close()
                            st.success(f"ID: {silinecek_id} başarıyla silindi!")
                            st.rerun()
                        else:
                            st.error("ID bulunamadı!")
        else:
            st.info("Henüz kayıtlı veri bulunmuyor.")
            
    elif admin_sifre != "":
        st.error("Hatalı Şifre!")
