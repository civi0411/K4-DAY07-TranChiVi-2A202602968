# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trần Chí Vĩ (TranChiVi)
**MSSV:** 2A202602968
**Repo GitHub:** https://github.com/civi0411/K4-DAY07-TranChiVi-2A202602968
**Nhóm:** Nhóm L3A-Team01 (Chủ đề: Dịch vụ & Quy định Đại học)
**Ngày:** 19/09/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao (tiến gần về 1.0) nghĩa là góc giữa hai vector trong không gian đa chiều rất nhỏ, biểu thị hai đoạn văn bản có sự tương đồng lớn về mặt ngữ nghĩa và hướng biểu diễn, bất kể độ dài hay số lượng từ vựng của hai đoạn có khác biệt.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên diện hộ nghèo được nhà trường hỗ trợ miễn toàn bộ học phí học kỳ."
- Câu B: "Người học có hoàn cảnh gia đình khó khăn được áp dụng chính sách trợ cấp không phải đóng tiền học."
- Tại sao tương đồng: Hai câu sử dụng từ vựng hoàn toàn khác nhau (sinh viên / người học; hộ nghèo / gia đình khó khăn; miễn học phí / trợ cấp không phải đóng tiền), nhưng cùng hướng về một bản chất chính sách hỗ trợ tài chính cho người học có hoàn cảnh khó khăn.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Sinh viên phải tích lũy tối thiểu 14 tín chỉ trong mỗi học kỳ chính."
- Câu B: "Cổng ký túc xá đóng cửa vào lúc 23h00 và nghiêm cấm sử dụng bếp gas trong phòng ở."
- Tại sao khác: Câu A thuộc về quy chế đào tạo học vụ (đăng ký học phần, tín chỉ), trong khi Câu B thuộc về nội quy sinh hoạt cơ sở vật chất (ký túc xá, an toàn cháy nổ).

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Khoảng cách Euclid bị phụ thuộc mạnh vào độ lớn (magnitude/độ dài) của vector, khiến cho một câu ngắn và một đoạn văn dài cùng chủ đề bị coi là cách rất xa nhau. Ngược lại, Cosine similarity chỉ đo góc giữa hai vector (chuẩn hóa độ dài về 1), giúp đánh giá chính xác độ tương đồng về mặt ý nghĩa ngữ nghĩa mà không bị thiên vị bởi độ dài văn bản.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> Áp dụng công thức: `số lượng chunk = ceil((độ_dài_tài_liệu - độ_chồng_chéo) / (kích_thước_chunk - độ_chồng_chéo))`
> `số lượng chunk = ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.111...) = 23 chunks`.
> Kiểm tra thực nghiệm bằng `FixedSizeChunker(chunk_size=500, overlap=50).chunk('a'*10000)` cho kết quả chính xác: 23 chunks (các điểm bắt đầu: 0, 450, 900, ..., 9900).
> *Đáp án:* **23 chunks**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi tăng overlap lên 100, bước nhảy giảm xuống `500 - 100 = 400`, số chunk tăng lên `ceil((10000 - 100) / 400) = ceil(9900 / 400) = 25 chunks` (tăng thêm 2 chunks). Chúng ta muốn độ chồng chéo nhiều hơn nhằm đảm bảo các mệnh đề, số liệu hoặc từ khóa quan trọng nằm ngay ranh giới chia cắt không bị đứt đoạn, giúp mô hình retrieval không bị mất ngữ cảnh của câu khi người dùng truy vấn.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Sử dụng biểu thức chính quy (regex) có lookbehind `r'(?<=[.!?])(?:\s+|\n+)'` để tách câu ngay sau dấu kết thúc câu (`.`, `!`, `?`) kèm khoảng trắng hoặc xuống dòng mà không làm mất dấu câu gốc (tránh câu bị cụt). Sau đó gom nhóm tối đa `max_sentences_per_chunk` câu liên tiếp vào một chunk và `strip()` khoảng trắng thừa. Xử lý trường hợp chuỗi rỗng trả về `[]`, và ghi nhận hạn chế đối với từ viết tắt (`TS.`, `v.v.`) hoặc số thập phân (`3.60`).

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Triển khai phân tách đệ quy theo thứ tự ưu tiên separator `["\n\n", "\n", ". ", " ", ""]`. Base case dừng khi đoạn văn có độ dài `<= chunk_size` hoặc danh sách separator rỗng / `sep == ""` (sẽ cắt lát cứng theo `chunk_size`). Đặc biệt, sau khi tách đệ quy, thuật toán thực hiện cơ chế gộp (merge) liên tiếp các đoạn ngắn liền kề cho đến sát ngưỡng `chunk_size`, ngăn ngừa tình trạng sinh ra các chunk vụn 5–10 ký tự làm giảm chất lượng retrieval.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Sử dụng cấu trúc lưu trữ in-memory `self._store` chứa danh sách các record chuẩn hóa gồm `id`, `content`, `metadata` và `embedding`. Khi `add_documents`, hệ thống gán `metadata['doc_id']` trỏ về tài liệu gốc và tính vector embedding thông qua `_embedding_fn`. Khi `search`, vector truy vấn được tính toán và so khớp qua tích vô hướng `_dot` với tất cả các vector đã lưu (đã được chuẩn hóa L2 nên tương đương cosine similarity), sau đó sắp xếp giảm dần và lấy top_k.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` bắt buộc thực hiện **tiền lọc (pre-filtering)** trên metadata trước khi tính toán độ tương tự; nếu lọc sau (post-filtering), các tài liệu sai điều kiện có thể chiếm trọn top_k khiến kết quả trả về bị rỗng dù trong store vẫn có tài liệu hợp lệ. `delete_document` lọc bỏ mọi bản ghi có `id == doc_id` hoặc `metadata['doc_id'] == doc_id`, so sánh độ dài danh sách trước và sau khi xóa để trả về `True` nếu có xóa hoặc `False` nếu không tìm thấy.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Tác tử thực hiện tìm kiếm ngữ cảnh qua `self.store.search(question, top_k=top_k)`. Nếu kết quả rỗng, trả về thông báo an toàn; nếu có kết quả, định dạng ngữ cảnh có đánh số rõ ràng `[1] (Nguồn: doc_id): nội dung...`. Prompt được thiết kế theo cấu trúc RAG chuẩn, yêu cầu LLM trả lời bám sát ngữ cảnh, trích dẫn nguồn số tương ứng và tuyệt đối không bịa đặt thông tin nếu không có trong dữ liệu (chống hallucination).

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts ==============================
platform darwin -- Python 3.11.16, pytest-9.1.1, pluggy-1.6.0 -- /Users/mac/AITC/LAB/Lab07/K4-L3A-Data-Foundations/.venv/bin/python3
cachedir: .pytest_cache
rootdir: /Users/mac/AITC/LAB/Lab07/K4-L3A-Data-Foundations
collecting ... collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================== 42 passed in 0.05s ==============================
```

**Số lượng bài test vượt qua (pass):** **42** / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Chạy `compute_similarity(_mock_embed(A), _mock_embed(B))` trên 5 cặp câu thực tế:

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên hoàn thành nghĩa vụ học phí đúng thời hạn quy định. | Người học cần đóng tiền học đúng theo lịch của nhà trường. | cao | -0.0541 | Sai (bị âm) |
| 2 | Thư viện cho phép sinh viên mượn tối đa năm cuốn sách. | Hệ thống máy chủ sử dụng thuật toán mã hóa khóa công khai RSA. | thấp | +0.1747 | Sai (dương cao) |
| 3 | Sinh viên bị hủy học phần do không đóng học phí. | Sinh viên được miễn toàn bộ học phí do hoàn cảnh khó khăn. | cao | -0.0813 | Sai (bị âm) |
| 4 | Thời hạn mượn sách thư viện tối đa là bao nhiêu ngày? | Thời gian mượn tài liệu cho sinh viên không quá mười bốn ngày. | cao | +0.0019 | Đúng (gần 0) |
| 5 | Quy chế nội trú ký túc xá nghiêm cấm nấu ăn bằng bếp gas. | Quy chế nội trú ký túc xá nghiêm cấm nấu ăn bằng bếp gas. | cao | +1.0000 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Bất ngờ nhất là Cặp 1 (hai câu đồng nghĩa hoàn toàn) lại có score âm (-0.0541), trong khi Cặp 2 (hai câu hoàn toàn khác chủ đề) lại có điểm dương tương đối cao (+0.1747). Điều này chứng minh `MockEmbedder` chỉ băm chuỗi MD5 thành số giả ngẫu nhiên nên không thể mã hóa ngữ nghĩa thực tế. Để hệ thống RAG hoạt động chính xác trong thực tế, bắt buộc phải sử dụng các mô hình embedding học sâu (như multilingual MiniLM, OpenAI text-embedding-3 hoặc Gemini embedding) có không gian biểu diễn ngữ nghĩa liên tục dựa trên phân bố ngữ cảnh.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân trong gói `src` kết hợp chiến lược chia nhỏ của tôi (Heading/Section Chunker):

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Sinh viên được mượn tối đa bao nhiêu tài liệu về nhà và thời hạn mượn sách tham khảo tiếng Việt, ngoại văn là bao lâu? | `fpt-muon-sach-sinh-vien#2`: Mục 3 — Thời hạn mượn tài liệu: Sách tiếng Việt mượn 7 ngày, sách ngoại văn mượn 14 ngày. | 0.475 | Có (Chính xác Mục 1 & Mục 3) | Sinh viên được mượn tối đa 10 tài liệu cùng lúc; sách tiếng Việt mượn 7 ngày, sách ngoại văn mượn 14 ngày [1]. |
| 2 | Hạn ngạch được phép mượn tài liệu về nhà tối đa là bao nhiêu cuốn cùng một lúc? *(Lọc: audience=student)* | `fpt-muon-sach-sinh-vien#0`: Mục 1 — Hạn ngạch mượn: Sinh viên được mượn tối đa 10 tài liệu cùng lúc về nhà. | 0.389 | Có (Chính xác đối tượng sinh viên) | Sinh viên được mượn tối đa 10 tài liệu cùng một lúc về nhà [1]. |
| 3 | Mức phí phạt trả sách quá hạn mỗi ngày là bao nhiêu và có những phương thức thanh toán trực tuyến nào? | `fpt-phi-thu-vien#0`: Mục 1 — Phí phạt quá hạn 5.000 VNĐ/tài liệu/ngày; Mục 2 — Thanh toán qua ví FAP và cổng DNG. | 0.463 | Có (Chính xác Mục 1 & Mục 2) | Phí phạt quá hạn là 5.000 VNĐ/tài liệu/ngày; thanh toán trực tuyến qua ví FAP hoặc cổng DNG (quét QR) [1]. |
| 4 | Thời gian sử dụng phòng học nhóm tối đa là bao lâu mỗi ca và sau bao nhiêu phút không đến nhận phòng thì ca đặt sẽ bị hủy? | `fpt-phong-hoc-nhom#1`: Mục 2 — Thời gian sử dụng tối đa 2 giờ / ca; sau 15 phút không đến nhận phòng thì ca đặt sẽ tự động bị hủy. | 0.350 | Có (Chính xác Mục 2) | Thời gian sử dụng tối đa 2 giờ/ca; ca đặt sẽ tự động bị hủy sau 15 phút nếu nhóm không đến nhận phòng [1]. |
| 5 | Mỗi cuốn sách được phép gia hạn tối đa mấy lượt và bạn đọc có thể thực hiện gia hạn qua những kênh nào? | `fpt-gia-han-tai-lieu#0`: Mục 1 — Gia hạn tối đa 4 lượt; Mục 2 — 4 kênh: cổng OPAC, email, hotline 024 6680 5912, Fanpage. | 0.357 | Có (Chính xác Mục 1 & Mục 2) | Mỗi cuốn sách được gia hạn tối đa 4 lượt; gia hạn qua 4 kênh: cổng OPAC, email, điện thoại 024 6680 5912, Fanpage [1]. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **5** / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Chiến lược chia nhỏ theo Section/Heading vượt trội về tính toàn vẹn ngữ nghĩa của văn bản quy chế đại học, vì mỗi điều khoản là một đơn vị logic hoàn chỉnh. Tuy nhiên, nếu một section quá dài, việc gắn tiêu đề vào các chunk con (context prepending) của thành viên số 3 là mấu chốt giúp giữ được ngữ cảnh; đồng thời kỹ thuật metadata filtering của nhóm đã chứng minh rõ giá trị khi tách biệt hoàn hảo giữa quy định sinh viên và giảng viên.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
