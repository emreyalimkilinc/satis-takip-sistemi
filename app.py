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

tab1, tab2 = st.tabs(["📝 Yeni Satış Girişi", "📊 Canlı Raporlar"])

# --- SEKME 1: VERİ GİRİŞİ (Satıcılar İçin) ---
with tab1:
    st.subheader("Günlük Satış Verisi Girişi")
    with st.form("satis_form", clear_on_submit=True):
        tarih = st.date_input("Satış Tarihi", datetime.now())
        
        # İstediğiniz hazır isim listesi buraya eklendi (Açılır Menü):
        satici = st.selectbox("Satıcı Adı Soyadı", [
            "Emre YALIMKILINÇ", 
            "Derya DEMİR", 
            "Sevim TEKİN", 
            "Nurdagül MENEKŞE", 
            "Betül Merve GÜNGÖR", 
            "Elif DEMİR", 
            "Onur VARAN", 
            "Özge KEL", 
            "Rabia ÇALHAN", 
            "Merve KARAASLAN", 
            "Bilge TURAN", 
            "Seda SOYDAN", 
            "Şennur ŞAHİN"
        ])
        
        # Departmanlar:
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

# --- SEKME 2: RAPORLAMA ---
with tab2:
    st.subheader("Tarih Bazlı Ciro ve Performans Analizi")
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM satislar", conn)
    conn.close()
    
    if not df.empty:
        df['tarih'] = pd.to_datetime(df['tarih'])
        df['Yıl'] = df['tarih'].dt.year
        df['Ay'] = df['tarih'].dt.strftime('%Y-%m')
        df['Gün'] = df['tarih'].dt.strftime('%Y-%m-%d')
        
        periyot = st.radio("Raporlama Dönemi Seçin:", ["Günlük", "Aylık", "Yıllık"], horizontal=True)
