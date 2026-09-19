# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store (Nhóm 18)

**Nhóm:** Nhóm 18 (Chủ đề: Dịch vụ & Nội quy Thư viện - University Library Services)
**Thành viên:**
1. Tuấn — Data Lead (Trưởng ban Dữ liệu)
2. Khánh — Benchmark Lead (Trưởng ban Khảo thí)
3. Trần Chí Vĩ (TranChiVi - MSSV: 2A202602968) — Strategy Lead (Trưởng ban Chiến lược)
4. Nhật — Report & Demo Lead (Trưởng ban Báo cáo & Thuyết trình)

**Ngày:** 19/09/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Quy định và Dịch vụ Thư viện Đại học FPT (FPTU Library Regulations & Services).

**Tại sao nhóm chọn chủ đề này?**
> Thư viện Đại học FPT có hệ thống quy chế, dịch vụ và chính sách phân cấp cực kỳ rõ ràng giữa các đối tượng độc giả (sinh viên, giảng viên, toàn trường). Dữ liệu chứa rất nhiều số liệu định lượng chuẩn xác (hạn mức tài liệu, số ngày mượn, mức phí phạt, thời gian sử dụng phòng học nhóm, lượt gia hạn) và các quy trình hành chính (thanh toán FAP/DNG, kênh liên hệ). Đây là ngữ cảnh lý tưởng để chứng minh sức mạnh của phân mảnh theo tiêu đề (Heading Chunking) và kỹ thuật tiền lọc siêu dữ liệu (Metadata Pre-filtering).

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Quy định mượn trả tài liệu cho sinh viên tại Thư viện FPT | `https://library.fpt.edu.vn/Pages/Index/9` | 2026-09-19 / 2021-05-14 | 1,240 | `audience: student`, `dept: library`, `cat: circulation` |
| 2 | Chính sách mượn trả tài liệu cho cán bộ giảng viên tại Thư viện FPT | `https://library.fpt.edu.vn/Pages/Index/9` | 2026-09-19 / 2021-05-14 | 1,158 | `audience: faculty`, `dept: library`, `cat: circulation` |
| 3 | Quy định phí thư viện và hướng dẫn thanh toán phí phạt quá hạn FPT | `https://library.fpt.edu.vn/Pages/Index/18` | 2026-09-19 / 2024-04-12 | 1,220 | `audience: student`, `dept: library`, `cat: fee` |
| 4 | Quy định đặt và sử dụng phòng học nhóm tại Thư viện FPT | `https://library.fpt.edu.vn/Pages/Index/17` | 2026-09-19 / 2023-09-22 | 1,267 | `audience: student`, `dept: library`, `cat: facility` |
| 5 | Hướng dẫn các phương thức gia hạn sách tại Thư viện FPT | `https://library.fpt.edu.vn/Pages/Index/1` | 2026-09-19 / 2021-05-14 | 1,303 | `audience: all`, `dept: library`, `cat: circulation` |
| 6 | Thời gian hoạt động và lịch phục vụ mượn trả tại Thư viện FPT | `https://library.fpt.edu.vn/Pages/Index/3` | 2026-09-19 / 2021-05-14 | 1,166 | `audience: all`, `dept: library`, `cat: schedule` |
| 7 | Nội quy chung bạn đọc tại Thư viện Đại học FPT | `https://library.fpt.edu.vn/Pages/Index/15` | 2026-09-19 / 2022-12-12 | 1,210 | `audience: all`, `dept: library`, `cat: policy` |
| 8 | Chính sách tiếp cận tài nguyên điện tử và dịch vụ số FPTU | `https://library.fpt.edu.vn/Pages/Index/22` | 2026-09-19 / 2025-09-29 | 1,246 | `audience: all`, `dept: library`, `cat: digital-resource` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.
- [x] Tách riêng rẽ giữa quy định mượn sách sinh viên (`audience: student`) và giảng viên (`audience: faculty`) để phục vụ thực nghiệm lọc metadata A/B bắt buộc của Lab 07.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | `str` | `fpt-muon-sach-sinh-vien` | Định danh tài liệu gốc; dùng để truy vết nguồn gốc và phục vụ hàm `delete_document` toàn bộ chunks. |
| `audience` | `str` | `student`, `faculty`, `all` | **Trọng tâm Lab 07**: Phân tách đối tượng độc giả, ngăn chặn xung đột giữa hạn ngạch của sinh viên và giảng viên. |
| `department` | `str` | `library` | Lọc theo đơn vị quản lý chức năng của trường. |
| `category` | `str` | `circulation`, `fee`, `facility` | Phân loại nghiệp vụ thư viện (mượn trả, phí phạt, cơ sở vật chất) để thu hẹp không gian tìm kiếm. |
| `source_url` | `str` | `https://library.fpt.edu.vn/...` | Cung cấp liên kết kiểm chứng nguồn gốc cho người đọc. |
| `retrieved_at` | `str` | `2026-09-19` | Quản lý thời điểm thu thập dữ liệu, bảo đảm tính tươi mới của quy định. |
| `document_version` | `str` | `2021-05-14` | Ghi nhận phiên bản/ngày ban hành văn bản quy định chính thức. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

### Đánh giá chiến lược phân rã văn bản (Chunking Strategies)

Để tối ưu hóa Vector Store, nhóm đã tiến hành phân rã tài liệu bằng 4 chiến lược khác nhau. Dưới đây là bảng phân tích so sánh giữa các thành viên:

| Thành viên phụ trách | Tên Chiến lược | Số lượng Chunk sinh ra | Điểm Benchmark | Đánh giá & Nhận xét sơ bộ |
|---|---|:---:|:---:|---|
| **Tuấn (Data)** | `SentenceChunker` | 48 | **6/10** | Cắt theo từng câu nên số lượng chunk sinh ra nhiều nhất. Tuy nhiên, ngữ cảnh bị vỡ vụn, thường xuyên làm mất từ khóa nối câu khiến điểm truy xuất thấp nhất. |
| **Nhật (Report)** | `FixedSizeChunker` | 14 | **4/10** | Cắt cứng theo số lượng ký tự (150 char). Ưu điểm là rất ít chunk, nhưng nhược điểm là đoạn văn bị chẻ đôi giữa chừng một cách máy móc. Câu 4 và 5 bị cắt đứt đoạn chứa Keyword quan trọng nên lấy sai hoàn toàn. |
| **Khánh (Benchmark)** | `RecursiveChunker` | 31 | **8/10** | Cắt đệ quy rất linh hoạt, dung hòa tốt giữa số lượng chunk và ngữ cảnh. Lấy được điểm tuyệt đối ở 4/5 câu hỏi. |
| **Vĩ (Strategy)** | `HeadingChunker` | 32 | **9/10** | **Chiến lược xuất sắc nhất.** Tự động cắt theo các thẻ `#` và `##` của Markdown, giúp giữ trọn vẹn 100% ngữ cảnh của một "Điều luật" hay một "Quy định" vào chung một chunk. |

---

### Chiến lược của từng thành viên (Phân công không trùng lặp)

**Thành viên 1 — Tuấn (Data Lead)**
- **Loại chiến lược:** SentenceChunker (`by_sentences`, `max_sentences_per_chunk=3`)
- **Mô tả & lý do chọn cho chủ đề này:** Tách văn bản dựa trên ranh giới ngữ pháp câu hoàn chỉnh. Các câu quy định thư viện luôn chứa cấu trúc điều kiện chặt chẽ ("Khi mượn tài liệu... sinh viên phải..."). Giữ trọn câu giúp không làm đứt đoạn nghĩa.
- **Code snippet:**
```python
class SentenceChunker:
    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])(?:\s+|\n+)', text.strip()) if s.strip()]
        chunks = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            chunk = " ".join(sentences[i : i + self.max_sentences_per_chunk]).strip()
            if chunk:
                chunks.append(chunk)
        return chunks
```

**Thành viên 2 — Khánh (Benchmark Lead)**
- **Loại chiến lược:** RecursiveChunker (`recursive`, `chunk_size=300`)
- **Mô tả & lý do chọn:** Phân đoạn đệ quy theo thứ tự `["\n\n", "\n", ". ", " ", ""]`. Ưu tiên bảo toàn các đoạn văn hoàn chỉnh hoặc các danh sách gạch đầu dòng, chỉ chia nhỏ khi vượt quá 300 ký tự và gộp các mảnh ngắn để kích thước đồng đều.
- **Code snippet:**
```python
class RecursiveChunker:
    def __init__(self, separators: list[str] | None = None, chunk_size: int = 300) -> None:
        self.separators = ["\n\n", "\n", ". ", " ", ""] if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        return self._split(text, list(self.separators))
```

**Thành viên 3 — Trần Chí Vĩ (TranChiVi - MSSV: 2A202602968) (Strategy Lead)**
- **Loại chiến lược:** HeadingChunker (`heading_section`, `max_section_size=400`)
- **Mô tả & lý do chọn:** Cắt tài liệu trực tiếp theo cấu trúc tiêu đề tự nhiên của văn bản thư viện (`## Mục 1`, `## Mục 2...`). Mỗi mục là một thực thể nghiệp vụ độc lập (Hạn ngạch, Thời hạn, Phí phạt, Hủy ca). Khi một mục dài quá 400 ký tự, chunker tự động phân tách nhỏ nhưng luôn gắn kèm dòng tiêu đề cha (Context Prepending) để đảm bảo chunk con không mất ngữ cảnh.
- **Code snippet:**
```python
class HeadingChunker:
    def __init__(self, max_section_size: int = 400) -> None:
        self.max_section_size = max_section_size
        self._fallback = RecursiveChunker(chunk_size=max_section_size)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        sections = re.split(r"(?m)(?=^#{1,3}\s+)", text.strip())
        chunks = []
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
```

**Thành viên 4 — Nhật (Report & Demo Lead)**
- **Loại chiến lược:** FixedSizeChunker (`fixed_size`, `chunk_size=150`)
- **Mô tả & lý do chọn:** Phương án so sánh đối chiếu cắt cứng theo số lượng ký tự (150 char) nhằm kiểm tra xem việc chia cắt máy móc có gây đứt gãy từ khóa hay không.

---

### Chiến lược nào tốt nhất cho chủ đề này? Tại sao?
> **Chiến lược `HeadingChunker` của Vĩ là xuất sắc và tối ưu nhất (9/10 điểm)** cho văn bản quy định thư viện. Lý do: mỗi điều khoản quy định (như hạn ngạch mượn, mức phí phạt, quy định hủy phòng học nhóm) được người soạn thảo đóng gói thành từng mục logic độc lập. `HeadingChunker` tôn trọng tuyệt đối ranh giới này, giúp các số liệu (10 tài liệu, 5.000 VNĐ, 2 giờ, 15 phút, 4 lượt) nằm trọn vẹn trong chunk, không bao giờ bị cắt rời khỏi tiêu đề điều khoản.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Kết quả Benchmark (5 câu hỏi truy xuất)

Nhóm sử dụng bộ 5 câu hỏi chuẩn để test hệ thống. Điểm số dưới đây lấy từ chiến lược tốt nhất (`HeadingChunker` của Vĩ):

* **Câu 1 (Fact & Numbers):** *"Sinh viên được mượn tối đa bao nhiêu tài liệu về nhà và thời hạn mượn sách tham khảo tiếng Việt, ngoại văn là bao lâu?"*
  * **Đáp án chuẩn:** Sinh viên được mượn tối đa 10 tài liệu cùng lúc về nhà; sách tiếng Việt mượn 7 ngày; sách ngoại văn và song ngữ mượn 14 ngày.
  * **Kết quả:** Đạt **1/2 điểm**. (Hệ thống lấy đúng ý nhưng top-1 bị nhầm lẫn nhẹ sang quy định của giảng viên do không có filter).
* **Câu 2 (Conditions):** *"Hạn ngạch được phép mượn tài liệu về nhà tối đa là bao nhiêu cuốn cùng một lúc?"*
  * **Đáp án chuẩn:** 10 tài liệu đối với sinh viên (nếu là cán bộ giảng viên thì được mượn tối đa 20 tài liệu).
  * **Kết quả:** Đạt **2/2 điểm** tuyệt đối nhờ sử dụng Metadata Filter `{"audience": "student"}`.
* **Câu 3 (Finance):** *"Mức phí phạt trả sách quá hạn mỗi ngày là bao nhiêu và có những phương thức thanh toán trực tuyến nào?"*
  * **Đáp án chuẩn:** Phí phạt quá hạn là 5.000 VNĐ / tài liệu / ngày; có 2 phương thức thanh toán trực tuyến: qua ví FAP và qua cổng DNG.
  * **Kết quả:** Đạt **2/2 điểm**. Bốc chính xác `fpt-phi-thu-vien`.
* **Câu 4 (Facility):** *"Thời gian sử dụng phòng học nhóm tối đa là bao lâu mỗi ca và sau bao nhiêu phút không đến nhận phòng thì ca đặt sẽ bị hủy?"*
  * **Đáp án chuẩn:** Thời gian sử dụng tối đa 2 giờ / ca; sau 15 phút nếu nhóm không đến nhận phòng thì ca đặt sẽ tự động bị hủy.
  * **Kết quả:** Đạt **2/2 điểm**. Trích xuất đúng con số `2 giờ` và `15 phút`.
* **Câu 5 (Channels):** *"Mỗi cuốn sách được phép gia hạn tối đa mấy lượt và bạn đọc có thể thực hiện gia hạn qua những kênh nào?"*
  * **Đáp án chuẩn:** Mỗi cuốn sách được phép gia hạn tối đa 4 lượt; gia hạn qua 4 kênh: OPAC, email, 024 6680 5912, Fanpage.
  * **Kết quả:** Đạt **2/2 điểm**.

👉 **Tổng điểm hệ thống: 9/10 điểm.**

---

### Bằng chứng thực nghiệm A/B: Metadata Filtering
*(Chứng minh sự cần thiết của lọc siêu dữ liệu trong kiến trúc Multi-tenant)*

**Câu hỏi Test:** *"Hạn ngạch được phép mượn tài liệu về nhà tối đa là bao nhiêu cuốn cùng một lúc?"*

* **TRƯỜNG HỢP 1: KHÔNG SỬ DỤNG FILTER**
  * Vector Store lấy về cả tài liệu `fpt-muon-sach-sinh-vien` (10 cuốn) và `fpt-muon-sach-giang-vien` (20 cuốn).
  * Tài liệu của giảng viên nằm chễm chệ ở Rank 2 với score khá cao (0.275). Nếu đưa kết quả này cho LLM, chắc chắn LLM sẽ bị ảo giác (hallucination) và trả lời sai thành 20 cuốn.
* **TRƯỜNG HỢP 2: CÓ SỬ DỤNG FILTER `{"audience": "student"}`**
  * Vector Store loại bỏ hoàn toàn tài liệu của giảng viên từ trước khi tính toán cosine similarity (Pre-filtering).
  * Hệ thống cô lập 100% dữ liệu, lấy về đúng tài liệu sinh viên (Score: 0.395).

**💡 Kết luận:** Bắt buộc phải triển khai tính năng Metadata Filtering để đảm bảo an toàn thông tin và tính chính xác, không cho phép sinh viên đọc chéo quy định của giảng viên.

---

### Phân tích lỗi (Failure Case Analysis)

Nhóm đã phát hiện một rủi ro kiến trúc vô cùng lớn khi sử dụng `SentenceChunker` (Thuật toán của Tuấn).

**1. Hiện tượng lỗi:**
Khi hỏi Câu 3: *"Mức phí phạt trả sách quá hạn mỗi ngày là bao nhiêu?"*, chiến lược `SentenceChunker` đạt 0/2 điểm. Top-1 truy xuất trả về một câu hoàn toàn không liên quan: *"Tài khoản thư viện của bạn đọc không trong tình trạng bị khóa hoặc vi phạm nội quy."*

**2. Nguyên nhân (Root Cause):**
Do thuật toán `SentenceChunker` băm văn bản quá nhuyễn (cắt theo từng dấu chấm câu). Câu văn chứa con số "5.000 VNĐ" bị tách rời hoàn toàn khỏi câu văn chứa chữ "Mức phí phạt quá hạn". Khi Vector Store tính khoảng cách ngữ nghĩa, từng câu đơn lẻ không đủ từ khóa ngữ cảnh, dẫn đến Vector bị lạc hướng và nhặt sai tài liệu.

**3. Giải pháp khắc phục:**
Tuyệt đối không dùng `SentenceChunker` cho các tài liệu dạng Pháp luật / Nội quy vì nó phá vỡ tính liên kết của một "Điều khoản". Phải sử dụng `HeadingChunker` (Giữ nguyên văn bản từ thẻ Header này đến thẻ Header tiếp theo) để gom trọn vẹn ngữ cảnh vào một Vector duy nhất.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
1. **Kiến trúc dữ liệu quyết định chất lượng RAG:** Cấu trúc tài liệu (Domain-specific Heading Chunking) vượt trội hơn chia nhỏ ngẫu nhiên theo ký tự. Với văn bản quy định, mỗi Mục là một đơn vị ý nghĩa khép kín.
2. **Sức mạnh của Tiền lọc Metadata (Pre-filtering):** Phân chia rõ `audience` giúp giải quyết triệt để vấn đề xung đột hạn ngạch giữa sinh viên (10 cuốn) và giảng viên (20 cuốn).
3. **Thực nghiệm A/B trực quan:** Demo trực tiếp tại quầy phản biện: so sánh câu hỏi 2 khi bật và tắt filter để giảng viên thấy rõ sự khác biệt trong kết quả top-k.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ ứng dụng thêm cơ chế **Contextual Chunk Headers** (tự động đính kèm tên tài liệu và breadcrumb vào đầu từng chunk) và kết hợp **Hybrid Search** (kết hợp BM25 cho từ khóa chính xác như số điện thoại, tên cổng DNG với vector embedding).

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |

