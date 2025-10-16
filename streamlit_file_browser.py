"""
Windows File Explorer Style Browser for Streamlit
"""
import streamlit as st
import os
from pathlib import Path
from datetime import datetime

def format_size(size_bytes):
    """Dosya boyutunu okunabilir formata çevir"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def get_file_info(path):
    """Dosya/klasör bilgilerini al"""
    try:
        stat = os.stat(path)
        return {
            'name': os.path.basename(path),
            'path': path,
            'is_dir': os.path.isdir(path),
            'size': stat.st_size if not os.path.isdir(path) else 0,
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'type': 'Klasör' if os.path.isdir(path) else Path(path).suffix.upper()[1:] or 'Dosya'
        }
    except:
        return None

def render_file_browser():
    """Windows Explorer benzeri file browser"""
    
    # Session state başlat
    if 'current_path' not in st.session_state:
        st.session_state.current_path = os.path.abspath(".")
    
    if 'selected_path' not in st.session_state:
        st.session_state.selected_path = None
    
    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = 'list'  # list veya grid
    
    # Üst toolbar
    st.markdown("### 📁 Klasör Tarayıcı")
    
    # Navigation bar
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 6])
    
    with col1:
        if st.button("⬅️", help="Geri", use_container_width=True):
            parent = os.path.dirname(st.session_state.current_path)
            if os.path.exists(parent):
                st.session_state.current_path = parent
                st.rerun()
    
    with col2:
        if st.button("⬆️", help="Üst klasör", use_container_width=True):
            parent = os.path.dirname(st.session_state.current_path)
            if os.path.exists(parent):
                st.session_state.current_path = parent
                st.rerun()
    
    with col3:
        if st.button("🔄", help="Yenile", use_container_width=True):
            st.rerun()
    
    with col4:
        if st.button("🏠", help="Ana dizin", use_container_width=True):
            st.session_state.current_path = os.path.expanduser("~")
            st.rerun()
    
    # Adres çubuğu
    st.text_input(
        "Konum",
        value=st.session_state.current_path,
        key="address_bar",
        label_visibility="collapsed"
    )
    
    # Breadcrumb navigation
    path_parts = Path(st.session_state.current_path).parts
    breadcrumb_cols = st.columns(len(path_parts))
    
    for i, part in enumerate(path_parts):
        with breadcrumb_cols[i]:
            if st.button(f"📁 {part}", key=f"breadcrumb_{i}", use_container_width=True):
                new_path = os.path.join(*path_parts[:i+1])
                if os.path.exists(new_path):
                    st.session_state.current_path = new_path
                    st.rerun()
    
    st.markdown("---")
    
    # Hızlı erişim sidebar
    col_sidebar, col_main = st.columns([1, 3])
    
    with col_sidebar:
        st.markdown("**Hızlı Erişim**")
        
        # Sürücüler
        st.markdown("**💾 Sürücüler**")
        for drive in ['C:\\', 'D:\\', 'E:\\']:
            if os.path.exists(drive):
                if st.button(f"💿 {drive}", key=f"drive_{drive}", use_container_width=True):
                    st.session_state.current_path = drive
                    st.rerun()
        
        st.markdown("---")
        
        # Özel klasörler
        st.markdown("**⭐ Özel Klasörler**")
        
        special_folders = {
            "🏠 Ana Dizin": os.path.expanduser("~"),
            "📄 Belgeler": os.path.join(os.path.expanduser("~"), "Documents"),
            "⬇️ İndirilenler": os.path.join(os.path.expanduser("~"), "Downloads"),
            "🖼️ Resimler": os.path.join(os.path.expanduser("~"), "Pictures"),
            "💼 Masaüstü": os.path.join(os.path.expanduser("~"), "Desktop"),
        }
        
        for name, path in special_folders.items():
            if os.path.exists(path):
                if st.button(name, key=f"special_{path}", use_container_width=True):
                    st.session_state.current_path = path
                    st.rerun()
    
    with col_main:
        # Arama kutusu
        search_term = st.text_input(
            "🔍 Ara",
            placeholder="Dosya veya klasör ara...",
            label_visibility="collapsed"
        )
        
        # Görünüm modu ve sıralama
        col_view, col_sort = st.columns([1, 2])
        
        with col_view:
            view_mode = st.radio(
                "Görünüm",
                ["📋 Liste", "🔲 Izgara"],
                horizontal=True,
                label_visibility="collapsed"
            )
            st.session_state.view_mode = 'list' if '📋' in view_mode else 'grid'
        
        with col_sort:
            sort_by = st.selectbox(
                "Sırala",
                ["İsim", "Tarih", "Boyut", "Tür"],
                label_visibility="collapsed"
            )
        
        st.markdown("---")
        
        # Dosya/klasör listesi
        try:
            items = []
            
            for item_name in os.listdir(st.session_state.current_path):
                item_path = os.path.join(st.session_state.current_path, item_name)
                info = get_file_info(item_path)
                if info:
                    items.append(info)
            
            # Arama filtresi
            if search_term:
                items = [item for item in items if search_term.lower() in item['name'].lower()]
            
            # Sıralama
            if sort_by == "İsim":
                items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
            elif sort_by == "Tarih":
                items.sort(key=lambda x: (not x['is_dir'], x['modified']), reverse=True)
            elif sort_by == "Boyut":
                items.sort(key=lambda x: (not x['is_dir'], x['size']), reverse=True)
            elif sort_by == "Tür":
                items.sort(key=lambda x: (not x['is_dir'], x['type']))
            
            # Klasörler önce
            folders = [item for item in items if item['is_dir']]
            files = [item for item in items if not item['is_dir']]
            items = folders + files
            
            if not items:
                st.info("📭 Bu klasör boş")
            else:
                st.markdown(f"**{len(items)} öğe** ({len(folders)} klasör, {len(files)} dosya)")
                
                # Liste görünümü
                if st.session_state.view_mode == 'list':
                    # Başlık satırı
                    header_cols = st.columns([3, 2, 2, 2, 1])
                    with header_cols[0]:
                        st.markdown("**📛 İsim**")
                    with header_cols[1]:
                        st.markdown("**📅 Değiştirilme**")
                    with header_cols[2]:
                        st.markdown("**📏 Boyut**")
                    with header_cols[3]:
                        st.markdown("**📑 Tür**")
                    with header_cols[4]:
                        st.markdown("**⚡**")
                    
                    st.markdown("---")
                    
                    # Öğeleri göster
                    for item in items:
                        cols = st.columns([3, 2, 2, 2, 1])
                        
                        with cols[0]:
                            icon = "📁" if item['is_dir'] else "📄"
                            st.text(f"{icon} {item['name'][:40]}...")
                        
                        with cols[1]:
                            st.text(item['modified'].strftime("%d.%m.%Y %H:%M"))
                        
                        with cols[2]:
                            if item['is_dir']:
                                st.text("-")
                            else:
                                st.text(format_size(item['size']))
                        
                        with cols[3]:
                            st.text(item['type'])
                        
                        with cols[4]:
                            if item['is_dir']:
                                if st.button("➡️", key=f"open_{item['path']}", help="Aç"):
                                    st.session_state.current_path = item['path']
                                    st.rerun()
                            else:
                                if st.button("✓", key=f"select_{item['path']}", help="Seç"):
                                    st.session_state.selected_path = item['path']
                                    st.success(f"✓ Seçildi: {item['name']}")
                
                # Izgara görünümü
                else:
                    # 4 sütunlu grid
                    num_cols = 4
                    for i in range(0, len(items), num_cols):
                        cols = st.columns(num_cols)
                        for j, col in enumerate(cols):
                            if i + j < len(items):
                                item = items[i + j]
                                with col:
                                    # Kart görünümü
                                    with st.container():
                                        icon = "📁" if item['is_dir'] else "📄"
                                        st.markdown(f"### {icon}")
                                        st.markdown(f"**{item['name'][:15]}...**")
                                        st.caption(item['type'])
                                        
                                        if item['is_dir']:
                                            if st.button("Aç", key=f"grid_open_{item['path']}", use_container_width=True):
                                                st.session_state.current_path = item['path']
                                                st.rerun()
                                        else:
                                            if st.button("Seç", key=f"grid_select_{item['path']}", use_container_width=True):
                                                st.session_state.selected_path = item['path']
                                                st.success(f"✓ Seçildi: {item['name']}")
        
        except PermissionError:
            st.error("❌ Bu klasöre erişim izni yok")
        except Exception as e:
            st.error(f"❌ Hata: {str(e)}")
    
    # Seçili öğe bilgisi
    if st.session_state.selected_path:
        st.markdown("---")
        st.markdown("### ✅ Seçili Öğe")
        
        info_cols = st.columns([3, 1])
        with info_cols[0]:
            st.info(f"📁 **{st.session_state.selected_path}**")
        with info_cols[1]:
            if st.button("🗑️ Seçimi Temizle", use_container_width=True):
                st.session_state.selected_path = None
                st.rerun()
    
    return st.session_state.selected_path


# Test için
if __name__ == "__main__":
    st.set_page_config(page_title="File Browser", layout="wide")
    st.title("🗂️ Windows File Explorer")
    
    selected = render_file_browser()
    
    if selected:
        st.success(f"Seçili dosya: {selected}")
