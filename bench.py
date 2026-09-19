"""
Benchmark Script for Lab 07: Data Foundations (K4-L3A)
Compares chunking strategies on the university regulations corpus.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from src.chunking import FixedSizeChunker, RecursiveChunker, SentenceChunker
from src.embeddings import _mock_embed
from src.models import Document
from src.store import EmbeddingStore


class HeadingChunker:
    """
    Chunk Markdown regulations by section headings (e.g. ## Điều 1, ## Điều 2).
    Keeps section title attached to sub-chunks if section exceeds max_section_size.
    """

    def __init__(self, max_section_size: int = 450) -> None:
        self.max_section_size = max_section_size
        self._fallback = RecursiveChunker(chunk_size=max_section_size)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        # Split at markdown headings (## or #)
        sections = re.split(r"(?m)(?=^#{1,3}\s+)", text.strip())
        chunks: list[str] = []
        for sec in sections:
            sec = sec.strip()
            if not sec:
                continue
            if len(sec) <= self.max_section_size:
                chunks.append(sec)
            else:
                lines = sec.split("\n", 1)
                header = lines[0].strip()
                body = lines[1].strip() if len(lines) > 1 else ""
                sub_chunks = self._fallback.chunk(body)
                for sc in sub_chunks:
                    chunks.append(f"{header}\n{sc}")
        return chunks


BENCHMARK_QUERIES = [
    {
        "id": 1,
        "query": "Sinh viên có học lực bình thường phải đăng ký tối thiểu bao nhiêu tín chỉ và rút học phần trước tuần thứ mấy?",
        "filter": None,
        "gold_doc": "dang-ky-hoc-phan",
        "gold_keywords": ["14 tín chỉ", "tuần thứ 4"],
        "gold_answer": "Sinh viên có học lực bình thường đăng ký tối thiểu 14 tín chỉ (tối đa 24 tín chỉ) và thời hạn rút học phần là trước khi kết thúc tuần thứ 4 của học kỳ.",
    },
    {
        "id": 2,
        "query": "Thời hạn đóng học phí học kỳ là khi nào và đối tượng nào được miễn 100% học phí?",
        "filter": None,
        "gold_doc": "hoc-phi-va-mien-giam",
        "gold_keywords": ["tuần thứ 3", "miễn 100%"],
        "gold_answer": "Hạn nộp học phí trước 17h00 thứ Sáu của tuần thứ 3 trong học kỳ; sinh viên thuộc hộ nghèo hoặc mồ côi cả cha lẫn mẹ được miễn 100% học phí.",
    },
    {
        "id": 3,
        "query": "Điều kiện về GPA và điểm rèn luyện để đạt học bổng khuyến khích loại Xuất sắc là gì?",
        "filter": None,
        "gold_doc": "hoc-bong-khuyen-khich",
        "gold_keywords": ["3.60", "90"],
        "gold_answer": "Học bổng Xuất sắc yêu cầu GPA từ 3.60 đến 4.00, điểm rèn luyện từ 90 điểm trở lên, tích lũy tối thiểu 15 tín chỉ và không có môn nào dưới điểm C.",
    },
    {
        "id": 4,
        "query": "Thời hạn mượn sách thư viện tối đa là bao nhiêu ngày và được mượn cùng lúc bao nhiêu cuốn?",
        "filter": {"audience": "student"},
        "gold_doc": "muon-tra-thu-vien-sinh-vien",
        "gold_keywords": ["5 cuốn", "14 ngày"],
        "gold_answer": "Sinh viên được mượn tối đa 5 cuốn sách giáo trình/tham khảo trong 14 ngày (gia hạn 1 lần 7 ngày).",
    },
    {
        "id": 5,
        "query": "Thủ tục và lệ phí xin phúc khảo bài thi kết thúc học phần như thế nào, trường hợp nào được hoàn tiền?",
        "filter": None,
        "gold_doc": "phuc-khao-diem-thi",
        "gold_keywords": ["7 ngày làm việc", "50.000 đồng", "hoàn trả lại 100%"],
        "gold_answer": "Sinh viên nộp đơn phúc khảo trong 7 ngày làm việc kể từ ngày công bố điểm, lệ phí 50.000 đồng/bài; được hoàn 100% lệ phí nếu kết quả tăng điểm sau phúc khảo.",
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


def build_store(raw_docs: list[dict[str, Any]], chunker: Any) -> tuple[EmbeddingStore, int]:
    store = EmbeddingStore(collection_name="bench_store", embedding_fn=_mock_embed)
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

    # Check presence of gold doc and content match
    top_doc_ids = [r["metadata"].get("doc_id") for r in results]
    gold_in_top3 = gold_doc in top_doc_ids
    gold_at_top1 = len(top_doc_ids) > 0 and top_doc_ids[0] == gold_doc

    # Check if context contains keywords
    context_text = " ".join([r["content"] for r in results])
    keywords_matched = sum(1 for kw in gold_keywords if kw.lower() in context_text.lower())
    content_matches = keywords_matched == len(gold_keywords)

    # 2 points: gold in top-1 + content contains answer
    # 1 point: gold in top-2/3 or partial content
    # 0 points: not retrieved in top-3
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
    data_dir = Path("data/university")
    raw_docs = load_raw_documents(data_dir)
    print(f"Loaded {len(raw_docs)} raw documents from {data_dir}")

    strategies = {
        "Member 1: SentenceChunker": SentenceChunker(max_sentences_per_chunk=3),
        "Member 2: RecursiveChunker": RecursiveChunker(chunk_size=300),
        "Member 3: HeadingChunker": HeadingChunker(max_section_size=400),
        "Baseline: FixedSizeChunker": FixedSizeChunker(chunk_size=250, overlap=40),
    }

    report_lines = []
    report_lines.append("================================================================================")
    report_lines.append("                     KẾT QUẢ BENCHMARK RETRIEVAL LAB 07 (L3A)                  ")
    report_lines.append("================================================================================\n")

    overall_results = {}
    for strat_name, chunker in strategies.items():
        store, chunk_count = build_store(raw_docs, chunker)
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
    report_lines.append(f"{'Chiến lược':<32} | {'Số Chunks':<10} | {'Điểm (/10)':<10} | {'Đánh giá'}")
    report_lines.append("-" * 75)
    for s_name, res in overall_results.items():
        report_lines.append(f"{s_name:<32} | {res['chunk_count']:<10} | {res['total_points']}/10{'':<6} | {'Tốt' if res['total_points']>=8 else 'Trung bình'}")
    report_lines.append("\n" + "=" * 80 + "\n")

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
        report_lines.append("-" * 80)

    # A/B Test for Query 4 (Library borrowing query: student vs faculty)
    report_lines.append("\n### BẰNG CHỨNG THỰC NGHIỆM A/B: METADATA FILTERING TRÊN CÂU HỎI 4")
    q4 = BENCHMARK_QUERIES[3]
    h_store, _ = build_store(raw_docs, strategies["Member 3: HeadingChunker"])
    res_filtered = evaluate_query(h_store, q4, use_filter=True)
    res_unfiltered = evaluate_query(h_store, q4, use_filter=False)

    report_lines.append(f"Câu hỏi: {q4['query']}")
    report_lines.append("\n[1] KHI CÓ FILTER (metadata_filter={'audience': 'student'}):")
    for idx, r in enumerate(res_filtered["results"], start=1):
        report_lines.append(f"  Rank {idx}: doc_id={r['metadata'].get('doc_id')}, audience={r['metadata'].get('audience')}, score={r['score']:.3f}")
        report_lines.append(f"         Preview: {r['content'].replace(chr(10), ' ')[:100]}...")

    report_lines.append("\n[2] KHI KHÔNG CÓ FILTER (Unfiltered):")
    for idx, r in enumerate(res_unfiltered["results"], start=1):
        report_lines.append(f"  Rank {idx}: doc_id={r['metadata'].get('doc_id')}, audience={r['metadata'].get('audience')}, score={r['score']:.3f}")
        report_lines.append(f"         Preview: {r['content'].replace(chr(10), ' ')[:100]}...")

    report_lines.append("\nKết luận A/B: Filter audience=student loại trừ triệt để tài liệu giảng viên (120 ngày, 20 cuốn), bảo đảm kết quả trả về chính xác hạn mức sinh viên (14 ngày, 5 cuốn).\n")

    output_text = "\n".join(report_lines)
    print(output_text)
    Path("ket_qua_benchmark.txt").write_text(output_text, encoding="utf-8")
    print("-> Đã lưu kết quả vào ket_qua_benchmark.txt")


if __name__ == "__main__":
    run_benchmark()
