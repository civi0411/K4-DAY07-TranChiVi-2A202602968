# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Nhóm L3A-Team01 (Chủ đề: Dịch vụ & Quy định Đại học - Thư viện FPT)
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

### Phân tích đường cơ sở (Baseline Analysis)

Vĩ (Strategy Lead) đã chạy `ChunkingStrategyComparator().compare()` kết hợp thuật toán `HeadingChunker` trên 3 tài liệu đại diện của Thư viện FPT và chuyển giao số liệu cho Nhật (Report Lead):

| Tài liệu | Thành viên phụ trách | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|---|---|---|---|---|---|
| `fpt-muon-sach-sinh-vien.md` (916 ký tự) | Nhật | FixedSizeChunker (`fixed_size`, size=200, overlap=20) | 5 | 199.2 | Kém (bị ngắt giữa cụm từ số ngày mượn sách tiếng Việt và ngoại văn) |
| | Tuấn | SentenceChunker (`by_sentences`, max=3) | 4 | 227.8 | Khá (câu ngữ pháp nguyên vẹn, tách theo mục tốt) |
| | Khánh | RecursiveChunker (`recursive`, size=200) | 7 | 129.3 | Trung bình (cắt theo ranh giới dòng, chunk hơi ngắn) |
| | **Vĩ** | **HeadingChunker** (`heading_section`, size=400) | **4** | **229.0** | **Xuất sắc** (nguyên vẹn từng Mục điều khoản logic) |
| `fpt-phi-thu-vien.md` (901 ký tự) | Nhật | FixedSizeChunker (`fixed_size`, size=200, overlap=20) | 5 | 196.2 | Kém (cắt đứt cụm từ "5.000 VNĐ / tài liệu / ngày") |
| | Tuấn | SentenceChunker (`by_sentences`, max=3) | 2 | 449.0 | Tương đối (gộp chung cả mục phí phạt và cổng thanh toán FAP) |
| | Khánh | RecursiveChunker (`recursive`, size=200) | 6 | 149.0 | Khá (tách các mục độc lập) |
| | **Vĩ** | **HeadingChunker** (`heading_section`, size=400) | **4** | **225.2** | **Xuất sắc** (tách rành mạch Mục Phí phạt và Mục Cổng thanh toán) |
| `fpt-phong-hoc-nhom.md` (952 ký tự) | Nhật | FixedSizeChunker (`fixed_size`, size=200, overlap=20) | 6 | 175.3 | Kém (cắt ngang quy định hủy ca sau 15 phút) |
| | Tuấn | SentenceChunker (`by_sentences`, max=3) | 2 | 474.5 | Khá (giữ trọn vẹn câu điều kiện) |
| | Khánh | RecursiveChunker (`recursive`, size=200) | 8 | 117.6 | Trung bình (chia nhỏ các điều kiện) |
| | **Vĩ** | **HeadingChunker** (`heading_section`, size=400) | **4** | **238.0** | **Xuất sắc** (giữ trọn Điều kiện số người và Thời gian sử dụng) |

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
- **Loại chiến lược:** Tuned FixedSizeChunker (`fixed_size`, `chunk_size=250`, `overlap=40`)
- **Mô tả & lý do chọn:** Phương án so sánh đối chiếu có tối ưu overlap 40 ký tự nhằm kiểm tra xem việc cắt theo độ dài cố định có bị suy giảm chất lượng retrieval so với các chiến lược dựa trên cấu trúc hay không.

---

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|---|---|---|---|---|
| **Tuấn** | `SentenceChunker` (max 3 câu) | 7/10 | Giữ câu ngữ pháp trọn vẹn, độ tương đồng câu cao. | Dễ gom nhầm 2 mục khác nhau nếu các câu quá ngắn. |
| **Khánh** | `RecursiveChunker` (size 300) | 8/10 | Cân bằng kích thước tốt, tôn trọng cấu trúc đoạn văn `\n\n`. | Có thể cắt trúng giữa một danh sách điều kiện liệt kê. |
| **Vĩ (Trần Chí Vĩ)** | **`HeadingChunker`** (size 400) | **9/10** | **Tối ưu nhất**: Mỗi chunk là 1 Mục nghiệp vụ hoàn chỉnh, ngữ cảnh trọn vẹn 100%. | Phụ thuộc vào tài liệu có cấu trúc Markdown chuẩn (`#`, `##`). |
| **Nhật** | `FixedSizeChunker` (250/40) | 8/10 | Đơn giản, độ dài đồng nhất, có overlap giảm đứt gãy từ. | Vẫn cắt ngang câu ngẫu nhiên theo số ký tự, nhiễu ranh giới ngữ nghĩa. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> **Chiến lược `HeadingChunker` của Vĩ là tối ưu và phù hợp nhất** cho văn bản quy định thư viện. Lý do: mỗi điều khoản quy định (như hạn ngạch mượn, mức phí phạt, quy định hủy phòng học nhóm) được người soạn thảo đóng gói thành từng mục logic độc lập. `HeadingChunker` tôn trọng tuyệt đối ranh giới này, giúp các số liệu (10 tài liệu, 5.000 VNĐ, 2 giờ, 15 phút, 4 lượt) nằm trọn vẹn trong chunk, không bao giờ bị cắt rời khỏi tiêu đề điều khoản.


---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Sinh viên được mượn tối đa bao nhiêu tài liệu về nhà và thời hạn mượn sách tham khảo tiếng Việt, ngoại văn là bao lâu? | Sinh viên được mượn tối đa 10 tài liệu cùng lúc về nhà; sách tiếng Việt mượn 7 ngày; sách ngoại văn và song ngữ mượn 14 ngày. | `fpt-muon-sach-sinh-vien.md` (Mục 1 & Mục 3) |
| 2 | Hạn ngạch được phép mượn tài liệu về nhà tối đa là bao nhiêu cuốn cùng một lúc? *(Bắt buộc: `audience="student"`)* | 10 tài liệu đối với sinh viên (nếu là cán bộ giảng viên thì được mượn tối đa 20 tài liệu). | `fpt-muon-sach-sinh-vien.md` (Mục 1) |
| 3 | Mức phí phạt trả sách quá hạn mỗi ngày là bao nhiêu và có những phương thức thanh toán trực tuyến nào? | Phí phạt quá hạn là 5.000 VNĐ / tài liệu / ngày; có 2 phương thức thanh toán trực tuyến: qua ví FAP và qua cổng DNG (quét mã QR ngân hàng). | `fpt-phi-thu-vien.md` (Mục 1 & Mục 2) |
| 4 | Thời gian sử dụng phòng học nhóm tối đa là bao lâu mỗi ca và sau bao nhiêu phút không đến nhận phòng thì ca đặt sẽ bị hủy? | Thời gian sử dụng tối đa 2 giờ / ca (1 ca / nhóm / ngày); sau 15 phút kể từ giờ bắt đầu nếu nhóm không đến nhận phòng hoặc không đủ người tối thiểu thì ca đặt sẽ tự động bị hủy. | `fpt-phong-hoc-nhom.md` (Mục 2) |
| 5 | Mỗi cuốn sách được phép gia hạn tối đa mấy lượt và bạn đọc có thể thực hiện gia hạn qua những kênh nào? | Mỗi cuốn sách được phép gia hạn tối đa 4 lượt (nếu chưa có người đặt trước); gia hạn qua 4 kênh: cổng OPAC trực tuyến, gửi email, gọi điện thoại (024 6680 5912), hoặc nhắn tin qua Fanpage Thư viện FPTU. | `fpt-gia-han-tai-lieu.md` (Mục 1 & Mục 2) |

---

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Hạn ngạch & thời hạn mượn sách SV | `HeadingChunker` / `SentenceChunker` | Có (Top-1) | Trả về chính xác 10 cuốn, 7 ngày tiếng Việt, 14 ngày ngoại văn. |
| 2 | Hạn ngạch mượn tối đa *(có filter)* | `HeadingChunker` (với filter `student`) | Có (Top-1) | **Bắt buộc có filter**: Lọc bỏ hoàn toàn tài liệu giảng viên (20 cuốn). |
| 3 | Phí phạt quá hạn & thanh toán FAP/DNG | `HeadingChunker` | Có (Top-1) | Trích xuất chuẩn xác 5.000 VNĐ, ví FAP và cổng DNG. |
| 4 | Phòng học nhóm (2 giờ, hủy sau 15p) | `HeadingChunker` | Có (Top-1) | Trả về chuẩn xác ca 2 giờ và mốc 15 phút tự động hủy. |
| 5 | Lượt gia hạn & 4 kênh liên hệ | `HeadingChunker` / `SentenceChunker` | Có (Top-1) | Trích xuất đầy đủ 4 lượt gia hạn, OPAC, 024 6680 5912, Fanpage. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> **Metadata filtering mang tính sống còn ở Câu hỏi 2.**
> Khi đặt câu hỏi mơ hồ: *"Hạn ngạch được phép mượn tài liệu về nhà tối đa là bao nhiêu cuốn cùng một lúc?"*, trong cơ sở tri thức có 2 tài liệu cùng chủ đề:
> - Sinh viên (`fpt-muon-sach-sinh-vien.md`): 10 cuốn.
> - Giảng viên (`fpt-muon-sach-giang-vien.md`): 20 cuốn.
> Nếu **không lọc**, tài liệu của giảng viên xuất hiện ngay trong top-3 (score=0.299), khiến agent dễ trả lời nhầm hạn ngạch 20 cuốn cho sinh viên. Khi bật `metadata_filter={"audience": "student"}`, toàn bộ tài liệu giảng viên bị loại bỏ ngay từ bước tiền lọc, đảm bảo câu trả lời luôn trích xuất chính xác con số 10 cuốn dành cho sinh viên.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
1. **Kiến trúc dữ liệu quyết định chất lượng RAG:** Cấu trúc tài liệu (Domain-specific Heading Chunking) vượt trội hơn chia nhỏ ngẫu nhiên theo ký tự. Với văn bản quy định, mỗi Mục là một đơn vị ý nghĩa khép kín.
2. **Sức mạnh của Tiền lọc Metadata (Pre-filtering):** Phân chia rõ `audience` giúp giải quyết triệt để vấn đề xung đột hạn ngạch giữa sinh viên (10 cuốn) và giảng viên (20 cuốn).
3. **Thực nghiệm A/B trực quan:** Demo trực tiếp tại quầy phản biện: so sánh câu hỏi 2 khi bật và tắt filter để giảng viên thấy rõ sự khác biệt trong kết quả top-k.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng bộ dữ liệu Thư viện FPT, chiến lược FixedSize bị cắt cụm từ quan trọng (5.000 VNĐ, 15 phút); SentenceChunker an toàn về ngữ pháp nhưng đôi khi gộp 2 mục khác nhau; HeadingChunker là giải pháp hoàn hảo nhất cho văn bản có cấu trúc quy chế.

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
