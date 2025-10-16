"""
SAP ME/MII Folder Analyzer — Extended Version
Supports: Java, XML, Config, JavaScript (SAPUI5/Fiori), manifest.json

Usage:
  python me_mii_folder_analyzer_extended.py --root "/path/to/folder" --out ./out
"""
from pathlib import Path
import json
import re
import subprocess
import sys

# Ana analyzer'ı import et
import me_mii_folder_analyzer as base_analyzer

def parse_manifest_json(fp: Path):
    """SAPUI5/Fiori manifest.json dosyasını parse et"""
    try:
        data = json.loads(fp.read_text(encoding='utf-8'))
        
        info = {
            "type": "SAPUI5/Fiori",
            "file": str(fp),
            "app_id": None,
            "app_title": None,
            "routes": [],
            "views": [],
            "models": [],
            "dependencies": []
        }
        
        # App bilgileri
        if "sap.app" in data:
            info["app_id"] = data["sap.app"].get("id")
            info["app_title"] = data["sap.app"].get("title")
        
        # Routing bilgileri
        if "sap.ui5" in data and "routing" in data["sap.ui5"]:
            routing = data["sap.ui5"]["routing"]
            
            # Routes
            if "routes" in routing:
                for route in routing["routes"]:
                    info["routes"].append({
                        "name": route.get("name"),
                        "pattern": route.get("pattern"),
                        "target": route.get("target")
                    })
            
            # Targets (Views)
            if "targets" in routing:
                for target_name, target_data in routing["targets"].items():
                    info["views"].append({
                        "name": target_name,
                        "viewName": target_data.get("viewName"),
                        "viewPath": target_data.get("viewPath")
                    })
        
        # Models
        if "sap.ui5" in data and "models" in data["sap.ui5"]:
            for model_name, model_data in data["sap.ui5"]["models"].items():
                info["models"].append({
                    "name": model_name,
                    "type": model_data.get("type")
                })
        
        # Dependencies
        if "sap.ui5" in data and "dependencies" in data["sap.ui5"]:
            deps = data["sap.ui5"]["dependencies"]
            if "libs" in deps:
                info["dependencies"] = list(deps["libs"].keys())
        
        return info
        
    except Exception as e:
        print(f"Warning: Could not parse {fp}: {e}")
        return None


def parse_javascript_file(fp: Path):
    """JavaScript dosyasını basit parse et (controller, API calls, vb.)"""
    try:
        text = fp.read_text(encoding='utf-8', errors='ignore')
        
        info = {
            "file": str(fp),
            "type": "JavaScript",
            "controllers": [],
            "api_calls": [],
            "odata_services": []
        }
        
        # Controller tespit et
        controller_match = re.search(r'sap\.ui\.define\s*\(\s*\[([^\]]+)\]', text)
        if controller_match:
            info["type"] = "SAPUI5 Controller"
        
        # HTTP/API çağrıları
        http_patterns = [
            r'jQuery\.ajax\s*\(\s*\{[^}]*url\s*:\s*["\']([^"\']+)["\']',
            r'fetch\s*\(\s*["\']([^"\']+)["\']',
            r'\.get\s*\(\s*["\']([^"\']+)["\']',
            r'\.post\s*\(\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in http_patterns:
            for match in re.finditer(pattern, text):
                info["api_calls"].append(match.group(1))
        
        # OData servisleri
        odata_pattern = r'new\s+sap\.ui\.model\.odata\.v[24]\.ODataModel\s*\(\s*["\']([^"\']+)["\']'
        for match in re.finditer(odata_pattern, text):
            info["odata_services"].append(match.group(1))
        
        return info if (info["api_calls"] or info["odata_services"]) else None
        
    except Exception as e:
        return None


def analyze_folder_extended(root: Path):
    """Genişletilmiş analiz - base + JavaScript/SAPUI5"""
    
    # Base analiz
    print(f"[1/2] Running base analysis...")
    base_result = base_analyzer.analyze_folder(root)
    
    # Ek analizler
    print(f"[2/2] Analyzing JavaScript/SAPUI5 files...")
    
    js_files = []
    manifest_files = []
    sapui5_info = {
        "manifests": [],
        "controllers": [],
        "api_calls": [],
        "odata_services": [],
        "routes": [],
        "views": []
    }
    
    for fp in root.rglob("*"):
        if not fp.is_file():
            continue
        
        # manifest.json
        if fp.name == "manifest.json":
            manifest_data = parse_manifest_json(fp)
            if manifest_data:
                sapui5_info["manifests"].append(manifest_data)
                sapui5_info["routes"].extend(manifest_data["routes"])
                sapui5_info["views"].extend(manifest_data["views"])
        
        # JavaScript files
        elif fp.suffix.lower() == ".js":
            js_data = parse_javascript_file(fp)
            if js_data:
                if js_data["type"] == "SAPUI5 Controller":
                    sapui5_info["controllers"].append(js_data)
                sapui5_info["api_calls"].extend(js_data["api_calls"])
                sapui5_info["odata_services"].extend(js_data["odata_services"])
    
    return base_result, sapui5_info


def build_extended_summary(base_result, sapui5_info):
    """Genişletilmiş özet rapor oluştur"""
    
    # Base özet
    base_summary = base_analyzer.build_summary_doc(base_result)
    
    # SAPUI5 eklentisi
    sapui5_section = "\n## SAPUI5/Fiori Analizi\n\n"
    
    if sapui5_info["manifests"]:
        sapui5_section += f"### Uygulama Bilgileri\n"
        for manifest in sapui5_info["manifests"]:
            sapui5_section += f"- **App ID:** {manifest['app_id']}\n"
            sapui5_section += f"- **Title:** {manifest['app_title']}\n"
            sapui5_section += f"- **Type:** {manifest['type']}\n"
            sapui5_section += f"- **Routes:** {len(manifest['routes'])} adet\n"
            sapui5_section += f"- **Views:** {len(manifest['views'])} adet\n"
            sapui5_section += f"- **Dependencies:** {', '.join(manifest['dependencies'])}\n\n"
    
    if sapui5_info["routes"]:
        sapui5_section += f"### Routing ({len(sapui5_info['routes'])} route)\n"
        for route in sapui5_info["routes"][:20]:
            sapui5_section += f"- **{route['name']}:** `{route['pattern']}` → {route['target']}\n"
        if len(sapui5_info["routes"]) > 20:
            sapui5_section += f"- ... (+{len(sapui5_info['routes']) - 20} more)\n"
        sapui5_section += "\n"
    
    if sapui5_info["views"]:
        sapui5_section += f"### Views ({len(sapui5_info['views'])} view)\n"
        for view in sapui5_info["views"][:15]:
            sapui5_section += f"- **{view['name']}:** {view.get('viewPath', '')}.{view.get('viewName', '')}\n"
        if len(sapui5_info["views"]) > 15:
            sapui5_section += f"- ... (+{len(sapui5_info['views']) - 15} more)\n"
        sapui5_section += "\n"
    
    if sapui5_info["api_calls"]:
        sapui5_section += f"### API Çağrıları ({len(sapui5_info['api_calls'])} adet)\n"
        unique_apis = list(set(sapui5_info["api_calls"]))
        for api in unique_apis[:10]:
            sapui5_section += f"- {api}\n"
        if len(unique_apis) > 10:
            sapui5_section += f"- ... (+{len(unique_apis) - 10} more)\n"
        sapui5_section += "\n"
    
    if sapui5_info["odata_services"]:
        sapui5_section += f"### OData Servisleri ({len(sapui5_info['odata_services'])} adet)\n"
        unique_odata = list(set(sapui5_info["odata_services"]))
        for odata in unique_odata:
            sapui5_section += f"- {odata}\n"
        sapui5_section += "\n"
    
    if not any([sapui5_info["manifests"], sapui5_info["routes"], sapui5_info["api_calls"]]):
        sapui5_section += "- SAPUI5/Fiori artifact'i bulunamadı\n\n"
    
    # Birleştir
    return base_summary + sapui5_section


def main_extended():
    """Extended analyzer main function"""
    import click
    from rich import print
    
    @click.command()
    @click.option('--root', type=click.Path(path_type=Path, exists=True, file_okay=False), required=True)
    @click.option('--out', type=click.Path(path_type=Path, file_okay=False), default=Path('./out'))
    def run(root: Path, out: Path):
        print(f"[bold green]SAP ME/MII Extended Analyzer[/bold green] — scanning: [cyan]{root}[/cyan]")
        out.mkdir(parents=True, exist_ok=True)
        
        # Analiz
        base_result, sapui5_info = analyze_folder_extended(root)
        
        # Özet oluştur
        summary = build_extended_summary(base_result, sapui5_info)
        (out / 'SUMMARY.md').write_text(summary, encoding='utf-8')
        
        # Training (base)
        training = base_analyzer.build_training_doc(base_result)
        (out / 'TRAINING.md').write_text(training, encoding='utf-8')
        
        # SAPUI5 detay JSON
        (out / 'sapui5_details.json').write_text(
            json.dumps(sapui5_info, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        
        # Graph (base)
        import networkx as nx
        G = nx.DiGraph()
        for r in base_result.relations:
            G.add_edge(r.src, r.dst, type=r.type, **r.meta)
        
        # SAPUI5 ilişkilerini ekle
        for route in sapui5_info["routes"]:
            G.add_edge(f"Route:{route['name']}", f"View:{route['target']}", type="ROUTE_TO_VIEW")
        
        for api in set(sapui5_info["api_calls"]):
            G.add_edge("SAPUI5_App", f"API:{api}", type="CALLS_API")
        
        # Mermaid
        lines = ["graph LR"]
        for u, v, d in G.edges(data=True):
            lines.append(f'  "{u}" -->|{d.get("type","rel")}| "{v}"')
        (out / 'graph.mmd').write_text("\n".join(lines), encoding='utf-8')
        
        # JSON
        edges = []
        for u, v, d in G.edges(data=True):
            edges.append({"src": u, "dst": v, "type": d.get('type','rel'), "meta": {k:v for k,v in d.items() if k!="type"}})
        (out / 'graph.json').write_text(json.dumps(edges, indent=2, ensure_ascii=False), encoding='utf-8')
        
        print(f"\n[bold]Done.[/bold] Outputs -> {out.resolve()}")
        print(" - SUMMARY.md")
        print(" - TRAINING.md")
        print(" - sapui5_details.json")
        print(" - graph.mmd")
        print(" - graph.json\n")
    
    run()


if __name__ == '__main__':
    main_extended()
