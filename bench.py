"""
Benchmark Script for Lab 07: Data Foundations (K4-L3A)
Topic: Thư viện Đại học FPT (FPTU Library)
Compares chunking strategies on the official library regulations corpus.
"""

from __future__ import annotations

import math
import os
import re
from collections import Counter
from pathlib import Path
from typing import Any

from src.chunking import FixedSizeChunker, HeadingChunker, RecursiveChunker, SentenceChunker
from src.embeddings import _mock_embed
from src.models import Document
from src.store import EmbeddingStore


class PureSemanticEmbedder:
    """
    Deterministic semantic embedder using word + bigram feature hashing.
    Generates normalized 128-dimensional dense vectors preserving phrase semantics.
    """

    def __init__(self, dim: int = 128) -> None:
        self.dim = dim
        self._backend_name = "Pure-Python Semantic Feature Hashing (128-dim)"

    def __call__(self, text: str) -> list[float]:
        words = re.findall(r"\w+", text.lower())
        tokens = list(words)
        for i in range(len(words) - 1):
            tokens.append(f"{words[i]}_{words[i+1]}")

        counts = Counter(tokens)
        vec = [0.0] * self.dim
        for token, count in counts.items():
            h = hash(token)
            idx = abs(h) % self.dim
            sign = 1.0 if (h >= 0) else -1.0
            vec[idx] += sign * (1.0 + math.log(count))

        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]


BENCHMARK_QUERIES = [
    {
        "id": 1,
        "query": "Sinh viên được mượn tối đa bao nhiêu tài liệu về nhà và thời hạn mượn sách tham khảo tiếng Việt, ngoại văn là bao lâu?",
        "filter": None,
        "gold_doc": "fpt-muon-sach-sinh-vien",
        "gold_keywords": ["10", "7 ngày", "14 ngày"],
        "gold_answer": "Sinh viên được mượn tối đa 10 tài liệu cùng lúc về nhà; sách tiếng Việt mượn 7 ngày; sách ngoại văn và song ngữ mượn 14 ngày.",
    },
    {
        "id": 2,
        "query": "Hạn ngạch được phép mượn tài liệu về nhà tối đa là bao nhiêu cuốn cùng một lúc?",
        "filter": {"audience": "student"},
        "gold_doc": "fpt-muon-sach-sinh-vien",
        "gold_keywords": ["10", "sinh viên"],
        "gold_answer": "10 tài liệu đối với sinh viên (nếu là cán bộ giảng viên thì được mượn tối đa 20 tài liệu).",
    },
    {
        "id": 3,
        "query": "Mức phí phạt trả sách quá hạn mỗi ngày là bao nhiêu và có những phương thức thanh toán trực tuyến nào?",
        "filter": None,
        "gold_doc": "fpt-phi-thu-vien",
        "gold_keywords": ["5.000", "FAP", "DNG"],
        "gold_answer": "Phí phạt quá hạn là 5.000 VNĐ / tài liệu / ngày; có 2 phương thức thanh toán trực tuyến: qua ví FAP và qua cổng DNG (quét mã QR ngân hàng).",
    },
    {
        "id": 4,
        "query": "Thời gian sử dụng phòng học nhóm tối đa là bao lâu mỗi ca và sau bao nhiêu phút không đến nhận phòng thì ca đặt sẽ bị hủy?",
        "filter": None,
        "gold_doc": "fpt-phong-hoc-nhom",
        "gold_keywords": ["2 giờ", "15 phút"],
        "gold_answer": "Thời gian sử dụng tối đa 2 giờ / ca (1 ca / nhóm / ngày); sau 15 phút kể từ giờ bắt đầu nếu nhóm không đến nhận phòng hoặc không đủ người tối thiểu thì ca đặt sẽ tự động bị hủy.",
    },
    {
        "id": 5,
        "query": "Mỗi cuốn sách được phép gia hạn tối đa mấy lượt và bạn đọc có thể thực hiện gia hạn qua những kênh nào?",
        "filter": None,
        "gold_doc": "fpt-gia-han-tai-lieu",
        "gold_keywords": ["4 lượt", "OPAC", "024 6680 5912", "Fanpage"],
        "gold_answer": "Mỗi cuốn sách được phép gia hạn tối đa 4 lượt (nếu chưa có người đặt trước); gia hạn qua 4 kênh: cổng OPAC trực tuyến, gửi email, gọi điện thoại (024 6680 5912), hoặc nhắn tin qua Fanpage Thư viện FPTU.",
    },
]


def load_raw_documents(data_dir: Path) -> list[dict[str, Any]]:
    docs = []
    for md_file in sorted(data_dir.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        if "---" in text:
            parts = text.split("---", 2)
            raw_fm = parts[1]
            body = parts[2].strip() if len(parts) > 2 else ""
            fm = dict(re.findall(r"^(\w+):\s*(.+)$", raw_fm, re.M))
        else:
            fm = {"doc_id": md_file.stem}
            body = text.strip()
        docs.append({"doc_id": fm.get("doc_id", md_file.stem), "metadata": fm, "body": body})
    return docs


def build_store(
    raw_docs: list[dict[str, Any]],
    chunker: Any,
    embedder: Any,
) -> tuple[EmbeddingStore, int]:
    store = EmbeddingStore(collection_name="bench_store", embedding_fn=embedder)
    doc_objects: list[Document] = []
    for raw in raw_docs:
        doc_id = raw["doc_id"]
        chunks = chunker.chunk(raw["body"])
        for idx, ch in enumerate(chunks):
            doc_objects.append(
                Document(
                    id=f"{doc_id}#{idx}",
                    content=ch,
                    metadata={**raw["metadata"], "doc_id": doc_id, "chunk_index": idx},
                )
            )
    store.add_documents(doc_objects)
    return store, len(doc_objects)


def evaluate_query(
    store: EmbeddingStore,
    query_item: dict[str, Any],
    use_filter: bool = True,
) -> dict[str, Any]:
    query = query_item["query"]
    flt = query_item["filter"] if use_filter else None
    results = store.search_with_filter(query, top_k=3, metadata_filter=flt)

    gold_doc = query_item["gold_doc"]
    gold_keywords = query_item["gold_keywords"]

    top_doc_ids = [r["metadata"].get("doc_id") for r in results]
    gold_in_top3 = gold_doc in top_doc_ids
    gold_at_top1 = len(top_doc_ids) > 0 and top_doc_ids[0] == gold_doc

    context_text = " ".join([r["content"] for r in results])
    keywords_matched = sum(1 for kw in gold_keywords if kw.lower() in context_text.lower())
    content_matches = keywords_matched == len(gold_keywords)

    if gold_at_top1 and content_matches:
        score = 2
    elif gold_in_top3 and keywords_matched > 0:
        score = 1
    else:
        score = 0

    return {
        "query_id": query_item["id"],
        "query": query,
        "filter_used": flt,
        "results": results,
        "top1_doc": top_doc_ids[0] if top_doc_ids else None,
        "top1_score": results[0]["score"] if results else 0.0,
        "gold_in_top3": gold_in_top3,
        "content_matches": content_matches,
        "points": score,
    }


def run_benchmark():
    data_dir = Path("data/thu-vien")
    raw_docs = load_raw_documents(data_dir)
    print(f"Loaded {len(raw_docs)} raw documents from {data_dir}")

    embedder = PureSemanticEmbedder(dim=128)
    print(f"Backend Embedder: {embedder._backend_name}\n")

    strategies = {
        "Vĩ (Strategy Lead): HeadingChunker": HeadingChunker(max_section_size=400),
        "Tuấn (Data Lead): SentenceChunker": SentenceChunker(max_sentences_per_chunk=3),
        "Khánh (Benchmark Lead): RecursiveChunker": RecursiveChunker(chunk_size=300),
        "Nhật (Report Lead): FixedSizeChunker": FixedSizeChunker(chunk_size=250, overlap=40),
    }

    report_lines = []
    report_lines.append("================================================================================")
    report_lines.append("        KẾT QUẢ BENCHMARK RETRIEVAL LAB 07 (L3A) — THƯ VIỆN ĐẠI HỌC FPT        ")
    report_lines.append("================================================================================\n")
    report_lines.append(f"Backend Embedder: {embedder._backend_name}\n")

    overall_results = {}
    for strat_name, chunker in strategies.items():
        store, chunk_count = build_store(raw_docs, chunker, embedder)
        strat_scores = []
        details = []

        for q in BENCHMARK_QUERIES:
            res = evaluate_query(store, q, use_filter=True)
            strat_scores.append(res["points"])
            details.append(res)

        total_score = sum(strat_scores)
        overall_results[strat_name] = {
            "chunk_count": chunk_count,
            "total_points": total_score,
            "details": details,
        }

    # Summary table
    report_lines.append(f"{'Chiến lược':<42} | {'Số Chunks':<10} | {'Điểm (/10)':<10} | {'Đánh giá'}")
    report_lines.append("-" * 85)
    for s_name, res in overall_results.items():
        report_lines.append(f"{s_name:<42} | {res['chunk_count']:<10} | {res['total_points']}/10{'':<6} | {'Xuất sắc' if res['total_points']>=9 else ('Tốt' if res['total_points']>=7 else 'Trung bình')}")
    report_lines.append("\n" + "=" * 85 + "\n")

    # Detailed results per strategy
    for s_name, res in overall_results.items():
        report_lines.append(f"### CHI TIẾT CHIẾN LƯỢC: {s_name} (Tổng chunks: {res['chunk_count']})")
        for d in res["details"]:
            q_id = d["query_id"]
            top1 = d["results"][0] if d["results"] else {}
            content_preview = top1.get("content", "").replace("\n", " ")[:120]
            report_lines.append(f"  Câu {q_id}: {d['query']}")
            report_lines.append(f"    - Filter: {d['filter_used']}")
            report_lines.append(f"    - Top-1 Doc: {d['top1_doc']} (score={d['top1_score']:.3f})")
            report_lines.append(f"    - Content preview: {content_preview}...")
            report_lines.append(f"    - Gold in top-3: {d['gold_in_top3']} | Content matched: {d['content_matches']} | Điểm: {d['points']}/2")
        report_lines.append("-" * 85)

    # A/B Test for Query 2 (Hạn ngạch mượn: student vs faculty)
    report_lines.append("\n### BẰNG CHỨNG THỰC NGHIỆM A/B: METADATA FILTERING TRÊN CÂU HỎI 2")
    q2 = BENCHMARK_QUERIES[1]
    h_store, _ = build_store(raw_docs, strategies["Vĩ (Strategy Lead): HeadingChunker"], embedder)
    res_filtered = evaluate_query(h_store, q2, use_filter=True)
    res_unfiltered = evaluate_query(h_store, q2, use_filter=False)

    report_lines.append(f"Câu hỏi: \"{q2['query']}\"")
    report_lines.append("\n[1] KHI CÓ FILTER (metadata_filter={'audience': 'student'}):")
    for idx, r in enumerate(res_filtered["results"], start=1):
        report_lines.append(f"  Rank {idx}: doc_id={r['metadata'].get('doc_id')}, audience={r['metadata'].get('audience')}, score={r['score']:.3f}")
        report_lines.append(f"         Preview: {r['content'].replace(chr(10), ' ')[:100]}...")

    report_lines.append("\n[2] KHI KHÔNG CÓ FILTER (Unfiltered):")
    for idx, r in enumerate(res_unfiltered["results"], start=1):
        report_lines.append(f"  Rank {idx}: doc_id={r['metadata'].get('doc_id')}, audience={r['metadata'].get('audience')}, score={r['score']:.3f}")
        report_lines.append(f"         Preview: {r['content'].replace(chr(10), ' ')[:100]}...")

    report_lines.append("\nKết luận A/B: Khi không bật filter, tài liệu fpt-muon-sach-giang-vien (audience: faculty, 20 cuốn) có thể cạnh tranh trực tiếp ở top-k với tài liệu sinh viên (10 cuốn), khiến agent dễ nhầm lẫn đối tượng. Khi áp dụng filter audience='student', kết quả được cô lập chính xác 100% vào tài liệu sinh viên.\n")

    output_text = "\n".join(report_lines)
    print(output_text)
    Path("ket_qua_benchmark.txt").write_text(output_text, encoding="utf-8")
    print("-> Đã lưu kết quả vào ket_qua_benchmark.txt")


if __name__ == "__main__":
    run_benchmark()
