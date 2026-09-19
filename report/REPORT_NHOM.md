# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Nhóm L3A-Team01
**Thành viên:**
1. [Thành viên 1] — Data Lead (Trưởng ban Dữ liệu)
2. [Thành viên 2] — Benchmark Lead (Trưởng ban Khảo thí)
3. Trần Chí Vĩ (TranChiVi - MSSV: 2A202602968) — Strategy Lead (Trưởng ban Chiến lược)
4. [Thành viên 4] — Report & Demo Lead (Trưởng ban Báo cáo & Thuyết trình)

**Ngày:** 19/09/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Dịch vụ & Quy định Đại học (Đăng ký học phần, Học phí, Học bổng, Thư viện, Ký túc xá, Phúc khảo điểm).

**Tại sao nhóm chọn chủ đề này?**
> Văn bản quy chế và dịch vụ học vụ đại học có tính chuẩn tắc cao, kết cấu phân tầng rõ rệt (Điều khoản, Tiêu chuẩn, Định mức định lượng). Chủ đề này đặc biệt phân tách đối tượng áp dụng rõ ràng giữa sinh viên (`student`) và cán bộ giảng viên (`faculty`), là ngữ cảnh hoàn hảo để kiểm chứng tính ưu việt của phân đoạn theo tiêu đề (Heading Chunking) và kỹ thuật lọc siêu dữ liệu (Metadata Pre-filtering).

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Quy định đăng ký và rút học phần | `https://vlearn.edu.vn/quy-dinh/dang-ky-hoc-phan` | 2026-09-18 / 2026.1 | 1,234 | `audience: student`, `dept: academic-affairs`, `cat: registration` |
| 2 | Quy định thu nộp học phí và chính sách miễn giảm | `https://vlearn.edu.vn/tai-chinh/hoc-phi-mien-giam` | 2026-09-18 / 2026.1 | 1,359 | `audience: student`, `dept: finance`, `cat: tuition` |
| 3 | Quy chế xét cấp học bổng khuyến khích học tập | `https://vlearn.edu.vn/cong-tac-sinh-vien/hoc-bong-khuyen-khich` | 2026-09-18 / 2026.2 | 1,292 | `audience: student`, `dept: student-affairs`, `cat: scholarship` |
| 4 | Quy định mượn trả tài liệu thư viện (Sinh viên) | `https://vlearn.edu.vn/thu-vien/quy-dinh-sinh-vien` | 2026-09-18 / 2026.1 | 1,275 | `audience: student`, `dept: library`, `cat: library` |
| 5 | Quy định mượn trả tài liệu thư viện (Giảng viên) | `https://vlearn.edu.vn/thu-vien/quy-dinh-giang-vien` | 2026-09-18 / 2026.1 | 1,388 | `audience: faculty`, `dept: library`, `cat: library` |
| 6 | Quy chế quản lý nội trú ký túc xá sinh viên | `https://vlearn.edu.vn/ky-tuc-xa/quy-che-noi-tru` | 2026-09-18 / 2026.1 | 1,300 | `audience: student`, `dept: dormitory`, `cat: housing` |
| 7 | Quy trình phúc khảo điểm thi kết thúc học phần | `https://vlearn.edu.vn/khao-thi/quy-trinh-phuc-khao` | 2026-09-18 / 2026.1 | 1,343 | `audience: student`, `dept: testing-quality`, `cat: examination` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.
- [x] Phân chia `audience` rõ rệt với 2 giá trị khác nhau (`student` và `faculty`), tách riêng file quy định mượn sách thư viện của sinh viên và giảng viên để phục vụ bài toán lọc metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | `str` | `muon-tra-thu-vien-sinh-vien` | Định danh tài liệu gốc; dùng để truy vết nguồn gốc và cho phép `delete_document` toàn bộ chunks. |
| `audience` | `str` | `student`, `faculty` | Phân loại đối tượng thụ hưởng; giải quyết triệt để vấn đề truy vấn mơ hồ về quy định mượn sách. |
| `department` | `str` | `library`, `finance`, `academic-affairs` | Cho phép lọc theo phòng ban chức năng, tránh xung đột câu hỏi giữa các nghiệp vụ. |
| `category` | `str` | `scholarship`, `tuition`, `registration` | Phân loại chủ đề học vụ để thu hẹp phạm vi tìm kiếm của tác tử. |
| `source_url` | `str` | `https://vlearn.edu.vn/...` | Cung cấp đường dẫn nguồn để trích dẫn kiểm chứng độ tin cậy của câu trả lời. |
| `retrieved_at` | `str` | `2026-09-18` | Quản lý độ tươi mới của dữ liệu, phục vụ kiểm định thời hạn hiệu lực. |
| `document_version` | `str` | `2026.1` | Quản lý phiên bản quy chế áp dụng, tránh lẫn lộn các thông tư cũ và mới. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu đại diện:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `dang-ky-hoc-phan.md` (927 ký tự) | FixedSizeChunker (`fixed_size`, size=200, overlap=20) | 6 | 171.2 | Kém (bị cắt ngang câu, mất số liệu tín chỉ ở mép chunk) |
| | SentenceChunker (`by_sentences`, max=3) | 2 | 462.0 | Tương đối (câu trọn vẹn nhưng chunk dài, lẫn nhiều điều khoản) |
| | RecursiveChunker (`recursive`, size=200) | 7 | 130.9 | Trung bình (cắt theo dòng/câu, chunk hơi ngắn) |
| `muon-tra-thu-vien-sinh-vien.md` (947 ký tự) | FixedSizeChunker (`fixed_size`, size=200, overlap=20) | 6 | 174.5 | Kém (cắt đứt cụm từ "14 ngày" và "gia hạn 7 ngày") |
| | SentenceChunker (`by_sentences`, max=3) | 2 | 472.0 | Khá (giữ trọn câu quy định mượn) |
| | RecursiveChunker (`recursive`, size=200) | 8 | 117.0 | Trung bình (chia nhỏ các điều khoản) |
| `hoc-phi-va-mien-giam.md` (1044 ký tự) | FixedSizeChunker (`fixed_size`, size=200, overlap=20) | 6 | 190.7 | Kém (mất tiêu đề Điều 3 ở cuối chunk 4) |
| | SentenceChunker (`by_sentences`, max=3) | 3 | 346.7 | Khá (giữ đúng ranh giới ngữ pháp) |
| | RecursiveChunker (`recursive`, size=200) | 8 | 129.4 | Khá (phân đoạn theo các gạch đầu dòng tốt) |

---

### Chiến lược của từng thành viên

**Thành viên 1 — [Thành viên 1] (Data Lead)**
- **Loại chiến lược:** SentenceChunker (`by_sentences`, `max_sentences_per_chunk=3`)
- **Mô tả & lý do chọn cho chủ đề này:** Tách văn bản dựa trên ranh giới ngữ pháp của câu hoàn chỉnh. Các câu văn quy chế luôn có cấu trúc chủ - vị và điều kiện đầy đủ ("Sinh viên được phép... nếu..."). Việc giữ trọn vẹn câu giúp chunk không bị cụt ý như FixedSize.
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

**Thành viên 2 — [Thành viên 2] (Benchmark Lead)**
- **Loại chiến lược:** RecursiveChunker (`recursive`, `chunk_size=300`)
- **Mô tả & lý do chọn:** Chia phân tầng đệ quy ưu tiên `["\n\n", "\n", ". ", " ", ""]`. Chiến lược này ưu tiên giữ trọn đoạn văn hoặc các ý liệt kê trong điều khoản, chỉ chia nhỏ khi đoạn quá dài và tự động gộp các mảnh ngắn để kích thước chunk đồng đều quanh ngưỡng 300 ký tự.
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
- **Mô tả & lý do chọn:** Cắt tài liệu trực tiếp theo các mục tiêu đề Markdown (`## Điều 1`, `## Điều 2...`). Đây là cấu trúc tự nhiên do người soạn thảo quy định đặt ra, mỗi Điều là một thực thể thông tin độc lập. Khi một điều quá dài, chunker đệ quy cắt nhỏ nhưng gắn kèm tiêu đề gốc vào đầu mỗi chunk con để không bị mất ngữ cảnh (Context Prepending).
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

**Thành viên 4 — [Thành viên 4] (Report & Demo Lead)**
- **Loại chiến lược:** Tuned FixedSizeChunker (`fixed_size`, `chunk_size=250`, `overlap=40`)
- **Mô tả & lý do chọn:** Dùng làm phương án so sánh đường cơ sở có tối ưu hóa overlap. Bằng cách thiết lập overlap 40 ký tự trên kích thước 250 ký tự, chiến lược này khắc phục nhược điểm mất thông tin ở biên của FixedSize không có overlap.

---

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Thành viên 1 | `SentenceChunker` (max 3 câu) | 7/10 | Giữ câu ngữ pháp trọn vẹn, không bị đứt câu lơ lửng. | Dễ gộp nhầm 2 điều khoản khác nhau vào chung một chunk nếu các điều ngắn. |
| Thành viên 2 | `RecursiveChunker` (size 300) | 8/10 | Cân bằng kích thước tốt, tôn trọng cấu trúc đoạn văn `\n\n`. | Có thể cắt trúng giữa một danh sách điều kiện liệt kê. |
| Thành viên 3 (Trần Chí Vĩ) | `HeadingChunker` (size 400) | 10/10 | **Tối ưu nhất**: Mỗi chunk là 1 Điều luật hoàn chỉnh, ngữ cảnh trọn vẹn 100%. | Phụ thuộc vào tài liệu có cấu trúc Markdown chuẩn (`#`, `##`). |
| Thành viên 4 | `FixedSizeChunker` (250/40) | 6/10 | Đơn giản, độ dài đồng nhất, có overlap giảm đứt gãy từ. | Vẫn cắt ngang câu ngẫu nhiên theo số ký tự, nhiễu ranh giới ngữ nghĩa. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> **Chiến lược `HeadingChunker` (của Thành viên 3) là tốt nhất** cho chủ đề quy chế và dịch vụ đại học. Lý do cốt lõi: văn bản quy chế mang cấu trúc pháp quy rõ ràng, trong đó mỗi "Điều" hoặc "Mục" là một đơn vị ý nghĩa độc lập chứa đựng đầy đủ chủ thể, điều kiện và chế tài. Khi truy vấn tìm kiếm một thông tin cụ thể (ví dụ: điều kiện miễn giảm học phí hay hạn mức mượn sách), toàn bộ điều khoản liên quan nằm trọn vẹn trong duy nhất một chunk, giúp tác tử RAG trích xuất số liệu chính xác tuyệt đối mà không bị đứt đoạn hay pha lẫn nội dung của điều khoản khác.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Sinh viên có học lực bình thường phải đăng ký tối thiểu bao nhiêu tín chỉ và rút học phần trước tuần thứ mấy? | Sinh viên học lực bình thường phải đăng ký tối thiểu 14 tín chỉ (tối đa 24 tín chỉ) và thời hạn nộp đơn rút học phần là trước khi kết thúc tuần thứ 4 của học kỳ chính. | `dang-ky-hoc-phan#1` (Điều 1 & Điều 2) |
| 2 | Thời hạn đóng học phí học kỳ là khi nào và đối tượng nào được miễn 100% học phí? | Hạn nộp học phí là trước 17h00 thứ Sáu của tuần thứ 3 trong học kỳ. Sinh viên thuộc hộ nghèo và sinh viên mồ côi cả cha lẫn mẹ được miễn 100% học phí. | `hoc-phi-va-mien-giam#1` & `#2` (Điều 1 & Điều 3) |
| 3 | Điều kiện về GPA và điểm rèn luyện để đạt học bổng khuyến khích loại Xuất sắc là gì? | Học bổng Xuất sắc yêu cầu điểm trung bình học kỳ (GPA) đạt từ 3.60 đến 4.00, điểm rèn luyện đạt từ 90 điểm trở lên, tích lũy tối thiểu 15 tín chỉ và không có môn nào dưới điểm C. | `hoc-bong-khuyen-khich#2` (Điều 2) |
| 4 | Thời hạn mượn sách thư viện tối đa là bao nhiêu ngày và được mượn cùng lúc bao nhiêu cuốn? *(Yêu cầu lọc: `audience="student"`)* | Sinh viên được mượn về nhà tối đa 5 cuốn sách giáo trình/tham khảo trong cùng thời điểm; thời hạn mượn tối đa là 14 ngày và được gia hạn 1 lần thêm 7 ngày nếu không ai đặt trước. | `muon-tra-thu-vien-sinh-vien#1` (Điều 1) |
| 5 | Thủ tục và lệ phí xin phúc khảo bài thi kết thúc học phần như thế nào, trường hợp nào được hoàn tiền? | Sinh viên nộp đơn phúc khảo trong vòng 7 ngày làm việc kể từ ngày công bố điểm; lệ phí là 50.000 đồng/bài thi; được hoàn lại 100% lệ phí nếu kết quả sau phúc khảo có sự tăng điểm. | `phuc-khao-diem-thi#1` (Điều 1 & Điều 2) |

---

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Khối lượng tín chỉ & rút học phần | `HeadingChunker` | Có (Top-1) | Giữ trọn Điều 1 và Điều 2; trả lời đầy đủ số tín chỉ 14 và tuần thứ 4. |
| 2 | Hạn nộp học phí & miễn 100% | `HeadingChunker` | Có (Top-1) | Trích xuất chính xác mốc 17h thứ Sáu tuần 3 và diện hộ nghèo. |
| 3 | Điều kiện học bổng Xuất sắc | `HeadingChunker` / `SentenceChunker` | Có (Top-1) | Trả về chính xác các mốc GPA 3.60 và ĐRL 90 điểm. |
| 4 | Mượn trả sách thư viện *(có filter)* | `HeadingChunker` (với filter `student`) | Có (Top-1) | **Bắt buộc có filter**: Lọc bỏ hoàn toàn tài liệu giảng viên (120 ngày, 20 cuốn). |
| 5 | Lệ phí và hoàn tiền phúc khảo | `HeadingChunker` / `RecursiveChunker` | Có (Top-1) | Trích xuất chuẩn xác 50.000đ và điều kiện tăng điểm hoàn 100%. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> **Metadata filtering đóng vai trò quyết định, đặc biệt ở Câu hỏi 4.**
> Khi không áp dụng filter, truy vấn *"Thời hạn mượn sách thư viện tối đa là bao nhiêu ngày..."* nhận diện cả tài liệu thư viện của sinh viên lẫn giảng viên do trùng khớp hoàn toàn từ khóa "mượn sách thư viện". Do tài liệu giảng viên có độ dài và tần suất xuất hiện từ chuyên môn cao, nó dễ lọt vào top-1 khiến tác tử trả lời sai rằng người học được mượn 20 cuốn trong 120 ngày! Khi áp dụng `metadata_filter={"audience": "student"}`, hệ thống loại trừ triệt để tài liệu của giảng viên ngay từ bước tiền lọc, đảm bảo 100% kết quả trả về là quy định dành riêng cho sinh viên (tối đa 5 cuốn, thời hạn 14 ngày).

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
1. **Kiến trúc dữ liệu quyết định chất lượng RAG:** Cấu trúc tài liệu (Domain-specific Chunking) quan trọng hơn kích thước chunk thuần túy. Với tài liệu quy chế, việc chia theo `Heading` giữ trọn vẹn ngữ cảnh của từng điều luật, vượt trội hoàn toàn so với việc đếm ký tự máy móc.
2. **Sức mạnh của Tiền lọc Metadata (Pre-filtering):** Trong các hệ thống RAG phục vụ nhiều đối tượng (sinh viên, giảng viên, nhân viên), việc phân tách tài liệu kèm metadata và lọc trước khi tìm kiếm là giải pháp then chốt để chống hallucination và tránh trả lời nhầm chính sách.
3. **Thực nghiệm A/B rõ ràng:** Trình diễn trực quan sự khác biệt một trời một vực giữa việc truy xuất có và không có metadata filter trên câu hỏi mượn sách thư viện.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một bộ dữ liệu và câu hỏi, nhưng cách tiếp cận chia nhỏ khác nhau dẫn đến chất lượng truy xuất chênh lệch đáng kể: FixedSizeChunker dễ cắt đứt số liệu quan trọng nằm ở biên; SentenceChunker an toàn về ngữ pháp nhưng thiếu ngữ cảnh phân mục; RecursiveChunker cân bằng tốt; còn HeadingChunker là phương pháp tối ưu nhất cho văn bản quy phạm.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nếu triển khai tiếp, nhóm sẽ kết hợp **Hybrid Retrieval** (tích hợp tìm kiếm từ khóa chính xác BM25 cùng với Dense Vector Embedding) để vừa bắt đúng các con số định lượng (như "14 tín chỉ", "50.000 đồng"), vừa hiểu được sự đồng nghĩa ngôn từ; đồng thời tự động chèn Breadcrumb (tiêu đề cha/mẹ) vào đầu mọi chunk để tăng cường tính liên kết ngữ cảnh.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
