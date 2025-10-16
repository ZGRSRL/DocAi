"""
SAP ME/MII Folder Analyzer — Agent-based MVP (single-file)

What it does (MVP):
- Walk a local FOLDER (no git required) containing SAP ME/MII Java sources and MII artifacts
- Parse:
  • Java (.java) → classes, methods, @Path, @GET/@POST, JDBC heuristics, outbound HTTP calls
  • XML (.xml) → MII BLS/Transaction steps (Action/Target), simple WSDL endpoint extraction
  • Properties/Config (.properties, .yaml, .yml, .json) → endpoints/DSNs heuristics
- Build a relationship graph (NetworkX)
- Generate:
  • SUMMARY.md (architecture & integration overview)
  • TRAINING.md (role-based training outline + FAQ skeleton)
  • graph.mmd (Mermaid) and graph.json (edges)

Usage:
  pip install -r requirements.txt
  python me_mii_folder_analyzer.py --root "/path/to/your/folder" --out ./out

Requirements (create requirements.txt):
  javalang
  lxml
  networkx
  pydantic
  click
  rich

Notes:
- This is an MVP. It uses heuristics where exact parsing is complex.
- Replace/extend the heuristics with tree-sitter-java, antlr, or WSDL/OpenAPI toolchains if needed.
- Ollama/RAG/AutoGen integration hooks are stubbed at the end (see: TODO section).
"""
from __future__ import annotations
import re
import os
import json
import pathlib
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

import click
from rich import print
from pydantic import BaseModel, Field
import networkx as nx

# Optional deps guarded
try:
    import javalang  # type: ignore
    HAS_JAVALANG = True
except Exception:
    HAS_JAVALANG = False

try:
    from lxml import etree  # type: ignore
    HAS_LXML = True
except Exception:
    HAS_LXML = False

# -----------------------------
# Data Models
# -----------------------------
class JavaMethod(BaseModel):
    name: str
    params: List[str] = Field(default_factory=list)
    endpoints: List[Dict[str, Any]] = Field(default_factory=list)  # {method, path}
    sql_usages: List[str] = Field(default_factory=list)            # raw sql snippets/flags
    http_calls: List[str] = Field(default_factory=list)            # urls/hosts

class JavaClass(BaseModel):
    name: str
    package: Optional[str] = None
    methods: List[JavaMethod] = Field(default_factory=list)
    file: Optional[str] = None

class BLSNode(BaseModel):
    action: Optional[str] = None
    target: Optional[str] = None
    name: Optional[str] = None

class Relation(BaseModel):
    src: str
    dst: str
    type: str
    meta: Dict[str, Any] = Field(default_factory=dict)

class AnalysisResult(BaseModel):
    classes: List[JavaClass] = Field(default_factory=list)
    bls: List[BLSNode] = Field(default_factory=list)
    relations: List[Relation] = Field(default_factory=list)
    endpoints: List[Dict[str, Any]] = Field(default_factory=list)
    db_usages: List[Dict[str, Any]] = Field(default_factory=list)

# -----------------------------
# Utilities
# -----------------------------
JAVA_HTTP_PAT = re.compile(r"(https?://[\w\.-]+(?::\d+)?(?:/[^\s'\"]*)?)")
JDBC_PAT = re.compile(r"jdbc:[\w:;@/\-\.\?=&]+", re.IGNORECASE)
SQL_PAT = re.compile(r"\b(SELECT|UPDATE|INSERT\s+INTO|DELETE\s+FROM)\b", re.IGNORECASE)

WSDL_SVC_PAT = re.compile(r"<service\s+name=\"([^\"]+)\"", re.IGNORECASE)
WSDL_PORT_PAT = re.compile(r"<port\s+name=\"([^\"]+)\"\s+binding=\"([^\"]+)\"", re.IGNORECASE)
WSDL_ADDRESS_PAT = re.compile(r"address\s+location=\"([^\"]+)\"", re.IGNORECASE)

PATH_ANN_PAT = re.compile(r"@Path\(\s*\"([^\"]+)\"\s*\)")
HTTP_ANN_PAT = re.compile(r"@(GET|POST|PUT|DELETE|PATCH)\b")

CONFIG_URL_PAT = re.compile(r"\bhttps?://[\w\.-]+(?::\d+)?(?:/[^\s]*)?\b")
CONFIG_DSN_PAT = re.compile(r"\bjdbc:[^\s]+\b", re.IGNORECASE)

SUPPORTED_XML_HINTS = ("BLS", "Transaction", "WSDL")

# -----------------------------
# Parsers
# -----------------------------

def parse_java_file(fp: Path) -> Optional[JavaClass]:
    try:
        text = fp.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None

    if HAS_JAVALANG:
        try:
            tree = javalang.parse.parse(text)
        except Exception:
            tree = None
    else:
        tree = None

    cls: Optional[JavaClass] = None

    if tree is not None:  # AST path
        # package
        pkg = None
        try:
            if hasattr(tree, 'package') and tree.package:
                pkg = tree.package.name
        except Exception:
            pkg = None

        # classes
        classes = []
        try:
            for path, node in tree.filter(javalang.tree.ClassDeclaration):  # type: ignore
                jc = JavaClass(name=node.name, package=pkg, methods=[], file=str(fp))
                for m in node.methods:
                    jm = JavaMethod(name=m.name, params=[getattr(p.type, 'name', str(p.type)) for p in (m.parameters or [])])
                    # annotations → HTTP method & @Path
                    ann_names = [getattr(a, 'name', '') for a in (m.annotations or [])]
                    http_methods = [a for a in ann_names if a in {"GET","POST","PUT","DELETE","PATCH"}]
                    m_text_slice = text[m.position.offset if hasattr(m, 'position') and m.position else 0:]
                    path_match = PATH_ANN_PAT.search(m_text_slice)
                    if http_methods and path_match:
                        jm.endpoints.append({"method": http_methods[0], "path": path_match.group(1)})
                    # heuristics: SQL & HTTP calls in method body
                    body_hint = m_text_slice[:2000]
                    if SQL_PAT.search(body_hint) or JDBC_PAT.search(body_hint):
                        jm.sql_usages.append("heuristic")
                    for u in JAVA_HTTP_PAT.findall(body_hint):
                        jm.http_calls.append(u)
                    jc.methods.append(jm)
                classes.append(jc)
        except Exception:
            classes = []

        if classes:
            # pick first class if multiple (usually 1 per file in enterprise code)
            cls = classes[0]
    else:
        # Heuristic fallback without AST
        # class name
        m = re.search(r"class\s+(\w+)", text)
        name = m.group(1) if m else fp.stem
        pkg = None
        m2 = re.search(r"package\s+([\w\.]+);", text)
        if m2:
            pkg = m2.group(1)
        jc = JavaClass(name=name, package=pkg, methods=[], file=str(fp))
        # crude method detection
        for mm in re.finditer(r"(public|protected|private)\s+[\w\<\>\[\]]+\s+(\w+)\s*\(([^)]*)\)\s*\{", text):
            meth_name = mm.group(2)
            params = [p.strip().split()[-1] if " " in p.strip() else p.strip() for p in mm.group(3).split(',') if p.strip()]
            jm = JavaMethod(name=meth_name, params=params)
            # annotations
            # find annotations above this method (up to 3 lines back)
            start = max(0, mm.start() - 300)
            ann_block = text[start:mm.start()]
            http_match = HTTP_ANN_PAT.search(ann_block)
            path_match = PATH_ANN_PAT.search(ann_block)
            if http_match and path_match:
                jm.endpoints.append({"method": http_match.group(1), "path": path_match.group(1)})
            # sql/http
            body_hint = text[mm.end():mm.end()+1200]
            if SQL_PAT.search(body_hint) or JDBC_PAT.search(body_hint):
                jm.sql_usages.append("heuristic")
            for u in JAVA_HTTP_PAT.findall(body_hint):
                jm.http_calls.append(u)
            jc.methods.append(jm)
        cls = jc

    return cls


def parse_xml_file(fp: Path) -> Tuple[List[BLSNode], List[Relation], List[Dict[str, Any]]]:
    """Return (bls_nodes, relations, endpoints_from_wsdl)
    Detects simple MII BLS/Transaction elements and WSDL endpoints (if any).
    """
    bls_nodes: List[BLSNode] = []
    rels: List[Relation] = []
    wsdl_eps: List[Dict[str, Any]] = []

    try:
        text = fp.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return bls_nodes, rels, wsdl_eps

    # WSDL quick extraction
    if "definitions" in text and ("wsdl" in text.lower() or "xmlns:wsdl" in text.lower()):
        for m in WSDL_SVC_PAT.finditer(text):
            svc = m.group(1)
            wsdl_eps.append({"type": "SOAP-Service", "service": svc, "file": str(fp)})
        for m in WSDL_PORT_PAT.finditer(text):
            wsdl_eps.append({"type": "SOAP-Port", "name": m.group(1), "binding": m.group(2), "file": str(fp)})
        for m in WSDL_ADDRESS_PAT.finditer(text):
            wsdl_eps.append({"type": "SOAP-Address", "location": m.group(1), "file": str(fp)})

    if not HAS_LXML:
        # Heuristic XML parsing if lxml not available
        # MII BLS/Transaction rough detection
        if "<BLS" in text or "<Transaction" in text:
            for step in re.finditer(r"<Step[^>]*Action=\"([^\"]*)\"[^>]*Target=\"([^\"]*)\"[^>]*/?>", text):
                bls_nodes.append(BLSNode(action=step.group(1), target=step.group(2), name=None))
        return bls_nodes, rels, wsdl_eps

    # lxml-based parsing
    try:
        root = etree.fromstring(text.encode("utf-8"))
    except Exception:
        # try a more lenient parser
        try:
            parser = etree.XMLParser(recover=True)
            root = etree.fromstring(text.encode("utf-8"), parser=parser)
        except Exception:
            return bls_nodes, rels, wsdl_eps

    tag_up = (root.tag or "").upper()
    is_mii = any(hint in tag_up for hint in SUPPORTED_XML_HINTS) or any(h in text for h in SUPPORTED_XML_HINTS)

    if is_mii:
        # Typical MII BLS/Transaction elements
        for step in root.xpath("//Step"):
            action = step.get("Action")
            target = step.get("Target")
            name = step.get("Name") or step.get("Id")
            node = BLSNode(action=action, target=target, name=name)
            bls_nodes.append(node)
            if target:
                rels.append(Relation(src=name or "BLS_STEP", dst=target, type="BLS_CALLS_TARGET", meta={"file": str(fp)}))

        # Params IO (optional)
        for par in root.xpath("//Parameter|//Input|//Output"):
            pname = par.get("Name") or par.get("Id")
            if pname:
                rels.append(Relation(src="PARAM", dst=pname, type="BLS_PARAM", meta={"file": str(fp)}))

    return bls_nodes, rels, wsdl_eps


def parse_config_file(fp: Path) -> Tuple[List[str], List[str]]:
    """Return (urls, dsns) heuristically from config-like files."""
    try:
        text = fp.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return [], []
    return CONFIG_URL_PAT.findall(text), CONFIG_DSN_PAT.findall(text)

# -----------------------------
# Graph & Exporters
# -----------------------------
class RelGraph:
    def __init__(self):
        self.G = nx.DiGraph()

    def add_edge(self, u: str, v: str, etype: str, **meta):
        if u and v:
            self.G.add_edge(u, v, type=etype, **meta)

    def add_endpoint(self, owner: str, method: str, path: str):
        node = f"REST:{method}:{path}"
        self.add_edge(owner, node, "SERVICE_EXPOSES_ENDPOINT")

    def add_http_call(self, owner: str, url: str):
        self.add_edge(owner, f"HTTP:{url}", "SERVICE_CALLS_HTTP")

    def add_sql_usage(self, owner: str, hint: str):
        self.add_edge(owner, f"SQL:{hint}", "METHOD_TOUCHES_SQL")

    def add_bls_rel(self, src: str, dst: str, meta: Dict[str, Any]):
        self.add_edge(src, dst, "BLS_CALLS_TARGET", **meta)

    def to_mermaid(self) -> str:
        lines = ["graph LR"]
        for u, v, d in self.G.edges(data=True):
            et = d.get("type", "rel")
            lines.append(f'  "{u}" -->|{et}| "{v}"')
        return "\n".join(lines)

    def to_edges(self) -> List[Dict[str, Any]]:
        edges = []
        for u, v, d in self.G.edges(data=True):
            edges.append({"src": u, "dst": v, "type": d.get("type", "rel"), "meta": {k:v for k,v in d.items() if k!="type"}})
        return edges

# -----------------------------
# Pipeline (folder-based)
# -----------------------------

def analyze_folder(root: Path) -> AnalysisResult:
    classes: List[JavaClass] = []
    bls_nodes: List[BLSNode] = []
    relations: List[Relation] = []
    endpoints: List[Dict[str, Any]] = []
    db_usages: List[Dict[str, Any]] = []

    graph = RelGraph()

    for fp in root.rglob("*"):
        if not fp.is_file():
            continue

        ext = fp.suffix.lower()
        # Java
        if ext == ".java":
            jc = parse_java_file(fp)
            if jc:
                classes.append(jc)
                owner = f"{jc.package}.{jc.name}" if jc.package else jc.name
                for m in jc.methods:
                    m_owner = f"{owner}.{m.name}()"
                    for ep in m.endpoints:
                        graph.add_endpoint(m_owner, ep.get("method","GET"), ep.get("path","/"))
                        endpoints.append({"class": owner, **ep})
                    if m.sql_usages:
                        graph.add_sql_usage(m_owner, "heuristic")
                        db_usages.append({"owner": m_owner, "type": "sql_heuristic"})
                    for url in m.http_calls:
                        graph.add_http_call(m_owner, url)
        # XML (MII BLS/Transaction, WSDL)
        elif ext == ".xml":
            bls, rels, wsdl_eps = parse_xml_file(fp)
            if bls:
                bls_nodes.extend(bls)
            if rels:
                relations.extend(rels)
                for r in rels:
                    graph.add_bls_rel(r.src, r.dst, r.meta)
            for ep in wsdl_eps:
                endpoints.append({"class": str(fp), **ep})
        # Configs
        elif ext in {".properties", ".yaml", ".yml", ".json"}:
            urls, dsns = parse_config_file(fp)
            for u in urls:
                graph.add_http_call(str(fp), u)
                endpoints.append({"class": str(fp), "type": "CFG-URL", "url": u})
            for dsn in dsns:
                graph.add_edge(str(fp), f"DSN:{dsn}", "CFG_DSN")
                db_usages.append({"owner": str(fp), "dsn": dsn})

    # Collect relations from graph (as list)
    rel_edges = [Relation(src=e[0], dst=e[1], type=e[2].get("type","rel"), meta={k:v for k,v in e[2].items() if k!="type"}) for e in graph.G.edges(data=True)]

    return AnalysisResult(
        classes=classes,
        bls=bls_nodes,
        relations=rel_edges,
        endpoints=endpoints,
        db_usages=db_usages,
    )

# -----------------------------
# Document Builders
# -----------------------------
SUMMARY_TMPL = """# Uygulama Özeti (MVP)

## Genel Mimari Bulgular
- Java Sınıf Sayısı: {n_classes}
- BLS/Transaction Adım Sayısı: {n_bls}
- Tespit Edilen İlişki Sayısı: {n_rels}
- Entegrasyon/Uç Nokta Sayısı: {n_eps}
- DB Erişim Sinyalleri: {n_db}

## REST/SOAP & Diğer Uç Noktalar (Örnekler)
{endpoint_lines}

## Olası Veritabanı Erişimleri (Heuristik)
{db_lines}

## Önemli Notlar / Riskler (MVP)
- Bu rapor ilk çıkarım sürümüdür ve heuristikler içerir.
- JDBC/SQL çıkarımı ve prepared-statement çözümlemesi geliştirilebilir.
- WSDL/SOAP analizi genişletilebilir (operation/binding detayları, XSD şemaları).
- Java AST için tree-sitter/ANTLR ile doğruluk artırılabilir.

"""

TRAINING_TMPL = """# Eğitim Dökümanı (MVP)

## Roller ve Görevler
### Operatör
- Tanımlı transaction akışlarını prosedüre uygun başlatır.
- Hata durumunda temel kontrol: bağlantı, parametre, veri kaynağı.

### Süpervizör
- BLS/Transaction akışlarını izler; kritik adımları ve bağımlılıkları bilir.
- Entegrasyon uç noktalarının (REST/SOAP) sağlık takibini koordine eder.

### Admin
- Konfigürasyon dosyaları ve DSN bağlantılarını yönetir.
- Log/izleme sistemlerini ve hata senaryolarını dokümante eder.

## İş Akışı Örnekleri
- [Örnek] Sipariş Oluşturma: REST endpoint → Transaction → BLS Step(Execute SQL) → DB INSERT
- [Örnek] Ürün Takibi: UI → Service → Query → Raporlama

## SSS (Skeleton)
- S: X Transaction hangi tabloyu günceller?  
  C: SUMMARY ve graph.mmd içindeki ilişkilere bakın; DB Inspector genişletmesi gerekebilir.
- S: Y Servisi hangi dış sisteme çağrı yapıyor?  
  C: SUMMARY'de HTTP/URL yakalamalarına ve WSDL adreslerine bakın.

## Sorun Giderme (Skeleton)
- BLS 'Execute SQL' adımı başarısız → DSN/credential, parametre türleri, indeks/lock kontrolü.
- REST 5xx → Bağımlı servis/ERP/IDoc uçları ve ağ izinleri.
- Timeout → Step zincirinde ağır sorgular veya dış sistem gecikmeleri.
"""


def build_summary_doc(res: AnalysisResult) -> str:
    ep_lines = []
    for e in res.endpoints[:50]:
        if e.get("type") == "CFG-URL":
            ep_lines.append(f"- [CFG] {e.get('url')}  (src: {Path(e.get('class','')).name})")
        elif e.get("type","" ).startswith("SOAP"):
            if e.get("location"):
                ep_lines.append(f"- [SOAP] {e.get('location')}  (file: {Path(e.get('class','')).name})")
            elif e.get("service"):
                ep_lines.append(f"- [SOAP] service={e.get('service')}  (file: {Path(e.get('class','')).name})")
            else:
                ep_lines.append(f"- [SOAP] {json.dumps(e)}")
        else:
            method = e.get('method','GET')
            path = e.get('path','/')
            owner = e.get('class','')
            ep_lines.append(f"- [REST] {method} {path}  (owner: {Path(owner).name if owner else '-'})")
    if len(res.endpoints) > 50:
        ep_lines.append(f"- ... (+{len(res.endpoints)-50} more)")

    db_lines = [f"- {x.get('owner')} — {x.get('type','dsn')} {x.get('dsn','')}" for x in res.db_usages[:50]]
    if len(res.db_usages) > 50:
        db_lines.append(f"- ... (+{len(res.db_usages)-50} more)")

    return SUMMARY_TMPL.format(
        n_classes=len(res.classes),
        n_bls=len(res.bls),
        n_rels=len(res.relations),
        n_eps=len(res.endpoints),
        n_db=len(res.db_usages),
        endpoint_lines="\n".join(ep_lines) if ep_lines else "- (bulunamadı)",
        db_lines="\n".join(db_lines) if db_lines else "- (bulunamadı)",
    )


def build_training_doc(res: AnalysisResult) -> str:
    return TRAINING_TMPL

# -----------------------------
# CLI
# -----------------------------
@click.command()
@click.option('--root', type=click.Path(path_type=Path, exists=True, file_okay=False), required=True, help='Analyze this folder recursively.')
@click.option('--out', type=click.Path(path_type=Path, file_okay=False), default=Path('./out'), help='Output directory for docs/graph files.')
@click.option('--mermaid', is_flag=True, default=True, help='Export Mermaid graph file (graph.mmd).')
@click.option('--jsonedges', is_flag=True, default=True, help='Export raw edges as JSON (graph.json).')
def main(root: Path, out: Path, mermaid: bool, jsonedges: bool):
    print(f"[bold green]SAP ME/MII Folder Analyzer[/bold green] — scanning: [cyan]{root}[/cyan]")
    out.mkdir(parents=True, exist_ok=True)

    res = analyze_folder(root)
    summary = build_summary_doc(res)
    training = build_training_doc(res)

    (out / 'SUMMARY.md').write_text(summary, encoding='utf-8')
    (out / 'TRAINING.md').write_text(training, encoding='utf-8')

    # Graph exports
    G = nx.DiGraph()
    for r in res.relations:
        G.add_edge(r.src, r.dst, type=r.type, **r.meta)

    # Add endpoint & sql hints to graph as well for visualization completeness
    for e in res.endpoints:
        if e.get('type') == 'CFG-URL' and e.get('url'):
            G.add_edge(e.get('class','CFG'), f"HTTP:{e['url']}", type='CFG_URL')
        elif e.get('type','').startswith('SOAP'):
            node = e.get('location') or e.get('service') or e.get('name') or 'SOAP'
            G.add_edge(e.get('class','WSDL'), f"SOAP:{node}", type='SOAP_DEF')
        else:
            owner = e.get('class','JAVA')
            G.add_edge(owner, f"REST:{e.get('method','GET')}:{e.get('path','/')} ", type='SERVICE_EXPOSES_ENDPOINT')

    # Mermaid export
    if mermaid:
        lines = ["graph LR"]
        for u,v,d in G.edges(data=True):
            lines.append(f'  "{u}" -->|{d.get("type","rel")}| "{v}"')
        (out / 'graph.mmd').write_text("\n".join(lines), encoding='utf-8')

    # JSON edges
    if jsonedges:
        edges = []
        for u,v,d in G.edges(data=True):
            edges.append({"src": u, "dst": v, "type": d.get('type','rel'), "meta": {k:v for k,v in d.items() if k!="type"}})
        (out / 'graph.json').write_text(json.dumps(edges, indent=2, ensure_ascii=False), encoding='utf-8')

    print(f"\n[bold]Done.[/bold] Outputs -> {out.resolve()}\n - SUMMARY.md\n - TRAINING.md\n - graph.mmd\n - graph.json\n")


if __name__ == '__main__':
    main()

# -----------------------------
# TODO (next iterations)
# -----------------------------
# - Replace javalang with tree-sitter-java for more robust parsing (method bodies, call graph).
# - Implement JDBC prepared-statement parameter/value reconstruction; extract concrete table/column ops.
# - Proper WSDL/XSD parser: operations, bindings, messages, and target endpoints.
# - Add SAP ME API & MII-specific artifact handlers (Query, Data Server, IDoc, ODP, ISA, KPIs). 
# - Integrate Neo4j and Cypher templates for complex impact analysis.
# - Add Streamlit UI and download buttons; Mermaid render preview.
# - RAG + Ollama: chunk sources & artifacts → pgvector; FAQ & doc generation using templates + LLM.
# - AutoGen/LangGraph orchestrator around these functions for true agent-based coordination.
