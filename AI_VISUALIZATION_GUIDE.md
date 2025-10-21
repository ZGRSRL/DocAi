# 🧠 AI Agent Visualization Guide

## 📋 Genel Bakış

Bu rehber, SAP ME/MII analiz sonuçlarını AI destekli görselleştirme ile nasıl sunacağınızı gösterir. Streamlit tabanlı interaktif dashboard'lar ile analiz verilerinizi profesyonel bir şekilde görselleştirebilirsiniz.

## 🚀 Hızlı Başlangıç

### 1. Temel Kullanım
```bash
# Ana analiz uygulaması
py -m streamlit run streamlit_app.py

# AI görselleştirme dashboard'u
py -m streamlit run ai_visualization_app.py --server.port 8502

# Demo uygulaması
py -m streamlit run demo_ai_visualization.py --server.port 8503
```

### 2. Port Yapılandırması
- **Ana Uygulama**: http://localhost:8501
- **AI Dashboard**: http://localhost:8502
- **Demo**: http://localhost:8503

## 🎨 Görselleştirme Özellikleri

### 📊 Metrik Kartları
- **Renkli Gradient Kartlar**: Ana metrikleri görsel olarak sunar
- **Gerçek Zamanlı Veri**: Analiz sonuçlarından otomatik güncelleme
- **Responsive Tasarım**: Farklı ekran boyutlarına uyum

```python
# Örnek metrik kartı
st.markdown(f"""
<div class="metric-card">
    <h3>🎮 Controllers</h3>
    <h1>{controller_count}</h1>
</div>
""", unsafe_allow_html=True)
```

### 📈 İnteraktif Grafikler

#### Bar Charts (Plotly)
```python
fig = px.bar(
    df,
    x='Count',
    y='Component',
    orientation='h',
    title="UI Components Distribution",
    color='Count',
    color_continuous_scale='viridis'
)
st.plotly_chart(fig, use_container_width=True)
```

#### Pie Charts
```python
fig = px.pie(
    api_df, 
    values='Usage Count', 
    names='API Class',
    title="SAP ME API Usage Distribution"
)
```

#### Scatter Plots
```python
fig = go.Scatter(
    x=df['Functions'], 
    y=df['Event Handlers'],
    mode='markers+text',
    text=df['Controller'],
    marker=dict(size=df['API Calls']*2+10)
)
```

### 🗺️ Navigasyon Haritaları

#### Mermaid Diyagramları
```python
mermaid_code = """
graph TD
    Home(Home.controller.js) --> PNL(panelView)
    Home --> TRC(traceabilityView)
    Home --> PCL(packageLabelView)
    
    style Home fill:#ADD8E6,stroke:#333
    style PNL fill:#90EE90,stroke:#333
"""
st.code(mermaid_code, language='mermaid')
```

## 🤖 AI Agent Entegrasyonu

### RAG Chat Arayüzü
```python
def create_rag_chat_interface(self, analysis_dir: Path):
    user_question = st.chat_input("Ask the AI agent...")
    
    if user_question:
        st.chat_message("user").write(user_question)
        
        with st.spinner("AI agent is thinking..."):
            ai_response = rag_ask(user_question, output_dir=str(analysis_dir))
            
            with st.chat_message("assistant"):
                st.markdown(f"**AI Response:** {ai_response}")
```

### Chat Geçmişi
- **Session State**: Kullanıcı sohbet geçmişi saklanır
- **Timestamp**: Her mesaj için zaman damgası
- **Expandable History**: Geçmiş sohbetleri genişletilebilir format

## 🏭 ME/MII Özel Analizi

### SAP ME API Görselleştirmesi
```python
# API kullanım sayılarını hesapla
api_counts = {}
for api in self.analysis_data['sap_me_apis']:
    class_name = api.get('class', 'Unknown')
    api_counts[class_name] = api_counts.get(class_name, 0) + 1

# Pie chart oluştur
fig = px.pie(api_df, values='Usage Count', names='API Class')
```

### SFC Operasyon Analizi
```python
# SFC operasyonlarını grupla
sfc_counts = {}
for sfc in self.analysis_data['sfc_operations']:
    operation = sfc.get('operation', 'Unknown')
    op_type = operation.split('=')[0].strip()
    sfc_counts[op_type] = sfc_counts.get(op_type, 0) + 1
```

## 📱 Responsive Dashboard

### Sidebar Kontrolleri
- **Analiz Seçimi**: Farklı görünümler arasında geçiş
- **Veri Yenileme**: Gerçek zamanlı güncelleme
- **Export Seçenekleri**: PDF rapor oluşturma

### Ana İçerik Alanları
- **Overview**: Genel proje metrikleri
- **Controllers**: Controller analizi ve karşılaştırması
- **UI Components**: Kullanıcı arayüzü bileşenleri
- **ME/MII Analysis**: SAP entegrasyon analizi
- **Navigation**: Uygulama akış haritası
- **AI Chat**: İnteraktif AI danışman

## 🎯 Kullanım Senaryoları

### 1. Yönetici Sunumu
- **Metrik Kartları**: Ana performans göstergeleri
- **Executive Summary**: Yüksek seviye özet
- **PDF Export**: Profesyonel rapor oluşturma

### 2. Teknik Analiz
- **Controller Dashboard**: Detaylı kod analizi
- **API Usage Charts**: Entegrasyon noktaları
- **Navigation Flow**: Uygulama mimarisi

### 3. AI Destekli Keşif
- **Chat Interface**: Doğal dil ile sorgulama
- **Interactive Charts**: Veri keşfi
- **Real-time Analysis**: Anlık analiz

## 🔧 Özelleştirme

### Renk Temaları
```python
# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)
```

### Chart Stilleri
```python
# Plotly tema ayarları
fig.update_layout(
    height=400,
    showlegend=False,
    color_continuous_scale='viridis'
)
```

### Responsive Layout
```python
# Column layout
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig1, use_container_width=True)
with col2:
    st.plotly_chart(fig2, use_container_width=True)
```

## 📦 Gerekli Kütüphaneler

```bash
pip install streamlit plotly pandas matplotlib seaborn networkx
```

## 🚀 Gelişmiş Özellikler

### 1. Gerçek Zamanlı Güncelleme
- **Auto-refresh**: Veri değişikliklerini otomatik algılama
- **Live Metrics**: Canlı metrik güncellemeleri
- **Dynamic Charts**: Dinamik grafik yenileme

### 2. İnteraktif Filtreleme
- **Date Range**: Tarih aralığı filtreleme
- **Category Filter**: Kategori bazlı filtreleme
- **Search Function**: Arama ve filtreleme

### 3. Export Seçenekleri
- **PDF Reports**: Profesyonel PDF raporları
- **Excel Export**: Veri tablosu export
- **Image Export**: Grafik görsel export

## 🎉 Sonuç

Bu AI destekli görselleştirme sistemi, SAP ME/MII analiz sonuçlarınızı:

- ✅ **Profesyonel** bir şekilde sunar
- ✅ **İnteraktif** olarak keşfetmenizi sağlar
- ✅ **AI destekli** analiz imkanı verir
- ✅ **Responsive** tasarım ile her cihazda çalışır
- ✅ **Export** seçenekleri ile paylaşım kolaylığı sağlar

**Bu sistem, analiz verilerinizin değerini görsel ve etkileşimli bir şekilde kat kat artırır!** 🚀

