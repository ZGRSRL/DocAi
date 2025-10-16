"""
SAP ME/MII Folder Analyzer - Streamlit Web UI (Basit Versiyon)

Kullanım:
    streamlit run streamlit_app_simple.py
"""
import streamlit as st
import subprocess
import json
from pathlib import Path
import sys
import os

# Sayfa yapılandırması
st.set_page_config(
    page_title="SAP ME/MII Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Ana başlık
st.markdown('<h1 class="main-header">🔍 SAP ME/MII Folder Analyzer</h1>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Ayarlar")
    
    # Klasör seçimi
    st.markdown("### 📁 Klasör Seçimi")
    
    root_folder = st.text_input(
        "Analiz Edilecek Klasör",
        value=st.session_state.get('selected_folder', './example_test'),
        help="SAP ME/MII kaynak kodlarının bulunduğu klasör yolu"
    )
    
    # Windows File Explorer butonu
    if st.button("📂 Klasör Seç (Windows Explorer)", use_container_width=True, type="primary"):
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            # Tkinter root oluştur (gizli)
            root_tk = tk.Tk()
            root_tk.withdraw()
            root_tk.wm_attributes('-topmost', 1)
            
            # Klasör seçim dialogu aç
            folder_selected = filedialog.askdirectory(
                title="Analiz edilecek klasörü seçin",
                initialdir=st.session_state.get('selected_folder', os.path.expanduser("~"))
            )
            
            root_tk.destroy()
            
            if folder_selected:
                st.session_state.selected_folder = folder_selected
                st.success(f"✅ Seçildi: {folder_selected}")
                st.rerun()
            
        except Exception as e:
            st.error(f"❌ Hata: {str(e)}")
            st.info("💡 Manuel olarak klasör yolunu yukarıdaki kutuya yazabilirsiniz")
    
    # Seçili klasör varsa göster
    if 'selected_folder' in st.session_state and st.session_state.selected_folder:
        st.info(f"📁 Seçili: {st.session_state.selected_folder}")
        root_folder = st.session_state.selected_folder
    
    st.markdown("---")
    
    # Çıktı klasörü
    output_folder = st.text_input(
        "📂 Çıktı Klasörü",
        value="./streamlit_output",
        help="Analiz sonuçlarının kaydedileceği klasör"
    )
    
    st.markdown("---")
    
    # Çıktı seçenekleri
    st.markdown("### 📊 Çıktı Formatları")
    generate_mermaid = st.checkbox("Mermaid Diyagram (.mmd)", value=True)
    generate_json = st.checkbox("JSON İlişkiler (.json)", value=True)
    
    st.markdown("---")
    
    # Analiz butonu
    analyze_button = st.button("🚀 Analizi Başlat", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 📚 Hızlı Bağlantılar")
    st.markdown("- [Mermaid Live Editor](https://mermaid.live)")
    st.markdown("- [Dokümantasyon](./README.md)")

# Ana içerik alanı
if analyze_button:
    # Klasör kontrolü
    if not Path(root_folder).exists():
        st.error(f"❌ Klasör bulunamadı: {root_folder}")
        st.stop()
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("🔍 Analiz başlatılıyor...")
    progress_bar.progress(10)
    
    # Python yolu
    python_path = Path(os.environ.get('LOCALAPPDATA', '')) / 'Programs' / 'Python' / 'Python313' / 'python.exe'
    if not python_path.exists():
        python_path = 'python'
    
    # Analiz komutu (extended analyzer kullan)
    cmd = [
        str(python_path),
        "me_mii_folder_analyzer_extended.py",
        "--root", root_folder,
        "--out", output_folder
    ]
    
    status_text.text("⚙️ Dosyalar taranıyor...")
    progress_bar.progress(30)
    
    try:
        # Analizi çalıştır
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        progress_bar.progress(70)
        status_text.text("📊 Sonuçlar işleniyor...")
        
        if result.returncode == 0:
            progress_bar.progress(100)
            status_text.text("✅ Analiz tamamlandı!")
            
            st.success("🎉 Analiz başarıyla tamamlandı!")
            
            # Sonuçları göster
            output_path = Path(output_folder)
            
            # Metrikleri oku
            summary_path = output_path / "SUMMARY.md"
            if summary_path.exists():
                summary_text = summary_path.read_text(encoding='utf-8')
                
                # İstatistikleri çıkar
                import re
                java_classes = re.search(r'Java Sınıf Sayısı:\s*(\d+)', summary_text)
                bls_steps = re.search(r'BLS/Transaction Adım Sayısı:\s*(\d+)', summary_text)
                relations = re.search(r'Tespit Edilen İlişki Sayısı:\s*(\d+)', summary_text)
                endpoints = re.search(r'Entegrasyon/Uç Nokta Sayısı:\s*(\d+)', summary_text)
                
                # SAPUI5 bilgileri
                routes = re.search(r'Routes:\s*(\d+)\s*adet', summary_text)
                views = re.search(r'Views:\s*(\d+)\s*adet', summary_text)
                
                # Metrikler
                st.markdown("## 📊 Analiz Sonuçları")
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("Java Sınıfları", java_classes.group(1) if java_classes else "0")
                
                with col2:
                    st.metric("BLS Adımları", bls_steps.group(1) if bls_steps else "0")
                
                with col3:
                    st.metric("İlişkiler", relations.group(1) if relations else "0")
                
                with col4:
                    st.metric("Endpoint'ler", endpoints.group(1) if endpoints else "0")
                
                with col5:
                    if routes:
                        st.metric("SAPUI5 Routes", routes.group(1))
                    else:
                        st.metric("Views", views.group(1) if views else "0")
                
                st.markdown("---")
                
                # Tabs ile içerik gösterimi
                tab1, tab2, tab3, tab4 = st.tabs([
                    "📄 Özet Rapor",
                    "🎨 Mermaid Diyagram",
                    "📊 JSON Veriler",
                    "💾 İndir"
                ])
                
                with tab1:
                    st.markdown("### 📄 SUMMARY.md")
                    st.markdown(summary_text)
                
                with tab2:
                    mermaid_path = output_path / "graph.mmd"
                    if mermaid_path.exists():
                        mermaid_content = mermaid_path.read_text(encoding='utf-8')
                        st.markdown("### 🎨 Mermaid Diyagram")
                        
                        st.info("💡 Diyagramı görselleştirmek için [Mermaid Live Editor](https://mermaid.live) kullanın")
                        
                        st.code(mermaid_content, language='mermaid')
                    else:
                        st.warning("graph.mmd dosyası bulunamadı")
                
                with tab3:
                    json_path = output_path / "graph.json"
                    sapui5_path = output_path / "sapui5_details.json"
                    
                    if json_path.exists():
                        st.markdown("### 📊 graph.json")
                        json_data = json.loads(json_path.read_text(encoding='utf-8'))
                        st.json(json_data)
                    
                    if sapui5_path.exists():
                        st.markdown("### 📱 SAPUI5 Details")
                        sapui5_data = json.loads(sapui5_path.read_text(encoding='utf-8'))
                        st.json(sapui5_data)
                
                with tab4:
                    st.markdown("### 💾 Dosyaları İndir")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if summary_path.exists():
                            st.download_button(
                                label="📄 SUMMARY.md İndir",
                                data=summary_path.read_bytes(),
                                file_name="SUMMARY.md",
                                mime="text/markdown"
                            )
                        
                        if mermaid_path.exists():
                            st.download_button(
                                label="🎨 graph.mmd İndir",
                                data=mermaid_path.read_bytes(),
                                file_name="graph.mmd",
                                mime="text/plain"
                            )
                    
                    with col2:
                        if json_path.exists():
                            st.download_button(
                                label="📊 graph.json İndir",
                                data=json_path.read_bytes(),
                                file_name="graph.json",
                                mime="application/json"
                            )
                        
                        if sapui5_path.exists():
                            st.download_button(
                                label="📱 sapui5_details.json İndir",
                                data=sapui5_path.read_bytes(),
                                file_name="sapui5_details.json",
                                mime="application/json"
                            )
            
        else:
            progress_bar.progress(0)
            status_text.text("❌ Analiz başarısız!")
            st.error(f"Hata: {result.stderr}")
            st.code(result.stdout)
    
    except Exception as e:
        progress_bar.progress(0)
        status_text.text("❌ Hata oluştu!")
        st.error(f"Beklenmeyen hata: {str(e)}")

else:
    # İlk açılış ekranı
    st.info("👈 Sol menüden **'📂 Klasör Seç'** butonuna tıklayın ve klasörü seçin, sonra **'🚀 Analizi Başlat'** butonuna tıklayın")
    
    # Özellikler
    st.markdown("## ✨ Özellikler")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 📊 Analiz
        - Java sınıf ve metodları
        - REST endpoint tespiti
        - SQL/JDBC kullanımı
        - HTTP çağrıları
        - **SAPUI5/Fiori desteği** ⭐
        """)
    
    with col2:
        st.markdown("""
        ### 🔗 Entegrasyon
        - MII BLS/Transaction
        - WSDL/SOAP servisleri
        - Config dosyaları
        - Veritabanı bağlantıları
        - **manifest.json parsing** ⭐
        """)
    
    with col3:
        st.markdown("""
        ### 📈 Çıktılar
        - Mimari özet raporu
        - Eğitim dökümanı
        - Mermaid diyagram
        - JSON ilişki verileri
        - **SAPUI5 detayları** ⭐
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>SAP ME/MII Folder Analyzer v1.1.0 (Extended) | Made with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)
