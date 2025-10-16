# Streamlit Başlatma Script'i
Write-Host "🚀 Streamlit başlatılıyor..." -ForegroundColor Green

# Python yolu
$pythonPath = "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"

# Streamlit'i başlat
& $pythonPath -m streamlit run streamlit_app.py

Write-Host "`n✅ Streamlit durduruldu." -ForegroundColor Yellow
