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

st.set_page_config(page_title="Canlı Satış Portalı", page_icon="📈", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>📱 Web Tabanlı Gelişmiş Satış Portalı</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📝 Yeni Satış Girişi", "🔒 Yönetici Paneli (Admin)"])

# --- SEKME 1: VERİ GİRİŞİ ---
with tab1:
    st.subheader("Günlük Satış Verisi Girişi")
    with st.form("satis_form", clear_on_submit=True):
        tarih = st.date_input("Satış Tarihi", datetime.now().date())
        satici = st.selectbox("Satıcı Adı Soyadı", PERSONEL_LISTESI)
        dept = st.selectbox("Departman", DEPARTMAN_LISTESI)
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
                st.success(f"Başarılı: {satici} - {dept} departmanı için {tutar:,.2f} ₺ satış kaydedildi.")
                st.rerun()
            else:
                st.error("Lütfen tutarın 0'dan büyük olduğundan emin olun.")

# --- SEKME 2: YÖNETİCİ PANELİ ---
with tab2:
    st.subheader("Yönetici Girişi")
    admin_sifre = st.text_input("Lütfen Admin Şifresini Giriniz:", type="password")
    
    if admin_sifre == "577339":
        st.success("Giriş Başarılı!")
        st.markdown("---")
        
        conn = get_db_connection()
        df = pd.read_sql_query("SELECT * FROM satislar", conn)
        c = conn.cursor()
        c.execute("SELECT hedef_tutar FROM hedefler WHERE tur='aylik_genel'")
        mevcut_hedef = c.fetchone()[0]
        conn.close()
        
        st.sidebar.markdown("### 🎯 Yönetici Hedef Ayarı")
        yeni_hedef = st.sidebar.number_input("Aylık Genel Ciro Hedefi (₺):", min_value=0.0, value=float(mevcut_hedef), step=10000.0)
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
            
            admin_modu = st.radio("İnceleme Türü Seçin:", [
                "📅 Tarih Aralıklı Genel Rapor", 
                "👤 Personel Bazlı Özel İnceleme", 
                "🏆 Liderlik Tablosu (Şampiyonlar)", 
                "🗑️ Satış Kaydı Düzenle / Sil"
            ], horizontal=True)
            st.markdown("---")
            
            # --- MOD 1: TARİH ARALIKLI GENEL RAPOR ---
            if admin_modu == "📅 Tarih Aralıklı Genel Rapor":
                st.markdown("### 📅 Tarih Aralığı Filtresi (Genel Şirket)")
                try:
                    min_date = df['tarih_formatli'].min().date()
                    max_date = df['tarih_formatli'].max().date()
                    varsayilan_baslangic = max_date - timedelta(days=7)
                    if varsayilan_baslangic < min_date:
                        varsayilan_baslangic = min_date
                except Exception:
                    min_date, max_date, varsayilan_baslangic = datetime.now().date(), datetime.now().date(), datetime.now().date()
                    
                tarih_secimi = st.date_input("Tarih Aralığı Seçin:", value=(varsayilan_baslangic, max_date), min_value=min_date, max_value=max_date, key="genel_t")
                
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
                    st.markdown(f"#### 🎯 Aylık Hedef İlerleme Durumu (Hedef: {mevcut_hedef:,.2f} ₺)")
                    yuzde = min(toplam_ciro / mevcut_hedef, 1.0)
                    st.progress(yuzde)
                    st.subheader(f"Seçilen Dönem Toplam Ciro: {toplam_ciro:,.2f} ₺ (%{yuzde*100:.1f})")
                    
                    try:
                        fig = px.bar(f_df, x='satici', y='tutar', color='departman', title="Seçilen Aralıktaki Satıcı Performansları")
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        st.info("Grafik yüklenirken geçici bir hata oluştu, verileriniz güvendedir.")
                    
                    st.markdown("#### 📋 Satış Listesi Detayları")
                    
                    try:
                        output = io.BytesIO()
                        excel_df = f_df[['tarih', 'satici', 'departman', 'tutar']].copy()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            excel_df.to_excel(writer, index=False, sheet_name='Satis_Raporu')
                        processed_data = output.getvalue()
                        
                        st.download_button(
                            label="📥 Seçili Raporu Excel Olarak İndir",
                            data=processed_data,
                            file_name=f"Satis_Raporu_{baslangic_tarihi}_to_{bitis_tarihi}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    except Exception:
                        pass
                    
                    try:
                        goster_df = f_df[['id', 'tarih', 'satici', 'departman', 'tutar']].copy()
                        goster_df['tarih'] = pd.to_datetime(goster_df['tarih']).dt.strftime('%d.%m.%Y')
                        goster_df.columns = ['Kayıt ID', 'Satış Tarihi', 'Satıcı Adı Soyadı', 'Departman', 'Tutar (₺)']
                        st.dataframe(goster_df.sort_values(by='Kayıt ID', ascending=False), use_container_width=True)
                    except Exception:
                        st.error("Tablo detayları hazırlanırken bir hata oluştu.")
                else:
                    st.warning("Seçilen tarih aralığında herhangi bir satış kaydı bulunamadı.")
            
            # --- MOD 2: PERSONEL BAZLI ÖZEL İNCELEME ---
            elif admin_modu == "👤 Personel Bazlı Özel İnceleme":
                st.markdown("### 👤 Personel Bazlı Tarih Aralıklı Gözlem")
                secilen_personel = st.selectbox("Kullanıcı Seçin:", ["Seçiniz..."] + PERSONEL_LISTESI, key="admin_personel_sec")
                
                if secilen_personel != "Seçiniz...":
                    ham_personel_df = df[df['satici'] == secilen_personel].copy()
                    
                    if not ham_personel_df.empty:
                        try:
                            p_min, p_max = ham_personel_df['tarih_formatli'].min().date(), ham_personel_df['tarih_formatli'].max().date()
                        except Exception:
                            p_min, p_max = datetime.now().date(), datetime.now().date()
                            
                        p_tarih = st.date_input(f"{secilen_personel} İçin Tarih Aralığı:", value=(p_min, p_max), min_value=p_min, max_value=p_max, key="p_t")
                        
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
                            kol1, kol2 = st.columns(2)
                            kol1.metric("💰 Seçilen Dönem Cirosu", f"{personel_df['tutar'].sum():,.2f} ₺")
                            kol2.metric("📦 Toplam Satış Adedi", f"{len(personel_df)} Adet")
                            
                            try:
                                fig_p = px.pie(personel_df, values='tutar', names='departman', title="Departman Dağılımı")
                                st.plotly_chart(fig_p, use_container_width=True)
                            except Exception:
                                pass
                            
                            try:
                                goster_p_df = personel_df[['id', 'tarih', 'departman', 'tutar']].copy()
                                goster_p_df['tarih'] = pd.to_datetime(goster_p_df['tarih']).dt.strftime('%d.%m.%Y')
                                goster_p_df.columns = ['Kayıt ID', 'Satış Tarihi', 'Departman', 'Tutar (₺)']
                                st.dataframe(goster_p_df.sort_values(by='Kayıt ID', ascending=False), use_container_width=True)
                            except Exception:
                                pass
                        else:
                            st.warning("Seçilen tarih aralığında veri bulunamadı.")
                    else:
                        st.info("Bu personele ait henüz kayıt yok.")

            # --- MOD 3: LİDERLİK TABLOSU ---
            elif admin_modu == "🏆 Liderlik Tablosu (Şampiyonlar)":
                st.markdown("### 🏆 En Çok Satış Yapanlar Sıralaması")
                try:
                    l_min, l_max = df['tarih_formatli'].min().date(), df['tarih_formatli'].max().date()
                except Exception:
                    l_min, l_max = datetime.now().date(), datetime.now().date()
                    
                l_tarih = st.date_input("Tarih Aralığı Seçin:", value=(l_min, l_max), key="l_t")
                
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
                    liderlik.columns = ['Personel Adı', 'Toplam Yaptığı Ciro (₺)']
                    
                    st.markdown("#### 🥇 TOP 3 ŞAMPİYON")
                    c1, c2, c3 = st.columns(3)
                    if len(liderlik) >= 1:
                        c1.success(f"**1. {liderlik.iloc[0]['Personel Adı']}** \n\n 💰 {liderlik.iloc[0]['Toplam Yaptığı Ciro (₺)']:,.2f} ₺")
                    if len(liderlik) >= 2:
                        c2.info(f"**2. {liderlik.iloc[1]['Personel Adı']}** \n\n 💰 {liderlik.iloc[1]['Toplam Yaptığı Ciro (₺)']:,.2f} ₺")
                    if len(liderlik) >= 3:
                        c3.warning(f"**3. {liderlik.iloc[2]['Personel Adı']}** \n\n 💰 {liderlik.iloc[2]['Toplam Yaptığı Ciro (₺)']:,.2f} ₺")
                    
                    st.markdown("---")
                    st.markdown("#### 📋 Tüm Personel Sıralama Listesi")
                    st.table(liderlik.style.format({'Toplam Yaptığı Ciro (₺)': '{:,.2f} ₺'}))
                else:
                    st.warning("Bu tarih aralığında veri bulunamadı.")

            # --- MOD 4: KAYIT SİLME ---
            elif admin_modu == "🗑️ Satış Kaydı Düzenle / Sil":
                st.markdown("### 🗑️ Hatalı Girilen Satış Kayıtlarını Temizleme")
                st.warning("Buradan sileceğiniz kayıtlar veritabanından kalıcı olarak kaldırılır.")
                
                try:
                    gosterilecek_df = df[['id', 'tarih', 'satici', 'departman', 'tutar']].copy()
                    gosterilecek_df['tarih'] = pd.to_datetime(gosterilecek_df['tarih']).dt.strftime('%d.%m.%Y')
                    gosterilecek_df.columns = ['Kayıt ID', 'Satış Tarihi', 'Satıcı Adı Soyadı', 'Departman', 'Tutar (₺)']
                    st.dataframe(gosterilecek_df.sort_values(by='Kayıt ID', ascending=False).head(50), use_container_width=True)
                except Exception:
                    pass
                
                with st.form("silme_formu"):
                    silinecek_id = st.number_input("Silmek İstediğiniz Satışın ID Numarasını Girin:", min_value=1, step=1)
                    silme_onayi = st.form_submit_button("🚨 SEÇİLİ KAYDI KALICI OLARAK SİL")
                    
                    if silme_onayi:
                        if int(silinecek_id) in df['id'].values:
                            conn = get_db_connection()
                            c = conn.cursor()
                            c.execute("DELETE FROM satislar WHERE id = ?", (int(silinecek_id),))
                            conn.commit()
                            conn.close()
                            st.success(f"ID: {silinecek_id} numaralı kayıt başarıyla silindi!")
                            st.rerun()
                        else:
                            st.error("Girdiğiniz ID numarasına ait bir satış kaydı bulunamadı!")
        else:
            st.info("Sistemde henüz kayıtlı veri bulunmuyor.")
            
    elif admin_sifre != "":
        st.error("Hatalı Şifre! İstatistikleri görme yetkiniz yoktur.")
