import os
import json
from pathlib import Path
from typing import List, Tuple

import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def load_corpus(output_dir: Path) -> List[Tuple[str, str]]:
    """Load analysis outputs as (doc_id, text)."""
    docs: List[Tuple[str, str]] = []
    candidates = [
        output_dir / "SUMMARY.md",
        output_dir / "ADVANCED_SUMMARY.md",
        output_dir / "graph.json",
        output_dir / "sapui5_details.json",
        output_dir / "sapui5_deep_analysis.json",
    ]
    for fp in candidates:
        if fp.exists():
            try:
                text = fp.read_text(encoding="utf-8", errors="ignore")
                docs.append((fp.name, text))
            except Exception:
                pass
    return docs


def retrieve(query: str, docs: List[Tuple[str, str]], k: int = 5) -> List[Tuple[str, str, float]]:
    """Return top-k (doc_id, text, score) by TF-IDF cosine."""
    if not docs:
        return []
    ids = [d[0] for d in docs]
    texts = [d[1] for d in docs]
    vectorizer = TfidfVectorizer(max_features=20000)
    X = vectorizer.fit_transform(texts + [query])
    doc_vectors = X[:-1]
    query_vector = X[-1]
    sims = cosine_similarity(doc_vectors, query_vector)
    scores = sims.reshape(-1)
    ranked = sorted(zip(ids, texts, scores), key=lambda x: x[2], reverse=True)
    return ranked[:k]


def build_prompt(contexts: List[Tuple[str, str, float]], question: str) -> str:
    ctx = []
    for doc_id, text, score in contexts:
        snippet = text[:4000]
        ctx.append(f"[DOC:{doc_id} | score={score:.3f}]\n{snippet}")
    joined = "\n\n".join(ctx) if ctx else "(no context)"
    prompt = f"""
Sistem: SAP ME/MII ve SAPUI5/Fiori uzman danışmansın. Somut SAP örnekleriyle, kısa ve uygulanabilir yanıtlar ver. Gerekirse adım adım çözüm ve risk notları ekle.

[CONTEXT]
{joined}

[QUESTION]
{question}
""".strip()
    return prompt


def ollama_chat(model: str, prompt: str, host: str = "http://localhost:11434", timeout_s: int = 600) -> str:
    url = f"{host}/api/chat"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }
    resp = requests.post(url, json=payload, timeout=timeout_s)
    resp.raise_for_status()
    data = resp.json()
    return data.get("message", {}).get("content", "")


def ask(question: str, output_dir: str = "./streamlit_output", model: str = "me-mii-consultant", host: str = "http://localhost:11434", timeout_s: int = 600) -> str:
    docs = load_corpus(Path(output_dir))
    top = retrieve(question, docs, k=5)
    prompt = build_prompt(top, question)
    return ollama_chat(model, prompt, host=host, timeout_s=timeout_s)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("question", type=str, help="Consultant question")
    parser.add_argument("--out", type=str, default="./streamlit_output", help="Analysis output dir")
    parser.add_argument("--model", type=str, default="me-mii-consultant", help="Ollama model name")
    parser.add_argument("--host", type=str, default="http://localhost:11434", help="Ollama host URL")
    parser.add_argument("--timeout", type=int, default=600, help="HTTP timeout seconds (model cold start may take long)")
    args = parser.parse_args()
    answer = ask(args.question, output_dir=args.out, model=args.model, host=args.host, timeout_s=args.timeout)
    print(answer)



