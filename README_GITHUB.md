# 🔍 SAP ME/MII Folder Analyzer

**Advanced code analysis tool for SAP ME/MII and SAPUI5/Fiori projects**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 Features

### 📊 Multi-Technology Support
- **Java Analysis** — Classes, methods, REST endpoints (@Path, @GET/@POST), JDBC/SQL, HTTP calls
- **XML Analysis** — MII BLS/Transaction steps, WSDL endpoints
- **SAPUI5/Fiori** — Controllers, Views, Fragments, i18n, manifest.json
- **Configuration Files** — .properties, .yaml, .json parsing

### 🎨 Deep SAPUI5 Analysis
- **Controllers:** Functions, event handlers, API calls, OData operations
- **Views:** UI controls (buttons, tables, inputs), data bindings, events
- **i18n:** Translation keys extraction
- **Navigation Flow:** Route mapping
- **UI Components:** Detailed component counting

### 📈 Outputs
- **ADVANCED_SUMMARY.md** — Detailed analysis report
- **SUMMARY.md** — Architecture overview
- **TRAINING.md** — Role-based training outline
- **graph.mmd** — Mermaid diagram
- **graph.json** — Relationship data
- **sapui5_deep_analysis.json** — Deep SAPUI5 data

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/ZGRSRL/DocAi.git
cd DocAi

# Install dependencies
pip install -r requirements.txt
```

### Usage

#### 1. Command Line (Advanced Analysis)
```bash
python me_mii_analyzer_advanced.py --root /path/to/project --out ./output
```

#### 2. Streamlit Web UI (Recommended)
```bash
streamlit run streamlit_app.py
```

Then:
1. Click "📁 TVMES" or select folder
2. Click "🚀 Analizi Başlat"
3. View results in tabs

---

## 📦 Requirements

```
javalang
lxml
networkx
pydantic
click
rich
streamlit
pandas
```

---

## 📊 Example Output

### SAPUI5 Project Analysis
```
📊 Executive Summary
- Controllers: 12 files
- Views: 9 files
- i18n Keys: 2,761 translations
- UI Components: 48 buttons, 32 tables, 14 inputs
- Navigation: 9 routes

🎮 Controllers Analysis
- BaseController.js: 91 functions
- Event Handlers: onInit, onScanBarcode, onPressHome...
- API Calls: REST endpoints detected
- OData Operations: READ, CREATE, UPDATE, DELETE

📱 Views Analysis
- UI Controls: Buttons, Tables, Inputs, Dialogs
- Data Bindings: 51-74 bindings per view
- Events: Press, scan, change handlers
```

---

## 🎨 Streamlit UI Features

- **One-Click Folder Selection** — Quick access buttons
- **Real-time Progress** — Progress bar and status updates
- **Interactive Results** — Tabbed interface with multiple views
- **Download Options** — Individual files or ZIP archive
- **Responsive Design** — Works on desktop and mobile

---

## 📁 Project Structure

```
DocAı/
├── me_mii_folder_analyzer.py          # Base analyzer
├── me_mii_folder_analyzer_extended.py # SAPUI5 basic support
├── me_mii_analyzer_advanced.py        # Deep SAPUI5 analysis
├── streamlit_app.py                   # Web UI
├── requirements.txt                   # Dependencies
├── start_streamlit.ps1                # Windows launcher
├── example_test/                      # Test data
│   ├── TestService.java
│   ├── OrderTransaction.xml
│   ├── ProductService.wsdl
│   └── application.properties
└── docs/                              # Documentation
    ├── README.md
    ├── INSTALLATION.md
    ├── QUICKSTART.md
    ├── PROJECT_OVERVIEW.md
    └── STREAMLIT_GUIDE.md
```

---

## 🔧 Advanced Features

### Deep Analysis Capabilities
- **Controller Functions:** Extract all function definitions
- **Event Handlers:** Detect on* methods
- **API Calls:** jQuery.ajax, fetch, $.get, $.post
- **OData Models:** v2/v4 model creation
- **OData Operations:** CRUD operation detection
- **Message Handling:** Toast and MessageBox
- **Navigation:** navTo route detection
- **Validation Logic:** Validation detection

### View Analysis
- **Control Detection:** Button, Input, Table, List, Panel, Form, Dialog
- **Binding Analysis:** Model binding paths
- **Event Mapping:** Press, change, scan events
- **Fragment Detection:** Fragment usage

### i18n Support
- **Key Extraction:** All translation keys
- **Value Parsing:** Translation values
- **Language Detection:** Multi-language support

---

## 💡 Use Cases

### 1. New Project Onboarding
- Quickly understand project structure
- Identify key components and flows
- Generate documentation automatically

### 2. Code Review
- Analyze architecture and patterns
- Detect integration points
- Review API usage

### 3. Documentation Generation
- Auto-generate technical docs
- Create training materials
- Build knowledge base

### 4. Migration Planning
- Inventory existing components
- Map dependencies
- Plan refactoring

---

## 🛠️ Development

### Running Tests
```bash
# Test with example data
python me_mii_analyzer_advanced.py --root ./example_test --out ./test_output
```

### Extending Analyzers
```python
# Add custom parser
def parse_custom_file(fp: Path) -> Dict[str, Any]:
    # Your parsing logic
    return info

# Register in analyze_sapui5_deep()
```

---

## 📚 Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [Quick Start](docs/QUICKSTART.md)
- [Project Overview](docs/PROJECT_OVERVIEW.md)
- [Streamlit Guide](docs/STREAMLIT_GUIDE.md)
- [File Explorer Guide](docs/FILE_EXPLORER_GUIDE.md)

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [NetworkX](https://networkx.org/)
- Java parsing with [javalang](https://github.com/c2nes/javalang)
- XML parsing with [lxml](https://lxml.de/)

---

## 📞 Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/ZGRSRL/DocAi/issues)
- Documentation: [Read the docs](docs/)

---

**Made with ❤️ for SAP ME/MII developers**
