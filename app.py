import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

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
            tutar INTEGER
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS hedefler (
            tur TEXT PRIMARY KEY,
            hedef_tutar INTEGER
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS kullanicilar (
            kod TEXT PRIMARY KEY,
            isim TEXT,
            sifre TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS admin_hesap (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sifre TEXT
        )
    ''')
    c.execute("INSERT OR IGNORE INTO admin_hesap (id, sifre) VALUES (1, '577339')")

    for kod, p_isim in PERSONEL_KODLARI.items():
        c.execute("INSERT OR IGNORE INTO hedefler (tur, hedef_tutar) VALUES (?, 1500000)", (p_isim,))
        c.execute("INSERT OR IGNORE INTO kullanicilar (kod, isim, sifre) VALUES (?, ?, '123456')", (kod, p_isim))
    conn.commit()
    conn.close()

# SABİT PERSONEL LİSTESİ
PERSONEL_KODLARI = {
    "2646": "Emre YALIMKILINÇ", "1303": "Derya DEMİR", "3253": "Onur VARAN",
    "3267": "Sevim TEKİN", "2079": "Seda SOYDAN", "3111": "Betül Merve GÜNGÖR",
    "3313": "Merve KARAASLAN", "2497": "Rabia ÇALHAN", "3310": "Nurdagül MENEKŞE",
    "2993": "Elif DEMİR", "3123": "Özge KEL", "3271": "Bilge TURAN",
    "2288": "Fatih", "3103": "Şennur ŞAHİN"
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
        padding: 16px !important;
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
        height: 45px !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
    }
    button[kind="primaryFormSubmit"] {
        background-color: #3B82F6 !important;
        color: white !important;
    }
    
    /* PREMIUM KARTLAR */
    .dashboard-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        box-shadow: 0 4px 20px 0 rgba(0,0,0,0.2);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        text-align: center;
    }
    .dashboard-card h3 { margin: 0; font-size: 14px; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px; }
    .dashboard-card h2 { margin: 10px 0 5px 0; font-size: 28px; font-weight: 800; color: #10B981; }
    .dashboard-card p { margin: 0; font-size: 13px; color: #3B82F6; }

    .modern-card {
        background: #1E293B;
        border-left: 5px solid #10B981;
        border-top: 1px solid #334155;
        border-right: 1px solid #334155;
        border-bottom: 1px solid #334155;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 0px;
        height: 100%;
    }
    .modern-card.iade { border-left: 5px solid #EF4444; }
    .card-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
    .card-title { font-size: 14px; font-weight: bold; color: #F8FAFC; }
    .card-date { font-size: 11px; color: #94A3B8; }
    .card-dept { font-size: 12px; color: #cbd5e1; }
    .card-price { font-size: 14px; font-weight: 700; color: #10B981; }
    .modern-card.iade .card-price { color: #EF4444; }
    
    #MainMenu, footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

init_db()

# --- OTURUM DURUMU KONTROLLERİ ---
if 'admin_modu_aktif' not in st.session_state: st.session_state.admin_modu_aktif = False
if 'admin_sifre_dogrulandi' not in st.session_state: st.session_state.admin_sifre_dogrulandi = False
if 'user_oturum_aktif' not in st.session_state: st.session_state.user_oturum_aktif = False
if 'aktif_satici_adi' not in st.session_state: st.session_state.aktif_satici_adi = None
if 'aktif_satici_kodu' not in st.session_state: st.session_state.aktif_satici_kodu = None

# Canlı Düzenleme Durum Yönetimi
if 'duzenleme_id' not in st.session_state: st.session_state.duzenleme_id = None
if 'silme_id' not in st.session_state: st.session_state.silme_id = None

# --- ÜST BAŞLIK ALANI ---
hdr_col1, hdr_col2 = st.columns([2, 1])
with hdr_col1:
    st.markdown(f"""
        <div style='text-align: left; padding: 5px 0px;'>
            <h1 style='color: #F8FAFC; font-size: 22px; font-weight: 700; margin: 0;'>Sales Portal</h1>
            <p style='color: #94A3B8; font-size: 12px; margin: 2px 0 0 0;'>
                {f"Aktif: {st.session_state.aktif_satici_adi}" if st.session_state.user_oturum_aktif else "Lütfen Giriş Yapın"}
            </p>
        </div>
    """, unsafe_allow_html=True)

with hdr_col2:
    st.markdown("<div style='margin-top: 4px;'></div>", unsafe_allow_html=True)
    if not st.session_state.admin_modu_aktif:
        if st.button("🔒 Admin"):
            st.session_state.admin_modu_aktif = True
            st.rerun()
    else:
        if st.button("📝 Satış"):
            st.session_state.admin_modu_aktif = False
            st.rerun()

st.markdown("---")

# --- GÖRÜNÜM 1: KULLANICI MODU ---
if not st.session_state.admin_modu_aktif:
    if not st.session_state.user_oturum_aktif:
        st.markdown("### 🔑 Personel Girişi")
        with st.form("personel_giris_formu"):
            girilen_kod = st.text_input("Personel Kodunuz:", type="password")
            girilen_sifre = st.text_input("Şifre:", type="password")
            if st.form_submit_button("GİRİŞ YAP"):
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("SELECT isim, sifre FROM kullanicilar WHERE kod = ?", (girilen_kod,))
                user_data = c.fetchone()
                conn.close()
                if user_data and girilen_sifre == user_data[1]:
                    st.session_state.user_oturum_aktif = True
                    st.session_state.aktif_satici_adi = user_data[0]
                    st.session_state.aktif_satici_kodu = girilen_kod
                    st.rerun()
                else:
                    st.error("Hatalı Kod veya Şifre!")
    else:
        if st.button("🚪 Oturumu Kapat"):
            st.session_state.user_oturum_aktif = False
            st.session_state.aktif_satici_adi = None
            st.session_state.aktif_satici_kodu = None
            st.rerun()
        
        # Bireysel Kota İlerlemesi
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT SUM(tutar) FROM satislar WHERE satici = ?", (st.session_state.aktif_satici_adi,))
        user_toplam_ciro = c.fetchone()[0] or 0
        c.execute("SELECT hedef_tutar FROM hedefler WHERE tur = ?", (st.session_state.aktif_satici_adi,))
        user_kota = c.fetchone()[0] or 1500000
        conn.close()
        
        kalan_kota = user_kota - user_toplam_ciro
        user_yuzde = min(max(user_toplam_ciro / user_kota, 0.0), 1.0)
        
        st.markdown(f"""
            <div class="dashboard-card">
                <h3>🎯 Güncel Kota Durumunuz</h3>
                <h2>{user_toplam_ciro:,} TL / {user_kota:,} TL</h2>
                <p>{f"Kalan Kota: <b>{kalan_kota:,} TL</b>" if kalan_kota > 0 else "🎉 Tebrikler, Kota Tamamlandı!"}</p>
            </div>
        """, unsafe_allow_html=True)
        st.progress(user_yuzde)

        # SATIŞ FORMU
        with st.form("satis_form", clear_on_submit=True):
            tarih = st.date_input("Satış Tarihi", datetime.now().date())
            dept = st.selectbox("Departman", DEPARTMAN_LISTESI)
            tutar_input = st.text_input("Tutar Girişi (TL) [İptaller için başına eksi (-) koyun]", value="", placeholder="Örn: 233455")
            
            temiz_tutar = 0
            is_negative = False
            
            if tutar_input:
                ham_input = tutar_input.strip()
                if ham_input.startswith("-"):
                    is_negative = True
                    ham_input = ham_input[1:]
                temiz_karakterler = ham_input.replace(".", "").replace(",", "").replace(" ", "")
                
                if temiz_karakterler.isdigit():
                    temiz_tutar = int(temiz_karakterler)
                    if is_negative: temiz_tutar = -temiz_tutar
                    renk = "#EF4444" if is_negative else "#10B981"
                    etiket = "İptal/İade" if is_negative else "Satış"
                    st.markdown(f"<h3 style='color: {renk}; margin: 5px 0;'>💰 Teyit ({etiket}): {temiz_tutar:,} TL</h3>", unsafe_allow_html=True)
                else:
                    st.error("⚠️ Lütfen sadece geçerli sayısal rakamlar giriniz!")

            if st.form_submit_button("KAYDET"):
                if temiz_tutar != 0:
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute("INSERT INTO satislar (tarih, satici, departman, tutar) VALUES (?,?,?,?)",
                              (tarih.strftime('%Y-%m-%d'), st.session_state.aktif_satici_adi, dept, temiz_tutar))
                    conn.commit()
                    conn.close()
                    st.success("Başarıyla Kaydedildi!")
                    st.rerun()

        # Personel Şifre Değiştirme
        st.markdown("---")
        with st.expander("🔐 Şifremi Değiştir"):
            with st.form("sifre_degis_form", clear_on_submit=True):
                p_eski = st.text_input("Mevcut Şifre:", type="password")
                p_yeni = st.text_input("Yeni Şifre:", type="password")
                p_yeni_onay = st.text_input("Yeni Şifre (Tekrar):", type="password")
                if st.form_submit_button("ŞİFREMİ GÜNCELLE"):
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute("SELECT sifre FROM kullanicilar WHERE kod = ?", (st.session_state.aktif_satici_kodu,))
                    mevcut_db_sifre = c.fetchone()[0]
                    if p_eski != mevcut_db_sifre: st.error("Mevcut şifreniz hatalı.")
                    elif p_yeni != p_yeni_onay: st.error("Yeni şifreler birbiriyle uyuşmuyor.")
                    elif len(p_yeni) < 4: st.error("Yeni şifre en az 4 karakter olmalıdır.")
                    else:
                        c.execute("UPDATE kullanicilar SET sifre = ? WHERE kod = ?", (p_yeni, st.session_state.aktif_satici_kodu))
                        conn.commit()
                        st.success("Şifreniz başarıyla güncellendi!")
                    conn.close()

        # Grafik ve Geçmiş Veriler
        conn = get_db_connection()
        df_personel = pd.read_sql_query("SELECT * FROM satislar WHERE satici = ?", conn, params=(st.session_state.aktif_satici_adi,))
        conn.close()
        
        st.markdown("#### 📊 Günlük Satış Performansı")
        if not df_personel.empty:
            df_grafik = df_personel.groupby('tarih').agg({'tutar': 'sum'}).reset_index()
            df_grafik['tarih_dt'] = pd.to_datetime(df_grafik['tarih'])
            df_grafik = df_grafik.sort_values('tarih_dt')
            df_grafik['Tarih_Gosterim'] = df_grafik['tarih_dt'].dt.strftime('%d.%m')
            
            if not df_grafik.empty:
                fig_user = go.Figure()
                fig_user.add_trace(go.Bar(
                    x=df_grafik['Tarih_Gosterim'], y=df_grafik['tutar'],
                    marker=dict(
                        color=df_grafik['tutar'],
                        colorscale=['#1E293B', '#3B82F6', '#10B981'],
                        line=dict(color='#10B981', width=1)
                    ),
                    text=df_grafik['tutar'].map(lambda x: f"{x:,} TL"),
                    textposition='auto',
                    textfont=dict(color='#FFFFFF', size=11, weight='bold'),
                    hovertemplate='<b>Tarih:</b> %{x}<br><b>Net Ciro:</b> %{y:,} TL<extra></extra>'
                ))
                fig_user.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=10, r=10, t=10, b=10), showlegend=False,
                    xaxis=dict(type='category', showgrid=False, tickfont=dict(color='#94A3B8', size=12)),
                    yaxis=dict(showgrid=True, gridcolor='#334155', tickfont=dict(color='#94A3B8'))
                )
                st.plotly_chart(fig_user, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True})
            else:
                st.info("📉 Grafiği çizmek için yeterli veri bulunamadı.")
        else:
            st.info("✨ Henüz herhangi bir satış kaydınız bulunmamaktadır.")

        if not df_personel.empty:
            st.markdown("#### 📋 Son İşlemleriniz")
            df_personel = df_personel.sort_values(by='id', ascending=False)
            for _, row in df_personel.iterrows():
                is_iade = "iade" if row['tutar'] < 0 else ""
                t_str = datetime.strptime(row['tarih'], '%Y-%m-%d').strftime('%d.%m.%Y')
                st.markdown(f"""
                    <div class="modern-card {is_iade}">
                        <div class="card-row"><span class="card-title">{row['departman']}</span><span class="card-date">{t_str}</span></div>
                        <div class="card-row" style="margin-top:5px;"><span class="card-dept">İşlem</span><span class="card-price">{row['tutar']:,} TL</span></div>
                    </div>
                """, unsafe_allow_html=True)

# --- GÖRÜNÜM 2: YÖNETİCİ PANELİ ---
else:
    if not st.session_state.admin_sifre_dogrulandi:
        st.markdown("### 🔒 Yönetici Girişi")
        admin_kod_giris = st.text_input("Admin Şifresi:", type="password")
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT sifre FROM admin_hesap WHERE id=1")
        guncel_admin_sifre = c.fetchone()[0]
        conn.close()

        if admin_kod_giris == guncel_admin_sifre:
            st.session_state.admin_sifre_dogrulandi = True
            st.rerun()
            
    if st.session_state.admin_sifre_dogrulandi:
        conn = get_db_connection()
        df = pd.read_sql_query("SELECT * FROM satislar", conn)
        c = conn.cursor()
        kotalar = {p: (c.execute("SELECT hedef_tutar FROM hedefler WHERE tur=?", (p,)).fetchone() or [1500000])[0] for p in PERSONEL_KODLARI.values()}
        conn.close()

        admin_modu = st.selectbox("⚙️ İşlem Menüsü Seçin:", ["📊 Genel Rapor & Kotalar", "👤 Personel Detay", "🏆 Şampiyonlar Ligi", "🔑 Şifre Yönetimi"])
        st.markdown("---")
        
        if not df.empty:
            df['tarih_dt'] = pd.to_datetime(df['tarih'])
            min_date = df['tarih_dt'].min().date()
            max_date = df['tarih_dt'].max().date()
        else:
            min_date = datetime.now().date() - timedelta(days=30)
            max_date = datetime.now().date()

        if admin_modu == "📊 Genel Rapor & Kotalar":
            
            # --- CANLI SİLME ONAYI ---
            if st.session_state.silme_id:
                st.warning(f"🚨 ID: {st.session_state.silme_id} numaralı satışı tamamen silmek istediğinize emin misiniz?")
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    if st.button("🗑️ EVET, KESİNLİKLE SİL"):
                        conn = get_db_connection()
                        conn.cursor().execute("DELETE FROM satislar WHERE id = ?", (st.session_state.silme_id,))
                        conn.commit()
                        conn.close()
                        st.session_state.silme_id = None
                        st.success("İşlem Başarıyla Silindi!")
                        st.rerun()
                with col_s2:
                    if st.button("❌ İPTAL"):
                        st.session_state.silme_id = None
                        st.rerun()
                st.markdown("---")

            st.markdown("#### 📅 Rapor Dönemi Seçimi")
            tarih_secimi = st.date_input("Dönem Aralığı:", value=(min_date, max_date), min_value=min_date, max_value=max_date)
            
            if isinstance(tarih_secimi, tuple) and len(tarih_secimi) == 2:
                b_tarih, bit_tarih = tarih_secimi
            else:
                b_tarih = tarih_secimi if not isinstance(tarih_secimi, (tuple, list)) else tarih_secimi[0]
                bit_tarih = b_tarih

            if not df.empty:
                f_df = df[(df['tarih_dt'].dt.date >= b_tarih) & (df['tarih_dt'].dt.date <= bit_tarih)].copy()
            else:
                f_df = pd.DataFrame()

            toplam_ciro = f_df['tutar'].sum() if not f_df.empty else 0
            
            st.markdown(f"""
                <div class="dashboard-card" style="background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%); border-color: #3B82F6;">
                    <h3 style="color: #93C5FD;">🏢 Mağaza Seçili Dönem Toplam Net Ciro</h3>
                    <h2 style="color: #38BDF8;">{toplam_ciro:,} TL</h2>
                </div>
            """, unsafe_allow_html=True)
            
            if not f_df.empty:
                st.markdown("#### 📊 Mağaza Günlük Ciro Dağılımı")
                df_magaza_grafik = f_df.groupby('tarih').agg({'tutar': 'sum'}).reset_index()
                df_magaza_grafik['tarih_dt'] = pd.to_datetime(df_magaza_grafik['tarih'])
                df_magaza_grafik = df_magaza_grafik.sort_values('tarih_dt')
                df_magaza_grafik['Tarih_Gosterim'] = df_magaza_grafik['tarih_dt'].dt.strftime('%d.%m')
                
                fig_store = go.Figure()
                fig_store.add_trace(go.Bar(
                    x=df_magaza_grafik['Tarih_Gosterim'], y=df_magaza_grafik['tutar'],
                    marker=dict(color='#3B82F6', line=dict(color='#38BDF8', width=1)),
                    text=df_magaza_grafik['tutar'].map(lambda x: f"{x:,} TL"),
                    textposition='auto',
                    textfont=dict(color='#FFFFFF', size=11, weight='bold'),
                    hovertemplate='<b>Tarih:</b> %{x}<br><b>Toplam:</b> %{y:,} TL<extra></extra>'
                ))
                fig_store.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=10, r=10, t=10, b=10), showlegend=False,
                    xaxis=dict(type='category', showgrid=False, tickfont=dict(color='#94A3B8', size=12)),
                    yaxis=dict(showgrid=True, gridcolor='#334155', tickfont=dict(color='#94A3B8'))
                )
                st.plotly_chart(fig_store, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True})

            # --- DÖNEM İÇİ TÜM PERSONEL SATIŞLARI (SAĞ KÖŞE BUTONLU SÜTUN DÜZENİ) ---
            st.markdown("### 📋 Dönem İçi Tüm Personel Satışları")
            if not f_df.empty:
                f_df_sorted = f_df.sort_values(by='id', ascending=False)
                for _, row in f_df_sorted.iterrows():
                    is_iade = "iade" if row['tutar'] < 0 else ""
                    t_str = datetime.strptime(row['tarih'], '%Y-%m-%d').strftime('%d.%m.%Y')
                    
                    # Bilgiler sola kaydırıldı ([5, 1, 1] Oranıyla butonlar en sağ köşeye sıkıştırıldı)
                    col_info, col_btn1, col_btn2 = st.columns([5, 1, 1])
                    
                    with col_info:
                        st.markdown(f"""
                            <div class="modern-card {is_iade}">
                                <div class="card-row"><span class="card-title">👤 {row['satici']}</span><span class="card-date">{t_str}</span></div>
                                <div class="card-row" style="margin-top:5px;"><span class="card-dept">{row['departman']} (ID: {row['id']})</span><span class="card-price">{row['tutar']:,} TL</span></div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col_btn1:
                        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                        if st.button(f"✏️ Düzenle", key=f"edit_{row['id']}", use_container_width=True):
                            st.session_state.duzenleme_id = row['id']
                            st.session_state.silme_id = None
                            st.rerun()
                            
                    with col_btn2:
                        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                        if st.button(f"🗑️ Sil", key=f"delete_{row['id']}", use_container_width=True):
                            st.session_state.silme_id = row['id']
                            st.session_state.duzenleme_id = None
                            st.rerun()

                    # --- DÜZENLE DENİLDİĞİNDE HEMEN ALTA DİNAMİK SEKME (FORM) AÇILIR ---
                    if st.session_state.duzenleme_id == row['id']:
                        with st.form(f"hizli_duzenleme_form_{row['id']}"):
                            st.markdown(f"**⚙️ Satış Kaydını Düzenle (ID: {row['id']})**")
                            
                            # Sadece Personel ve Satış Rakamı değiştirilebilir
                            p_isimler = list(PERSONEL_KODLARI.values())
                            yeni_satici = st.selectbox("Personel Seçin", p_isimler, index=p_isimler.index(row['satici']))
                            yeni_tutar_input = st.text_input("Satış Rakamı (TL)", value=str(row['tutar']))
                            
                            c1, c2 = st.columns(2)
                            with c1:
                                if st.form_submit_button("💾 Güncelle"):
                                    clean_val = yeni_tutar_input.strip().replace(".", "").replace(",", "").replace(" ", "")
                                    is_neg = yeni_tutar_input.strip().startswith("-")
                                    if is_neg: clean_val = clean_val.replace("-", "")
                                    
                                    if clean_val.isdigit():
                                        final_val = -int(clean_val) if is_neg else int(clean_val)
                                        conn = get_db_connection()
                                        conn.cursor().execute("UPDATE satislar SET satici=?, tutar=? WHERE id=?", 
                                                  (yeni_satici, final_val, row['id']))
                                        conn.commit()
                                        conn.close()
                                        st.session_state.duzenleme_id = None
                                        st.success("Başarıyla Güncellendi!")
                                        st.rerun()
                            with c2:
                                if st.form_submit_button("❌ Vazgeç"):
                                    st.session_state.duzenleme_id = None
                                    st.rerun()
                            
                    st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)
            else:
                st.info("Seçilen tarih aralığında kaydedilmiş herhangi bir satış bulunamadı.")

            st.markdown("---")
            st.markdown("### 🎯 Bireysel Kota Düzenleme")
            kota_list = [{"Personel": p, "Kota (TL)": int(kotalar[p])} for p in PERSONEL_KODLARI.values()]
            duzenlenmis = st.data_editor(pd.DataFrame(kota_list), use_container_width=True, disabled=["Personel"])
            
            if st.button("💾 Kotaları Kaydet", type="primary"):
                conn = get_db_connection()
                c = conn.cursor()
                for _, row in duzenlenmis.iterrows():
                    c.execute("UPDATE hedefler SET hedef_tutar = ? WHERE tur = ?", (int(row["Kota (TL)"]), row["Personel"]))
                conn.commit()
                conn.close()
                st.success("Güncellendi!")
                st.rerun()

        elif admin_modu == "👤 Personel Detay":
            secilen = st.selectbox("Personel Seçin:", list(PERSONEL_KODLARI.values()))
            p_df = df[df['satici'] == secilen].sort_values('id', ascending=False)
            
            st.markdown(f"""
                <div class="dashboard-card">
                    <h3>👤 {secilen} Toplam Cirosu</h3>
                    <h2>{p_df['tutar'].sum():,} TL</h2>
                </div>
            """, unsafe_allow_html=True)
            
            for _, row in p_df.iterrows():
                is_iade = "iade" if row['tutar'] < 0 else ""
                st.markdown(f"""
                    <div class="modern-card {is_iade}">
                        <div class="card-row"><span class="card-title">{row['departman']}</span><span class="card-date">{row['tarih']}</span></div>
                        <div class="card-row" style="margin-top:5px;"><span class="card-dept">Tutar</span><span class="card-price">{row['tutar']:,} TL</span></div>
                    </div>
                """, unsafe_allow_html=True)

        elif admin_modu == "🏆 Şampiyonlar Ligi":
            if not df.empty:
                st.markdown("#### 📊 Personel Başarı Sıralaması")
                liderlik = df.groupby('satici')['tutar'].sum().reset_index().sort_values(by='tutar', ascending=False).reset_index(drop=True)
                
                fig_bar = px.bar(
                    liderlik, x='tutar', y='satici',
                    orientation='h', text_auto=',.0f',
                    template='plotly_dark',
                    color='tutar',
                    color_continuous_scale=['#1E293B', '#3B82F6', '#10B981']
                )
                fig_bar.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=10, r=10, t=10, b=10), coloraxis_showscale=False,
                    xaxis=dict(showgrid=False, visible=False),
                    yaxis=dict(autorange="reversed", tickfont=dict(color='#F1F5F9', size=12))
                )
                fig_bar.update_traces(textposition='outside', textfont=dict(color='#F1F5F9', weight='bold'))
                st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True})
                st.markdown("---")

                for idx, row in liderlik.iterrows():
                    st.markdown(f"""
                        <div class="modern-card">
                            <div class="card-row"><span class="card-title">🏆 {idx+1}. {row['satici']}</span><span class="card-price">{row['tutar']:,} TL</span></div>
                        </div>
                    """, unsafe_allow_html=True)

        elif admin_modu == "🔑 Şifre Yönetimi":
            st.markdown("### 👤 Personel Şifre Listesi")
            conn = get_db_connection()
            df_k = pd.read_sql_query("SELECT kod as 'Kod', isim as 'Personel', sifre as 'Şifre' FROM kullanicilar", conn)
            conn.close()
            st.data_editor(df_k, use_container_width=True, disabled=["Kod", "Personel", "Şifre"])
            
            st.markdown("---")
            st.markdown("### 🔒 Yönetici Şifresini Değiştir")
            with st.form("admin_sifre_form", clear_on_submit=True):
                a_eski = st.text_input("Mevcut Admin Şifresi:", type="password")
                a_yeni = st.text_input("Yeni Admin Şifresi:", type="password")
                a_yeni_onay = st.text_input("Yeni Admin Şifresi (Tekrar):", type="password")
                if st.form_submit_button("ADMİN ŞİFRESİNİ GÜNCELLE"):
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute("SELECT sifre FROM admin_hesap WHERE id=1")
                    m_sif = c.fetchone()[0]
                    if a_eski != m_sif: st.error("Mevcut admin şifresi hatalı.")
                    elif a_yeni != a_yeni_onay: st.error("Şifreler uyuşmuyor.")
                    elif len(a_yeni) < 4: st.error("Yeni şifre en az 4 karakter olmalıdır.")
                    else:
                        c.execute("UPDATE admin_hesap SET sifre=? WHERE id=1", (a_yeni,))
                        conn.commit()
                        st.success("Yönetici şifresi başarıyla güncellendi!")
                    conn.close()
