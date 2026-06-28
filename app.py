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
    # Hedefler Tablosu (Genel ve Departman Kotaları için)
    c.execute('''
        CREATE TABLE IF NOT EXISTS hedefler (
            tur TEXT PRIMARY KEY,
            hedef_tutar REAL
        )
    ''')
    # Varsayılan Kotalar
    c.execute("INSERT OR IGNORE INTO hedefler (tur, hedef_tutar) VALUES ('aylik_genel', 500000.0)")
    c.execute("INSERT OR IGNORE INTO hedefler (tur, hedef_tutar) VALUES ('Giriş kat', 150000.0)")
    c.execute("INSERT OR IGNORE INTO hedefler (tur, hedef_tutar) VALUES ('Züccaciye', 100000.0)")
    c.execute("INSERT OR IGNORE INTO hedefler (tur, hedef_tutar) VALUES ('Kasa', 50000.0)")
    c.execute("INSERT OR IGNORE INTO hedefler (tur, hedef_tutar) VALUES ('Mobilya', 200000.0)")
    conn.commit()
    conn.close()

init_db()

PERSONEL_LISTESI = [
    "Emre YALIMKILINÇ", "Derya DEMİR", "Sevim TEKİN", "Nurdagül MENEKŞE", 
    "Betül Merve GÜNGÖR", "Elif DEMİR", "Onur VARAN", "Özge KEL", 
    "Rabia ÇALHAN", "Merve KARAASLAN", "Bilge TURAN", "Seda SOYDAN", "Şennur ŞAHİN"
]
DEPARTMAN_LISTESI = ["Giriş kat", "Züccaciye", "Kasa", "Mobilya"]

# --- GLOBAL PREMIUM DARK MOD MOBİL CSS ---
st.set_page_config(page_title="Sales Portal", page_icon="📈", layout="centered")

st.markdown("""
    <style>
    /* Global Saf Karanlık Arka Plan */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #0F172A !important;
        color: #F1F5F9 !important;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Form Kartı Tasarımı */
    div[data-testid="stForm"], div.stAlert {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Yazı Renkleri */
    label, p, span, div[data-testid="stMarkdownContainer"] p, h1, h2, h3, h4 {
        color: #F1F5F9 !important;
        font-weight: 500 !important;
    }
    
    /* Girdiler ve Seçim Kutuları */
    div[data-baseweb="select"], div[data-baseweb="input"], input, div[data-baseweb="popover"] {
        background-color: #0F172A !important;
        color: #F1F5F9 !important;
        border: 1px solid #475569 !important;
        border-radius: 10px !important;
    }
    
    /* Form İçindeki Büyük Kaydet Butonları */
    div[data-testid="stForm"] div.stButton > button {
        width: 100% !important;
        height: 52px !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        border: none !important;
    }
    
    /* Mavi kaydet ve düzenle buton rengi */
    button[kind="primaryFormSubmit"] {
        background-color: #3B82F6 !important;
        color: white !important;
    }
    
    /* Üst Sağdaki Geçiş Butonlarının Mobil Uyumu */
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
    
    /* Excel İndirme Butonu Özelleştirme */
    div[data-testid="stDownloadButton"] button {
        width: 100% !important;
        height: 46px !important;
        border-radius: 10px !important;
        background-color: #10B981 !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
    }
    
    /* Streamlit Logolarını Gizle */
    #MainMenu, footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Admin Paneli Durum Kontrolü
if 'admin_modu_aktif' not in st.session_state:
    st.session_state.admin_modu_aktif = False

# --- ÜST BAŞLIK VE SAĞ BUTON ALANI ---
hdr_col1, hdr_col2 = st.columns([2, 1])

with hdr_col1:
    st.markdown("""
        <div style='text-align: left; padding: 5px 0px;'>
            <h1 style='color: #F8FAFC; font-size: 24px; font-weight: 700; letter-spacing: -0.5px; margin: 0;'>Sales Entry</h1>
            <p style='color: #94A3B8; font-size: 12px; margin: 2px 0 0 0;'>Hızlı Veri Giriş Portalı</p>
        </div>
    """, unsafe_allow_html=True)

with hdr_col2:
    st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
    if not st.session_state.admin_modu_aktif:
        if st.button("🔒 Admin"):
            st.session_state.admin_modu_aktif = True
            st.rerun()
    else:
        if st.button("📝 Form"):
            st.session_state.admin_modu_aktif = False
            st.rerun()

st.markdown("---")

# --- GÖRÜNÜM 1: STANDART SATIŞ GİRİŞİ ---
if not st.session_state.admin_modu_aktif:
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

# --- GÖRÜNÜM 2: GİZLİ YÖNETİCİ PANELİ ---
else:
    st.markdown("### 🔒 Yönetici Kimlik Doğrulama")
    admin_sifre = st.text_input("Admin Şifresini Girin:", type="password", placeholder="•••••")
            
    if admin_sifre == "577339":
        st.success("Giriş Başarılı!")
        st.markdown("---")
        
        conn = get_db_connection()
        df = pd.read_sql_query("SELECT * FROM satislar", conn)
        c = conn.cursor()
        
        c.execute("SELECT hedef_tutar FROM hedefler WHERE tur='aylik_genel'")
        mevcut_hedef = c.fetchone()[0]
        
        kotalar = {}
        for d_name in DEPARTMAN_LISTESI:
            c.execute("SELECT hedef_tutar FROM hedefler WHERE tur=?", (d_name,))
            res = c.fetchone()
            kotalar[d_name] = res[0] if res else 0.0
        conn.close()
        
        # --- GENEL HEDEF PANELİ (Açılır Kutu Kaldırıldı, Pratikleştirildi) ---
        yeni_hedef = st.number_input("🎯 Aylık Genel Mağaza Hedefi (₺):", min_value=0.0, value=float(mevcut_hedef), step=10000.0)
        if yeni_hedef != mevcut_hedef:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("UPDATE hedefler SET hedef_tutar = ? WHERE tur='aylik_genel'", (yeni_hedef,))
            conn.commit()
            conn.close()
            st.success("Genel hedef güncellendi!")
            st.rerun()

        if not df.empty:
            try:
                df['tarih_formatli'] = pd.to_datetime(df['tarih'])
            except Exception:
                pass
            
            admin_modu = st.radio("İnceleme Türü:", ["📊 Genel Rapor", "👤 Personel", "🏆 Şampiyonlar", "⚙️ Düzenle/Sil"], horizontal=True)
            st.markdown("---")
            
            # --- MOD 1: GENEL RAPOR VE CANLI KOTA DÜZENLEME TABLOSU ---
            if admin_modu == "📊 Genel Rapor":
                try:
                    min_date = df['tarih_formatli'].min().date()
                    max_date = df['tarih_formatli'].max().date()
                    varsayilan_baslangic = max_date - timedelta(days=7)
                    if varsayilan_baslangic < min_date:
                        varsayilan_baslangic = min_date
                except Exception:
                    min_date, max_date, varsayilan_baslangic = datetime.now().date(), datetime.now().date(), datetime.now().date()
                    
                tarih_secimi = st.date_input("Filtre Aralığı:", value=(varsayilan_baslangic, max_date), min_value=min_date, max_value=max_date)
                
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
                    yuzde = min(toplam_ciro / mevcut_hedef, 1.0)
                    
                    st.markdown(f"""
                        <div style='background-color: #1E293B; border: 1px solid #334155; border-radius: 12px; padding: 15px; margin-bottom: 15px;'>
                            <p style='margin:0; color:#94A3B8; font-size:13px; font-weight:600;'>TOPLAM DÖNEM CİROSU</p>
                            <h2 style='margin:5px 0; color:#3B82F6; font-size:24px;'>{toplam_ciro:,.2f} ₺</h2>
                            <p style='margin:0; color:#10B981; font-size:12px;'>Genel Hedef İlerlemesi: %{yuzde*100:.1f} (Hedef: {mevcut_hedef:,.0f} ₺)</p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.progress(yuzde)
                    
                    # --- INTERAKTİF DÜZENLENEBİLİR KOTA TABLOSU ---
                    st.markdown("### 📝 Mağaza Kota Durumu")
                    st.info("💡 Kotaları değiştirmek için **'Yeni Kota (₺)'** sütunundaki rakamlara çift tıklayıp değiştirebilir, ardından alttaki mavi butona basabilirsiniz.")
                    
                    kota_duzenleme_listesi = []
                    for d_name in DEPARTMAN_LISTESI:
                        dept_satis_toplam = f_df[f_df['departman'] == d_name]['tutar'].sum()
                        dept_hedef = kotalar.get(d_name, 0.0)
                        kalan = dept_hedef - dept_satis_toplam
                        
                        basari_yuzde = (dept_satis_toplam / dept_hedef) * 100 if dept_hedef > 0 else 0.0
                        kalan_str = f"{kalan:,.2f} ₺" if kalan > 0 else "0.00 ₺ (Hedef Tamamlandı 🎉)"
                        
                        kota_duzenleme_listesi.append({
                            "Bölüm / Departman": d_name,
                            "Mevcut Ciro (₺)": round(dept_satis_toplam, 2),
                            "Yeni Kota (₺)": float(dept_hedef), # Düzenlenebilir kolon
                            "Hedefe Kalan Tutar": kalan_str,
                            "Başarı Oranı": f"% {basari_yuzde:.1f}"
                        })
                    
                    girdi_df = pd.DataFrame(kota_duzenleme_listesi)
                    
                    # Streamlit Data Editör Yapılandırması (Sadece Yeni Kota kolonu düzenlenebilir)
                    duzenlenmis_durum = st.data_editor(
                        girdi_df,
                        column_config={
                            "Bölüm / Departman": st.column_config.TextColumn(disabled=True),
                            "Mevcut Ciro (₺)": st.column_config.NumberColumn(format="%.2f ₺", disabled=True),
                            "Yeni Kota (₺)": st.column_config.NumberColumn(format="%.2f ₺", min_value=0.0, step=1000.0),
                            "Hedefe Kalan Tutar": st.column_config.TextColumn(disabled=True),
                            "Başarı Oranı": st.column_config.TextColumn(disabled=True)
                        },
                        disabled=["Bölüm / Departman", "Mevcut Ciro (₺)", "Hedefe Kalan Tutar", "Başarı Oranı"],
                        use_container_width=True,
                        key="kota_editor_anahtari"
                    )
                    
                    # Veritabanına Değişiklikleri Kaydetme Butonu
                    if st.button("💾 Kotaları Kaydet ve Güncelle", type="primary"):
                        conn = get_db_connection()
                        c = conn.cursor()
                        for index, row in duzenlenmis_durum.iterrows():
                            d_adi = row["Bölüm / Departman"]
                            guncel_kota_degeri = float(row["Yeni Kota (₺)"])
                            c.execute("UPDATE hedefler SET hedef_tutar = ? WHERE tur = ?", (guncel_kota_degeri, d_adi))
                        conn.commit()
                        conn.close()
                        st.success("Tüm mağaza alan kotaları başarıyla güncellendi!")
                        st.rerun()
                        
                    st.markdown("---")

                    try:
                        fig = px.bar(f_df, x='satici', y='tutar', color='departman', template="plotly_dark")
                        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=20, b=10))
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        pass
                    
                    try:
                        output = io.BytesIO()
                        excel_df = f_df[['tarih', 'satici', 'departman', 'tutar']].copy()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            excel_df.to_excel(writer, index=False, sheet_name='Satis_Raporu')
                        processed_data = output.getvalue()
                        
                        st.download_button(label="📥 Excel Raporu İndir", data=processed_data, file_name=f"Rapor_{baslangic_tarihi}_{bitis_tarihi}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    except Exception:
                        pass
                    
                    try:
                        goster_df = f_df[['id', 'tarih', 'satici', 'departman', 'tutar']].copy()
                        goster_df['tarih'] = pd.to_datetime(goster_df['tarih']).dt.strftime('%d.%m.%Y')
                        goster_df.columns = ['ID', 'Tarih', 'Satıcı', 'Departman', 'Tutar (₺)']
                        st.dataframe(goster_df.sort_values(by='ID', ascending=False), use_container_width=True)
                    except Exception:
                        st.error("Tablo yüklenemedi.")
                else:
                    st.warning("Veri bulunamadı.")
            
            # --- MOD 2: PERSONEL BAZLI İNCELEME ---
            elif admin_modu == "👤 Personel":
                secilen_personel = st.selectbox("Personel Seçin:", ["Seçiniz..."] + PERSONEL_LISTESI)
                if secilen_personel != "Seçiniz...":
                    ham_personel_df = df[df['satici'] == secilen_personel].copy()
                    if not ham_personel_df.empty:
                        try:
                            p_min, p_max = ham_personel_df['tarih_formatli'].min().date(), ham_personel_df['tarih_formatli'].max().date()
                        except Exception:
                            p_min, p_max = datetime.now().date(), datetime.now().date()
                            
                        p_tarih = st.date_input("Dönem Filtresi:", value=(p_min, p_max), min_value=p_min, max_value=p_max)
                        
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
                                <div style='background-color: #1E293B; border: 1px solid #475569; border-radius: 10px; padding: 12px; margin-bottom:15px;'>
                                    <p style='margin:0; color:#3B82F6;'><b>💰 Toplam Ciro:</b> {personel_df['tutar'].sum():,.2f} ₺</p>
                                    <p style='margin:5px 0 0 0; color:#3B82F6;'><b>📦 Satış Adedi:</b> {len(personel_df)} Adet</p>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            try:
                                fig_p = px.pie(personel_df, values='tutar', names='departman', template="plotly_dark")
                                fig_p.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=20, b=10))
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
                            st.warning("Kayıt yok.")

            # --- MOD 3: LİDERLİK TABLOSU ---
            elif admin_modu == "🏆 Şampiyonlar":
                try:
                    l_min, l_max = df['tarih_formatli'].min().date(), df['tarih_formatli'].max().date()
                except Exception:
                    l_min, l_max = datetime.now().date(), datetime.now().date()
                    
                l_tarih = st.date_input("Sıralama Aralığı:", value=(l_min, l_max))
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
                    st.dataframe(liderlik, use_container_width=True)

            # --- MOD 4: DOĞRUDAN SATIR GÜNCELLEME VE SİLME PANELİ ---
            elif admin_modu == "⚙️ Düzenle/Sil":
                st.markdown("### ⚙️ Canlı Satır Güncelleme ve Silme")
                
                try:
                    gosterilecek_df = df[['id', 'tarih', 'satici', 'departman', 'tutar']].copy()
                    gosterilecek_df['tarih'] = pd.to_datetime(gosterilecek_df['tarih']).dt.strftime('%d.%m.%Y')
                    gosterilecek_df.columns = ['ID', 'Tarih', 'Satıcı', 'Departman', 'Tutar (₺)']
                    st.dataframe(gosterilecek_df.sort_values(by='ID', ascending=False).head(15), use_container_width=True)
                except Exception:
                    pass
                
                st.markdown("---")
                islem_tipi = st.radio("İşlem Seçin:", ["✏️ Satırı Seç ve Güncelle", "🚨 Satırı Sil"], horizontal=True)
                
                if islem_tipi == "✏️ Satırı Seç ve Güncelle":
                    mevcut_id_listesi = sorted(df['id'].tolist(), reverse=True)
                    if mevcut_id_listesi:
                        edit_id = st.selectbox("Düzenlenecek Satışın ID Numarasını Seçin:", mevcut_id_listesi)
                        secilen_satir = df[df['id'] == edit_id].iloc[0]
                        eski_tarih = datetime.strptime(secilen_satir['tarih'], '%Y-%m-%d').date()
                        
                        try: s_idx = PERSONEL_LISTESI.index(secilen_satir['satici'])
                        except: s_idx = 0
                        try: d_idx = DEPARTMAN_LISTESI.index(secilen_satir['departman'])
                        except: d_idx = 0
                        
                        st.markdown(f"<p style='color:#3B82F6; font-size:13px; font-weight:bold;'>💡 ID {edit_id} için güncelleme formu aşağıda açıldı:</p>", unsafe_allow_html=True)
                        
                        with st.form("canli_duzenleme_formu"):
                            yeni_tarih = st.date_input("Tarih Değiştir", eski_tarih)
                            yeni_satici = st.selectbox("Satıcı Değiştir", PERSONEL_LISTESI, index=s_idx)
                            yeni_dept = st.selectbox("Departman Değiştir", DEPARTMAN_LISTESI, index=d_idx)
                            yeni_tutar = st.number_input("Tutar Değiştir (₺)", min_value=0.0, value=float(secilen_satir['tutar']), step=50.0)
                            
                            edit_onayi = st.form_submit_button("🔁 DEĞİŞİKLİKLERİ SATIRA UYGULA (GÜNCELLE)")
                            
                            if edit_onayi:
                                if yeni_tutar > 0:
                                    conn = get_db_connection()
                                    c = conn.cursor()
                                    c.execute("""
                                        UPDATE satislar 
                                        SET tarih = ?, satici = ?, departman = ?, tutar = ? 
                                        WHERE id = ?
                                    """, (yeni_tarih.strftime('%Y-%m-%d'), yeni_satici, yeni_dept, yeni_tutar, int(edit_id)))
                                    conn.commit()
                                    conn.close()
                                    st.success(f"Başarılı: ID {edit_id} güncellendi!")
                                    st.rerun()
                                else:
                                    st.error("Tutar 0'dan büyük olmalıdır.")
                    else:
                        st.info("Düzenlenecek kayıt yok.")
                                
                elif islem_tipi == "🚨 Satırı Sil":
                    mevcut_id_listesi_sil = sorted(df['id'].tolist(), reverse=True)
                    if mevcut_id_listesi_sil:
                        with st.form("silme_formu"):
                            silinecek_id = st.selectbox("Silinecek Satış ID Seçin:", mevcut_id_listesi_sil)
                            silme_onayi = st.form_submit_button("🚨 SEÇİLİ SATIRI TAMAMEN SİL")
                            
                            if silme_onayi:
                                conn = get_db_connection()
                                c = conn.cursor()
                                c.execute("DELETE FROM satislar WHERE id = ?", (int(silinecek_id),))
                                conn.commit()
                                conn.close()
                                st.success(f"ID: {silinecek_id} kalıcı olarak silindi.")
                                st.rerun()
                    else:
                        st.info("Silinecek kayıt yok.")
        else:
            st.info("Henüz veri yok.")
    elif admin_sifre != "":
        st.error("Hatalı Şifre!")
