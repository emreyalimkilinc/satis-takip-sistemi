import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px

# 1. VERİTABANI BAĞLANTISI (Eşzamanlı istekler için optimize edildi)
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

tab1, tab2 = st.tabs(["📝 Yeni Satış Girişi", "📊 Canlı Raporlar"])

# --- SEKME 1: VERİ GİRİŞİ (Satıcılar İçin) ---
with tab1:
    st.subheader("Günlük Satış Verisi Girişi")
    with st.form("satis_form", clear_on_submit=True):
        tarih = st.date_input("Satış Tarihi", datetime.now())
        satici = st.text_input("Satıcı Adı Soyadı")
        
        # İstediğiniz departmanlar buraya eklendi:
        dept = st.selectbox("Departman", ["Giriş kat", "Züccaciye", "Kasa", "Mobilya"])
        
        tutar = st.number_input("Satış Tutarı (₺)", min_value=0.0, step=50.0)
        submit = st.form_submit_button("Sisteme Kaydet")
        
        if submit:
            if satici.strip() != "" and tutar > 0:
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("INSERT INTO satislar (tarih, satici, departman, tutar) VALUES (?,?,?,?)",
                          (tarih.strftime('%Y-%m-%d'), satici.strip(), dept, tutar))
                conn.commit()
                conn.close()
                st.success(f"Başarılı: {satici} adlı çalışanın {tutar} ₺ değerindeki satışı sisteme işlendi.")
            else:
                st.error("Lütfen satıcı adını girin ve tutarın 0'dan büyük olduğundan emin olun.")

# --- SEKME 2: RAPORLAMA (Yönetici İçin Tarih Tarih Filtre) ---
with tab2:
    st.subheader("Tarih Bazlı Ciro ve Performans Analizi")
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM satislar", conn)
    conn.close()
    
    if not df.empty:
        # Tarih süzgeçlerini hazırlama
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
            
        # Büyük Gösterge Kartı
        toplam = f_df['tutar'].sum()
        st.metric(label=f"Seçilen Dönem Toplam Ciro ({periyot})", value=f"{toplam:,.2f} ₺")
        
        # İnteraktif Grafik
        fig = px.bar(f_df, x='satici', y='tutar', color='departman', title="Satıcı Bazlı Dağılım Gözlemi")
        st.plotly_chart(fig, use_container_width=True)
        
        # Detay Tablosu
        st.dataframe(f_df[['tarih', 'satici', 'departman', 'tutar']].sort_values(by='tarih', ascending=False), use_container_width=True)
    else:
        st.info("Sistemde henüz kayıtlı veri bulunmuyor. İlk satışı yan sekmeden ekleyebilirsiniz.")
