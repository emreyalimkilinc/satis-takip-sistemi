import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

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
    conn.commit()
    conn.close()

init_db()

PERSONEL_LISTESI = [
    "Emre YALIMKILINÇ", "Derya DEMİR", "Sevim TEKİN", "Nurdagül MENEKŞE", 
    "Betül Merve GÜNGÖR", "Elif DEMİR", "Onur VARAN", "Özge KEL", 
    "Rabia ÇALHAN", "Merve KARAASLAN", "Bilge TURAN", "Seda SOYDAN", "Şennur ŞAHİN"
]
DEPARTMAN_LISTESI = ["Giriş kat", "Züccaciye", "Kasa", "Mobilya"]

# --- GLOBAL DARK MOD MOBİL TASARIM AYARLARI (CSS) ---
st.set_page_config(page_title="Sales Portal", page_icon="📈", layout="centered")

st.markdown("""
    <style>
    /* Global Saf Karanlık Arka Plan */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #0F172A !important;
        color: #F1F5F9 !important;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Form Alanını Şık Bir Gece Mavisi Karta Dönüştürme */
    div[data-testid="stForm"] {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Yazı Etiketlerini Beyaz Yapma */
    label, p, div[data-testid="stMarkdownContainer"] p {
        color: #F1F5F9 !important;
        font-weight: 500 !important;
    }
    
    /* Seçim Kutuları ve Girdilerin Dark Mod Uyumu */
    div[data-baseweb="select"], div[data-baseweb="input"], input {
        background-color: #0F172A !important;
        color: #F1F5F9 !important;
        border: 1px solid #475569 !important;
        border-radius: 10px !important;
    }
    
    /* Odaklanmış Input Alanı Sınırı */
    div[data-baseweb="select"]:focus-within, div[data-baseweb="input"]:focus-within {
        border-color: #3B82F6 !important;
    }
    
    /* Global Minimalist Dokunmatik Buton */
    div.stButton > button {
        width: 100% !important;
        height: 52px !important;
        border-radius: 12px !important;
        background: #3B82F6 !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        border: none !important;
        margin-top: 10px !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:active {
        background: #2563EB !important;
        transform: scale(0.98) !important;
    }
    
    /* Streamlit Alt Bilgilerini Gizleme */
    #MainMenu, footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Başlık - Premium Global Minimal Tasarım
st.markdown("""
    <div style='text-align: center; padding: 20px 0px 10px 0px;'>
        <h1 style='color: #F8FAFC; font-size: 26px; font-weight: 700; letter-spacing: -0.5px; margin-bottom: 2px;'>Sales Entry</h1>
        <p style='color: #94A3B8; font-size: 13px;'>Hızlı Satış Veri Giriş Portalı</p>
    </div>
""", unsafe_allow_html=True)

# --- TEK VE SADE VERİ GİRİŞ FORMU ---
with st.form("satis_form", clear_on_submit=True):
    tarih = st.date_input("Satış Tarihi", datetime.now().date())
    satici = st.selectbox("Satıcı Adı Soyadı", PERSONEL_LISTESI)
    dept = st.selectbox("Departman", DEPARTMAN_LISTESI)
    tutar = st.number_input("Satış Tutarı (₺)", min_value=0.0, step=50.0, value=0.0)
    
    submit = st.form_submit_button("KAYDET")
    
    if submit:
        if tutar > 0:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("INSERT INTO satislar (tarih, satici, departman, tutar) VALUES (?,?,?,?)",
                      (tarih.strftime('%Y-%m-%d'), satici, dept, tutar))
            conn.commit()
            conn.close()
            st.success(f"Kayıt Başarılı: {satici} ({tutar:,.2f} ₺)")
        else:
            st.error("Lütfen geçerli bir tutar girin.")
