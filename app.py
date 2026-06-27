import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
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

# 2. MOBİL VE WEB ARAYÜZ TASARIMI
st.set_page_config(page_title="Canlı Satış Portalı", page_icon="📈", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>📱 Web Tabanlı Satış Takip Sistemi</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📝 Yeni Satış Girişi", "🔒 Yönetici Paneli (Admin)"])

# --- SEKME 1: VERİ GİRİŞİ (Herkes Kullanabilir) ---
with tab1:
    st.subheader("Günlük Satış Verisi Girişi")
    with st.form("satis_form", clear_on_submit=True):
        tarih = st.date_input("Satış Tarihi", datetime.now())
        
        satici = st.selectbox("Satıcı Adı Soyadı", [
            "Emre YALIMKILINÇ", "Derya DEMİR", "Sevim TEKİN", "Nurdagül MENEKŞE", 
            "Betül Merve GÜNGÖR", "Elif DEMİR", "Onur VARAN", "Özge KEL", 
            "Rabia ÇALHAN", "Merve KARAASLAN", "Bilge TURAN", "Seda SOYDAN", "Şennur ŞAHİN"
        ])
        
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

# --- SEKME 2: YÖNETİCİ PANELİ (Sadece Emre Bey / Şifreyi Bilenler) ---
with tab2:
    st.subheader("Yönetici Girişi")
    
    # Şifre Giriş Kutusu (Yazılan harfler/rakamlar yıldız olarak görünür)
    admin_sifre = st.text_input("Lütfen Admin Şifresini Giriniz:", type="password")
    
    # NOT: Aşağıdaki '1234' kısmını istediğiniz bir şifreyle değiştirebilirsiniz.
    if admin_sifre == "1234":
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
            
            periyot = st.radio("Raporlama Dönemi Seçin:", ["Günlük", "Aylık", "Yıllık"], horizontal=True)
            
            if periyot == "Günlük":
                secim = st.selectbox("Tarih Seçin", sorted(df['Gün'].unique(), reverse=True))
                f_df = df[df['Gün'] == secim]
            elif periyot == "Aylık":
                secim = st.selectbox("Ay Seçin (Yıl-Ay)", sorted(df['Ay'].unique(), reverse=True))
                f_df = df[df['Ay'] == secim]
            else:
                secim = st.selectbox("Yıl Seçin", sorted(df['Yıl'].unique(), reverse=True))
                f_df = df[df['Yıl'] == secim]
                
            toplam = f_df['tutar'].sum()
            st.metric(label=f"Seçilen Dönem Toplam Ciro ({periyot})", value=f"{toplam:,.2f} ₺")
            
            # Grafik
            fig = px.bar(f_df, x='satici', y='tutar', color='departman', title="Satıcı Bazlı Dağılım Gözlemi")
            st.plotly_chart(fig, use_container_width=True)
            
            # Detay Tablosu
            st.dataframe(f_df[['tarih', 'satici', 'departman', 'tutar']].sort_values(by='tarih', ascending=False), use_container_width=True)
        else:
            st.info("Sistemde henüz kayıtlı veri bulunmuyor.")
            
    elif admin_sifre != "":
        # Şifre girildi ama yanlışsa uyarı ver
        st.error("Hatalı Şifre! İstatistikleri görme yetkiniz yoktur.")
